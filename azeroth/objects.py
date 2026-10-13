"""Places trees, landmarks, start locations, gold mines, creeps, shops and waygates."""
import math

import numpy as np

from . import geography as geo
from .biomes import B
from .raster import dilate, smoothstep
from .terrain import MAP_W, MAP_H, ground_z_at, world_xy

NEUTRAL_HOSTILE, NEUTRAL_PASSIVE = 12, 15     # classic (12 player) numbering used by war3mapUnits.doo
ITEM_CLASS = {'permanent': 'i', 'charged': 'j', 'powerup': 'k', 'artifact': 'l'}
TREE_VARIATIONS = {'LTlt': 10, 'FTtw': 10, 'ATtr': 5, 'CTtr': 5, 'BTtw': 10, 'ZTtw': 10, 'WTst': 10, 'NTtw': 10, 'ITtw': 10,
                   'ATtc': 3, 'ZTtc': 3, 'CTtc': 3}
DETAIL_VARIATIONS = {'LRrk': 10, 'ARrk': 10, 'CRrk': 10, 'BRrk': 10, 'BRsp': 8, 'ZRrk': 10, 'ZRsp': 8, 'NRrk': 10, 'IRrs': 10,
                     'ORrk': 10, 'DRrk': 10, 'ZPfw': 5, 'ZPsh': 3, 'APms': 4, 'CPms': 4, 'APct': 1, 'LPrs': 4, 'LPfp': 3}
# per biome: (rock, rock spire or None) scattered over steep slopes
ROCKS = {'nightelf': ('ARrk', None), 'worldtree': ('ARrk', None), 'crystal': ('ARrk', None), 'fel': ('CRrk', None),
         'savanna': ('BRrk', None), 'reddesert': ('BRrk', 'BRsp'), 'needles': ('BRrk', 'BRsp'), 'barren': ('BRrk', None),
         'desert': ('BRrk', 'BRsp'), 'amber': ('BRrk', 'BRsp'), 'jungle': ('ZRrk', 'ZRsp'), 'swamp': ('ZRrk', None),
         'snow': ('NRrk', None), 'tundra': ('NRrk', None), 'icecrown': ('IRrs', None), 'frozen': ('IRrs', None),
         'volcanic': ('ORrk', None), 'lava': ('ORrk', None), 'halls': ('DRrk', None), 'crypt': ('DRrk', None)}
# per biome: small plants without pathing, dotted over open ground
PLANTS = {'temperate': ['ZPfw', 'ZPsh'], 'farmland': ['ZPfw', 'ZPsh'], 'plains': ['ZPfw', 'ZPsh'], 'autumn': ['ZPsh', 'ZPfw'],
          'highland': ['ZPsh', 'ZPfw'], 'darkforest': ['ZPsh', 'APms'], 'nightelf': ['APms', 'ZPfw', 'ZPsh'],
          'worldtree': ['APms', 'ZPfw'], 'jungle': ['ZPsh', 'ZPfw'], 'swamp': ['ZPsh', 'APms'], 'grotto': ['APms', 'ZPsh'],
          'troll': ['ZPsh'], 'fel': ['CPms', 'ZPsh'], 'plague': ['CPms'], 'grizzly': ['ZPsh', 'ZPfw'], 'fjord': ['ZPsh', 'ZPfw'],
          'savanna': ['ZPsh'], 'barren': ['ZPsh'], 'reddesert': ['ZPsh'], 'needles': ['ZPsh'], 'crystal': ['APms', 'ZPfw']}
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
    blocked_tile = T.cliff_tile | T.steep_tile | T.ramp_tile
    ok = ~blocked_tile & T.land[:-1, :-1] & T.land[1:, 1:] & T.land[:-1, 1:] & T.land[1:, :-1]
    ok &= ~T.water_flag[:-1, :-1] & ~T.water_flag[1:, 1:] & ~T.water_flag[:-1, 1:] & ~T.water_flag[1:, :-1]
    tile_ok[:-1, :-1] = ok
    tile_ok &= ~T.edge
    reserved = np.zeros((n, n), bool)     # no trees here
    label, sizes = walkable_regions(T)
    main_ground = main_regions(T, label, sizes)
    tile_ok &= main_ground
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
        for dist in (7.5, 8.5, 9.5, 10.5, 11.5, 12.5):
            for ang in np.linspace(0, 2 * math.pi, 24, endpoint=False):
                mx, my = sx + dist * math.cos(ang), sy + dist * math.sin(ang)
                mx, my = round(mx * 2) / 2, round(my * 2) / 2
                if area_ok(mx, my, 2.5):
                    return mx, my, ang
        return None

    for idx, name, cx, cy, race in geo.CAPITALS:
        placed = None
        for base_r in (5, 4.5, 4):                     # prefer a roomy base, settle for a tighter one
            for rad in np.arange(0, 24, 0.5):
                for k in range(max(1, int(rad * 6))):
                    a = 2 * math.pi * k / max(1, int(rad * 6))
                    sx, sy = round((cx + rad * math.cos(a)) * 2) / 2, round((cy + rad * math.sin(a)) * 2) / 2
                    if area_ok(sx, sy, base_r):
                        placed = mine_spot_for(sx, sy)
                        if placed:
                            break
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
            spot = find_spot(tx, ty, 2.0, max_search=16, accept=lambda x, y: sea_dist[int(y), int(x)] <= 6)
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
        elif strength == 2:
            roster = [rng.choice(high) for _ in range(2)] + [rng.choice(mid) for _ in range(2)]
            drop = ('permanent' if rng.random() < 0.7 else 'artifact', int(rng.integers(5, 8)))
        else:                                   # a raid boss and its retinue
            roster = [rng.choice(high) for _ in range(3)] + [rng.choice(mid) for _ in range(2)]
            drop = ('artifact', 7)
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
            elif k == 1 and strength == 3:
                kw['drops'] = [[('YiI6', 100)]]
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

    # ---- instances: guards and bosses without a gold mine ------------------------------------
    for name, tx, ty, strength in geo.DUNGEON_CAMPS:
        spot = find_spot(tx, ty, 1.5, max_search=6)
        assert spot, 'no room for %s' % name
        if creep_camp(spot[0], spot[1], strength, zone_at(*spot), label=name):
            mark(occupied, spot[0], spot[1], 2.5); mark(reserved, spot[0], spot[1], 3)
            camp_count += 1

    # ---- roaming camps spread over every zone ---------------------------------------------
    # (only on ground big enough to be part of the world, not on sealed-off plateaus)
    zone_tiles = {}
    land_tiles = np.argwhere(tile_ok & ~occupied)
    for ty, tx in land_tiles[rng.permutation(len(land_tiles))]:
        zi = T.zone_of[ty, tx]
        zone_tiles.setdefault(zi, []).append((tx + 0.5, ty + 0.5))
    for zi, tiles in zone_tiles.items():
        zdef = geo.ZONES[zi]
        if zdef.get('instance'):
            continue
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
    # Woods come from the terrain's forest mask (T.forest_score > 0 inside a wood).
    # They grow on slopes too (anything but cliffs and water), stand a little
    # thinner inside, and fray at the edges into scattered trees.
    score = T.forest_score
    tree_ids = np.array([B[z['biome']]['tree'] or '' for z in geo.ZONES])[T.zone_of]
    mix = [B[z['biome']].get('tree2') for z in geo.ZONES]
    clear = reserved | dilate(occupied, 1) | (T.road_d < 2.2)
    ground = np.zeros((n, n), bool)
    ground[:-1, :-1] = ~T.cliff_tile & ~T.ramp_tile & T.land[:-1, :-1] & T.land[1:, 1:] & T.land[:-1, 1:] & T.land[1:, :-1]
    ground[:-1, :-1] &= ~T.water_flag[:-1, :-1] & ~T.water_flag[1:, 1:] & ~T.water_flag[:-1, 1:] & ~T.water_flag[1:, :-1]
    ground &= ~T.edge
    land_dry = tile_ok & (T.slope < 70)
    near_shore = ~T.land | dilate(~T.land, 1)
    keep_prob = np.select([score > 0.12, score > 0, score > -0.04, score > -0.12], [0.96, 0.86, 0.32, 0.05], 0.0)
    candidates = (rng.random((n, n)) < keep_prob) & ground & ~clear & ~near_shore & (tree_ids != '')
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
        other = mix[T.zone_of[ty, tx]]
        if other and rng.random() < other[1]:
            tid = other[0]
        jx, jy = rng.uniform(-0.2, 0.2, 2)
        x, y = world_xy(tx + 0.5 + jx, ty + 0.5 + jy)
        trees.append(dict(id=tid, var=int(rng.integers(0, TREE_VARIATIONS[tid])), x=x, y=y,
                          z=ground_z_at(T, tx + 0.5 + jx, ty + 0.5 + jy), angle=4.712389,
                          scale=float(rng.uniform(0.8, 1.2)), state=2, life=100, tx=tx + 0.5, ty=ty + 0.5))
    O.trees = trees
    O.doodads = O.doodads + [{k: v for k, v in t.items() if k not in ('tx', 'ty')} for t in trees]

    # ---- ground detail -----------------------------------------------------------------------
    # Rocks only where the ground is already impassable (steep slopes), so the baked
    # pathing map stays true; flowers, shrubs, mushrooms and reeds have no pathing.
    detail = []
    biome_of = np.array([z['biome'] for z in geo.ZONES])[T.zone_of]
    is_tree = candidates
    steep = np.zeros((n, n), bool)
    steep[:-1, :-1] = T.steep_tile & ~T.cliff_tile
    near_water = dilate(T.lake | T.river, 2) & ~(T.lake | T.river)

    def add_detail(did, tx, ty, scale=(0.8, 1.2), z=None, fixed=None):
        x, y = world_xy(tx, ty)
        detail.append(dict(id=did, var=int(rng.integers(0, DETAIL_VARIATIONS[did])), x=x, y=y,
                           z=ground_z_at(T, tx, ty) if z is None else z,
                           angle=fixed if fixed is not None else float(rng.uniform(0, 2 * math.pi)),
                           scale=float(rng.uniform(*scale)), state=2, life=255))

    roll = rng.random((n, n))
    # rubble at the foot and brow of mountain cliffs: walkable ground, so its tile is blocked in the pathing map
    by_cliff = np.zeros((n, n), bool)
    by_cliff[:-1, :-1] = T.cliff_tile
    by_cliff = dilate(by_cliff, 1) & tile_ok & (T.relief > 120) & (T.road_d > 5) & ~T.ramp_near
    rubble = by_cliff & ~is_tree & ~clear & (roll < 0.10)
    for ty, tx in np.argwhere((steep & ground & ~clear & (roll < 0.2)) | rubble):
        rock, spire = ROCKS.get(str(biome_of[ty, tx]), ('LRrk', None))
        if spire and rng.random() < 0.25:
            add_detail(spire, tx + 0.5, ty + 0.5, scale=(0.28, 0.42))
        else:
            add_detail(rock, tx + 0.5, ty + 0.5, scale=(0.8, 1.4), fixed=4.712389 if rock == 'ORrk' else None)
        if rubble[ty, tx]:
            detail[-1]['tile'] = (ty, tx)
            T.pathing[ty * 4:ty * 4 + 4, tx * 4:tx * 4 + 4] = 0xCA
            occupied[ty, tx] = True
    unblock_rubble(T, label, sizes, rubble, detail)
    lush = dilate(occupied, 1) | (T.road_d < 1.6)
    open_ground = tile_ok & ~is_tree & ~lush & ~steep
    roll = rng.random((n, n))
    for ty, tx in np.argwhere(open_ground & (roll < 0.09)):
        plants = PLANTS.get(str(biome_of[ty, tx]))
        if plants:
            add_detail(str(rng.choice(plants)), tx + rng.uniform(0.2, 0.8), ty + rng.uniform(0.2, 0.8))
    for ty, tx in np.argwhere(near_water & tile_ok & ~is_tree & ~lush & (roll > 0.80)):
        add_detail('APct' if rng.random() < 0.6 else 'LPrs', tx + rng.uniform(0.2, 0.8), ty + rng.uniform(0.2, 0.8))
    lake_pts = T.lake & ~dilate(~T.lake, 1)
    for ty, tx in np.argwhere(lake_pts & (roll < 0.05)):
        add_detail('LPfp', tx + rng.uniform(-0.3, 0.3), ty + rng.uniform(-0.3, 0.3), z=-89.6)
    detail = [{k: v for k, v in d.items() if k != 'tile'} for d in detail]
    O.details = detail
    O.doodads = O.doodads + detail
    O.mines, O.creeps, O.shops = mines, creeps, shops

    # world coordinates and heights for every unit
    for u in O.units:
        u['x'], u['y'] = world_xy(u['tx'], u['ty'])
        u['z'] = ground_z_at(T, u['tx'], u['ty'])
    return O


def walkable_regions(T):
    """Label the walkable areas (tile resolution); returns (label map, area sizes), label -1 = unwalkable."""
    cells = T.pathing.reshape(MAP_H, 4, MAP_W, 4)
    walk = ((cells & 0x02) == 0).mean(axis=(1, 3)) >= 0.5
    label = -np.ones((MAP_H + 1, MAP_W + 1), np.int64)
    sizes = []
    for sy, sx in np.argwhere(walk):
        if label[sy, sx] >= 0:
            continue
        cid, stack, count = len(sizes), [(sy, sx)], 0
        label[sy, sx] = cid
        while stack:
            y, x = stack.pop()
            count += 1
            for yy, xx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                if 0 <= yy < MAP_H and 0 <= xx < MAP_W and walk[yy, xx] and label[yy, xx] < 0:
                    label[yy, xx] = cid
                    stack.append((yy, xx))
        sizes.append(count)
    return label, np.array(sizes + [0])


def main_regions(T, label, sizes):
    """Tiles on the main walkable area of their landmass (its largest), as opposed to sealed-off plateaus."""
    owner = np.where(T.land, T.land_id, -1)
    sel = (owner >= 0) & (label >= 0)
    keys, counts = np.unique(owner[sel] * (len(sizes) + 1) + label[sel], return_counts=True)
    best = {}
    for key, count in zip(keys, counts):
        land, lab = divmod(int(key), len(sizes) + 1)
        if count > best.get(land, (0, -1))[0]:
            best[land] = (count, lab)
    return np.isin(label, [lab for _, lab in best.values()]) & (label >= 0)


def unblock_rubble(T, label, sizes, rubble, detail):
    """Take away rubble that cut off part of an area that used to be connected."""
    for _ in range(6):
        new_label, new_sizes = walkable_regions(T)
        cut = (label >= 0) & (new_label >= 0) & (sizes[label] >= 600) & (new_sizes[new_label] < 0.9 * sizes[label])
        culprits = dilate(cut, 1) & rubble
        if not culprits.any():
            return
        for ty, tx in np.argwhere(culprits):
            T.pathing[ty * 4:ty * 4 + 4, tx * 4:tx * 4 + 4] = 0x40
            rubble[ty, tx] = False
        detail[:] = [d for d in detail if not ('tile' in d and not rubble[d['tile']])]
