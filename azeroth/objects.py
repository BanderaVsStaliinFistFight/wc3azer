"""Places trees, doodads, landmarks, start locations, waygates and critters."""
import collections
import math

import numpy as np

from . import cities
from . import geography as geo
from .biomes import B, TILE
from .decor import (BATS, BIRDS, CLUTTER, DOODADS, FLIES, HOUSE_KIND, ICE_FLOES, KIND_OF, KINDS, LILIES, RUINS, RUSHES, SCATTER,
                    SEAWEED, SHELLS, SIGNPOST, WATER_VARIATIONS)
from .raster import Field, dilate, label_regions
from .terrain import BOTTOM, LEFT, MAP_W, MAP_H, SEA_Z, ground_z_at, world_xy

NEUTRAL_PASSIVE = 15                          # classic (12 player) numbering used by war3mapUnits.doo
# tree species: (model variations, smallest scale, largest scale) from the game's destructable data;
# a tree's size is drawn round the middle of its species' range (see TREE_SIZE)
TREES = {'LTlt': (10, 0.8, 1.2), 'FTtw': (10, 0.8, 1.2), 'WTtw': (10, 0.8, 1.2), 'WTst': (10, 0.8, 1.2), 'JTtw': (10, 0.8, 1.2),
         'ATtr': (5, 0.8, 1.2), 'CTtr': (5, 0.8, 1.2), 'ITtw': (10, 0.8, 1.0), 'BTtw': (10, 0.8, 1.2), 'NTtw': (10, 0.8, 1.2),
         'ZTtw': (10, 0.65, 1.05), 'ATtc': (3, 0.8, 1.2), 'BTtc': (3, 0.8, 1.2), 'CTtc': (3, 0.8, 1.2), 'ITtc': (3, 0.8, 1.2),
         'NTtc': (3, 0.8, 1.2), 'ZTtc': (3, 0.8, 1.2), 'YTct': (2, 0.8, 1.2), 'YTft': (2, 0.8, 1.2), 'YTst': (2, 0.8, 1.2),
         'KTtw': (10, 0.65, 0.85), 'DTsh': (8, 0.8, 1.2), 'GTsh': (8, 0.8, 1.2)}
# Tree sizes, as a share of the species' middle size: groves of old trees and of young growth
# come and go across a wood, trees grow taller deep inside it than at its fraying edge, and
# each tree differs from its neighbours. (smallest, largest)
TREE_SIZE = (0.6, 1.6)
DETAIL_VARIATIONS = {'LRrk': 10, 'ARrk': 10, 'CRrk': 10, 'BRrk': 10, 'BRsp': 8, 'ZRrk': 10, 'ZRsp': 8, 'NRrk': 10, 'IRrs': 10,
                     'ORrk': 10, 'DRrk': 10, 'BRrs': 8, 'CRrs': 8, 'ORrs': 10, 'ZRrs': 8, 'IRgc': 10, 'ZPfw': 5, 'ZPsh': 3, 'APms': 4,
                     'CPms': 4, 'APct': 1, 'LPrs': 4, 'LPfp': 3, 'LPwh': 1, 'LPcw': 2, 'ZPru': 2}
# per biome: (rock, rock spire or None) scattered over steep slopes
ROCKS = {'nightelf': ('ARrk', None), 'worldtree': ('ARrk', None), 'crystal': ('ARrk', None), 'fel': ('CRrk', None),
         'savanna': ('BRrk', None), 'reddesert': ('BRrk', 'BRsp'), 'needles': ('BRrk', 'BRsp'), 'barren': ('BRrk', None),
         'desert': ('BRrk', 'BRsp'), 'amber': ('BRrk', 'BRsp'), 'jungle': ('ZRrk', 'ZRsp'), 'swamp': ('ZRrk', None),
         'snow': ('NRrk', None), 'tundra': ('NRrk', None), 'icecrown': ('IRrs', None), 'frozen': ('IRrs', None),
         'volcanic': ('ORrk', None), 'lava': ('ORrk', None), 'halls': ('DRrk', None), 'crypt': ('DRrk', None)}
# per biome: the great spire raised on the heights of a massif
SPIRES = {'snow': 'IRgc', 'tundra': 'IRgc', 'icecrown': 'IRgc', 'crystal': 'IRgc', 'savanna': 'BRrs', 'reddesert': 'BRrs',
          'needles': 'BRrs', 'barren': 'BRrs', 'desert': 'BRrs', 'amber': 'BRrs', 'volcanic': 'ORrs', 'fel': 'CRrs'}
# per biome: small plants without pathing, dotted over open ground: wild flowers, shrubs,
# mushrooms and tufts of wild grass (wheat), and withered stalks (scorched wheat) on blighted land
PLANTS = {'temperate': ['ZPfw', 'ZPsh', 'LPwh', 'APms'], 'farmland': ['ZPfw', 'ZPsh', 'LPwh'],
          'plains': ['ZPfw', 'ZPsh', 'LPwh'], 'autumn': ['ZPsh', 'ZPfw', 'APms', 'LPwh'],
          'highland': ['ZPsh', 'ZPfw', 'LPwh'], 'darkforest': ['ZPsh', 'APms', 'CPms'], 'nightelf': ['APms', 'ZPfw', 'ZPsh'],
          'worldtree': ['APms', 'ZPfw', 'ZPsh'], 'jungle': ['ZPsh', 'ZPfw', 'APms'], 'swamp': ['ZPsh', 'APms', 'CPms'],
          'grotto': ['APms', 'ZPsh', 'CPms'], 'troll': ['ZPsh', 'ZPfw'], 'fel': ['CPms', 'ZPsh', 'LPcw'],
          'plague': ['CPms', 'LPcw'], 'grizzly': ['ZPsh', 'ZPfw', 'APms', 'LPwh'], 'fjord': ['ZPsh', 'ZPfw', 'LPwh'],
          'savanna': ['ZPsh', 'LPwh'], 'barren': ['ZPsh'], 'tundra': ['ZPsh'],
          'reddesert': ['ZPsh'], 'needles': ['ZPsh'], 'crystal': ['APms', 'ZPfw']}
# per biome: the fallen log lying at the edges of its woods
LOGS = {'temperate': 'AOlg', 'autumn': 'AOlg', 'highland': 'AOlg', 'grizzly': 'AOlg', 'fjord': 'AOlg', 'nightelf': 'AOlg',
        'worldtree': 'AOlg', 'jungle': 'AOlg', 'darkforest': 'COlg', 'fel': 'COlg', 'plague': 'COlg', 'swamp': 'COlg'}
# per biome: what grows on the floor of the woods, between the trunks
FOREST_FLOOR = {'temperate': ['ZPsh', 'APms'], 'autumn': ['ZPsh', 'APms'], 'highland': ['ZPsh'], 'grizzly': ['ZPsh', 'APms'],
                'fjord': ['ZPsh'], 'darkforest': ['APms', 'CPms', 'ZPsh'], 'nightelf': ['APms', 'ZPsh'],
                'worldtree': ['APms', 'ZPsh'], 'crystal': ['APms'], 'jungle': ['ZPsh', 'APms', 'ZPfw'], 'swamp': ['APms', 'ZPsh'],
                'troll': ['ZPsh'], 'fel': ['CPms', 'ZPsh'], 'plague': ['CPms'], 'farmland': ['ZPsh'], 'plains': ['ZPsh']}
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

    def off_the_road(tx, ty, clear):
        """The nearest point to (tx, ty) on dry land at least `clear` tiles from any road."""
        for rad in np.arange(0, 8.01, 0.5):
            for k in range(max(1, int(rad * 6))):
                a = 2 * math.pi * k / max(1, int(rad * 6))
                x, y = tx + rad * math.cos(a), ty + rad * math.sin(a)
                ix, iy = int(round(x)), int(round(y))
                if 0 < ix < MAP_W and 0 < iy < MAP_H and T.land[iy, ix] and not T.water_flag[iy, ix] \
                        and T.road_d[iy, ix] >= clear:
                    return x, y
        return tx, ty

    # ---- landmark doodads first so nothing is built on top of them; none stands on a road ----
    for did, tx, ty, scale, ang in geo.LANDMARKS:
        tx, ty = off_the_road(tx, ty, 3.0)
        x, y = world_xy(tx, ty)
        O.doodads.append(dict(id=did, var=0, x=x, y=y, z=ground_z_at(T, tx, ty), angle=ang, scale=scale, state=2, life=255))
        mark(reserved, tx, ty, 5); mark(occupied, tx, ty, 4)
    for did, tx, ty, scale in geo.DESTRUCTABLE_LANDMARKS:
        tx, ty = off_the_road(tx, ty, 2.5 + 2.0 * scale)
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
    road_ends = [p for line in T.road_lines for p in (line[0], line[-1])]

    def gate_spot(x, y):
        """A waygate stands at the end of the road leading to it, or beside a road, never across one."""
        return far_from_capitals(x, y, 17) and (T.road_d[int(y), int(x)] >= 2.2 or
                                                 min(math.hypot(x - ex, y - ey) for ex, ey in road_ends) < 3)

    for a, b in geo.PORTALS:
        spots = []
        for name, tx, ty in (a, b):
            spot = find_spot(tx, ty, 2.0, max_search=24, accept=gate_spot)
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
    grove_age = nf.fbm(12, 3)
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
        age = 1.0 + 0.5 * grove_age[ty, tx] + 0.12 * min(score[ty, tx] / 0.15, 1.0)
        size = float(np.clip(age * math.exp(rng.normal(0.0, 0.15)), *TREE_SIZE))
        jx, jy = rng.uniform(-0.2, 0.2, 2)
        x, y = world_xy(tx + 0.5 + jx, ty + 0.5 + jy)
        trees.append(dict(id=tid, var=int(rng.integers(0, variations)), x=x, y=y,
                          z=ground_z_at(T, tx + 0.5 + jx, ty + 0.5 + jy), angle=4.712389,
                          scale=(lo + hi) / 2 * size, state=2, life=100, tx=tx + 0.5, ty=ty + 0.5))
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
        w, h = size if isinstance(size, tuple) else (abs(size), abs(size))
        x0, y0 = int(round(tx * 4 - w / 2)), int(round(ty * 4 - h / 2))
        return y0, y0 + h, x0, x0 + w

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
        if isinstance(size, tuple) or size > 0:
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
        if isinstance(size, tuple) and rng.random() < 0.5:
            size, fixed = size[::-1], 0.0          # laid north-south: its pathing turns with it
        if not fits(tx, ty, size or 1, allow_reserved):
            return False
        d = add_detail(did, tx, ty, scale=scale, fixed=fixed, variations=variations)
        if size:
            bake(d, tx, ty, size)
        return True

    # Every piece goes where it would be found and keeps the company it would keep. The land is
    # read for shade and shelter by the woods, damp ground by the water, rough ground on and
    # below the slopes, and open sunny ground everywhere else.
    is_water = T.lake | T.river
    near_wood = dilate(is_tree, 2) & ~is_tree
    damp = dilate(is_water, 3) | (biome_of == 'swamp')
    rugged = dilate(steep, 2) | (T.relief > 300)
    sunny = ~near_wood & ~is_tree & ~rugged
    wood_edge = dilate(is_tree, 1)
    down_y, down_x = np.gradient(T.ground_z)
    df = Field(n, n, seed + 303)
    meadow = df.fbm(7, 3)                 # where wild plants gather
    beds = df.fbm(4, 2)                   # finer patches: reed beds, lily rafts, seaweed, mushroom beds
    all_plants = sorted({p for ps in list(PLANTS.values()) + list(FOREST_FLOOR.values()) for p in ps})
    plant_stand = {p: df.fbm(5, 2) for p in all_plants}      # each patch mostly of one kind

    snow_ground = T.tex == TILE['Wsnw']

    def small_ok(tx, ty, plant=False):
        """Room for a stone or a plant: dry, open ground off the road (and for a plant, not snow)."""
        ix, iy = int(tx), int(ty)
        return (0 < ix < MAP_W and 0 < iy < MAP_H and tile_ok[iy, ix] and T.road_d[iy, ix] > 1.6
                and not (plant and snow_ground[iy:iy + 2, ix:ix + 2].sum() >= 2))

    def around(did, tx, ty, count, r0, r1, scale, downhill=False, variations=None, fixed=None):
        """`count` pieces of `did` about (tx, ty); downhill ones spill down the slope like scree."""
        ix, iy = min(max(int(tx), 0), n - 1), min(max(int(ty), 0), n - 1)
        steep_here = math.hypot(down_x[iy, ix], down_y[iy, ix]) > 4
        fall = math.atan2(-down_y[iy, ix], -down_x[iy, ix]) if downhill and steep_here else None
        for _ in range(count):
            a = rng.uniform(0, 2 * math.pi) if fall is None else fall + rng.normal(0, 0.6)
            r = rng.uniform(r0, r1)
            px, py = tx + r * math.cos(a), ty + r * math.sin(a)
            if small_ok(px, py, plant=did not in KIND_OF):
                add_detail(did, px, py, scale=scale, variations=variations, fixed=fixed)

    def stones(tx, ty, count, r0=0.45, r1=0.95, downhill=True):
        rock = ROCKS.get(str(biome_of[int(ty), int(tx)]), ('LRrk', None))[0]
        around(rock, tx, ty, count, r0, r1, (0.22, 0.4), downhill, fixed=4.712389 if rock == 'ORrk' else None)

    def plant_for(b, ty, tx, pool=None):
        """The plant that suits this spot: flowers and wild grass in the sun, shrubs by the woods and
        among the rocks, mushrooms in the shade and the damp; each patch mostly of one kind."""
        pool = pool or PLANTS.get(b)
        if not pool:
            return None
        shade, wet = bool(near_wood[ty, tx] or is_tree[ty, tx]), bool(damp[ty, tx])
        home = {'ZPfw': bool(sunny[ty, tx]), 'LPwh': bool(sunny[ty, tx]), 'ZPsh': bool(wood_edge[ty, tx] or rugged[ty, tx]),
                'APms': shade or wet, 'CPms': shade or wet, 'LPcw': True}
        w = np.array([(3.0 if home.get(p, True) else 0.25) * math.exp(2.5 * plant_stand[p][ty, tx]) for p in pool])
        return pool[int(np.searchsorted(np.cumsum(w), rng.random() * w.sum()))]

    def clump(b, tx, ty, count, spread=0.35, pool=None):
        """A clump of one kind of plant round (tx, ty)."""
        p = plant_for(b, int(ty), int(tx), pool)
        if p:
            for _ in range(count):
                px, py = tx + rng.normal(0, spread), ty + rng.normal(0, spread)
                if small_ok(px, py, plant=True):
                    add_detail(p, px, py)

    def mushrooms_for(b):
        return 'CPms' if b in ('fel', 'plague') else 'APms' if b in PLANTS and not B[b]['cold'] else None

    # Rocks lie where they would fall: outcrops on the steep slopes, scree at their foot and rubble
    # below the mountain cliffs, each boulder with smaller stones spilled down the slope from it.
    roll = rng.random((n, n))
    foot = dilate(steep, 1) & ~steep & ground & ~clear & ~is_tree
    rubble = by_cliff & tile_ok & (T.relief > 120) & (T.road_d > 5) & ~T.ramp_near & ~is_tree & ~clear & (roll < 0.05)
    outcrop = steep & ground & ~clear & (roll < 0.045)
    for ty, tx in np.argwhere(outcrop | rubble):
        rock, spire = ROCKS.get(str(biome_of[ty, tx]), ('LRrk', None))
        if spire and outcrop[ty, tx] and rng.random() < 0.3:
            add_detail(spire, tx + 0.5, ty + 0.5, scale=(0.28, 0.42))
            continue
        d = add_detail(rock, tx + 0.5, ty + 0.5, scale=(0.8, 1.4), fixed=4.712389 if rock == 'ORrk' else None)
        if rubble[ty, tx] and not blocked[ty, tx]:
            bake(d, tx + 0.5, ty + 0.5, 4)
        stones(tx + 0.5, ty + 0.5, int(rng.integers(1, 4)))
    for ty, tx in np.argwhere(foot & (roll > 0.95)):
        rock = ROCKS.get(str(biome_of[ty, tx]), ('LRrk', None))[0]
        if rock in DOODADS and decorate(rock, tx + 0.5, ty + 0.5):
            stones(tx + 0.5, ty + 0.5, int(rng.integers(1, 3)))
    # great rock spires and glaciers crown the massifs
    crown = np.zeros((n, n), bool)
    crown[:-1, :-1] = T.massif_core[:-1, :-1]
    for ty, tx in np.argwhere(crown & ground & (rng.random((n, n)) < 0.03)):
        spire = SPIRES.get(str(biome_of[ty, tx]), 'ZRrs')
        add_detail(spire, tx + 0.5, ty + 0.5, scale=(0.8, 1.2), fixed=4.712389 if spire in ('ORrs', 'IRgc') else None)

    def place_near(pool, cx, cy, r0, r1, tries=12, allow_reserved=False):
        """Put one of `pool` down as near (cx, cy) as there is room, between r0 and r1 tiles away."""
        for k in range(tries):
            a, r = rng.uniform(0, 2 * math.pi), r0 + (r1 - r0) * k / max(tries - 1, 1)
            tx, ty = round((cx + r * math.cos(a)) * 2) / 2, round((cy + r * math.sin(a)) * 2) / 2
            if 0 < tx < MAP_W and 0 < ty < MAP_H and decorate(str(rng.choice(pool)), tx, ty, allow_reserved):
                return tx, ty
        return None

    # About half the camp sites are marked by a single ruin near their middle, with fallen
    # stones about it and a plant or two grown up against it.
    for name, cx, cy, _ in geo.CAMPS:
        pool = RUINS.get(str(biome_of[int(cy), int(cx)]))
        if pool and rng.random() < 0.5:
            spot = place_near(pool, cx, cy, 0.0, 4.0)
            if spot:
                stones(spot[0], spot[1], int(rng.integers(1, 4)), 0.8, 1.4, downhill=False)
                clump(str(biome_of[int(cy), int(cx)]), spot[0] + rng.uniform(-0.8, 0.8), spot[1] + rng.uniform(-0.8, 0.8), 2)
    # Clutter by the buildings it belongs to: hay and carts by the barns, hitching posts by the
    # inn, a barrow by a cottage, racks and a brazier by the square; fire pits in the cold towns
    # and totems in the camps. Elven towns are kept clear.
    homes = [p for p in city_parts if p['id'] in HOUSE_KIND and p['box'] is not None]
    for name, cx, cy, _ in geo.TOWNS:
        b = str(biome_of[int(cy), int(cx)])
        if b in ('nightelf', 'worldtree', 'crystal'):
            continue
        group = 'cold' if B[b]['cold'] else 'camp' if b in ('savanna', 'reddesert', 'needles', 'barren', 'desert', 'amber') \
            else None
        here = [p for p in homes if math.hypot((p['x'] - LEFT) / 128 - cx, (p['y'] - BOTTOM) / 128 - cy) < 9]
        for _ in range(int(rng.integers(0, 3))):
            if here and rng.random() < 0.75:
                p = here[int(rng.integers(0, len(here)))]
                y0, y1, x0, x1 = p['box']
                pool = CLUTTER[group or HOUSE_KIND[p['id']]]
                sides = [((x1 / 4 + 0.75), rng.uniform(y0 / 4 + 0.5, y1 / 4 - 0.5)), ((x0 / 4 - 0.75), rng.uniform(y0 / 4 + 0.5, y1 / 4 - 0.5)),
                         (rng.uniform(x0 / 4 + 0.5, x1 / 4 - 0.5), (y1 / 4 + 0.75)), (rng.uniform(x0 / 4 + 0.5, x1 / 4 - 0.5), (y0 / 4 - 0.75))]
                for k in rng.permutation(4):
                    tx, ty = sides[k]
                    if 0 < tx < MAP_W and 0 < ty < MAP_H and decorate(str(rng.choice(pool)), tx, ty, allow_reserved=True):
                        break
            else:
                place_near(CLUTTER[group or 'square'], cx, cy, 1.8, 3.5, allow_reserved=True)

    # Open country: each piece in the kind of place it belongs, with the company it keeps.
    open_country = tile_ok & ~is_tree & ~reserved & ~dilate(occupied, 1) & (T.road_d > 2.5) & ~steep & ~by_cliff
    home_of = {'rock': rugged, 'wood': near_wood, 'bush': near_wood | damp, 'cactus': ~damp & ~rugged,
               'bones': ~near_wood, 'thorns': rugged | near_wood, 'fissure': rugged & ~damp, 'growth': damp | near_wood,
               'crop': sunny}
    roll = rng.random((n, n))
    for ty, tx in np.argwhere(open_country & (roll < 0.022)):
        b = str(biome_of[ty, tx])
        pool = SCATTER.get(b)
        if not pool:
            continue
        ids = [did for did, _ in pool]
        w = np.array([wt * (3.0 if KIND_OF.get(did) not in home_of or home_of[KIND_OF[did]][ty, tx] else 0.35)
                      for did, wt in pool])
        did = ids[int(np.searchsorted(np.cumsum(w), rng.random() * w.sum()))]
        x, y = tx + 0.5, ty + 0.5
        if not decorate(did, x, y):
            continue
        kind = KIND_OF.get(did)
        if kind == 'rock':
            stones(x, y, int(rng.integers(1, 4)))
            if rng.random() < 0.5:
                clump(b, x + rng.uniform(-0.7, 0.7), y + rng.uniform(-0.7, 0.7), int(rng.integers(1, 3)), 0.2)
        elif kind == 'wood':
            shroom = mushrooms_for(b)
            if shroom:
                around(shroom, x, y, int(rng.integers(2, 5)), 0.4, 0.9, (0.6, 1.0))
        elif kind in ('bush', 'thorns', 'cactus'):
            for _ in range(int(rng.integers(1, 3)) if kind != 'cactus' else int(rng.integers(0, 3))):
                place_near([did], x, y, 1.0 if kind != 'cactus' else 1.8, 1.6 if kind != 'cactus' else 2.6, tries=4)
            if kind == 'bush':
                clump(b, x, y, int(rng.integers(1, 3)), 0.6)
        elif kind == 'fissure':
            stones(x, y, int(rng.integers(2, 4)), 1.0, 1.4, downhill=False)
        elif kind == 'growth':
            clump(b, x, y, int(rng.integers(1, 3)), 0.5)
        elif kind == 'crop':
            a = rng.uniform(0, math.pi)
            for k in range(1, int(rng.integers(2, 5))):
                px, py = x + 0.55 * k * math.cos(a), y + 0.55 * k * math.sin(a)
                if small_ok(px, py):
                    add_detail(did, px, py, variations=DOODADS[did][0])
    # fallen logs at the edges of the woods, mushrooms growing on them where it is damp enough
    roll = rng.random((n, n))
    for ty, tx in np.argwhere(open_country & dilate(is_tree, 2) & ~dilate(is_tree, 1) & (roll < 0.08)):
        b = str(biome_of[ty, tx])
        log = LOGS.get(b)
        if log and decorate(log, tx + 0.5, ty + 0.5) and mushrooms_for(b):
            around(mushrooms_for(b), tx + 0.5, ty + 0.5, int(rng.integers(1, 4)), 0.5, 1.2, (0.6, 1.0))
    # signposts where roads fork, turned to face the junction
    forks = []
    for line in T.road_lines:
        for ex, ey in (line[0], line[-1]):
            if all(math.hypot(ex - fx, ey - fy) > 5 for fx, fy in forks):
                forks.append((ex, ey))
    for ex, ey in forks[::2]:
        for ox, oy in ((1.6, 1.6), (-1.6, 1.6), (1.6, -1.6), (-1.6, -1.6)):
            tx, ty = ex + ox, ey + oy
            if 0 < tx < MAP_W and 0 < ty < MAP_H and tile_ok[int(ty), int(tx)] and not occupied[int(ty), int(tx)] \
                    and T.road_d[int(ty), int(tx)] > 1.2:
                add_detail(SIGNPOST, tx, ty, scale=(0.9, 1.1), variations=1, fixed=math.atan2(-oy, -ox) % (2 * math.pi))
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
                around(rock, tx + 0.5, ty + 0.5, int(rng.integers(0, 2)), 0.45, 0.75, (0.22, 0.38), fixed=facing)
                placed = True
                break
            s_at += (rng.uniform(2.2, 3.6) if rough else rng.uniform(3.0, 5.0)) if placed else 1.0
    # shells washed up in drifts along the tide line; birds over the woods and shores, bats in the
    # dark woods and under the cliffs, flies over the swamp water
    coast = T.land & dilate(T.sea, 1)
    roll = rng.random((n, n))
    for ty, tx in np.argwhere(coast & T.beach & tile_ok & (beds > 0.2) & (roll < 0.3)):
        around(SHELLS, tx + 0.5, ty + 0.5, int(rng.integers(1, 4)), 0.0, 0.5, (0.8, 1.2), variations=10)
    edge_of_wood = dilate(is_tree, 1) & ~is_tree
    dark = np.isin(biome_of, ['plague', 'darkforest', 'crypt', 'fel', 'icecrown'])
    for mask, did, p in ((edge_of_wood | coast, BIRDS, 0.003), (dark & T.land & (is_tree | by_cliff), BATS, 0.004),
                         ((biome_of == 'swamp') & T.land & dilate(is_water, 2), FLIES, 0.02)):
        roll = rng.random((n, n))
        for ty, tx in np.argwhere(mask & (roll < p)):
            add_detail(did, tx + 0.5, ty + 0.5, variations=1)

    unblock(T, label, sizes, blockers, detail)

    # Wild plants grow in patches, each patch mostly of one kind: flowers and wild grass in the
    # sunny meadows, shrubs at the edges of the woods and among the rocks, mushrooms in the shade
    # and on damp ground.
    lush = dilate(occupied | blocked, 1) | (T.road_d < 1.6)
    open_ground = tile_ok & ~is_tree & ~lush & ~steep
    roll = rng.random((n, n))
    for ty, tx in np.argwhere(open_ground & (roll < np.clip((meadow - 0.1) * 0.3, 0.0, 0.12))):
        clump(str(biome_of[ty, tx]), tx + 0.5, ty + 0.5, int(rng.integers(2, 4)))
    # Along the roadsides they grow thick, in patches that come and go along the way.
    patches = Field(n, n, seed + 202).fbm(5, 2)
    verge = tile_ok & (road_tile > 1.5) & (road_tile < 4.0) & ~is_tree & ~reserved & ~occupied
    for ty, tx in np.argwhere(verge & (rng.random((n, n)) < np.clip(0.2 + patches * 0.6, 0.0, 0.55))):
        b = str(biome_of[ty, tx])
        wild = ['ZPfw'] if 'ZPfw' in PLANTS.get(b, []) and rng.random() < 0.5 else None     # wild flowers line the roads
        clump(b, tx + 0.5, ty + 0.5, int(rng.integers(1, 3)), 0.3, pool=wild)
    # Under the trees, shrubs and mushrooms gather in the damper hollows between the trunks; here
    # and there in a forest glade a ring of mushrooms.
    for ty, tx in np.argwhere(is_tree & (beds > 0.2) & (rng.random((n, n)) < 0.05)):
        b = str(biome_of[ty, tx])
        if b in FOREST_FLOOR:
            a = rng.uniform(0, 2 * math.pi)
            clump(b, tx + 0.5 + 0.45 * math.cos(a), ty + 0.5 + 0.45 * math.sin(a), int(rng.integers(2, 4)), 0.2,
                  pool=FOREST_FLOOR[b])
    trees_round = sum(np.roll(np.roll(is_tree, dy, 0), dx, 1) for dy in (-1, 0, 1) for dx in (-1, 0, 1))
    glade = ~is_tree & open_ground & (trees_round >= 5) & np.isin(biome_of, ['nightelf', 'worldtree', 'darkforest',
                                                                             'temperate', 'autumn', 'grizzly'])
    for ty, tx in np.argwhere(glade & (rng.random((n, n)) < 0.03)):
        shroom, k0 = mushrooms_for(str(biome_of[ty, tx])), rng.uniform(0, 2 * math.pi)
        for k in range(7 if shroom else 0):
            a = k0 + 2 * math.pi * k / 7
            px, py = tx + 0.5 + 0.8 * math.cos(a), ty + 0.5 + 0.8 * math.sin(a)
            if small_ok(px, py, plant=True):
                add_detail(shroom, px, py, scale=(0.7, 0.9))
    # Rushes and cattails grow in beds along the gentle banks, lily pads float in rafts in the
    # sheltered water near the shore, each in the kinds of its land.
    bank = dilate(is_water, 1) & ~is_water & tile_ok & ~is_tree & ~lush & ~steep
    roll = rng.random((n, n))
    for ty, tx in np.argwhere(bank & (beds > 0.15) & (roll < 0.5)):
        reeds = RUSHES.get(str(biome_of[ty, tx]), ['APct', 'APct', 'LPrs'])
        did = reeds[int((beds[ty, tx] * 37) % len(reeds))]          # one kind to a bed
        around(did, tx + 0.5, ty + 0.5, int(rng.integers(1, 3)), 0.0, 0.5, (0.8, 1.2), variations=WATER_VARIATIONS[did])
    def afloat(px, py):
        """Open water all round the point, so nothing floating sits half on the shore."""
        ix, iy = int(px), int(py)
        return 0 < ix < MAP_W and 0 < iy < MAP_H and bool(T.water_flag[iy:iy + 2, ix:ix + 2].all())

    rafts = T.lake & dilate(T.land, 2) & (beds > 0.25)
    for ty, tx in np.argwhere(rafts & (roll < 0.08)):
        did = LILIES.get(str(biome_of[ty, tx]), 'LPfp')
        for _ in range(int(rng.integers(2, 5))):
            px, py = tx + 0.5 + rng.normal(0, 0.3), ty + 0.5 + rng.normal(0, 0.3)
            if afloat(px, py):
                add_detail(did, px, py, z=SEA_Z, variations=WATER_VARIATIONS[did])
    # seaweed in beds in the shallows off the warmer coasts; ice floes drifting in bands in the
    # cold seas, thickest near the land
    cold_zone = np.array([B[z['biome']]['cold'] for z in geo.ZONES])[T.zone_of]
    in_map = ~dilate(T.edge, 2)
    in_map[MAP_H:, :] = in_map[:, MAP_W:] = False
    shallows = T.sea & dilate(T.land, 3) & ~dilate(T.land, 1) & in_map
    drift = T.sea & dilate(T.land, 8) & ~dilate(T.land, 2) & in_map
    roll = rng.random((n, n))
    for ty, tx in np.argwhere(shallows & ~cold_zone & (beds > 0.2) & (roll < 0.05)):
        for _ in range(int(rng.integers(1, 4))):
            px, py = tx + 0.5 + rng.normal(0, 0.4), ty + 0.5 + rng.normal(0, 0.4)
            if afloat(px, py):
                add_detail(SEAWEED, px, py, scale=(1.5, 2.0), z=SEA_Z, variations=5)
    for ty, tx in np.argwhere(drift & cold_zone & (meadow > 0.15) & (roll > 0.985)):
        px, py = tx + rng.uniform(0, 1), ty + rng.uniform(0, 1)
        if afloat(px, py):
            add_detail(str(rng.choice(ICE_FLOES)), px, py, z=SEA_Z, variations=1)
    # A last look over the small loose pieces (none of them has pathing): a pebble that ended up
    # half inside a boulder, a plant or stone dropped on top of another of its kind, or a water
    # plant over a ford is taken away.
    rock_ids = KINDS['rock'] | {r for r, _ in ROCKS.values()}
    AMBIENT = {BIRDS, BATS, FLIES}
    boulders = collections.defaultdict(list)
    for d in detail:
        if d['id'] in rock_ids and d['scale'] >= 0.42:
            boulders[(int((d['x'] - LEFT) / 128), int((d['y'] - BOTTOM) / 128))].append(d)
    loose, keep = collections.defaultdict(list), []
    for d in detail:
        tx, ty = (d['x'] - LEFT) / 128.0, (d['y'] - BOTTOM) / 128.0
        if d['id'] in rock_ids and d['scale'] < 0.42 and any(
                math.hypot(tx - (b['x'] - LEFT) / 128.0, ty - (b['y'] - BOTTOM) / 128.0) < 0.45
                for gx in (int(tx) - 1, int(tx), int(tx) + 1) for gy in (int(ty) - 1, int(ty), int(ty) + 1)
                for b in boulders.get((gx, gy), [])):
            continue
        if d['id'] in WATER_VARIATIONS and d['z'] == SEA_Z and T.road_d[min(int(ty), n - 1), min(int(tx), n - 1)] < 1.5:
            continue
        if d['id'] not in AMBIENT and (d['id'] in rock_ids and d['scale'] < 0.42 or not DOODADS.get(d['id'], (0, 0))[1]):
            cell = (int(tx), int(ty))
            if any(o['id'] == d['id'] and math.hypot(tx - ox, ty - oy) < (0.2 if d['id'] in rock_ids else 0.12)
                   for gx in (cell[0] - 1, cell[0], cell[0] + 1) for gy in (cell[1] - 1, cell[1], cell[1] + 1)
                   for o, ox, oy in loose.get((gx, gy), [])):
                continue
            loose[cell].append((d, tx, ty))
        keep.append(d)
    detail = keep
    O.details = detail
    O.doodads = O.doodads + detail

    # wildlife caught on ground a decoration has since taken moves to the nearest open ground
    for u in [u for u in O.units if u['kind'] == 'critter']:
        if not T.pathing[int(u['ty'] * 4), int(u['tx'] * 4)] & 0x02:
            continue
        free = [(u['tx'] + r * math.cos(a), u['ty'] + r * math.sin(a)) for r in (0.5, 1.0, 1.5, 2.0)
                for a in np.linspace(0, 2 * math.pi, 8, endpoint=False)]
        free = [(x, y) for x, y in free if 0 < x < MAP_W and 0 < y < MAP_H and tile_ok[int(y), int(x)]
                and not T.pathing[int(y * 4), int(x * 4)] & 0x02]
        if free:
            u['tx'], u['ty'] = free[0]
        else:
            O.units.remove(u)

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
