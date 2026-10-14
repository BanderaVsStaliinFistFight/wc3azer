"""Places trees, doodads, landmarks, start locations, waygates and critters."""
import math

import numpy as np

from . import cities
from . import geography as geo
from .biomes import B
from .decor import BATS, BIRDS, DOODADS, FLIES, RUINS, SCATTER, SHELLS, SIGNPOST, VILLAGE, VILLAGE_COLD, VILLAGE_DRY
from .raster import Field, dilate, label_regions
from .terrain import MAP_W, MAP_H, ground_z_at, world_xy

NEUTRAL_PASSIVE = 15                          # classic (12 player) numbering used by war3mapUnits.doo
# tree species: (model variations, smallest scale, largest scale) from the game's destructable data
TREES = {'LTlt': (10, 0.8, 1.2), 'FTtw': (10, 0.8, 1.2), 'WTtw': (10, 0.8, 1.2), 'WTst': (10, 0.8, 1.2), 'JTtw': (10, 0.8, 1.2),
         'ATtr': (5, 0.8, 1.2), 'CTtr': (5, 0.8, 1.2), 'ITtw': (10, 0.8, 1.0), 'BTtw': (10, 0.8, 1.2), 'NTtw': (10, 0.8, 1.2),
         'ZTtw': (10, 0.65, 1.05), 'ATtc': (3, 0.8, 1.2), 'BTtc': (3, 0.8, 1.2), 'CTtc': (3, 0.8, 1.2), 'ITtc': (3, 0.8, 1.2),
         'NTtc': (3, 0.8, 1.2), 'ZTtc': (3, 0.8, 1.2), 'YTct': (2, 0.8, 1.2), 'YTft': (2, 0.8, 1.2), 'YTst': (2, 0.8, 1.2),
         'KTtw': (10, 0.65, 0.85), 'DTsh': (8, 0.8, 1.2), 'GTsh': (8, 0.8, 1.2)}
DETAIL_VARIATIONS = {'LRrk': 10, 'ARrk': 10, 'CRrk': 10, 'BRrk': 10, 'BRsp': 8, 'ZRrk': 10, 'ZRsp': 8, 'NRrk': 10, 'IRrs': 10,
                     'ORrk': 10, 'DRrk': 10, 'BRrs': 8, 'CRrs': 8, 'ORrs': 10, 'ZRrs': 8, 'IRgc': 10, 'ZPfw': 5, 'ZPsh': 3, 'APms': 4, 'CPms': 4, 'APct': 1, 'LPrs': 4, 'LPfp': 3}
# per biome: (rock, rock spire or None) scattered over steep slopes
ROCKS = {'nightelf': ('ARrk', None), 'worldtree': ('ARrk', None), 'crystal': ('ARrk', None), 'fel': ('CRrk', None),
         'savanna': ('BRrk', None), 'reddesert': ('BRrk', 'BRsp'), 'needles': ('BRrk', 'BRsp'), 'barren': ('BRrk', None),
         'desert': ('BRrk', 'BRsp'), 'amber': ('BRrk', 'BRsp'), 'jungle': ('ZRrk', 'ZRsp'), 'swamp': ('ZRrk', None),
         'snow': ('NRrk', None), 'tundra': ('NRrk', None), 'icecrown': ('IRrs', None), 'frozen': ('IRrs', None),
         'volcanic': ('ORrk', None), 'lava': ('ORrk', None), 'halls': ('DRrk', None), 'crypt': ('DRrk', None)}
# per biome: the great spire raised on the heights of a massif
SPIRES = {'snow': 'IRgc', 'tundra': 'IRgc', 'icecrown': 'IRgc', 'crystal': 'IRgc', 'savanna': 'BRrs', 'reddesert': 'BRrs',
          'needles': 'BRrs', 'barren': 'BRrs', 'desert': 'BRrs', 'amber': 'BRrs', 'volcanic': 'ORrs', 'fel': 'CRrs'}
# per biome: small plants without pathing, dotted over open ground
PLANTS = {'temperate': ['ZPfw', 'ZPsh'], 'farmland': ['ZPfw', 'ZPsh'], 'plains': ['ZPfw', 'ZPsh'], 'autumn': ['ZPsh', 'ZPfw'],
          'highland': ['ZPsh', 'ZPfw'], 'darkforest': ['ZPsh', 'APms'], 'nightelf': ['APms', 'ZPfw', 'ZPsh'],
          'worldtree': ['APms', 'ZPfw'], 'jungle': ['ZPsh', 'ZPfw'], 'swamp': ['ZPsh', 'APms'], 'grotto': ['APms', 'ZPsh'],
          'troll': ['ZPsh'], 'fel': ['CPms', 'ZPsh'], 'plague': ['CPms'], 'grizzly': ['ZPsh', 'ZPfw'], 'fjord': ['ZPsh', 'ZPfw'],
          'savanna': ['ZPsh'], 'barren': ['ZPsh'], 'tundra': ['ZPsh'], 'reddesert': ['ZPsh'], 'needles': ['ZPsh'], 'crystal': ['APms', 'ZPfw']}
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

    # ---- player start locations, one in each capital -----------------------------
    for idx, name, cx, cy, race in geo.CAPITALS:
        spot = None
        for base_r in (5, 4.5, 4):                     # prefer a roomy square, settle for a tighter one
            spot = find_spot(cx, cy, base_r, max_search=24)
            if spot:
                break
        assert spot, 'no room for start location %s' % name
        sx, sy = spot
        O.starts.append((idx, name, sx, sy, race))
        add_unit('sloc', sx, sy, idx, 'start')
        mark(occupied, sx, sy, 6); mark(reserved, sx, sy, 11)

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

    # ---- town sites stay open ground, free of trees, for whatever is built there ---------
    for name, tx, ty, building in geo.TOWNS:
        mark(reserved, tx, ty, 4)

    # ---- cities: walls, gateways and buildings at the capitals and towns ----------------------
    # Walls are destructables (the game gives them their pathing); buildings, posts and fences are
    # doodads whose footprints go into the pathing map with the other decorations below.
    walls, city_parts = cities.plan(T, rng, tile_ok, occupied, O.starts)
    walls, city_parts = cities.keep_open(T, walls, city_parts)
    for p in walls + city_parts:
        if p['box'] is not None:
            y0, y1, x0, x1 = p['box']
            occupied[max(y0 // 4, 0):(y1 - 1) // 4 + 1, max(x0 // 4, 0):(x1 - 1) // 4 + 1] = True
    O.walls = walls
    O.city_parts = city_parts
    O.doodads = O.doodads + [{k: v for k, v in w.items() if k not in ('box', 'kind')} for w in walls]

    # ---- critters: a few of each zone's wildlife ------------------------------------------
    zone_tiles = {}
    land_tiles = np.argwhere(tile_ok & ~occupied)
    for ty, tx in land_tiles[rng.permutation(len(land_tiles))]:
        zone_tiles.setdefault(T.zone_of[ty, tx], []).append((tx + 0.5, ty + 0.5))
    for zi, tiles in zone_tiles.items():
        critters = B[geo.ZONES[zi]['biome']]['critters']
        if critters:
            for tx, ty in tiles[-min(len(tiles), 40)::max(1, min(len(tiles), 40) // 4)][:4]:
                if area_ok(tx, ty, 0.5) and far_from_capitals(tx, ty, 12):
                    add_unit(str(rng.choice(critters)), tx, ty, NEUTRAL_PASSIVE, 'critter', angle=float(rng.uniform(0, 360)))

    # ---- trees ----------------------------------------------------------------------------
    # Woods come from the terrain's forest mask (T.forest_score > 0 inside a wood).
    # They grow on slopes too (anything but cliffs and water), stand with gaps
    # inside, and fray at the edges into scattered trees. Each zone's woods mix
    # several species; every species follows its own noise field, so it gathers
    # in stands (a grove of pines, then snowy trees, then a few canopy giants)
    # rather than being sprinkled evenly.
    score = T.forest_score
    has_trees = np.array([bool(B[z['biome']]['trees']) for z in geo.ZONES])[T.zone_of]
    species = sorted({t for b in B.values() for t, _ in b['trees']})
    nf = Field(n, n, seed + 101)
    stand = {t: nf.fbm(9, 3) for t in species}
    clear = reserved | dilate(occupied, 1) | (T.road_d < 2.2)
    ground = np.zeros((n, n), bool)
    ground[:-1, :-1] = ~T.cliff_tile & ~T.ramp_tile & T.land[:-1, :-1] & T.land[1:, 1:] & T.land[:-1, 1:] & T.land[1:, :-1]
    ground[:-1, :-1] &= ~T.water_flag[:-1, :-1] & ~T.water_flag[1:, 1:] & ~T.water_flag[:-1, 1:] & ~T.water_flag[1:, :-1]
    ground &= ~T.edge
    near_shore = ~T.land | dilate(~T.land, 1)
    keep_prob = np.select([score > 0.12, score > 0, score > -0.04, score > -0.12], [0.80, 0.70, 0.24, 0.035], 0.0)
    candidates = (rng.random((n, n)) < keep_prob) & ground & ~clear & ~near_shore & has_trees
    trees = []
    for ty, tx in np.argwhere(candidates):
        mix = B[geo.ZONES[T.zone_of[ty, tx]]['biome']]['trees']
        w = np.array([wt * math.exp(3.0 * stand[t][ty, tx]) for t, wt in mix])
        tid = mix[int(np.searchsorted(np.cumsum(w), rng.random() * w.sum()))][0]
        variations, lo, hi = TREES[tid]
        jx, jy = rng.uniform(-0.2, 0.2, 2)
        x, y = world_xy(tx + 0.5 + jx, ty + 0.5 + jy)
        trees.append(dict(id=tid, var=int(rng.integers(0, variations)), x=x, y=y,
                          z=ground_z_at(T, tx + 0.5 + jx, ty + 0.5 + jy), angle=4.712389,
                          scale=float(rng.uniform(lo, hi)), state=2, life=100, tx=tx + 0.5, ty=ty + 0.5))
    O.trees = trees
    O.doodads = O.doodads + [{k: v for k, v in t.items() if k not in ('tx', 'ty')} for t in trees]

    # ---- ground detail and decorations -----------------------------------------------------------
    # Solid pieces are written into the pathing map (their footprint blocks walking and building)
    # and any that cut off part of the walkable land are taken away again at the end.
    # Flowers, shrubs, mushrooms, reeds, shells and the ambient birds, bats and flies have no pathing.
    detail = []
    blockers = []                       # (doodad, cell box, pathing cells it replaced)
    blocked = np.zeros((n, n), bool)    # tiles under solid decorations
    biome_of = np.array([z['biome'] for z in geo.ZONES])[T.zone_of]
    is_tree = candidates
    steep = np.zeros((n, n), bool)
    steep[:-1, :-1] = T.steep_tile & ~T.cliff_tile
    near_water = dilate(T.lake | T.river, 2) & ~(T.lake | T.river)
    by_cliff = np.zeros((n, n), bool)
    by_cliff[:-1, :-1] = T.cliff_tile
    by_cliff = dilate(by_cliff, 1)

    def add_detail(did, tx, ty, scale=(0.8, 1.2), z=None, fixed=None, variations=None):
        x, y = world_xy(tx, ty)
        d = dict(id=did, var=int(rng.integers(0, variations or DETAIL_VARIATIONS[did])), x=x, y=y,
                 z=ground_z_at(T, tx, ty) if z is None else z,
                 angle=fixed if fixed is not None else float(rng.uniform(0, 2 * math.pi)),
                 scale=float(rng.uniform(*scale)), state=2, life=255)
        detail.append(d)
        return d

    def footprint(tx, ty, size):
        c = abs(size)
        x0, y0 = int(round(tx * 4 - c / 2)), int(round(ty * 4 - c / 2))
        return y0, y0 + c, x0, x0 + c

    def fits(tx, ty, size, allow_reserved=False):
        y0, y1, x0, x1 = footprint(tx, ty, size)
        if x0 < 0 or y0 < 0 or x1 > MAP_W * 4 or y1 > MAP_H * 4:
            return False
        tiles = (slice(y0 // 4, (y1 - 1) // 4 + 1), slice(x0 // 4, (x1 - 1) // 4 + 1))
        ok_here = tile_ok[tiles] & ~occupied[tiles] & ~blocked[tiles] & ~by_cliff[tiles] & ~T.ramp_near[tiles] & ~is_tree[tiles]
        if not allow_reserved:
            ok_here &= ~reserved[tiles]
        return bool(ok_here.all()) and T.road_d[int(ty), int(tx)] > 2.5

    def bake(d, tx, ty, size):
        y0, y1, x0, x1 = footprint(tx, ty, size)
        blockers.append((d, (y0, y1, x0, x1), T.pathing[y0:y1, x0:x1].copy()))
        if size > 0:
            T.pathing[y0:y1, x0:x1] = 0xCA
        else:
            T.pathing[y0:y1, x0:x1] |= 0x08
        blocked[y0 // 4:(y1 - 1) // 4 + 1, x0 // 4:(x1 - 1) // 4 + 1] = True

    def bake_box(d, box):
        y0, y1, x0, x1 = box
        blockers.append((d, box, T.pathing[y0:y1, x0:x1].copy()))
        T.pathing[y0:y1, x0:x1] = 0xCA
        blocked[y0 // 4:(y1 - 1) // 4 + 1, x0 // 4:(x1 - 1) // 4 + 1] = True

    # the cities' buildings, posts, monuments and fences
    for p in city_parts:
        d = {k: v for k, v in p.items() if k not in ('box', 'kind')}
        detail.append(d)
        if p['box'] is not None:
            bake_box(d, p['box'])

    def decorate(did, tx, ty, allow_reserved=False):
        variations, size, scale, fixed = DOODADS[did]
        if not fits(tx, ty, size or 1, allow_reserved):
            return False
        d = add_detail(did, tx, ty, scale=scale, fixed=fixed, variations=variations)
        if size:
            bake(d, tx, ty, size)
        return True

    roll = rng.random((n, n))
    # rocks on steep slopes, and rubble at the foot and brow of mountain cliffs
    rubble = by_cliff & tile_ok & (T.relief > 120) & (T.road_d > 5) & ~T.ramp_near & ~is_tree & ~clear & (roll < 0.05)
    for ty, tx in np.argwhere((steep & ground & ~clear & (roll < 0.09)) | rubble):
        rock, spire = ROCKS.get(str(biome_of[ty, tx]), ('LRrk', None))
        if spire and rng.random() < 0.25:
            d = add_detail(spire, tx + 0.5, ty + 0.5, scale=(0.28, 0.42))
        else:
            d = add_detail(rock, tx + 0.5, ty + 0.5, scale=(0.8, 1.4), fixed=4.712389 if rock == 'ORrk' else None)
        if rubble[ty, tx] and not blocked[ty, tx]:
            bake(d, tx + 0.5, ty + 0.5, 4)
    # great rock spires and glaciers crown the massifs
    crown = np.zeros((n, n), bool)
    crown[:-1, :-1] = T.massif_core[:-1, :-1]
    for ty, tx in np.argwhere(crown & ground & (rng.random((n, n)) < 0.03)):
        spire = SPIRES.get(str(biome_of[ty, tx]), 'ZRrs')
        add_detail(spire, tx + 0.5, ty + 0.5, scale=(0.8, 1.2), fixed=4.712389 if spire in ('ORrs', 'IRgc') else None)

    # ruins at the named sites
    def scatter_round(cx, cy, pool, count, r0, r1, allow_reserved=False):
        made = 0
        for _ in range(count * 4):
            if made >= count:
                break
            a, r = rng.uniform(0, 2 * math.pi), rng.uniform(r0, r1)
            tx, ty = round((cx + r * math.cos(a)) * 2) / 2, round((cy + r * math.sin(a)) * 2) / 2
            if 0 < tx < MAP_W and 0 < ty < MAP_H and decorate(str(rng.choice(pool)), tx, ty, allow_reserved):
                made += 1

    for name, cx, cy, _ in geo.CAMPS:
        pool = RUINS.get(str(biome_of[int(cy), int(cx)]))
        if pool:
            scatter_round(cx, cy, pool, int(rng.integers(1, 4)), 1.0, 7.0)
    # clutter round the towns
    for name, cx, cy, _ in geo.TOWNS:
        b = str(biome_of[int(cy), int(cx)])
        cold = B[b]['cold'] if b in B else False
        pool = VILLAGE_COLD if cold else VILLAGE_DRY if b in ('savanna', 'reddesert', 'needles', 'barren', 'desert', 'amber') else VILLAGE
        scatter_round(cx, cy, pool, int(rng.integers(2, 5)), 2.5, 7.0, allow_reserved=True)
        if pool is VILLAGE and rng.random() < 0.3:
            scatter_round(cx, cy, ['LSwl'], 1, 1.5, 4.0, allow_reserved=True)
    # boulders, bushes, stumps and the odd relic over open country
    open_country = tile_ok & ~is_tree & ~reserved & ~dilate(occupied, 1) & (T.road_d > 2.5) & ~steep & ~by_cliff
    roll = rng.random((n, n))
    for ty, tx in np.argwhere(open_country & (roll < 0.035)):
        pool = SCATTER.get(str(biome_of[ty, tx]))
        if pool:
            ids, weights = zip(*pool)
            decorate(str(rng.choice(ids, p=np.array(weights) / sum(weights))), tx + 0.5, ty + 0.5)
    # signposts where roads fork
    forks = []
    for line in T.road_lines:
        for ex, ey in (line[0], line[-1]):
            if all(math.hypot(ex - fx, ey - fy) > 5 for fx, fy in forks):
                forks.append((ex, ey))
    for ex, ey in forks:
        for ox, oy in ((1.6, 1.6), (-1.6, 1.6), (1.6, -1.6), (-1.6, -1.6)):
            tx, ty = ex + ox, ey + oy
            if 0 < tx < MAP_W and 0 < ty < MAP_H and tile_ok[int(ty), int(tx)] and not occupied[int(ty), int(tx)] \
                    and T.road_d[int(ty), int(tx)] > 1.2:
                add_detail(SIGNPOST, tx, ty, scale=(0.9, 1.1), variations=1)
                break
    # Stones line the roads: every few tiles along each road, on one side or the other, a rock
    # with a pebble or two at the edge of the verge (closer together where the land is rough or
    # too harsh for flowers). Each rock blocks its own tile, as the World Editor would make it.
    road_tile = np.full((n, n), 1e9)        # distance from the middle of each tile to the nearest road
    road_tile[:-1, :-1] = (T.road_d[:-1, :-1] + T.road_d[1:, :-1] + T.road_d[:-1, 1:] + T.road_d[1:, 1:]) / 4
    verge_stones = tile_ok & (road_tile > 2.0) & (road_tile < 4.0) & ~reserved & ~occupied & ~is_tree & ~by_cliff & ~T.ramp_near
    bare = ~np.isin(biome_of, list(PLANTS)) | (T.relief > 150)
    for line in T.road_lines:
        pts = np.array(line, float)
        seg = np.hypot(*np.diff(pts, axis=0).T)
        along = np.concatenate([[0.0], np.cumsum(seg)])
        s_at = rng.uniform(0, 3)
        while s_at < along[-1]:
            i = min(int(np.searchsorted(along, s_at, side='right')) - 1, len(seg) - 1)
            t = (s_at - along[i]) / max(seg[i], 1e-6)
            (ax, ay), (bx, by_) = pts[i], pts[i + 1]
            px, py = ax + (bx - ax) * t, ay + (by_ - ay) * t
            nx, ny = -(by_ - ay) / max(seg[i], 1e-6), (bx - ax) / max(seg[i], 1e-6)
            side = rng.choice([-1.0, 1.0])
            rough = placed = False
            for sd in (side, -side):
                off = rng.uniform(2.4, 3.3)
                tx, ty = int(px + nx * off * sd), int(py + ny * off * sd)
                if not (0 < tx < n - 1 and 0 < ty < n - 1) or not verge_stones[ty, tx] \
                        or blocked[ty - 1:ty + 2, tx - 1:tx + 2].any():
                    continue
                rough = bool(bare[ty, tx])
                rock = ROCKS.get(str(biome_of[ty, tx]), ('LRrk', None))[0]
                facing = 4.712389 if rock == 'ORrk' else None
                d = add_detail(rock, tx + 0.5, ty + 0.5, scale=(0.45, 0.75), fixed=facing)
                bake(d, tx + 0.5, ty + 0.5, 4)
                for _ in range(int(rng.integers(0, 2))):
                    add_detail(rock, tx + 0.5 + rng.uniform(-0.35, 0.35), ty + 0.5 + rng.uniform(-0.35, 0.35),
                               scale=(0.22, 0.38), fixed=facing)
                placed = True
                break
            s_at += (rng.uniform(2.2, 3.6) if rough else rng.uniform(3.0, 5.0)) if placed else 1.0
    # shells on the beaches, birds over woods and shores, bats in the dark places, flies over the swamps
    coast = T.land & dilate(T.sea, 1)
    roll = rng.random((n, n))
    for ty, tx in np.argwhere(coast & T.beach & tile_ok & (roll < 0.04)):
        add_detail(SHELLS, tx + rng.uniform(0.2, 0.8), ty + rng.uniform(0.2, 0.8), variations=10)
    edge_of_wood = dilate(is_tree, 1) & ~is_tree
    dark = np.isin(biome_of, ['plague', 'darkforest', 'crypt', 'fel', 'icecrown'])
    for mask, did, p in ((edge_of_wood | coast, BIRDS, 0.003), (dark & T.land, BATS, 0.002),
                         (np.isin(biome_of, ['swamp']) & T.land, FLIES, 0.004)):
        roll = rng.random((n, n))
        for ty, tx in np.argwhere(mask & (roll < p)):
            add_detail(did, tx + 0.5, ty + 0.5, variations=1)

    unblock(T, label, sizes, blockers, detail)

    # flowers, shrubs and mushrooms; reeds by the water; lily pads on the lakes
    lush = dilate(occupied | blocked, 1) | (T.road_d < 1.6)
    open_ground = tile_ok & ~is_tree & ~lush & ~steep
    roll = rng.random((n, n))
    for ty, tx in np.argwhere(open_ground & (roll < 0.05)):
        plants = PLANTS.get(str(biome_of[ty, tx]))
        if plants:
            add_detail(str(rng.choice(plants)), tx + rng.uniform(0.2, 0.8), ty + rng.uniform(0.2, 0.8))
    # Wild flowers, shrubs and mushrooms grow thick along the roadsides, in patches that come
    # and go along the way.
    patches = Field(n, n, seed + 202).fbm(5, 2)
    verge = tile_ok & (road_tile > 1.5) & (road_tile < 4.0) & ~is_tree & ~reserved & ~occupied
    for ty, tx in np.argwhere(verge & (rng.random((n, n)) < np.clip(0.2 + patches * 0.6, 0.0, 0.55))):
        plants = PLANTS.get(str(biome_of[ty, tx]))
        if not plants:
            continue
        for _ in range(int(rng.integers(1, 3))):
            plant = 'ZPfw' if 'ZPfw' in plants and rng.random() < 0.5 else str(rng.choice(plants))
            add_detail(plant, tx + rng.uniform(0.1, 0.9), ty + rng.uniform(0.1, 0.9))
    for ty, tx in np.argwhere(near_water & tile_ok & ~is_tree & ~lush & (roll > 0.90)):
        add_detail('APct' if rng.random() < 0.6 else 'LPrs', tx + rng.uniform(0.2, 0.8), ty + rng.uniform(0.2, 0.8))
    lake_pts = T.lake & ~dilate(~T.lake, 1)
    for ty, tx in np.argwhere(lake_pts & (roll < 0.04)):
        add_detail('LPfp', tx + rng.uniform(-0.3, 0.3), ty + rng.uniform(-0.3, 0.3), z=-89.6)
    O.details = detail
    O.doodads = O.doodads + detail

    # world coordinates and heights for every unit
    for u in O.units:
        u['x'], u['y'] = world_xy(u['tx'], u['ty'])
        u['z'] = ground_z_at(T, u['tx'], u['ty'])
    return O


def walkable_regions(T):
    """Label the walkable areas (tile resolution); returns (label map, area sizes), label -1 = unwalkable."""
    cells = T.pathing.reshape(MAP_H, 4, MAP_W, 4)
    walk = np.zeros((MAP_H + 1, MAP_W + 1), bool)
    walk[:-1, :-1] = ((cells & 0x02) == 0).mean(axis=(1, 3)) >= 0.5
    return label_regions(walk)


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


def unblock(T, label, sizes, blockers, detail):
    """Take away solid decorations that cut off part of an area that used to be connected."""
    for _ in range(6):
        new_label, new_sizes = walkable_regions(T)
        cut = (label >= 0) & (new_label >= 0) & (sizes[label] >= 600) & (new_sizes[new_label] < 0.9 * sizes[label])
        if not cut.any():
            return
        near = dilate(cut, 1)
        keep, gone = [], set()
        for d, (y0, y1, x0, x1), saved in blockers:
            if near[y0 // 4:(y1 - 1) // 4 + 1, x0 // 4:(x1 - 1) // 4 + 1].any():
                T.pathing[y0:y1, x0:x1] = saved
                gone.add(id(d))
            else:
                keep.append((d, (y0, y1, x0, x1), saved))
        blockers[:] = keep
        detail[:] = [d for d in detail if id(d) not in gone]
