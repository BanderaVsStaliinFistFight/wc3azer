"""Rasterises the geography into Warcraft III terrain data (480 x 480 tiles)."""
import numpy as np

from . import geography as geo
from .biomes import B, CLIFF_SNOW, GROUND_TILES, TILE
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
        amp_by_land.append(min(1.0, size / 9.0))
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
    for line, width in getattr(geo, 'SEA_INLETS', []):
        land &= ~(f.segment_distance(line) < width + f.fbm(5, 2) * 0.4)
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
    coast_ramp = smoothstep(0.0, 8.0, dc)
    z = 14 + (z - 14) * coast_ramp + detail * 3 * coast_ramp

    sea = water & ~lake & ~river
    z_sea = -(16 + 30 * np.minimum(dw, 9)) + f.fbm(10, 2) * 10
    lake_depth = distance_field(~lake, 8)
    z_lake = -(12 + 26 * np.minimum(lake_depth, 4))
    z = np.where(sea, z_sea, z)
    z = np.where(lake, z_lake, z)
    z = np.where(river, -26.0, z)
    strait = shallow_strait & water
    z = np.where(strait, np.maximum(z, -32.0), z)
    # The Maelstrom: a deep whirlpool
    md = f.distance(*geo.MAELSTROM)
    z = np.where(sea, z - 220 * smoothstep(16, 2, md), z)
    T.h_rel = z
    T.water = water
    T.lake, T.river, T.sea = lake, river, sea

    # ---- 5. cliff levels ------------------------------------------------------
    layer = np.full((n, n), 2, dtype=np.int32)
    for cx, cy, r, lv in geo.MESAS:
        d = f.distance(cx, cy) + f.fbm(3, 2) * 0.6
        layer = np.maximum(layer, np.where(d <= r, 2 + lv, 2))
    layer = np.where(dc > 3, layer, 2)
    for _ in range(4):           # neighbouring corners may differ by at most one level
        m = layer.copy()
        for dx, dy in NEIGHBOURS8:
            m = np.maximum(m, shift(layer, dx, dy, 2) - 1)
        layer = m
    layer = np.where(dc > 1.5, layer, 2)
    T.layer = layer

    z_world = SEA_Z + z
    raw = np.clip(np.round(8192 + 4 * z_world), 256, 16000).astype(np.int32)
    T.height_raw = raw
    T.ground_z = (raw - 8192) / 4.0 + (layer - 2) * 128.0   # final world z of each tilepoint

    # ---- 6. tile-level analysis (tile (i, j) has corners i..i+1, j..j+1) -------
    gz = T.ground_z
    c00, c10, c01, c11 = gz[:-1, :-1], gz[:-1, 1:], gz[1:, :-1], gz[1:, 1:]
    tile_range = np.maximum.reduce([c00, c10, c01, c11]) - np.minimum.reduce([c00, c10, c01, c11])
    l00, l10, l01, l11 = layer[:-1, :-1], layer[:-1, 1:], layer[1:, :-1], layer[1:, 1:]
    cliff_tile = (l00 != l10) | (l00 != l01) | (l00 != l11)
    T.cliff_tile = cliff_tile
    T.steep_tile = (tile_range > 95) & ~cliff_tile
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
    tex = np.where(steep & land, rock, tex)
    snowcap = land & (z > np.where(cold, 300, 720)) & (noises[1] > -0.4)
    tex = np.where(snowcap, TILE['Nsnw'], tex)
    beach_tile = per_zone('beach')
    beach = land & (dc < 1.6 + noises[2]) & (z < 45) & ~lake_adjacent(lake | river)
    tex = np.where(beach, beach_tile, tex)
    tex = np.where(water, per_zone('seabed'), tex)
    tex = np.where(lake | river, np.where(cold, TILE['Nice'], TILE['Ldrt']), tex)
    road = land & (road_d < 1.05 + noises[2] * 0.3)
    desertish = np.isin(biome_arr, ['savanna', 'desert', 'reddesert', 'needles', 'volcanic', 'amber'])
    tex = np.where(road, np.where(desertish, TILE['Ldrt'], np.where(cold, TILE['Wsng'], TILE['Ldrt'])), tex)
    tex = np.where(road & ~desertish & ~cold & (noises[1] > 0.3), TILE['Bdrt'], tex)
    T.tex = tex

    blight_zone = np.array([B[b]['blight'] for b in biome_names])[zone_of]
    T.blight = blight_zone & land & (noises[0] > -0.55)

    # ---- 8. flags, edges, variations ----------------------------------------------
    flags = np.zeros((n, n), dtype=np.int32)
    flags |= np.where(T.blight, 0x20, 0)
    flags |= np.where(water | (T.ground_z < SEA_Z), 0x40, 0)
    T.water_flag = (flags & 0x40) != 0
    T.flags = flags
    ii, jj = xs.astype(int), ys.astype(int)
    T.edge = ((ii < MARGIN_L) | (ii >= MAP_W - MARGIN_R) | (jj < MARGIN_B) | (jj >= MAP_H - MARGIN_T)) & (ii < MAP_W) & (jj < MAP_H)
    w = np.array(VARIATION_WEIGHTS, dtype=np.float64)
    T.variation = f.rng.choice(len(w), size=(n, n), p=w / w.sum()).astype(np.int32)
    cliff_tex = np.where(cold, CLIFF_SNOW, 0)
    T.cliff_tex = np.where(layer == 2, np.where(dilate(layer > 2, 2), cliff_tex, 15), cliff_tex)

    # ---- 9. pathing (4 x 4 cells per tile) ---------------------------------------
    T.pathing = compute_pathing(T)
    return T


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
