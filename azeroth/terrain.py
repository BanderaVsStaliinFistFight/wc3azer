"""Rasterises the geography into Warcraft III terrain data (480 x 480 tiles)."""
import numpy as np

from . import geography as geo
from .biomes import B, GROUND_TILES, TILE
from .raster import Field, blur, dilate, distance_field, erode, shift, smoothstep, NEIGHBOURS8

MAP_W = MAP_H = 480                  # tiles; the largest map size Warcraft III supports
MARGIN_L, MARGIN_R, MARGIN_B, MARGIN_T = 6, 6, 4, 8
LEFT = BOTTOM = -MAP_W * 64.0        # world coordinate of the south-west tilepoint
WATER_RAW = 0x2000                   # default water level; surface sits at z = -89.6
SEA_Z = -89.6
DEEP_WATER = 0.40 * 128              # deeper than this is impassable for ground units

# Distribution of tile variations produced by the World Editor's random brush.
VARIATION_WEIGHTS = [605, 76, 27, 3, 663, 80, 33, 2, 613, 70, 28, 13, 599, 82, 27, 5, 697, 602]


class Terrain:
    pass


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

    # ---- 2. inland water ---------------------------------------------------
    lake_sd = np.full((n, n), -1e9)
    for cx, cy, rx, ry in geo.LAKES:
        lake_sd = np.maximum(lake_sd, f.ellipse_sdf(cx, cy, rx, ry))
    lake = (lake_sd + f.fbm(5, 3) * 1.2 > 0) & land
    river_d = np.full((n, n), 1e9)
    for line in geo.RIVERS:
        river_d = np.minimum(river_d, f.segment_distance(line))
    river = (river_d < 1.3 + f.fbm(6, 2) * 0.5) & land
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

    road_d = np.full((n, n), 1e9)
    for line in geo.ROADS:
        road_d = np.minimum(road_d, f.segment_distance(line))
    T.road_d = road_d
    pass_factor = smoothstep(2.5, 6.0, road_d)       # roads cut passes through ridges

    # ---- 4. heights (relative to the water surface) ---------------------------
    dc = distance_field(water, 40)                 # inland distance from any water
    dw = distance_field(land, 40)                  # distance from land, out at sea
    hill_n = f.fbm(18, 5) * 0.5 + 0.5
    ridge_n = f.ridged(34, 5)
    detail = f.fbm(5, 2)
    z = base + hills * hill_n * (0.4 + 0.6 * pass_factor) + mountains * ridge_n ** 2 * pass_factor + detail * 8
    ridge_h = np.zeros((n, n))
    rough = f.fbm(9, 3)
    for line, width, height in geo.RIDGES:
        d = f.segment_distance(line)
        prof = smoothstep(width * 1.8, 0, d + rough * 1.5) * height * (0.8 + 0.35 * (rough + 1) / 2)
        ridge_h = np.maximum(ridge_h, prof)
    z = np.maximum(z, base * 0.6 + ridge_h * pass_factor)
    for cx, cy, r, depth in geo.BASINS:
        d = f.distance(cx, cy)
        z -= depth * smoothstep(r * 1.4, r * 0.5, d)
    z = np.maximum(z, 12)

    # Coasts are cliffs except where beaches are needed (see geography.BEACHES).
    instance_land = np.isin(land_id, [land_index[nm] for nm in geo.INSTANCE_NAMES]) & land
    beach_src = np.zeros((n, n), bool)
    for line in geo.SHALLOWS:
        beach_src |= f.segment_distance(line) < 7
    beach_src |= river_d < 4
    for name, tx, ty, building in geo.TOWNS:
        if building == 'nshp':
            beach_src |= f.distance(tx, ty) < 6
    for tx, ty, r in geo.BEACHES:
        beach_src |= f.distance(tx, ty) < r
    for name in geo.BEACH_ISLANDS:
        beach_src |= (land_id == land_index[name]) & (land_sd > -6)
    coast_pts = land & (dc <= 1)
    beach_noise = f.fbm(22, 3)
    beach_src |= coast_pts & (beach_noise > np.quantile(beach_noise[coast_pts], 0.86))
    beach_src &= ~dilate(instance_land, 8)
    cliffy = smoothstep(2.0, 6.0, distance_field(beach_src, 12))      # 0 on beaches, 1 on cliff coasts
    T.beach = cliffy < 0.5
    coast_level = 14 + 70 * blur(cliffy, 1)
    coast_ramp = smoothstep(0.0, 8.0, dc)
    z = coast_level + (z - coast_level) * coast_ramp + detail * 3 * coast_ramp

    # Terraces: high relief away from roads and coasts becomes stepped cliff levels;
    # the ground offset keeps a gentler, continuous copy of the relief.
    relief = np.maximum(z - base, 0)
    terrace = np.clip(np.floor((relief * pass_factor - 150) / 170) + 1, 0, 3).astype(np.int32)
    flat_spots = [(c[2], c[3], 14) for c in geo.CAPITALS] + [(t[1], t[2], 5) for t in geo.TOWNS + geo.CAMPS]
    flat_spots += [(x, y, 6) for pair in geo.PORTALS for _, x, y in pair] + [(l[1], l[2], 6) for l in geo.LANDMARKS]
    keep_flat = (dc <= 4) | (road_d < 6) | (distance_field(lake | river, 4) < 4) | instance_land
    for tx, ty, r in flat_spots:
        keep_flat |= f.distance(tx, ty) < r
    terrace[keep_flat] = 0
    terrace = np.minimum(terrace, np.floor((road_d - 6) / 2.5).clip(0, 3).astype(np.int32))   # step up away from roads
    z = np.where(z > base, base + (z - base) * 0.5, z)

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
    layer = np.where(land, 2 + level + terrace, 2)
    layer = np.where(sea & ~T.beach, 1, layer)
    for cx, cy, r, lv in geo.MESAS:
        d = f.distance(cx, cy) + f.fbm(3, 2) * 0.6
        layer = np.where((d <= r) & (dc > 3) & (road_d > 4), np.maximum(layer, 2 + level + lv), layer)
    layer = np.where(instance_land & (dc <= 1.2), 3, layer)              # instance ramparts
    for x0, y0, x1, y1, lv in geo.BLOCKS:
        layer = np.where((xs >= x0) & (xs <= x1) & (ys >= y0) & (ys <= y1) & land, 2 + lv, layer)
    for _ in range(6):           # neighbouring corners may differ by at most one level
        m = layer.copy()
        for dx, dy in NEIGHBOURS8:
            m = np.maximum(m, shift(layer, dx, dy, 1) - 1)
        layer = m
    ramp = np.zeros((n, n), bool)
    dry = land & ~lake & ~river
    T.ramps = stamp_ramps(layer, ramp, z, dry)
    for line, gates in getattr(geo, 'WALLS', []):     # ramparts: a raised line of corners, cliffs on both sides
        wall = (f.segment_distance(line) <= 0.8) & (land | (dw <= 4))
        for gx, gy in gates:
            wall &= f.distance(gx, gy) > 2.4
        layer = np.where(wall, np.maximum(layer, 3), layer)
        z = np.where(wall & water, z + 128 * (layer - 2), z)           # the rampart rises out of the water
    check_cliffs(layer)
    T.layer = layer
    T.ramp = ramp

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

    # ---- 7. ground textures -----------------------------------------------------
    biome_names = [z['biome'] for z in geo.ZONES]
    tex = np.zeros((n, n), dtype=np.int32)
    noises = [f.fbm(9, 3), f.fbm(6, 3), f.fbm(4, 3)]
    for zi, zdef in enumerate(geo.ZONES):
        sel = zone_of == zi
        if not sel.any():
            continue
        recipe = B[zdef['biome']]['tiles']
        for k, (tile, thr) in enumerate(recipe):
            tex[sel & (noises[k % 3] > thr)] = TILE[tile]
    biome_arr = np.array(biome_names)[zone_of]
    T.biome = biome_arr

    def per_zone(key):
        return np.array([TILE[B[b][key]] if B[b][key] else -1 for b in biome_names])[zone_of]

    cold = np.array([B[b]['cold'] for b in biome_names])[zone_of]
    rock = per_zone('rock')
    steep = slope_pt > 70
    instance_zone = np.array([bool(zd.get('instance')) for zd in geo.ZONES])[zone_of]
    tex = np.where(steep & land & ~instance_zone, rock, tex)
    height = T.h_rel
    snowcap = land & (height > np.where(cold, 300, 720)) & (noises[1] > -0.4) & ~instance_zone
    tex = np.where(snowcap, TILE['Nsnw'], tex)
    beach_tile = per_zone('beach')
    beach = land & T.beach & (dc < 1.6 + noises[2]) & (height < 45) & ~lake_adjacent(lake | river)
    tex = np.where(beach, beach_tile, tex)
    tex = np.where(water, per_zone('seabed'), tex)
    tex = np.where(lake | river, np.where(cold, TILE['Nice'], TILE['Ldrt']), tex)
    road = land & (road_d < 1.05 + noises[2] * 0.3)
    desertish = np.isin(biome_arr, ['savanna', 'desert', 'reddesert', 'needles', 'volcanic', 'amber'])
    tex = np.where(road, np.where(desertish, TILE['Ldrt'], np.where(cold, TILE['Wsng'], TILE['Ldrt'])), tex)
    tex = np.where(road & ~desertish & ~cold & (noises[1] > 0.3), TILE['Bdrt'], tex)
    # the capitals' streets are paved
    for idx, name, cx, cy, race in geo.CAPITALS:
        paved = land & (f.distance(cx, cy) + noises[0] * 2.5 < 7.5) & ~(lake | river)
        tex = np.where(paved & (noises[2] > -0.35), TILE['Ybtl'], tex)
    T.tex = tex

    blight_zone = np.array([B[b]['blight'] for b in biome_names])[zone_of]
    T.blight = blight_zone & land & (noises[0] > -0.55)

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
    T.cliff_tex = np.array([B[b]['cliff'] for b in biome_names])[zone_of]

    # ---- 9. pathing (4 x 4 cells per tile) ---------------------------------------
    T.pathing = compute_pathing(T)
    return T


def stamp_ramps(layer, ramp, z, dry):
    """Cut a ramp wherever a road climbs or drops one cliff level.

    Ramps follow the World Editor's layout: along a straight stretch of cliff
    edge, each column of the ramp flags its last upper corner and the two lower
    corners after it. The edge is straightened over a small window around the
    crossing and the ground there is levelled. Returns the ramp centres.
    """
    n = layer.shape[0]
    crossings = []
    for line in geo.ROADS:
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
        horizontal = abs(dx) >= abs(dy)            # the road runs along x: the ramp climbs along x
        s, t = (cx, cy) if horizontal else (cy, cx)

        def at(si, ti):                              # (row, column) of along/across indices
            return (ti, si) if horizontal else (si, ti)

        t0 = int(round(t))
        samples = [layer[at(int(round(s + o)), t0)] for o in (-3, 3)]
        if abs(samples[0] - samples[1]) != 1:
            continue
        upper = max(samples)
        sgn = -1 if samples[0] > samples[1] else 1     # -1: the upper side is at smaller s
        across = range(t0 - 4, t0 + 5)
        for shift_by in (0, -1, 1, -2, 2, -3, 3):      # slide along the road to a clean stretch of edge
            j0 = (int(np.floor(s)) if sgn < 0 else int(np.ceil(s))) + shift_by
            along = range(j0 - 2, j0 + 4) if sgn < 0 else range(j0 - 3, j0 + 3)
            cells = [(si, ti) for si in along for ti in across]
            if any(not (0 < si < n - 1 and 0 < ti < n - 1) for si, ti in cells):
                continue
            if any(not dry[at(si, ti)] or layer[at(si, ti)] not in (upper - 1, upper) for si, ti in cells):
                continue
            if any(ramp[at(si + a, ti + b)] for si, ti in cells for a in (-1, 0, 1) for b in (-1, 0, 1)
                   if 0 <= si + a < n and 0 <= ti + b < n):
                continue
            break
        else:
            continue
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
        done.append((cx, cy))
    return done


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
    blocked = T.cliff_tile[by, bx] | T.steep_tile[by, bx]
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
