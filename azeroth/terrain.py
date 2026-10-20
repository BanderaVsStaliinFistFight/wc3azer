"""Rasterises the geography into Warcraft III terrain data (480 x 480 tiles)."""
import math

import numpy as np

from . import geography as geo
from .biomes import B, CLIFF_DIRT, CLIFF_SNOW, GROUND_TILES, TILE
from .raster import (Field, blur, dilate, distance_field, erode, flow_accumulation, label_regions, meander, shift,
                     smoothstep, NEIGHBOURS8)

MAP_W = MAP_H = 480                  # tiles; the largest map size Warcraft III supports
RANGE_WIDTH, RANGE_HEIGHT = 1.45, 1.5  # mountain ranges relative to geography.RIDGES
MASSIF_HEIGHT = 0.9                  # scale of geography.MASSIFS heights
HILL_SCALE = 2.5                     # rolling hills relative to the biome `hills` amplitudes
INLAND_RISE = 90                     # how much higher the heart of a landmass stands than its shores
FOREST_DENSITY = 1.45                # forest cover relative to the biome densities
MARGIN_L, MARGIN_R, MARGIN_B, MARGIN_T = 6, 6, 4, 8
LEFT = BOTTOM = -MAP_W * 64.0        # world coordinate of the south-west tilepoint
WATER_RAW = 0x2000                   # default water level; surface sits at z = -89.6
SEA_Z = -89.6
DEEP_WATER = 0.40 * 128              # deeper than this is impassable for ground units

# Distribution of tile variations produced by the World Editor's random brush.
VARIATION_WEIGHTS = [605, 76, 27, 3, 663, 80, 33, 2, 613, 70, 28, 13, 599, 82, 27, 5, 697, 602]


class Terrain:
    pass


# Harsh neighbours and the ground that bridges them, as a careful hand blends a palette: grass
# gives way to snow through snowy grass, to sand through grassy earth and to lava through rough
# earth; sand meets snow across bare earth.
GRASSES = ('Lgrs', 'Lgrd', 'Vgrt', 'Fgrs')
BRIDGES = [(GRASSES, ('Wsnw',), 'Wsng'), (GRASSES, ('Bdsr',), 'Ldrg'), (GRASSES, ('Dlvc',), 'Ldro'),
           (('Bdsr',), ('Wsnw',), 'Ldrt')]


def soften_contrasts(tex, free, noise, both_sides=False):
    """Where two harsh grounds meet, the softer one turns to the bridging ground for a ragged
    point or two along the border, so no bright grass lies straight against snow, sand or lava.
    With both_sides, a harsh point still touching the softer ground (one that could not change,
    such as a corner the game draws with its cliff's own ground) turns to the bridge instead."""
    for soft, hard, bridge in BRIDGES:
        a = np.isin(tex, [TILE[t] for t in soft])
        b = np.isin(tex, [TILE[t] for t in hard])
        tex = np.where(a & free & (dilate(b, 1) | (dilate(b, 2) & (noise > 0.1))), TILE[bridge], tex)
        if both_sides:
            a = np.isin(tex, [TILE[t] for t in soft])
            tex = np.where(b & free & dilate(a, 1), TILE[bridge], tex)
    return tex


def nearest_on(line, p):
    """Nearest point of a polyline to p, and its distance."""
    a, b = np.asarray(line[:-1], float), np.asarray(line[1:], float)
    d = b - a
    t = np.clip(((p[0] - a[:, 0]) * d[:, 0] + (p[1] - a[:, 1]) * d[:, 1]) / np.maximum((d ** 2).sum(1), 1e-9), 0, 1)
    q = a + d * t[:, None]
    dist = np.hypot(q[:, 0] - p[0], q[:, 1] - p[1])
    k = int(dist.argmin())
    return (float(q[k, 0]), float(q[k, 1])), float(dist[k])


def road_networks(lines):
    """Group the roads (by index) into networks of roads that meet."""
    idx = [i for i, l in enumerate(lines) if len(l) > 1]
    box = {i: (min(p[0] for p in lines[i]) - 1, min(p[1] for p in lines[i]) - 1,
               max(p[0] for p in lines[i]) + 1, max(p[1] for p in lines[i]) + 1) for i in idx}
    parent = {i: i for i in idx}

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for k, a in enumerate(idx):
        for b in idx[k + 1:]:
            (ax0, ay0, ax1, ay1), (bx0, by0, bx1, by1) = box[a], box[b]
            if ax0 > bx1 or bx0 > ax1 or ay0 > by1 or by0 > ay1 or find(a) == find(b):
                continue
            la, lb = lines[a], lines[b]
            if min(nearest_on(lb, la[0])[1], nearest_on(lb, la[-1])[1], nearest_on(la, lb[0])[1], nearest_on(la, lb[-1])[1]) < 1.0:
                parent[find(a)] = find(b)
    nets = {}
    for i in idx:
        nets.setdefault(find(i), []).append(i)
    return list(nets.values())


def split_at_sea(lines, open_sea, max_run=3):
    """Roads stop at the shore: wherever a road would run on over more than `max_run` points of open
    sea it is cut there, and each side ends at its own shore. (Shorter clips across a cove are
    forded.)"""
    out = []
    for line in lines:
        wet = [bool(open_sea[min(max(int(round(y)), 0), open_sea.shape[0] - 1),
                             min(max(int(round(x)), 0), open_sea.shape[1] - 1)]) for x, y in line]
        piece, k = [], 0
        while k < len(line):
            run = 0
            while k + run < len(line) and wet[k + run]:
                run += 1
            if run > max_run:
                if len(piece) > 1:
                    out.append(piece)
                piece, k = [], k + run
            else:
                piece += line[k:k + max(run, 1)]
                k += max(run, 1)
        if len(piece) > 1:
            out.append(piece)
    return out


def link_networks(lines, ground, rng, reach=28.0):
    """Join road networks left apart to their nearest neighbour by a short new road from a dead end,
    wherever one can be laid over open ground clear of the great ranges (so not across the sea).
    Where the straight way would cross water, the road bends round it through a waypoint off to
    one side, as a road skirts a bay or finds the neck of land between two shores."""
    lines = list(lines)

    def route(p, q):
        clear = lambda a, b: overland(ground, a, b) and not geo._near_massif(a, b)
        if clear(p, q):
            return [p, q]
        d = math.hypot(q[0] - p[0], q[1] - p[1]) or 1.0
        nx, ny = -(q[1] - p[1]) / d, (q[0] - p[0]) / d
        for k in (3, -3, 6, -6, 9, -9, 12, -12):
            v = ((p[0] + q[0]) / 2 + nx * k, (p[1] + q[1]) / 2 + ny * k)
            if clear(p, v) and clear(v, q):
                return [p, v, q]
        return None

    while True:
        nets = road_networks(lines)
        cands = []
        for a, net in enumerate(nets):
            for p in [lines[i][k] for i in net for k in (0, -1)]:
                for b, other in enumerate(nets):
                    if b == a:
                        continue
                    for j in other:
                        q, d = nearest_on(lines[j], p)
                        if d <= reach:
                            cands.append((d, p, q))
        way = next((w for w in (route(p, q) for d, p, q in sorted(cands, key=lambda c: c[0])) if w), None)
        if way is None:
            break
        lines.append(meander(way, 0.8, 17, rng))
    # a stray stub of road a few tiles long, meeting no other (a track from an offshore camp down
    # to its shore), is left out
    nets = road_networks(lines)
    stubs = {net[0] for net in nets if len(net) == 1 and
             sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(lines[net[0]], lines[net[0]][1:])) < 10}
    return [l for i, l in enumerate(lines) if i not in stubs]


def overland(ground, p, q):
    """True if the straight way from p to q stays on `ground`."""
    k = max(2, int(math.hypot(q[0] - p[0], q[1] - p[1]) * 2))
    return all(ground[int(round(p[1] + (q[1] - p[1]) * t / k)), int(round(p[0] + (q[0] - p[0]) * t / k))]
               for t in range(k + 1))


def join_roads(lines, keep, ground, reach=3.5):
    """Carry each road's end the last stretch onto the road it was laid to meet, over the ground:
    once the roads wander, a road no longer passes exactly through the point where another was set
    to join it. Lines for which keep(line) is true (closed rings) are left be."""
    out = [list(l) for l in lines]
    for i, line in enumerate(out):
        if keep(line) or len(line) < 2:
            continue
        for at_start in (True, False):
            end = line[0] if at_start else line[-1]
            best = min((nearest_on(o, end) for j, o in enumerate(out) if j != i and len(o) > 1), key=lambda r: r[1])
            if 0.3 < best[1] < reach and overland(ground, end, best[0]):
                line.insert(0, best[0]) if at_start else line.append(best[0])
    return [[tuple(p) for p in l] for l in out]


def tidy_paint(tex, free, rounds=2):
    """Paint the way a careful hand would: a point whose texture has at most one neighbour of its
    own kind (a speck, or a ragged one-point fringe along a border) takes the texture most common
    round it. Only points in `free` change."""
    for _ in range(rounds):
        kinds = np.unique(tex)
        counts = np.stack([sum(shift(tex == k, dx, dy, False).astype(np.int8) for dx in (-1, 0, 1) for dy in (-1, 0, 1))
                           for k in kinds])
        own = np.take_along_axis(counts, np.searchsorted(kinds, tex)[None], 0)[0]
        change = free & (own <= 2) & (counts.max(0) >= 4)
        tex = np.where(change, kinds[counts.argmax(0)], tex)
    return tex


def build(seed=1):
    T = Terrain()
    f = Field(MAP_W + 1, MAP_H + 1, seed)
    T.field = f
    xs, ys = f.xs, f.ys
    n = MAP_W + 1

    # ---- 1. landmasses ---------------------------------------------------
    names = list(geo.LANDMASSES)
    land_sd = np.full((n, n), -1e9)
    land_id = np.full((n, n), -1, dtype=np.int32)
    amp_by_land = []
    for idx, name in enumerate(names):
        shape = geo.LANDMASSES[name]
        if shape[0] == 'ellipse':
            _, cx, cy, rx, ry = shape
            sd = f.ellipse_sdf(cx, cy, rx, ry)
            size = min(rx, ry)
        else:
            sd = f.polygon_sdf(shape)
            size = 30
        amp_by_land.append(min(1.0, size / 9.0) * geo.COAST_NOISE.get(name, 1.0))
        better = sd > land_sd
        land_sd[better] = sd[better]
        land_id[better] = idx
    coast_noise = f.fbm(30, 3) * 6.0 + f.fbm(12, 4) * 3.5 + f.fbm(4, 2) * 1.2
    amp = np.array(amp_by_land)[land_id]
    sd = land_sd + coast_noise * amp
    playable = (xs >= MARGIN_L + 3) & (xs <= MAP_W - MARGIN_R - 3) & (ys >= MARGIN_B + 3) & (ys <= MAP_H - MARGIN_T - 3)
    land = (sd > 0) & playable
    # tidy single-tile specks
    land = dilate(erode(land, 1), 1) | (land & (land_sd > 2))
    land &= playable
    inlet_noise = f.fbm(5, 2) * 0.4
    for line, width in getattr(geo, 'SEA_INLETS', []):
        land &= ~(f.segment_distance(line) < width + inlet_noise)
    land &= dilate(erode(land, 1), 1)          # drop one-tile slivers the inlets leave behind
    T.land_names = names
    T.land_id = land_id

    # ---- 2. inland water ---------------------------------------------------
    # Rivers wind from side to side, widen towards the mouth and rise from a pond where no lake feeds them.
    bends = np.random.default_rng(seed * 7 + 3)
    T.river_lines = [meander(line, 2.2, 13, bends) for line in geo.RIVERS]
    ponds = [(line[0][0], line[0][1], 2.2, 1.8) for line in geo.RIVERS
             if all(np.hypot(line[0][0] - cx, line[0][1] - cy) > max(rx, ry) + 3 for cx, cy, rx, ry in geo.LAKES)]
    lake_sd = np.full((n, n), -1e9)
    for cx, cy, rx, ry in list(geo.LAKES) + ponds:
        lake_sd = np.maximum(lake_sd, f.ellipse_sdf(cx, cy, rx, ry))
    lake_noise = f.fbm(5, 3)
    lake = (lake_sd + lake_noise * 1.2 > 0) & land
    river_d = np.full((n, n), 1e9)
    river_w = np.zeros((n, n))
    for line in T.river_lines:
        d, along = f.polyline_along(line)
        closer = d < river_d
        river_d = np.where(closer, d, river_d)
        river_w = np.where(closer, 0.75 + 1.4 * along, river_w)
    river = (river_d < river_w + f.fbm(6, 2) * 0.4) & land
    shallow_d = np.full((n, n), 1e9)
    for line in geo.SHALLOWS:
        shallow_d = np.minimum(shallow_d, f.segment_distance(line))
    shallow_strait = shallow_d < 3.2
    land &= ~(lake | river)
    T.land = land
    water = ~land

    # ---- 3. zones ------------------------------------------------------------
    wx = f.fbm(30, 3) * 10 + f.fbm(10, 2) * 3
    wy = f.fbm(30, 3) * 10 + f.fbm(10, 2) * 3
    best = np.full((n, n), 1e9)
    best_any = np.full((n, n), 1e9)
    zone_of = np.zeros((n, n), dtype=np.int32)
    zone_any = np.zeros((n, n), dtype=np.int32)
    land_index = {name: i for i, name in enumerate(names)}
    for zi, z in enumerate(geo.ZONES):
        d = np.hypot((xs + wx - z['cx']) / z['rx'], (ys + wy - z['cy']) / z['ry'])
        on_land = land_id == land_index[z['land']]
        dz = np.where(on_land, d, d + 1000)
        b = dz < best
        best[b] = dz[b]
        zone_of[b] = zi
        b2 = d < best_any
        best_any[b2] = d[b2]
        zone_any[b2] = zi
    zone_of = np.where(land | lake | river, zone_of, zone_any)
    T.zone_of = zone_of

    def zone_prop(key, default=None):
        vals = []
        for z in geo.ZONES:
            vals.append(z.get(key, B[z['biome']].get(key, default)))
        return np.array(vals, dtype=np.float64)[zone_of]

    base = blur(zone_prop('base'), 3)
    hills = blur(zone_prop('hills'), 3)
    mountains = blur(zone_prop('mountains'), 3)

    # Roads wander a little, except closed rings.
    wander = np.random.default_rng(seed * 11 + 5)
    T.road_lines = [line if line[0] == line[-1] else meander(line, 1.1, 17, wander) for line in geo.ROADS]
    T.road_lines = split_at_sea(T.road_lines, ~(land | lake | river) & ~shallow_strait)
    T.road_lines = join_roads(T.road_lines, lambda l: l[0] == l[-1], land | lake | river | shallow_strait)
    T.road_lines = link_networks(T.road_lines, land | lake | river, wander)
    road_d = np.full((n, n), 1e9)
    for line in T.road_lines:
        road_d = np.minimum(road_d, f.segment_distance(line, reach=30))
    T.road_d = road_d
    pass_factor = smoothstep(2.5, 6.0, road_d)       # roads cut passes through ridges
    # settlements, camps and landmarks keep the mountains at arm's length and stand in a levelled clearing
    flat_spots = [(c[2], c[3], 14) for c in geo.CAPITALS] + [(t[1], t[2], 5) for t in geo.TOWNS + geo.CAMPS]
    flat_spots += [(l[1], l[2], 6) for l in geo.LANDMARKS]
    clearing = np.zeros((n, n))
    for tx, ty, r in flat_spots:
        d = f.distance(tx, ty)
        pass_factor = np.minimum(pass_factor, smoothstep(r, r + 7, d))
        clearing = np.maximum(clearing, smoothstep(r + 5, r, d))

    # Natural lakes scattered over the interiors, clear of roads, settlements and the great ranges.
    T.lake_sites = scatter_lakes(f, land, zone_of, road_d, flat_spots, list(geo.LAKES) + ponds, seed)
    new_lake = np.zeros((n, n), bool)
    for cx, cy, rx, ry, angle in T.lake_sites:
        new_lake |= f.ellipse_sdf(cx, cy, rx, ry, angle) + lake_noise * 1.0 > 0
    new_lake &= land
    lake |= new_lake
    land &= ~new_lake
    T.land = land
    water = ~land

    # ---- 4. heights (relative to the water surface) ---------------------------
    dc = distance_field(water, 40)                 # inland distance from any water
    dw = distance_field(land, 40)                  # distance from land, out at sea
    hill_n = f.fbm(18, 5) * 0.5 + 0.5
    knolls = f.fbm(7, 3) * 0.5 + 0.5                                # smaller hills riding on the big ones
    hills = hills * HILL_SCALE
    ridge_n = f.ridged(34, 5)
    detail = f.fbm(5, 2)
    z = (base + hills * (hill_n + 0.6 * knolls) * (0.4 + 0.6 * pass_factor) + mountains * ridge_n ** 2 * pass_factor
         + detail * 8 + INLAND_RISE * smoothstep(3, 40, dc))
    # Mountain ranges: a broad massif along each ridge line, broken into peaks,
    # saddles and spurs by ridged noise, rising out of a skirt of foothills.
    ridge_h = np.zeros((n, n))
    foothills = np.zeros((n, n))
    rough = f.fbm(9, 3)
    crest = f.ridged(11, 4)
    folds = np.random.default_rng(seed * 13 + 7)                  # no mountain range runs ruler-straight
    summits = np.random.default_rng(seed * 19 + 1)
    for line, width, height in geo.RIDGES:
        w = width * RANGE_WIDTH
        crest_line = meander(line, 2.0, 18, folds, step=2.0)
        d = f.segment_distance(crest_line, reach=w * 4 + 4) + rough * 2.2
        shape = np.maximum(np.clip(1 - d / (w * 2.0), 0, 1) ** 1.3 * 0.7, peaks(f, crest_line, w * 2.0, summits, rough))
        ridge_h = np.maximum(ridge_h, shape * height * RANGE_HEIGHT * (0.6 + 0.5 * crest))
        foothills = np.maximum(foothills, smoothstep(w * 3.6, w * 1.2, d) * height * 0.22)
    z = np.maximum(z + foothills * hill_n * pass_factor, base * 0.6 + ridge_h * pass_factor)
    # Massifs: the great ranges, broad and towering, only broken where a road finds its pass.
    # Each is a chain of steep summits strung along its crest with saddles between them, so the
    # range ends in peaks rather than a level top.
    massif_h = np.zeros((n, n))
    massif_d = np.full((n, n), 1e9)            # distance from the crest in half-widths
    for line, width, height in geo.MASSIFS:
        crest_line = meander(line, 2.5, 20, folds, step=2.0)
        d = f.segment_distance(crest_line, reach=width * 3 + 4) + rough * 2.5
        shape = np.maximum(np.clip(1 - d / (width * 2.3), 0, 1) ** 1.2 * 0.66, peaks(f, crest_line, width * 2.3, summits, rough))
        massif_h = np.maximum(massif_h, shape * height * MASSIF_HEIGHT * (0.85 + 0.25 * crest))
        massif_d = np.minimum(massif_d, d / width)
    z = np.maximum(z, base * 0.6 + massif_h * pass_factor)
    in_massif = massif_d < 2.6
    for cx, cy, r, depth in geo.BASINS:
        d = f.distance(cx, cy)
        z -= depth * smoothstep(r * 1.4, r * 0.5, d)
    z = z + f.fbm(45, 3) * 35                                       # broad swells, so the plains are never flat
    z = np.maximum(z, 12)

    # Erosion: water running off the land gathers into streams that cut a branching
    # network of valleys, shallow in the lowlands and deep gullies in the mountains.
    route = blur(z, 2) + dc * 3.0 + f.fbm(25, 4) * 25
    flow = flow_accumulation(route, land)
    T.flow = flow
    carve = np.clip(6.0 * flow ** 0.45, 0, 140) * (0.55 + 0.45 * smoothstep(10, 260, z - base))
    z = np.maximum(z - blur(carve, 1), 12)
    upland = blur(z, 4)                                              # how high the land behind each shore stands

    # Coasts: shores that slope down into shallow water wherever low or rolling land meets the sea,
    # sea cliffs only where high ground does (headlands, mountains), and beaches
    # wherever units must reach the water (see geography.BEACHES).
    beach_src = np.zeros((n, n), bool)
    for line in geo.SHALLOWS:
        beach_src |= f.segment_distance(line) < 7
    beach_src |= river_d < 4
    beach_src |= dilate(lake, 2)                                     # lakes lie in hollows with gentle shores
    for name, tx, ty, building in geo.TOWNS:
        if building == 'nshp':
            beach_src |= f.distance(tx, ty) < 6
    for tx, ty, r in geo.BEACHES:
        beach_src |= f.distance(tx, ty) < r
    for name in geo.BEACH_ISLANDS:
        beach_src |= (land_id == land_index[name]) & (land_sd > -6)
    coast_pts = land & (dc <= 1)
    beach_noise = f.fbm(22, 3)
    beach_src |= coast_pts & (upland < 160 + beach_noise * 60)       # lowland and hill coasts slope into the sea
    for line, gates in getattr(geo, 'WALLS', []):      # no wading round the end of a wall
        beach_src &= f.segment_distance(line) > 10
    cliffy = smoothstep(2.0, 6.0, distance_field(beach_src, 12))      # 0 on beaches, 1 on cliff coasts
    T.beach = cliffy < 0.5
    coast_level = 14 + 70 * blur(cliffy, 1)
    coast_ramp = smoothstep(0.0, 8.0, dc)
    z = coast_level + (z - coast_level) * coast_ramp + detail * 3 * coast_ramp

    # Terraces: high relief away from roads and coasts becomes stepped cliff levels;
    # the ground offset keeps a gentler, continuous copy of the relief.
    relief = np.maximum(z - base, 0)
    T.relief = relief
    ledge = relief * pass_factor + f.fbm(13, 3) * 90           # ragged ledges rather than contour rings
    terrace = np.clip(np.floor((ledge - 200) / 230) + 1, 0, 3).astype(np.int32)
    keep_flat = (dc <= 4) | (road_d < 6) | (distance_field(lake | river, 4) < 4)
    for tx, ty, r in flat_spots:
        keep_flat |= f.distance(tx, ty) < r
    terrace[keep_flat] = 0
    terrace = np.minimum(terrace, np.floor((road_d - 6) / 2.5).clip(0, 5).astype(np.int32))   # step up away from roads
    tidy = np.zeros_like(terrace)
    for k in (1, 2, 3, 4, 5):                                  # no one-tile slivers of ledge
        tidy += dilate(erode(terrace >= k, 1), 1) & (tidy >= k - 1)
    terrace = tidy
    # only mountains are compressed, the massifs less so: their upper slopes climb to the summits
    # as open ground rather than more cliff bands, so they end in peaks, not ledges
    z = np.where(z > base + 180, base + 180 + (z - base - 180) * np.where(in_massif, 0.85, 0.65), z)
    z = z + (blur(z, 3) - z) * clearing * 0.85
    # Crowns: the top level of every terraced hill and mountain keeps rising from its rim towards
    # the middle, so it ends in a rounded crown or a peak rather than a flat table. (Ledges with
    # a higher level above them stay as they are, so no cliff face loses its height.)
    rim_d = np.zeros((n, n))
    for k in (1, 2, 3):
        lab, sizes = label_regions(terrace == k)
        if not len(sizes):
            continue
        under = np.unique(lab[dilate(terrace > k, 1) & (lab >= 0)])
        top = (lab >= 0) & ~np.isin(lab, under)
        rim_d = np.where(top, distance_field(~top, 40), rim_d)
    z = z + np.minimum(40 * rim_d ** 1.1, 560) * (0.6 + 0.6 * crest)

    sea = water & ~lake & ~river
    z_sea = -(16 + 30 * np.minimum(dw, 9)) + f.fbm(10, 2) * 10
    rim = dw <= 2.0 + f.fbm(7, 2) * 2.0                          # light shelf of shallows under the cliffs
    z_sea = np.where(rim, np.maximum(z_sea, -30 - 5 * dw), z_sea)
    lake_depth = distance_field(~lake, 8)
    z_lake = -(12 + 26 * np.minimum(lake_depth, 4))
    z = np.where(sea, z_sea, z)
    z = np.where(lake, z_lake, z)
    z = np.where(river, -26.0, z)
    strait = shallow_strait & water
    z = np.where(strait, np.maximum(z, -32.0), z)
    # fords: wherever a road crosses a river, a lake or a strait, the bed rises to wading depth
    ford = water & (road_d < 1.8)
    z = np.where(ford, np.maximum(z, -28.0), z)
    # Every landmass stands apart: wherever the shallows round two of them would meet, a channel of
    # deep water runs between, so no island can be reached on foot from another shore.
    owner, _ = label_regions(land | lake | river)
    for _ in range(12):                                   # each stretch of sea goes to its nearest shore
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nb = shift(owner, dx, dy, -1)
            owner = np.where((owner < 0) & (nb >= 0), nb, owner)
    between = np.zeros((n, n), bool)
    for dx, dy in ((1, 0), (0, 1)):
        nb = shift(owner, dx, dy, -1)
        between |= (owner >= 0) & (nb >= 0) & (nb != owner)
    channel = dilate(between, 1) & sea
    z = np.where(channel, np.minimum(z, -(DEEP_WATER + 30)), z)
    # The Maelstrom: spiral arms of shallows wheeling round a bottomless eye
    mx, my = geo.MAELSTROM
    R = geo.MAELSTROM_RADIUS
    md = f.distance(mx, my)
    swirl = np.cos(3 * np.arctan2(ys - my, xs - mx) + md * 0.3)
    z_whirl = np.where((swirl > 0.2) & (md > 5) & (md < R), -36 - 8 * md / R, -150 - 120 * smoothstep(R, 2, md))
    w = smoothstep(R + 6, R, md)
    z = np.where(sea, z * (1 - w) + z_whirl * w, z)
    T.water = water
    T.lake, T.river, T.sea = lake, river, sea

    # ---- 5. cliff levels ------------------------------------------------------
    level = zone_prop('level', 0).astype(np.int32)
    level = np.where(level < 0, np.where(dc > 6, level, 0), level)     # sunken zones keep a rim
    wet_d = distance_field(lake | river, 6)
    level = np.where((level > 0) & (wet_d < 3), 0, level)              # water in a raised zone lies in a sunken basin
    # Raised ground: a share of many zones' land (their 'rise') stands a cliff level up in broad
    # plateaus, clear of the roads, the shores, the water and the settlements.
    bumps = f.fbm(14, 3)
    room = land & (dc > 5) & (road_d > 5) & (wet_d > 4) & (massif_d > 1.6)
    for tx, ty, r in flat_spots:
        room &= f.distance(tx, ty) > r + 3
    up = np.zeros((n, n), bool)
    for zi, zd in enumerate(geo.ZONES):
        sel = room & (zone_of == zi)
        if zd.get('rise', 0) > 0 and sel.sum() > 40:
            up |= sel & (bumps > np.quantile(bumps[sel], 1 - zd['rise']))
    up = dilate(erode(up, 2), 2) & room
    level = level + up.astype(np.int32)
    layer = np.where(land, 2 + level + terrace, 2)
    layer = np.where(sea & ~T.beach, 1, layer)
    for cx, cy, r, lv in geo.MESAS:
        d = f.distance(cx, cy) + f.fbm(3, 2) * 0.6
        layer = np.where((d <= r) & (dc > 3) & (road_d > 4), np.maximum(layer, 2 + level + lv), layer)
    # Clean ledges: no ledge, notch, pit or spike a single corner wide, and no two levels meeting
    # only at a diagonal; the game draws those as stray shards and slivers of cliff. Mesas and the
    # coasts keep their exact shapes.
    tidy_ok = land & (dc > 2)
    for cx, cy, r, lv in geo.MESAS:
        tidy_ok &= f.distance(cx, cy) > r + 2
    layer = clean_ledges(layer, tidy_ok)
    for _ in range(6):           # neighbouring corners may differ by at most one level
        m = layer.copy()
        for dx, dy in NEIGHBOURS8:
            m = np.maximum(m, shift(layer, dx, dy, 1) - 1)
        layer = m
    ramp = np.zeros((n, n), bool)
    dry = land & ~lake & ~river
    core = land & (massif_d < 1.15) & (pass_factor > 0.7)          # the impassable heart of each massif
    T.massif_core = core
    no_ramp = in_massif.copy()
    for line, gates in getattr(geo, 'WALLS', []):
        no_ramp |= f.segment_distance(line) < 8
    T.ramps = stamp_ramps(layer, ramp, z, dry, T.road_lines, avoid=dilate(core, 1))
    T.ramps += edge_ramps(layer, ramp, z, dry & ~no_ramp, T.ramps, f.rng)
    near_core = massif_d < 1.4                                     # pockets may link up anywhere but a massif's heart
    for line, gates in getattr(geo, 'WALLS', []):
        near_core |= f.segment_distance(line) < 8
    T.ramps += link_pockets(layer, ramp, z, dry, water, core, near_core, np.where(land, land_id, -1))
    for line, gates in getattr(geo, 'WALLS', []):     # ramparts: a raised line of corners, cliffs on both sides
        wall = (f.segment_distance(line) <= 0.8) & (land | (dw <= 4))
        for gx, gy in gates:
            wall &= f.distance(gx, gy) > 2.4
        layer = np.where(wall, np.maximum(layer, 3), layer)
        z = np.where(wall & water, z + 128 * (layer - 2), z)           # the rampart rises out of the water
    check_cliffs(layer)
    T.layer = layer
    T.ramp = ramp
    T.ramp_near = dilate(ramp, 3)

    # ground offsets: land keeps its own height, water keeps its depth below the surface
    z = np.where(dry, np.maximum(z, 12 - 128 * (layer - 2)), z)
    z_raw = np.where(water, z - 128 * (layer - 2), z)
    raw = np.clip(np.round(8192 + 4 * (SEA_Z + z_raw)), 256, 16000).astype(np.int32)
    T.height_raw = raw
    gz = (raw - 8192) / 4.0 + (layer - 2) * 128.0
    # a ramp's middle row of corners sits half a level up
    rl = np.stack([layer[:-1, :-1], layer[:-1, 1:], layer[1:, :-1], layer[1:, 1:]])
    entrance = ramp[:-1, :-1] & ramp[:-1, 1:] & ramp[1:, :-1] & ramp[1:, 1:] & (rl.max(0) != rl.min(0))
    lift = np.zeros((n, n), bool)
    low = rl.min(0)
    for k, (oy, ox) in enumerate(((0, 0), (0, 1), (1, 0), (1, 1))):
        sel = entrance & (rl[k] == low)
        lift[oy:n - 1 + oy, ox:n - 1 + ox] |= sel
    T.ground_z = gz + np.where(lift, 64.0, 0.0)   # final world z of each tilepoint
    T.h_rel = T.ground_z - SEA_Z

    # ---- 6. tile-level analysis (tile (i, j) has corners i..i+1, j..j+1) -------
    gz = T.ground_z
    c00, c10, c01, c11 = gz[:-1, :-1], gz[:-1, 1:], gz[1:, :-1], gz[1:, 1:]
    tile_range = np.maximum.reduce([c00, c10, c01, c11]) - np.minimum.reduce([c00, c10, c01, c11])
    T.ramp_tile = entrance
    cliff_tile = (rl.max(0) != rl.min(0)) & ~entrance
    T.cliff_tile = cliff_tile
    T.steep_tile = (tile_range > 95) & ~cliff_tile & ~entrance
    slope_pt = np.zeros((n, n))
    for dx, dy in NEIGHBOURS8:
        slope_pt = np.maximum(slope_pt, np.abs(gz - shift(gz, dx, dy, 0)) * (1 if dx and dy else 1))
    slope_pt[0, :] = slope_pt[-1, :] = slope_pt[:, 0] = slope_pt[:, -1] = 0
    T.slope = slope_pt

    # ---- 6b. forests ---------------------------------------------------------------
    # Each zone's density is the share of its land under forest. Woods thicken by
    # rivers and lakes, thin out towards the treeline and break into clumps and
    # clearings; objects.py plants the trees and scatters a few beyond the edges.
    zcold = np.array([B[zd['biome']]['cold'] for zd in geo.ZONES])[zone_of]
    density = np.array([zd.get('density', B[zd['biome']]['density']) for zd in geo.ZONES])[zone_of] * FOREST_DENSITY
    density = density * (1 + 0.35 * smoothstep(10, 2, distance_field(lake | river, 10)))
    treeline = np.where(zcold, 420, 700)
    density = np.clip(density * smoothstep(treeline + 60, treeline - 120, T.h_rel), 0, 0.76)
    fn = (f.fbm(16, 4) + f.fbm(6, 3) * 0.6 + f.fbm(40, 2) * 0.5) / 2.1
    land_noise = np.sort(fn[land])
    thresh = land_noise[np.minimum(((1 - density) * (len(land_noise) - 1)).astype(int), len(land_noise) - 1)]
    T.forest_score = np.where(density > 0.005, fn - thresh, -9.0)
    T.forest = land & (T.forest_score > 0)

    # ---- 7. ground textures -----------------------------------------------------
    biome_names = [z['biome'] for z in geo.ZONES]
    tex = np.zeros((n, n), dtype=np.int32)
    noises = [f.fbm(9, 3), f.fbm(6, 3), f.fbm(4, 3)]
    # zone borders fray into each other instead of meeting on a clean line
    jx = np.clip(np.round(xs + f.fbm(3, 2) * 4), 0, n - 1).astype(int)
    jy = np.clip(np.round(ys + f.fbm(3, 2) * 4), 0, n - 1).astype(int)
    zone_tex = np.where(land & land[jy, jx] & (land_id[jy, jx] == land_id), zone_of[jy, jx], zone_of)
    # Each zone's tiles follow the land: its second tile (lusher or variant ground) gathers on
    # wet valley floors and by the water, its third (dirt or rock) on slopes and high, dry ground.
    wet = np.clip(smoothstep(10, 1, distance_field(lake | river, 10)) + np.clip(np.log1p(T.flow) / 7.0 - 0.35, 0, 1), 0, 1)
    rugged = np.clip(slope_pt / 80.0, 0, 1) * 0.55 + np.clip(T.relief / 350.0, 0, 1) * 0.3
    bias = [0.0, wet * 0.8 - 0.22, rugged * 1.2 - wet * 0.5 - 0.12]
    for zi, zdef in enumerate(geo.ZONES):
        sel = zone_tex == zi
        if not sel.any():
            continue
        recipe = B[zdef['biome']]['tiles']
        for k, (tile, thr) in enumerate(recipe):
            tex[sel & (noises[k % 3] + bias[min(k, 2)] > thr)] = TILE[tile]
    biome_arr = np.array(biome_names)[zone_of]
    T.biome = biome_arr

    def per_zone(key):
        return np.array([TILE[B[b][key]] if B[b][key] else -1 for b in biome_names])[zone_of]

    cold = np.array([B[b]['cold'] for b in biome_names])[zone_of]
    rock = per_zone('rock')
    steep = slope_pt > 70
    forest_floor = per_zone('floor')
    # the forest floor lies under the denser stands; the lighter woods keep the open ground's cover
    tex = np.where(T.forest & (T.forest_score > 0.1 + noises[1] * 0.1) & (forest_floor >= 0) & (noises[2] > -0.45),
                   forest_floor, tex)
    alpine = land & (T.relief > 210 + noises[0] * 70)                     # bare rock and scree up high
    tex = np.where(alpine & (noises[1] > -0.15), rock, np.where(alpine & (noises[2] > 0.2), TILE['Ldrt'], tex))
    tex = np.where(steep & land, rock, tex)
    # Bare rock shows where the ground is too steep to hold soil; level ground up high is gravel
    # and rough earth (snow in the cold) rather than a pavement of rock.
    level = slope_pt < 22 + noises[1] * 10
    rocky = np.isin(tex, [TILE['Lrok'], TILE['Wrok']]) & level & land
    tex = np.where(rocky, np.where(cold, TILE['Wsnw'], TILE['Ldro']), tex)
    height = T.h_rel
    snowcap = land & (height > np.where(cold, 420, 700) + noises[0] * 60) & (noises[1] > -0.4)
    tex = np.where(snowcap, TILE['Wsnw'], tex)
    beach_tile = per_zone('beach')
    beach = land & T.beach & (dc < 1.6 + noises[2]) & (height < 45) & ~lake_adjacent(lake | river)
    tex = np.where(beach, beach_tile, tex)
    tex = soften_contrasts(tex, land, noises[1])
    tex = np.where(water, per_zone('seabed'), tex)
    tex = np.where(lake | river, TILE['Ldrt'], tex)
    # mud banks: bare earth along some stretches of the shores of the lakes and rivers, where
    # the water laps at the land, and grass running down to the water along the others
    bank = (land & ~steep & ~cold & ~beach & (noises[1] > 0.0)
            & (distance_field(lake | river, 3) < 1.3 + noises[2] * 0.8))
    tex = np.where(bank, TILE['Ldrt'], tex)
    # Roads: wide cobbled roads through the old human lands, worn to bare earth in stretches;
    # earthen tracks elsewhere, with ruts of darker earth, and packed snow in the cold.
    paving = per_zone('road')
    cobbled = paving == TILE['Vcbp']
    road = (land | ford) & (road_d < np.where(cobbled, 1.3, 1.05) + noises[2] * 0.3)    # seen through the water at the fords
    desertish = np.isin(biome_arr, ['savanna', 'desert', 'reddesert', 'needles', 'volcanic', 'amber'])
    tex = np.where(road, np.where(cold & ~cobbled, TILE['Wsng'], paving), tex)
    tex = np.where(road & cobbled & (noises[1] > 0.4), TILE['Ldrt'], tex)
    tex = np.where(road & ~cobbled & ~desertish & ~cold & (noises[1] > 0.3), TILE['Bdrt'], tex)
    # the capitals: a paved square with streets leading out along the roads
    for idx, name, cx, cy, race in geo.CAPITALS:
        dist = f.distance(cx, cy) + noises[0] * 2.0
        paved = land & ~(lake | river) & ((dist < 3.5) | ((dist < 10) & (road_d < 1.4 + noises[2] * 0.4)))
        tex = np.where(paved, TILE['Ybtl'], tex)
    tex = tidy_paint(tex, land, rounds=3)
    # Cliff types. The game draws every corner beside a cliff or on a ramp with the cliff type's
    # own ground (dirt, snow or grass) whatever is painted there, and the cliff face takes that
    # type's look too. So each cliff takes the type that suits the ground around it: snow cliffs
    # in the snow (and on bare rock in cold zones), grass cliffs in the meadows, dirt cliffs on rock,
    # dirt and sand, with the zone's own type breaking ties. Those corners are then painted with
    # what the game will show, so the editor, the minimap and the game all agree.
    cliff_at = np.zeros((n, n), bool)
    cliff_at[:-1, :-1] = cliff_tile
    ramp_at = np.zeros((n, n), bool)
    ramp_at[:-1, :-1] = entrance
    around = lambda m: m | shift(m, 1, 0, False) | shift(m, 0, 1, False) | shift(m, 1, 1, False)
    shown = (around(cliff_at) & ~ramp) | around(ramp_at)
    # the vote looks past the cliff's own steep (rock-painted) edge to the dry ground on either side
    voters = ~shown & land & ~water
    snowy = np.isin(tex, [TILE[t] for t in ('Wsnw', 'Wsng')]) & voters
    grassy = np.isin(tex, [TILE[t] for t in ('Lgrs', 'Lgrd', 'Fgrs', 'Vgrt')]) & voters    # grassy earth counts as earth
    bare = voters & ~snowy & ~grassy
    zone_cliff = np.array([B[b]['cliff'] for b in biome_names])[zone_of]
    icy = zone_cliff == CLIFF_SNOW                                 # in the cold, bare rock ledges hold snow
    votes = np.stack([blur((bare & ~icy).astype(float), 2), blur((snowy | (bare & icy)).astype(float), 2),
                      blur(grassy.astype(float), 2)])
    votes += 0.03 * (np.arange(3)[:, None, None] == zone_cliff[None])
    # where a road climbs through a ramp the ramp shows the cliff's own ground, so outside the snow
    # those cliffs are dirt ones and the road runs on unbroken
    votes[CLIFF_DIRT] += np.where((road_d < 2.2) & ~cold, 2.0, 0.0)
    cliff_type = votes.argmax(0).astype(np.int32)                 # CLIFF_DIRT, CLIFF_SNOW, CLIFF_GRASS
    cliff_ground = np.array([TILE['Ldrt'], TILE['Wsnw'], TILE['Lgrs']])[cliff_type]
    tex = np.where(shown, cliff_ground, tex)
    # The cliff's ground also spills a ragged tile or so past it, like scree or drifted snow on the
    # ledges, so a cliff blends into the land instead of being outlined by a one-tile stripe.
    spill = land & ~water & ~road & (tex != TILE['Ybtl'])
    apron = dilate(shown, 1) & ~shown & spill & (noises[1] > -0.25)
    apron |= dilate(apron, 1) & ~shown & spill & (noises[2] > 0.3)
    tex = np.where(apron, cliff_ground, tex)
    tex = tidy_paint(tex, land & ~shown)
    tex = soften_contrasts(tex, land & ~shown, noises[1], both_sides=True)
    T.cliff_type = cliff_type
    T.tex = tex

    # Blight lies on the low ground and stops short of cliffs and mountains: beside a cliff the game
    # always draws the cliff's own ground, which would stand out against the dark blight.
    blight_zone = np.array([B[b]['blight'] for b in biome_names])[zone_of]
    clear_of_cliffs = distance_field(shown, 6) > 3.0 + noises[1] * 1.5
    T.blight = (blight_zone & land & ~water & clear_of_cliffs & (T.relief < 260 + noises[2] * 60)
                & (noises[0] > -0.55))

    # ---- 8. flags, edges, variations ----------------------------------------------
    flags = np.zeros((n, n), dtype=np.int32)
    flags |= np.where(ramp, 0x10, 0)
    flags |= np.where(T.blight, 0x20, 0)
    flags |= np.where(water | (T.ground_z < SEA_Z), 0x40, 0)
    T.water_flag = (flags & 0x40) != 0
    T.flags = flags
    ii, jj = xs.astype(int), ys.astype(int)
    T.edge = ((ii < MARGIN_L) | (ii >= MAP_W - MARGIN_R) | (jj < MARGIN_B) | (jj >= MAP_H - MARGIN_T)) & (ii < MAP_W) & (jj < MAP_H)
    w = np.array(VARIATION_WEIGHTS, dtype=np.float64)
    T.variation = f.rng.choice(len(w), size=(n, n), p=w / w.sum()).astype(np.int32)
    T.cliff_tex = T.cliff_type

    # ---- 9. pathing (4 x 4 cells per tile) ---------------------------------------
    T.pathing = compute_pathing(T)
    return T


def clean_ledges(layer, ok, rounds=6):
    """Fill one-corner notches and pits, shave one-corner slivers and spikes, and close diagonal pinches
    in the cliff levels, changing only corners where `ok`."""
    layer = layer.copy()
    for _ in range(rounds):
        before = layer.copy()
        for dx, dy in ((1, 0), (0, 1)):
            a, b = shift(layer, dx, dy, -1), shift(layer, -dx, -dy, -1)
            a, b = np.where(a < 0, layer, a), np.where(b < 0, layer, b)
            layer = np.where(ok & (layer < np.minimum(a, b)), np.minimum(a, b), layer)   # both sides higher
            layer = np.where(ok & (layer > np.maximum(a, b)), np.maximum(a, b), layer)   # both sides lower
        bl, br, tl, tr = layer[:-1, :-1], layer[:-1, 1:], layer[1:, :-1], layer[1:, 1:]
        pinch = (bl == tr) & (br == tl) & (bl != br)
        raise_br = pinch & (br < bl) & ok[:-1, 1:]              # lift one of the low pair to join the high one
        raise_bl = pinch & (bl < br) & ok[:-1, :-1]
        layer[:-1, 1:] = np.where(raise_br, bl, layer[:-1, 1:])
        layer[:-1, :-1] = np.where(raise_bl, br, layer[:-1, :-1])
        if (layer == before).all():
            break
    return layer


def peaks(f, line, reach, rng, rough):
    """Steep cones (0..1) for the summits of a mountain chain, spaced out along its crest line."""
    pts = np.array(line, float)
    seg = np.hypot(*np.diff(pts, axis=0).T)
    along = np.concatenate([[0.0], np.cumsum(seg)])
    out = np.zeros((f.h, f.w))
    at = rng.uniform(0, reach * 0.4)
    while at <= along[-1]:
        i = min(int(np.searchsorted(along, at, side='right')) - 1, len(seg) - 1)
        t = (at - along[i]) / max(seg[i], 1e-6)
        sx, sy = pts[i] + (pts[i + 1] - pts[i]) * t
        r = reach * rng.uniform(0.75, 1.05)
        x0, x1 = max(int(sx - r) - 1, 0), min(int(sx + r) + 2, f.w)
        y0, y1 = max(int(sy - r) - 1, 0), min(int(sy + r) + 2, f.h)
        ds = np.hypot(f.xs[y0:y1, x0:x1] - sx, f.ys[y0:y1, x0:x1] - sy) + rough[y0:y1, x0:x1] * 1.5
        cone = rng.uniform(0.8, 1.12) * np.clip(1 - ds / r, 0, 1) ** 1.35
        out[y0:y1, x0:x1] = np.maximum(out[y0:y1, x0:x1], cone)
        at += reach * rng.uniform(0.5, 0.85)
    return out


def scatter_lakes(f, land, zone_of, road_d, flat_spots, existing, seed, count=50, spacing=16):
    """Pick sites for natural lakes: inland, away from roads, settlements, other lakes and the mountain ranges."""
    rng = np.random.default_rng(seed * 17 + 9)
    inland = distance_field(~land, 16)
    ok = land & (inland >= 9) & (road_d > 6)
    for tx, ty, r in flat_spots:
        ok &= f.distance(tx, ty) > r + 9
    for line, width, height in geo.MASSIFS:
        ok &= f.segment_distance(line, reach=width * 3 + 4) > width * 2.8
    for line, width, height in geo.RIDGES:
        ok &= f.segment_distance(line, reach=width * RANGE_WIDTH * 2.5 + 4) > width * RANGE_WIDTH * 2.2
    biome = np.array([z['biome'] for z in geo.ZONES])[zone_of]
    plateau = np.array([z.get('level', 0) != 0 for z in geo.ZONES])[zone_of]   # water cannot sit up on a cliff level
    ok &= ~dilate(plateau, 5)
    dry_country = np.isin(biome, ['desert', 'savanna', 'reddesert', 'needles', 'barren', 'amber'])
    ok &= ~np.isin(biome, ['volcanic'])
    ok &= ~dry_country | (rng.random(land.shape) < 0.04)          # only the odd oasis in dry country
    centres = [(cx, cy) for cx, cy, rx, ry in existing]
    sites = []
    cand = np.argwhere(ok)
    for y, x in cand[rng.permutation(len(cand))]:
        if len(sites) >= count:
            break
        if any((x - cx) ** 2 + (y - cy) ** 2 < spacing ** 2 for cx, cy in centres):
            continue
        rx = float(rng.uniform(2.2, 5.5))
        if inland[y, x] < rx + 5 or road_d[y, x] < rx + 3.5:
            continue
        sites.append((float(x), float(y), rx, rx * float(rng.uniform(0.55, 0.95)), float(rng.uniform(0, np.pi))))
        centres.append((x, y))
    return sites


def stamp_ramps(layer, ramp, z, dry, roads, avoid=None):
    """Cut a ramp wherever a road climbs or drops one cliff level. Returns the ramp centres."""
    crossings = []
    for line in roads:
        pts = []
        for (ax, ay), (bx, by) in zip(line, line[1:]):
            steps = max(1, int(np.hypot(bx - ax, by - ay) / 0.25))
            pts += [(ax + (bx - ax) * k / steps, ay + (by - ay) * k / steps, bx - ax, by - ay) for k in range(steps)]
        prev = None
        for x, y, dx, dy in pts:
            i, j = int(round(x)), int(round(y))
            if not dry[j, i]:
                prev = None
                continue
            here = layer[j, i]
            if prev is not None and here != prev[0]:
                crossings.append(((prev[1] + x) / 2, (prev[2] + y) / 2, dx, dy))
            prev = (here, x, y)
    done = []
    for cx, cy, dx, dy in crossings:
        if any(np.hypot(cx - px, cy - py) < 6 for px, py in done):
            continue
        # where the edge is ragged right at the crossing (a terrace beside the road, a bend in the
        # cliff), try a little way up and down the road, and the ramp turned the other way
        norm, along = max(np.hypot(dx, dy), 1e-9), abs(dx) >= abs(dy)
        for k in (0, -1, 1, -2, 2, -3, 3):
            x, y = cx + dx / norm * k, cy + dy / norm * k
            if stamp_ramp(layer, ramp, z, dry, x, y, along, avoid) or stamp_ramp(layer, ramp, z, dry, x, y, not along, avoid):
                done.append((x, y))
                break
    return done


def edge_ramps(layer, ramp, z, dry, done, rng, spacing=24):
    """Ramps along the cliff edges between zones and up onto ledges, about every `spacing` tiles."""
    cands = [(i + 0.5, j, True) for j, i in np.argwhere((np.abs(layer[:, 1:] - layer[:, :-1]) == 1) & dry[:, 1:] & dry[:, :-1])]
    cands += [(i, j + 0.5, False) for j, i in np.argwhere((np.abs(layer[1:, :] - layer[:-1, :]) == 1) & dry[1:, :] & dry[:-1, :])]
    taken = np.zeros((MAP_H // 8 + 2, MAP_W // 8 + 2), bool)    # coarse grid of ramps already cut

    def near_taken(x, y):
        gx, gy = int(x // 8), int(y // 8)
        r = spacing // 8 + 1
        for px, py in [(px, py) for px, py in done if abs(px - x) < spacing and abs(py - y) < spacing]:
            if np.hypot(px - x, py - y) < spacing:
                return True
        return False

    new = []
    for k in rng.permutation(len(cands)):
        cx, cy, horizontal = cands[k]
        if near_taken(cx, cy):
            continue
        if stamp_ramp(layer, ramp, z, dry, cx, cy, horizontal):
            done = done + [(cx, cy)]
            new.append((cx, cy))
    return new


def walkable_tiles(layer, ramp, z, dry, water, core):
    """Rough walkability of each tile while the terrain is still being shaped (no pathing map yet)."""
    corners = lambda a: [a[:-1, :-1], a[:-1, 1:], a[1:, :-1], a[1:, 1:]]
    h = np.where(water, z, z + 128 * (layer - 2))
    foot = dry | (water & (z > -DEEP_WATER))
    rl = corners(layer)
    flat = np.maximum.reduce(rl) == np.minimum.reduce(rl)
    entrance = np.logical_and.reduce(corners(ramp)) & ~flat
    # a ramp's middle row of corners sits half a level up, as in the final ground heights, which
    # can leave the ground at the foot of the ramp too steep to walk
    lift = np.zeros(layer.shape, bool)
    n = layer.shape[0]
    for k, (oy, ox) in enumerate(((0, 0), (0, 1), (1, 0), (1, 1))):
        lift[oy:n - 1 + oy, ox:n - 1 + ox] |= entrance & (rl[k] == np.minimum.reduce(rl))
    hr = corners(h + np.where(lift, 64.0, 0.0))
    gentle = np.maximum.reduce(hr) - np.minimum.reduce(hr) <= 95
    walk = np.logical_and.reduce(corners(foot)) & ((flat & gentle) | entrance) & ~core[:-1, :-1]
    out = np.zeros(layer.shape, bool)
    out[:-1, :-1] = walk
    return out


def link_pockets(layer, ramp, z, dry, water, core, no_ramp, owner, rounds=6):
    """Give every sealed-off patch of walkable ground a ramp down (or up) to its neighbour."""
    new = []
    for _ in range(rounds):
        label, sizes = label_regions(walkable_tiles(layer, ramp, z, dry, water, core))
        sel = (owner >= 0) & (label >= 0)
        keys, counts = np.unique(owner[sel] * (len(sizes) + 1) + label[sel], return_counts=True)
        best = {}
        for key, count in zip(keys, counts):
            land, lab = divmod(int(key), len(sizes) + 1)
            if count > best.get(land, (0, -1))[0]:
                best[land] = (count, lab)
        main = np.zeros(len(sizes), bool)
        main[[lab for _, lab in best.values()]] = True
        pocket = (label >= 0) & ~main[label] & (sizes[label] >= 25)
        ok = dry & ~no_ramp
        tried = set()
        made = 0
        for horizontal in (True, False):
            if horizontal:      # edge between points (j, i) and (j, i + 1): tiles (j, i - 1) and (j, i + 1) either side
                a, b = layer[:, 1:-1], layer[:, 2:]
                la, lb = label[:, :-2], label[:, 2:]
                edge = (np.abs(a - b) == 1) & ok[:, 1:-1] & ok[:, 2:]
                coords = [(i + 1.5, j) for j, i in np.argwhere(edge & (la != lb) & (la >= 0) & (lb >= 0)
                                                                & (pocket[:, :-2] | pocket[:, 2:]))]
                owners = [(label[j, int(x) - 1], label[j, int(x) + 1]) for x, j in coords]
            else:
                a, b = layer[1:-1, :], layer[2:, :]
                la, lb = label[:-2, :], label[2:, :]
                edge = (np.abs(a - b) == 1) & ok[1:-1, :] & ok[2:, :]
                coords = [(i, j + 1.5) for j, i in np.argwhere(edge & (la != lb) & (la >= 0) & (lb >= 0)
                                                                & (pocket[:-2, :] | pocket[2:, :]))]
                owners = [(label[int(y) - 1, i], label[int(y) + 1, i]) for i, y in coords]
            for (cx, cy), pair in zip(coords, owners):
                key = tuple(sorted(int(v) for v in pair))
                if key in tried:
                    continue
                if stamp_ramp(layer, ramp, z, dry, cx, cy, horizontal, dilate(core, 1)):
                    tried.add(key)
                    new.append((cx, cy))
                    made += 1
        if not made:
            break
    return new


def stamp_ramp(layer, ramp, z, dry, cx, cy, horizontal, avoid=None):
    """Cut one ramp across the cliff edge at (cx, cy), climbing along x if `horizontal`, else along y.

    Ramps follow the World Editor's layout: along a straight stretch of cliff
    edge, each column of the ramp flags its last upper corner and the two lower
    corners after it. The edge is straightened over a small window around the
    crossing and the ground there is levelled. Returns whether it was cut.
    """
    n = layer.shape[0]
    s, t = (cx, cy) if horizontal else (cy, cx)

    def at(si, ti):                              # (row, column) of along/across indices
        return (ti, si) if horizontal else (si, ti)

    t0 = int(round(t))
    if not (6 < t0 < n - 7 and 6 < s < n - 7):
        return False
    samples = [layer[at(int(round(s + o)), t0)] for o in (-3, 3)]
    if abs(samples[0] - samples[1]) != 1:
        return False
    upper = max(samples)
    sgn = -1 if samples[0] > samples[1] else 1     # -1: the upper side is at smaller s
    across = range(t0 - 4, t0 + 5)
    for shift_by in (0, -1, 1, -2, 2, -3, 3):      # slide along the crossing to a clean stretch of edge
        j0 = (int(np.floor(s)) if sgn < 0 else int(np.ceil(s))) + shift_by
        along = range(j0 - 2, j0 + 4) if sgn < 0 else range(j0 - 3, j0 + 3)
        cells = [(si, ti) for si in along for ti in across]
        if any(not (0 < si < n - 1 and 0 < ti < n - 1) for si, ti in cells):
            continue
        if any(not dry[at(si, ti)] or layer[at(si, ti)] not in (upper - 1, upper) for si, ti in cells):
            continue
        if avoid is not None and any(avoid[at(si, ti)] for si, ti in cells):     # e.g. a massif's impassable heart
            continue
        if any(ramp[at(si + a, ti + b)] for si, ti in cells for a in (-1, 0, 1) for b in (-1, 0, 1)
               if 0 <= si + a < n and 0 <= ti + b < n):
            continue
        break
    else:
        return False
    for si, ti in cells:
        is_upper = si <= j0 if sgn < 0 else si >= j0
        layer[at(si, ti)] = upper if is_upper else upper - 1
    for k in range(3):                             # the upper corner and the two lower ones below it
        for ti in range(t0 - 2, t0 + 3):
            ramp[at(j0 - sgn * k, ti)] = True
    rows = [at(si, ti) for si, ti in cells]
    level_z = float(np.mean([z[r] for r in rows]))
    for si in range(min(along) - 2, max(along) + 3):
        for ti in range(t0 - 6, t0 + 7):
            if 0 <= si < n and 0 <= ti < n:
                inside = (si in along) and (ti in across)
                z[at(si, ti)] = level_z if inside else (z[at(si, ti)] + level_z) / 2
    return True


def check_cliffs(layer):
    """Every tile's corners must lie within two cliff levels of each other (the game has no taller cliff models)."""
    rl = np.stack([layer[:-1, :-1], layer[:-1, 1:], layer[1:, :-1], layer[1:, 1:]])
    bad = rl.max(0) - rl.min(0) > 2
    assert not bad.any(), 'cliff too tall at %s' % (np.argwhere(bad)[:5].tolist(),)


def lake_adjacent(mask):
    return dilate(mask, 2)


def compute_pathing(T):
    n = MAP_W * 4
    cy, cx = np.mgrid[0:n, 0:n]
    bx, by = cx // 4, cy // 4                                   # tile whose bottom-left corner owns the cell
    nx, ny = np.clip(np.round(cx / 4.0).astype(int), 0, MAP_W), np.clip(np.round(cy / 4.0).astype(int), 0, MAP_H)
    cells = np.full((n, n), 0x40, dtype=np.int32)              # walkable, buildable, dry land
    water_here = T.water_flag[ny, nx]
    depth = (SEA_Z - T.ground_z)[ny, nx]
    deep = water_here & (depth > DEEP_WATER)
    shallow = water_here & ~deep
    cells = np.where(shallow, 0x08, cells)
    cells = np.where(deep, 0x0A, cells)
    blocked = T.cliff_tile[by, bx] | T.steep_tile[by, bx] | T.massif_core[by, bx]
    cells = np.where(T.ramp_tile[by, bx] & ~water_here, 0x48, cells)
    cells = np.where(blocked & ~water_here, 0xCA, cells)
    cells = np.where(blocked & water_here, cells | 0x0A, cells)
    cells = np.where(T.blight[ny, nx], cells | 0x20, cells)
    cells = np.where(T.edge[by, bx], 0xCE, cells)
    return cells.astype(np.uint8)


def world_xy(tx, ty):
    """Tile coordinates -> world coordinates."""
    return LEFT + tx * 128.0, BOTTOM + ty * 128.0


def ground_z_at(T, tx, ty):
    """Bilinear ground height (world z) at fractional tile coordinates."""
    x0, y0 = int(np.floor(tx)), int(np.floor(ty))
    x0, y0 = min(max(x0, 0), MAP_W - 1), min(max(y0, 0), MAP_H - 1)
    fx, fy = tx - x0, ty - y0
    g = T.ground_z
    a = g[y0, x0] * (1 - fx) + g[y0, x0 + 1] * fx
    b = g[y0 + 1, x0] * (1 - fx) + g[y0 + 1, x0 + 1] * fx
    return float(a * (1 - fy) + b * fy)
