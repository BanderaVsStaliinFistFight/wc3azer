"""Small numpy raster toolkit: fractal noise, blurs, distance fields, shapes."""
import numpy as np
from PIL import Image, ImageDraw


class Field:
    """Grid of tilepoints; coordinates are tile units with (0, 0) at the south-west corner."""

    def __init__(self, width, height, seed):
        self.w, self.h = width, height
        self.ys, self.xs = np.mgrid[0:height, 0:width].astype(np.float64)
        self.rng = np.random.default_rng(seed)

    # -- noise ------------------------------------------------------------
    def value_noise(self, cell, xs=None, ys=None):
        """Smooth value noise in [-1, 1] with feature size `cell` tiles."""
        xs = self.xs if xs is None else xs
        ys = self.ys if ys is None else ys
        gw = int(np.ceil((self.w + 2 * cell) / cell)) + 3
        gh = int(np.ceil((self.h + 2 * cell) / cell)) + 3
        lattice = self.rng.uniform(-1, 1, (gh, gw))
        fx = np.clip((xs + cell) / cell, 0, gw - 2.0001)
        fy = np.clip((ys + cell) / cell, 0, gh - 2.0001)
        x0, y0 = np.floor(fx).astype(int), np.floor(fy).astype(int)
        tx, ty = fx - x0, fy - y0
        tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
        a = lattice[y0, x0] * (1 - tx) + lattice[y0, x0 + 1] * tx
        b = lattice[y0 + 1, x0] * (1 - tx) + lattice[y0 + 1, x0 + 1] * tx
        return a * (1 - ty) + b * ty

    def fbm(self, cell, octaves=4, gain=0.5, xs=None, ys=None):
        total, amp, norm = 0.0, 1.0, 0.0
        for o in range(octaves):
            total = total + amp * self.value_noise(cell / (2 ** o), xs, ys)
            norm += amp
            amp *= gain
        return total / norm

    def ridged(self, cell, octaves=4, xs=None, ys=None):
        """Ridged multifractal in [0, 1]: sharp crests, useful for mountains."""
        total, amp, norm = 0.0, 1.0, 0.0
        for o in range(octaves):
            n = 1.0 - np.abs(self.value_noise(cell / (2 ** o), xs, ys))
            total = total + amp * n * n
            norm += amp
            amp *= 0.5
        return total / norm

    # -- shapes -----------------------------------------------------------
    def polygon_mask(self, points, supersample=1):
        img = Image.new('L', (self.w * supersample, self.h * supersample), 0)
        ImageDraw.Draw(img).polygon([(x * supersample, y * supersample) for x, y in points], fill=255)
        m = np.asarray(img) > 127
        if supersample > 1:
            m = m.reshape(self.h, supersample, self.w, supersample).mean(axis=(1, 3)) > 0.5
        return m

    def segment_distance(self, points, closed=False, reach=None):
        """Distance (tiles) from every tilepoint to a polyline; with `reach`, only measured that far out (inf beyond)."""
        pts = list(points) + ([points[0]] if closed else [])
        best = np.full((self.h, self.w), np.inf)
        for (ax, ay), (bx, by) in zip(pts[:-1], pts[1:]):
            if reach is None:
                y0, y1, x0, x1 = 0, self.h, 0, self.w
            else:
                x0, x1 = int(max(min(ax, bx) - reach, 0)), int(min(max(ax, bx) + reach + 1, self.w))
                y0, y1 = int(max(min(ay, by) - reach, 0)), int(min(max(ay, by) + reach + 1, self.h))
                if x0 >= x1 or y0 >= y1:
                    continue
            xs, ys = self.xs[y0:y1, x0:x1], self.ys[y0:y1, x0:x1]
            dx, dy = bx - ax, by - ay
            l2 = dx * dx + dy * dy or 1e-9
            t = np.clip(((xs - ax) * dx + (ys - ay) * dy) / l2, 0, 1)
            d = np.hypot(xs - (ax + t * dx), ys - (ay + t * dy))
            np.minimum(best[y0:y1, x0:x1], d, out=best[y0:y1, x0:x1])
        return best

    def polyline_along(self, points):
        """Distance (tiles) to a polyline, and how far along it (0 at its first point, 1 at its last) the nearest point lies."""
        best = np.full((self.h, self.w), np.inf)
        along = np.zeros((self.h, self.w))
        lengths = [float(np.hypot(bx - ax, by - ay)) for (ax, ay), (bx, by) in zip(points[:-1], points[1:])]
        total = sum(lengths) or 1e-9
        start = 0.0
        for ((ax, ay), (bx, by)), seg in zip(zip(points[:-1], points[1:]), lengths):
            x0, x1 = int(max(min(ax, bx) - 12, 0)), int(min(max(ax, bx) + 13, self.w))
            y0, y1 = int(max(min(ay, by) - 12, 0)), int(min(max(ay, by) + 13, self.h))
            xs, ys = self.xs[y0:y1, x0:x1], self.ys[y0:y1, x0:x1]
            dx, dy = bx - ax, by - ay
            t = np.clip(((xs - ax) * dx + (ys - ay) * dy) / (seg * seg or 1e-9), 0, 1)
            d = np.hypot(xs - (ax + t * dx), ys - (ay + t * dy))
            closer = d < best[y0:y1, x0:x1]
            best[y0:y1, x0:x1] = np.where(closer, d, best[y0:y1, x0:x1])
            along[y0:y1, x0:x1] = np.where(closer, (start + t * seg) / total, along[y0:y1, x0:x1])
            start += seg
        return best, along

    def polygon_sdf(self, points):
        """Signed distance to a polygon outline: positive inside."""
        inside = self.polygon_mask(points)
        d = self.segment_distance(points, closed=True)
        return np.where(inside, d, -d)

    def ellipse_sdf(self, cx, cy, rx, ry, angle=0.0):
        dx, dy = self.xs - cx, self.ys - cy
        if angle:
            c, s = np.cos(angle), np.sin(angle)
            dx, dy = dx * c + dy * s, -dx * s + dy * c
        return (1.0 - np.hypot(dx / rx, dy / ry)) * min(rx, ry)

    def distance(self, cx, cy):
        return np.hypot(self.xs - cx, self.ys - cy)


# -- whole-array helpers ---------------------------------------------------
def shift(a, dx, dy, fill):
    out = np.full_like(a, fill)
    h, w = a.shape
    ys = slice(max(dy, 0), h + min(dy, 0)); yd = slice(max(-dy, 0), h + min(-dy, 0))
    xs = slice(max(dx, 0), w + min(dx, 0)); xd = slice(max(-dx, 0), w + min(-dx, 0))
    out[ys, xs] = a[yd, xd]
    return out


NEIGHBOURS8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]


def distance_field(mask, max_dist=64):
    """Approximate Euclidean distance (tiles) from every point to the nearest True cell."""
    d = np.where(mask, 0.0, np.inf)
    steps = [(dx, dy, np.hypot(dx, dy)) for dx, dy in NEIGHBOURS8]
    for _ in range(int(max_dist)):
        prev = d
        for dx, dy, cost in steps:
            d = np.minimum(d, shift(d, dx, dy, np.inf) + cost)
        if np.array_equal(prev, d):
            break
    return np.minimum(d, max_dist)


def box_blur(a, radius):
    if radius <= 0:
        return a.astype(np.float64)
    a = a.astype(np.float64)
    k = 2 * radius + 1
    for axis in (0, 1):
        pad = [(0, 0), (0, 0)]
        pad[axis] = (radius + 1, radius)
        c = np.cumsum(np.pad(a, pad, mode='edge'), axis=axis)
        if axis == 0:
            a = (c[k:, :] - c[:-k, :]) / k
        else:
            a = (c[:, k:] - c[:, :-k]) / k
    return a


def blur(a, radius, passes=3):
    for _ in range(passes):
        a = box_blur(a, radius)
    return a


def dilate(mask, steps=1):
    for _ in range(steps):
        out = mask.copy()
        for dx, dy in NEIGHBOURS8:
            out |= shift(mask, dx, dy, False)
        mask = out
    return mask


def erode(mask, steps=1):
    return ~dilate(~mask, steps)


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def label_regions(mask):
    """Label 4-connected areas of a boolean grid; returns (labels with -1 off the mask, sizes)."""
    h, w = mask.shape
    label = -np.ones((h, w), np.int64)
    sizes = []
    for sy, sx in np.argwhere(mask):
        if label[sy, sx] >= 0:
            continue
        cid, stack, count = len(sizes), [(sy, sx)], 0
        label[sy, sx] = cid
        while stack:
            y, x = stack.pop()
            count += 1
            for yy, xx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                if 0 <= yy < h and 0 <= xx < w and mask[yy, xx] and label[yy, xx] < 0:
                    label[yy, xx] = cid
                    stack.append((yy, xx))
        sizes.append(count)
    return label, np.array(sizes + [0])


def meander(points, amplitude, wavelength, rng, step=1.0):
    """Densify a polyline and let it wander from side to side, keeping its two ends in place."""
    dense = []
    for (ax, ay), (bx, by) in zip(points[:-1], points[1:]):
        k = max(1, int(np.hypot(bx - ax, by - ay) / step))
        dense += [(ax + (bx - ax) * i / k, ay + (by - ay) * i / k) for i in range(k)]
    dense.append(tuple(points[-1]))
    if len(dense) < 3:
        return dense
    pts = np.array(dense, dtype=np.float64)
    seg = np.hypot(*np.diff(pts, axis=0).T)
    s = np.concatenate([[0.0], np.cumsum(seg)])
    total = s[-1] or 1e-9
    phases = rng.uniform(0, 2 * np.pi, 3)
    wave = (np.sin(2 * np.pi * s / wavelength + phases[0]) + 0.5 * np.sin(2 * np.pi * s / (wavelength * 0.43) + phases[1])
            + 0.3 * np.sin(2 * np.pi * s / (wavelength * 2.3) + phases[2])) / 1.8
    taper = np.clip(np.minimum(s, total - s) / 4.0, 0, 1)
    tangent = np.gradient(pts, axis=0)
    tangent /= np.maximum(np.hypot(*tangent.T), 1e-9)[:, None]
    normal = np.stack([-tangent[:, 1], tangent[:, 0]], axis=1)
    out = pts + normal * (wave * amplitude * taper)[:, None]
    return [tuple(p) for p in out]


def flow_accumulation(height, mask):
    """Upstream area (in points) draining through each point of `mask`, water running to the lowest of its 8 neighbours."""
    h, w = height.shape
    big = np.where(mask, height, -1e9)
    best = big.copy()
    receiver = -np.ones((h, w), np.int64)
    idx = np.arange(h * w).reshape(h, w)
    for dx, dy in NEIGHBOURS8:
        nb = shift(big, dx, dy, 1e9)
        nb_idx = shift(idx, dx, dy, -1)
        lower = (nb < best) & mask & (nb_idx >= 0)
        best = np.where(lower, nb, best)
        receiver = np.where(lower, nb_idx, receiver)
    order = np.argsort(-big, axis=None)
    acc = np.where(mask, 1.0, 0.0).ravel().tolist()
    rec = receiver.ravel().tolist()
    for i in order[:int(mask.sum())].tolist():
        r = rec[i]
        if r >= 0:
            acc[r] += acc[i]
    return np.array(acc).reshape(h, w)
