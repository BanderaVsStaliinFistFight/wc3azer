"""Places trees, landmarks, start locations, gold mines, creeps, shops and waygates."""
import math

import numpy as np

from . import geography as geo
from .biomes import B
from .raster import dilate, smoothstep
from .terrain import MAP_W, MAP_H, ground_z_at, world_xy

NEUTRAL_HOSTILE, NEUTRAL_PASSIVE = 12, 15     # classic (12 player) numbering used by war3mapUnits.doo
ITEM_CLASS = {'permanent': 'i', 'charged': 'j', 'powerup': 'k', 'artifact': 'l'}
TREE_VARIATIONS = {'LTlt': 10, 'FTtw': 10, 'ATtr': 5, 'CTtr': 5, 'BTtw': 10, 'ZTtw': 10, 'WTst': 10, 'NTtw': 10, 'ITtw': 10}
FACING = 270.0


class Objects:
    def __init__(self):
        self.doodads = []      # war3map.doo entries
        self.units = []        # dicts: id, tx, ty, owner, kind, ...
        self.regions = []      # waygate destinations
        self.starts = []       # (index, name, tx, ty, race)
        self.tree_count = 0


def place(T, seed=7):
    rng = np.random.default_rng(seed)
    O = Objects()
    n = MAP_W + 1
    # Tiles where buildings/units can stand: dry, walkable, not a cliff or steep.
    tile_ok = np.zeros((n, n), bool)
    blocked_tile = T.cliff_tile | T.steep_tile
    ok = ~blocked_tile & T.land[:-1, :-1] & T.land[1:, 1:] & T.land[:-1, 1:] & T.land[1:, :-1]
    ok &= ~T.water_flag[:-1, :-1] & ~T.water_flag[1:, 1:] & ~T.water_flag[:-1, 1:] & ~T.water_flag[1:, :-1]
    tile_ok[:-1, :-1] = ok
    tile_ok &= ~T.edge
    reserved = np.zeros((n, n), bool)     # no trees here
    occupied = np.zeros((n, n), bool)     # no buildings/units here

    def area_ok(tx, ty, r, allow_occupied=False):
        x0, x1 = int(tx - r), int(math.ceil(tx + r))
        y0, y1 = int(ty - r), int(math.ceil(ty + r))
        if x0 < 0 or y0 < 0 or x1 >= MAP_W or y1 >= MAP_H:
            return False
        if not tile_ok[y0:y1, x0:x1].all():
            return False
        if not allow_occupied and occupied[y0:y1, x0:x1].any():
            return False
        z = T.ground_z[y0:y1 + 1, x0:x1 + 1]
        return z.max() - z.min() < 60 + 12 * r

    def find_spot(tx, ty, r, max_search=14, allow_occupied=False, step=0.5, accept=None):
        for rad in np.arange(0, max_search + 0.01, step):
            count = max(1, int(rad * 6))
            for k in range(count):
                a = 2 * math.pi * k / count
                x, y = tx + rad * math.cos(a), ty + rad * math.sin(a)
                x, y = round(x * 2) / 2, round(y * 2) / 2
                if area_ok(x, y, r, allow_occupied) and (accept is None or accept(x, y)):
                    return x, y
        return None

    def mark(arr, tx, ty, r):
        x0, x1 = max(int(tx - r), 0), min(int(math.ceil(tx + r)), MAP_W)
        y0, y1 = max(int(ty - r), 0), min(int(math.ceil(ty + r)), MAP_H)
        arr[y0:y1, x0:x1] = True

    def zone_at(tx, ty):
        return geo.ZONES[T.zone_of[int(ty), int(tx)]]

    def add_unit(uid, tx, ty, owner, kind, angle=FACING, **kw):
        u = dict(id=uid, tx=tx, ty=ty, owner=owner, kind=kind, angle=angle, **kw)
        O.units.append(u)
        return u

    # ---- landmark doodads first so nothing is built on top of them --------------
    for did, tx, ty, scale, ang in geo.LANDMARKS:
        x, y = world_xy(tx, ty)
        O.doodads.append(dict(id=did, var=0, x=x, y=y, z=ground_z_at(T, tx, ty), angle=ang, scale=scale, state=2, life=255))
        mark(reserved, tx, ty, 5); mark(occupied, tx, ty, 4)
    for did, tx, ty, scale in geo.DESTRUCTABLE_LANDMARKS:
        x, y = world_xy(tx, ty)
        O.doodads.append(dict(id=did, var=0, x=x, y=y, z=ground_z_at(T, tx, ty), angle=4.712389, scale=scale, state=2, life=100))
        mark(reserved, tx, ty, 6); mark(occupied, tx, ty, 5)

    # ---- player start locations, each with a main gold mine ---------------------
    mines = []
    def mine_spot_for(sx, sy):
        for dist in (7.5, 8.5, 9.5, 10.5):
            for ang in np.linspace(0, 2 * math.pi, 24, endpoint=False):
                mx, my = sx + dist * math.cos(ang), sy + dist * math.sin(ang)
                mx, my = round(mx * 2) / 2, round(my * 2) / 2
                if area_ok(mx, my, 2.5):
                    return mx, my, ang
        return None

    for idx, name, cx, cy, race in geo.CAPITALS:
        placed = None
        for rad in np.arange(0, 24, 0.5):
            for k in range(max(1, int(rad * 6))):
                a = 2 * math.pi * k / max(1, int(rad * 6))
                sx, sy = round((cx + rad * math.cos(a)) * 2) / 2, round((cy + rad * math.sin(a)) * 2) / 2
                if area_ok(sx, sy, 5):
                    placed = mine_spot_for(sx, sy)
                    if placed:
                        break
            if placed:
                break
        assert placed, 'no room for start location %s' % name
        O.starts.append((idx, name, sx, sy, race))
        add_unit('sloc', sx, sy, idx, 'start')
        mark(occupied, sx, sy, 6); mark(reserved, sx, sy, 11)
        mx, my, ang = placed
        add_unit('ngol', mx, my, NEUTRAL_PASSIVE, 'mine', gold=15000)
        mines.append((mx, my))
        mark(occupied, mx, my, 3); mark(reserved, mx, my, 4)
        # a grove behind the base guarantees lumber
        O.__dict__.setdefault('groves', []).append((sx, sy, ang + math.pi, zone_at(sx, sy)))

    capital_xy = [(s[2], s[3]) for s in O.starts]

    def far_from_capitals(tx, ty, d):
        return all(math.hypot(tx - cx, ty - cy) > d for cx, cy in capital_xy)

    # ---- waygates (portal network) -----------------------------------------------
    region_index = 0
    portals = []
    for a, b in geo.PORTALS:
        spots = []
        for name, tx, ty in (a, b):
            spot = find_spot(tx, ty, 2.0, max_search=24, accept=lambda x, y: far_from_capitals(x, y, 17))
            assert spot, 'no room for waygate %s' % name
            spots.append((name,) + spot)
            mark(occupied, spot[0], spot[1], 2.5); mark(reserved, spot[0], spot[1], 4)
        for (name, gx, gy), (dname, dx, dy) in ((spots[0], spots[1]), (spots[1], spots[0])):
            # arrive next to the partner gate, on open ground
            ex, ey = next(((dx + ox, dy + oy) for ox, oy in ((0, -3.5), (3.5, 0), (-3.5, 0), (0, 3.5), (2.5, -2.5), (-2.5, -2.5))
                           if area_ok(dx + ox, dy + oy, 1, allow_occupied=True)), (dx, dy - 3.5))
            rx, ry = world_xy(ex, ey)
            O.regions.append(dict(left=rx - 128, bottom=ry - 128, right=rx + 128, top=ry + 128,
                                  name='%s Exit' % dname.replace("'", ''), index=region_index, color=(160, 80, 255)))
            add_unit('nwgt', gx, gy, NEUTRAL_PASSIVE, 'waygate', waygate=region_index, label=name)
            region_index += 1
        portals.append(((spots[0][1], spots[0][2]), (spots[1][1], spots[1][2])))
    O.portals = portals

    # ---- towns: neutral shops ------------------------------------------------------
    shops = []
    deep_sea = T.water & (T.h_rel < -60)
    from .raster import distance_field
    sea_dist = distance_field(deep_sea, 12)
    for name, tx, ty, building in geo.TOWNS:
        if building == 'nshp':
            spot = find_spot(tx, ty, 2.0, max_search=14, accept=lambda x, y: sea_dist[int(y), int(x)] <= 4.5)
        else:
            spot = find_spot(tx, ty, 2.0, max_search=10)
        if spot is None:
            continue
        add_unit(building, spot[0], spot[1], NEUTRAL_PASSIVE, 'shop', label=name)
        mark(occupied, spot[0], spot[1], 3); mark(reserved, spot[0], spot[1], 4)
        shops.append(spot)

    # ---- expansions: gold mine guarded by a creep camp -------------------------------
    creeps = []
    camp_count = 0

    def creep_camp(tx, ty, strength, zdef, guard_of=None, label=''):
        biome = B[zdef['biome']]
        low, mid, high = biome['creeps']
        if strength == 0:
            roster = [rng.choice(mid)] + [rng.choice(low) for _ in range(rng.integers(1, 3))]
            drop = ('powerup' if rng.random() < 0.6 else 'permanent', int(rng.integers(1, 3)))
        elif strength == 1:
            roster = [rng.choice(high)] + [rng.choice(mid) for _ in range(2)]
            drop = ('permanent' if rng.random() < 0.6 else 'charged', int(rng.integers(2, 5)))
        else:
            roster = [rng.choice(high) for _ in range(2)] + [rng.choice(mid) for _ in range(2)]
            drop = ('permanent' if rng.random() < 0.7 else 'artifact', int(rng.integers(5, 8)))
        placed = 0
        for k, uid in enumerate(roster):
            a = rng.uniform(0, 2 * math.pi)
            ux, uy = tx + rng.uniform(0.6, 2.2) * math.cos(a), ty + rng.uniform(0.6, 2.2) * math.sin(a)
            if not area_ok(ux, uy, 0.5, allow_occupied=True):
                ux, uy = tx, ty
                if not area_ok(ux, uy, 0.5, allow_occupied=True):
                    continue
            facing = math.degrees(math.atan2(ty - uy, tx - ux)) % 360 if (ux, uy) != (tx, ty) else rng.uniform(0, 360)
            if guard_of:
                facing = math.degrees(math.atan2(guard_of[1] - uy, guard_of[0] - ux)) % 360
            kw = {}
            if k == 0:
                kw['drops'] = [[('Y%sI%d' % (ITEM_CLASS[drop[0]], drop[1]), 100)]]
            add_unit(str(uid), ux, uy, NEUTRAL_HOSTILE, 'creep', angle=facing, **kw)
            creeps.append((ux, uy))
            placed += 1
        return placed

    for name, tx, ty, strength in geo.CAMPS:
        spot = find_spot(tx, ty, 2.5, max_search=10)
        if spot is None or not far_from_capitals(spot[0], spot[1], 16):
            continue
        mx, my = spot
        add_unit('ngol', mx, my, NEUTRAL_PASSIVE, 'mine', gold=[8000, 12500, 15000][strength], label=name)
        mines.append((mx, my))
        mark(occupied, mx, my, 3); mark(reserved, mx, my, 5)
        # camp sits between the mine and open ground
        for ang in rng.permutation(np.linspace(0, 2 * math.pi, 12, endpoint=False)):
            cx, cy = mx + 4.5 * math.cos(ang), my + 4.5 * math.sin(ang)
            if area_ok(cx, cy, 1.5) and far_from_capitals(cx, cy, 14):
                creep_camp(cx, cy, strength, zone_at(cx, cy), guard_of=(mx, my), label=name)
                mark(occupied, cx, cy, 2); mark(reserved, cx, cy, 3)
                camp_count += 1
                break

    # ---- roaming camps spread over every zone ---------------------------------------------
    zone_tiles = {}
    land_tiles = np.argwhere(tile_ok & ~occupied)
    for ty, tx in land_tiles[rng.permutation(len(land_tiles))]:
        zi = T.zone_of[ty, tx]
        zone_tiles.setdefault(zi, []).append((tx + 0.5, ty + 0.5))
    for zi, tiles in zone_tiles.items():
        zdef = geo.ZONES[zi]
        want = max(1, min(5, len(tiles) // 340))
        made = 0
        for tx, ty in tiles:
            if made >= want:
                break
            if not far_from_capitals(tx, ty, 22) or not area_ok(tx, ty, 1.5):
                continue
            if any(math.hypot(tx - cx, ty - cy) < 9 for cx, cy in creeps[-40:]):
                continue
            strength = int(rng.choice([0, 0, 1, 1, 2]))
            if creep_camp(tx, ty, strength, zdef):
                mark(occupied, tx, ty, 2); mark(reserved, tx, ty, 2)
                made += 1
                camp_count += 1
        # critters
        critters = B[zdef['biome']]['critters']
        if critters:
            for tx, ty in tiles[-min(len(tiles), 40)::max(1, min(len(tiles), 40) // 4)][:4]:
                if area_ok(tx, ty, 0.5) and far_from_capitals(tx, ty, 12):
                    add_unit(str(rng.choice(critters)), tx, ty, NEUTRAL_PASSIVE, 'critter', angle=float(rng.uniform(0, 360)))
    O.camp_count = camp_count

    # ---- trees ----------------------------------------------------------------------------
    f = T.field
    forest_noise = (f.fbm(16, 4) + f.fbm(7, 3) * 0.5) / 1.5
    density = np.array([z.get('density', B[z['biome']]['density']) for z in geo.ZONES])[T.zone_of]
    tree_ids = np.array([B[z['biome']]['tree'] or '' for z in geo.ZONES])[T.zone_of]
    # per-zone threshold = the noise quantile that turns `density` of the land into forest
    land_noise = np.sort(forest_noise[T.land])
    q = np.clip(1.0 - density, 0.0, 1.0)
    thresh = land_noise[np.minimum((q * (len(land_noise) - 1)).astype(int), len(land_noise) - 1)]
    thresh = np.where(density <= 0, np.inf, thresh)
    forest = forest_noise > thresh
    clear = reserved | dilate(occupied, 1) | (T.road_d < 2.2)
    land_dry = tile_ok & (T.slope < 70)
    near_shore = ~T.land | dilate(~T.land, 1)
    candidates = forest & land_dry & ~clear & ~near_shore & (tree_ids != '')
    # thin out the interior of forests a little so they are not solid walls everywhere
    keep_prob = np.where(forest_noise > thresh + 0.12, 0.95, 0.8)
    candidates &= rng.random((n, n)) < keep_prob
    # groves behind each start location
    for sx, sy, ang, zdef in O.groves:
        tid = B[zdef['biome']]['tree'] or 'LTlt'
        for r in np.arange(13, 19.5, 1.0):
            for a in np.linspace(ang - 1.3, ang + 1.3, int(r * 2.6)):
                gx, gy = int(sx + r * math.cos(a)), int(sy + r * math.sin(a))
                if 0 <= gx < MAP_W and 0 <= gy < MAP_H and land_dry[gy, gx] and not occupied[gy, gx] and not near_shore[gy, gx]:
                    candidates[gy, gx] = True
                    if tree_ids[gy, gx] == '':
                        tree_ids[gy, gx] = tid
    trees = []
    for ty, tx in np.argwhere(candidates):
        tid = str(tree_ids[ty, tx])
        x, y = world_xy(tx + 0.5, ty + 0.5)
        trees.append(dict(id=tid, var=int(rng.integers(0, TREE_VARIATIONS[tid])), x=x, y=y,
                          z=ground_z_at(T, tx + 0.5, ty + 0.5), angle=4.712389,
                          scale=float(rng.uniform(0.8, 1.2)), state=2, life=100, tx=tx + 0.5, ty=ty + 0.5))
    O.trees = trees
    O.doodads = O.doodads + [{k: v for k, v in t.items() if k not in ('tx', 'ty')} for t in trees]
    O.mines, O.creeps, O.shops = mines, creeps, shops

    # world coordinates and heights for every unit
    for u in O.units:
        u['x'], u['y'] = world_xy(u['tx'], u['ty'])
        u['z'] = ground_z_at(T, u['tx'], u['ty'])
    return O
