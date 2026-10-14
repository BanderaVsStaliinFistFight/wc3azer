"""Walls, gateways and buildings for the capitals and towns.

Capitals get a stone curtain wall (a rectangle of 320-unit wall segments with corner posts),
open gateways wherever a road passes through it (and at least one on every side), and houses
lining the streets and filling the ring round the open square in the middle, where the start
location stays clear. The bigger towns (ports, markets, goblin towns) get a smaller stone wall;
the others a wooden fence, and Horde outposts a spiked palisade. Each place is built in the
style of its people or its land.

Every piece is a stock game object. Footprints are in 32-unit pathing cells, (width, height)
at the default facing. Walls and palisades are destructables, which the game gives their pathing;
the solid doodads (buildings, posts, fences) are written into the pathing map by objects.py.
"""
import math

import numpy as np

from . import geography as geo
from .raster import dilate, label_regions
from .terrain import BOTTOM, LEFT, MAP_H, MAP_W, ground_z_at

SEGMENT = 320.0                 # length of one wall segment, world units
FACING_DEFAULT = 4.712389       # 270 degrees, the facing walls and city buildings are drawn at
STONE, RUINS, ICE = ('LTw0', 'LTw2'), ('ZTw0', 'ZTw2'), ('ITw0', 'ITw2')   # (east-west, north-south) segments
CITY_HOUSES = [('YS09', (12, 12), 1), ('YS10', (12, 12), 1), ('YS11', (12, 12), 1), ('YS03', (12, 12), 1),
               ('YS04', (12, 12), 1), ('YS05', (12, 12), 1), ('YS12', (16, 16), 1), ('YS14', (16, 16), 1)]
ELVEN_HOUSES = [('LSeb', (6, 6), 2), ('LSeb', (6, 6), 2), ('ASv0', (8, 8), 1), ('ASv1', (8, 8), 1), ('ASv3', (8, 8), 1),
                ('ASv4', (8, 8), 1), ('ASv2', (4, 4), 1)]
VILLAGE_HOUSES = [('VSvb', (4, 4), 3), ('VSvb', (4, 4), 3), ('VSvb', (4, 4), 3), ('LSin', (12, 12), 1), ('LSba', (12, 12), 1)]
CAMP_PROPS = [('NOfg', (4, 4), 1), ('BOtt', (2, 2), 2), ('OOst', (2, 2), 2), ('LOss', (2, 2), 6), ('NOfp', (4, 4), 1)]

# Capital styles: wall segments or None (or a palisade), a post for corners and gateways,
# buildings [(id, (w, h) cells, variations)], monuments by the square, lights.
CITY_STYLES = {
    'human': dict(wall=STONE, post=('YSco', (4, 4)), houses=CITY_HOUSES + VILLAGE_HOUSES[:2],
                  monuments=[('YOfn', (8, 8), 1), ('YOks', (8, 8), 1), ('YOst', (8, 8), 1)], light=('YOlp', (2, 2)),
                  houses_n=28),
    'elf': dict(wall=STONE, post=('YSco', (4, 4)), houses=ELVEN_HOUSES,
                monuments=[('YOfn', (8, 8), 1), ('YOst', (8, 8), 1)], light=('YOlp', (2, 2)), houses_n=24),
    'orc': dict(wall=RUINS, post=('LOss', (2, 2)), houses=CAMP_PROPS,
                monuments=[('BOtt', (2, 2), 2), ('NOfg', (4, 4), 1)], light=('LOtz', None), houses_n=16),
    'tauren': dict(palisade=True, houses=CAMP_PROPS[:3] + CAMP_PROPS[4:],
                   monuments=[('BOtt', (2, 2), 2)], light=('LOtz', None), houses_n=12),
    'undead': dict(wall=STONE, post=('LObr', (2, 2)), ruined=0.3,       # Lordaeron's own walls, left broken
                   houses=[('YSr3', (12, 12), 1), ('YSr4', (12, 12), 1), ('YSr5', (12, 12), 1), ('YSr9', (12, 12), 1),
                           ('YSra', (12, 12), 1), ('YSrb', (12, 12), 1), ('YSrc', (16, 16), 1), ('YSre', (16, 16), 1)],
                   monuments=[('YScr', (20, 20), 1)], light=('LObr', (2, 2)), houses_n=18),
    'icecrown': dict(wall=ICE, post=('IOpr', (4, 4)),
                     houses=[('IOob', (4, 4), 3), ('IOpr', (4, 4), 3)],          # one crypt only, by the square
                     monuments=[('NSct', (8, 8), 1)], light=('IOst', (2, 2)), houses_n=12),
    'nightelf': dict(houses=ELVEN_HOUSES, monuments=[('AOgs', (8, 8), 1), ('AOks', (8, 8), 1)], light=None, houses_n=20),
}
CAPITAL_STYLE = {'Stormwind': 'human', 'Orgrimmar': 'orc', 'Undercity': 'undead', 'Darnassus': 'nightelf',
                 'Ironforge': 'human', 'Thunder Bluff': 'tauren', 'Icecrown Citadel': 'icecrown',
                 'Silvermoon City': 'elf', 'Dalaran': 'human', 'Warsong Hold': 'orc', 'Boralus': 'human',
                 'Valgarde': 'human'}
CAPITAL_WALL_SIDE = 11          # wall segments along each side of a capital (27.5 tiles)
TOWN_WALL_SIDE = 5              # ... and of a walled town (12.5 tiles)
WALLED_TOWNS = ('nshp', 'ngad', 'nmrk', 'ngme')     # ports, goblin towns and markets
# Horde outposts are camps behind spiked palisades, wherever they stand, never stone-walled
HORDE_TOWNS = {'Crossroads', 'Kargath', "Grom'gol", 'Hammerfall', 'Razor Hill', 'Camp Taurajo', 'Camp Mojache',
               'Freewind Post', 'Sun Rock Retreat', 'Splintertree Post', "Agmar's Hammer", "Zim'Torga"}

# Town styles by biome: a stone wall for the bigger towns, else a fence, houses, a centrepiece
# and lights. Horde outposts take the camp style and a palisade.
TOWN_STYLES = {
    'village': dict(wall=STONE, post=('YSco', (4, 4)), fence=('VOfl', (8, 2)), houses=VILLAGE_HOUSES,
                    centre=('LSwl', (4, 4), 1), light=('YOlp', (2, 2))),
    'farm': dict(wall=STONE, post=('YSco', (4, 4)), fence=('VOfl', (8, 2)),
                 houses=VILLAGE_HOUSES + [('LSgr', (8, 6), 1), ('LSwm', (6, 8), 1)], centre=('LSwl', (4, 4), 1),
                 light=('YOlp', (2, 2))),
    'cold': dict(wall=STONE, post=('YSco', (4, 4)), fence=('NOfl', (8, 2)), houses=VILLAGE_HOUSES[:4],
                 centre=('NOfp', (4, 4), 1), light=('LOtz', None)),
    'dry': dict(wall=STONE, post=('LOss', (2, 2)), houses=CAMP_PROPS + VILLAGE_HOUSES[:1],
                centre=('NOfg', (4, 4), 1), light=('LOtz', None)),
    'elven': dict(houses=ELVEN_HOUSES, centre=('YOfn', (8, 8), 1), light=None),
}
TOWN_STYLE_OF_BIOME = {'farmland': 'farm', 'plains': 'farm', 'snow': 'cold', 'tundra': 'cold', 'icecrown': 'cold',
                       'fjord': 'cold', 'grizzly': 'cold', 'savanna': 'dry', 'desert': 'dry', 'reddesert': 'dry',
                       'needles': 'dry', 'barren': 'dry', 'amber': 'dry', 'volcanic': 'dry', 'nightelf': 'elven',
                       'worldtree': 'elven', 'crystal': 'elven'}


def cell_box(x, y, w, h):
    """Pathing-cell box (y0, y1, x0, x1) of a w x h footprint centred on world point (x, y)."""
    cx, cy = (x - LEFT) / 32.0, (y - BOTTOM) / 32.0
    x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
    return y0, y0 + h, x0, x0 + w


def plan(T, rng, tile_ok, occupied, starts):
    """Lay out every capital and town. Returns (walls, parts): walls are destructables, parts are
    doodads; each carries 'box', the pathing cells it blocks (None for those without pathing)."""
    n = MAP_W + 1
    walls, parts = [], []
    taken = occupied.copy()                    # tiles already spoken for (units, gates, other pieces)

    def tiles(box, margin=0):
        y0, y1, x0, x1 = box
        return (slice(max(y0 // 4 - margin, 0), (y1 - 1) // 4 + 1 + margin),
                slice(max(x0 // 4 - margin, 0), (x1 - 1) // 4 + 1 + margin))

    def flat_free(box, overlap=False):
        y0, y1, x0, x1 = box
        if x0 < 0 or y0 < 0 or x1 > MAP_W * 4 or y1 > MAP_H * 4:
            return False
        ty, tx = tiles(box)
        if not tile_ok[ty, tx].all() or (not overlap and taken[ty, tx].any()):
            return False
        z = T.ground_z[ty.start:ty.stop + 1, tx.start:tx.stop + 1]
        return z.max() - z.min() < 90

    def claim(box, margin=0):
        taken[tiles(box, margin)] = True

    def piece(did, x, y, angle, scale=1.0, var=0, box=None, life=255, kind='part'):
        tx, ty = (x - LEFT) / 128.0, (y - BOTTOM) / 128.0
        return dict(id=did, var=var, x=x, y=y, z=ground_z_at(T, tx, ty), angle=angle, scale=scale, state=2, life=life,
                    box=box, kind=kind)

    def road_at(x, y):
        tx, ty = int((x - LEFT) / 128.0), int((y - BOTTOM) / 128.0)
        return T.road_d[min(max(ty, 0), n - 1), min(max(tx, 0), n - 1)]

    def place_thing(spec, x, y, margin=1, road_clear=1.4):
        """Put one building or prop down if its ground is free and flat; returns it or None."""
        did, size, variations = spec
        w, h = size
        fixed = did[:2] in ('YS', 'LS') or did in ('NSct',)
        facing = FACING_DEFAULT if fixed else float(rng.uniform(0, 2 * math.pi))
        box = cell_box(x, y, w, h)
        if road_at(x, y) < road_clear + max(w, h) / 8.0 or not flat_free(box):
            return None
        p = piece(did, x, y, facing, var=int(rng.integers(0, variations)), box=box)
        claim(box, margin)
        parts.append(p)
        return p

    def light(spec, x, y):
        if not spec:
            return
        did, size = spec
        if size is None:                       # lights without pathing (torches) stand anywhere dry
            tx, ty = int((x - LEFT) / 128.0), int((y - BOTTOM) / 128.0)
            if 0 <= tx < MAP_W and 0 <= ty < MAP_H and tile_ok[ty, tx]:
                parts.append(piece(did, x, y, float(rng.uniform(0, 2 * math.pi))))
            return
        place_thing((did, size, 1), x, y, margin=0, road_clear=1.0)

    def wall_ring(mx, my, side, segments, post, lamp, ruined=0.0):
        """A rectangle of wall segments round tile point (mx, my), laid the way the World Editor lays
        them: east-west segments on the 64-unit grid, north-south ones 32 off it, meeting at the corners."""
        span = side * SEGMENT
        xl = round((LEFT + mx * 128.0 - span / 2) / 64.0) * 64.0
        yb = round((BOTTOM + my * 128.0 - (span + 64) / 2 - 32) / 64.0) * 64.0 + 32
        xr, yt = xl + span, yb + span + 64
        ew, ns = segments
        runs = [(ew, [(xl + 160 + SEGMENT * i, yb) for i in range(side)], True),
                (ew, [(xl + 160 + SEGMENT * i, yt) for i in range(side)], True),
                (ns, [(xl - 32, yb + 192 + SEGMENT * j) for j in range(side)], False),
                (ns, [(xr + 32, yb + 192 + SEGMENT * j) for j in range(side)], False)]
        posts = [(xl - 32, yb), (xr + 32, yb), (xl - 32, yt), (xr + 32, yt)]
        for did, centres, along_x in runs:
            boxes = [cell_box(x, y, 10, 3) if along_x else cell_box(x, y, 3, 10) for x, y in centres]
            # a gateway wherever a road runs through the wall's line, and at least one on every side
            gateway = [min(road_at(*((x + o, y) if along_x else (x, y + o))) for o in (-150, -80, 0, 80, 150)) < 2.6
                       for x, y in centres]
            if not any(gateway):
                gateway[len(centres) // 2] = True
            built = [not g and rng.random() >= ruined and flat_free(b) for g, b in zip(gateway, boxes)]
            for (x, y), box, ok in zip(centres, boxes, built):
                if ok:
                    walls.append(piece(did, x, y, FACING_DEFAULT, var=int(rng.integers(0, 5)), box=box, life=100,
                                       kind='wall'))
                    claim(box)
            for k, (x, y) in enumerate(centres):          # posts either side of each gateway
                for s in (-1, 1):
                    if built[k] and 0 <= k + s < len(centres) and gateway[k + s]:
                        posts.append((x + s * 176, y) if along_x else (x, y + s * 176))
        for x, y in posts:
            if post:
                box = cell_box(x, y, *post[1])
                if flat_free(box, overlap=True):
                    parts.append(piece(post[0], x, y, FACING_DEFAULT, box=box))
                    claim(box)
            light(lamp, x + 96, y + 96)

    def perimeter(mx, my, half, step):
        """Points every `step` units round a square of half-width `half` tiles, with along-x flags."""
        x0, y0, size = LEFT + (mx - half) * 128.0, BOTTOM + (my - half) * 128.0, 2 * half * 128.0
        for i in range(int(size // step)):
            t = step / 2 + step * i
            yield x0 + t, y0, True
            yield x0 + t, y0 + size, True
            yield x0, y0 + t, False
            yield x0 + size, y0 + t, False

    def palisade(mx, my, half):
        """A ring of spiked wooden barricades, broken by the roads and here and there by gaps."""
        for x, y, along_x in perimeter(mx, my, half, 128.0):
            if road_at(x, y) < 2.6 or rng.random() < 0.12:
                continue
            box = cell_box(x, y, 4, 4)
            if flat_free(box):
                walls.append(piece('LTba', x, y, float(rng.uniform(0, 2 * math.pi)), var=int(rng.integers(0, 2)),
                                   box=box, life=100, kind='wall'))
                claim(box)

    def fence(mx, my, half, spec):
        """Wooden fences round a village, broken by the roads and by a gap here and there."""
        did, (fw, fh) = spec
        for x, y, along_x in perimeter(mx, my, half, 256.0):
            if road_at(x, y) < 2.6 or rng.random() < 0.3:
                continue
            box = cell_box(x, y, fw, fh) if along_x else cell_box(x, y, fh, fw)
            if flat_free(box):
                parts.append(piece(did, x, y, FACING_DEFAULT if along_x else 0.0, scale=1.2, box=box))
                claim(box)

    def houses(mx, my, inner, outer, specs, target):
        """Houses line the streets first, then fill the ring between `inner` and `outer` tiles."""
        street = []
        for line in T.road_lines:
            for (ax, ay), (bx, by) in zip(line[:-1], line[1:]):
                seg = math.hypot(bx - ax, by - ay)
                for t in np.arange(0, seg, 2.0):
                    px, py = ax + (bx - ax) * t / max(seg, 1e-6), ay + (by - ay) * t / max(seg, 1e-6)
                    if inner <= math.hypot(px - mx, py - my) <= outer:
                        nx, ny = -(by - ay) / max(seg, 1e-6), (bx - ax) / max(seg, 1e-6)
                        street += [(px + nx * s, py + ny * s) for s in (-2.6, 2.6, -3.4, 3.4)]
        rng.shuffle(street)
        ring = [(mx + r * math.cos(a), my + r * math.sin(a))
                for a, r in zip(rng.uniform(0, 2 * math.pi, target * 15), rng.uniform(inner, outer, target * 15))]
        made = 0
        for px, py in street + ring:
            if made >= target:
                break
            spec = specs[int(rng.integers(0, len(specs)))]
            if place_thing(spec, LEFT + px * 128.0, BOTTOM + py * 128.0):
                made += 1

    # ---- capitals ------------------------------------------------------------------------------
    start_of = {name: (sx, sy) for idx, name, sx, sy, race in starts}
    enclosed = []                              # (x, y, reach): no second wall or fence within reach
    for idx, name, cx, cy, race in geo.CAPITALS:
        style = CITY_STYLES[CAPITAL_STYLE.get(name, 'human')]
        sx, sy = start_of.get(name, (cx, cy))
        # the middle of the city: the capital's square, unless the start location had to move away
        mx, my = (cx, cy) if math.hypot(sx - cx, sy - cy) < 6 else (sx, sy)
        half = CAPITAL_WALL_SIDE * SEGMENT / 256.0
        enclosed.append((mx, my, half + 1.8))
        if style.get('wall'):
            wall_ring(mx, my, CAPITAL_WALL_SIDE, style['wall'], style.get('post'), style['light'], style.get('ruined', 0.0))
        elif style.get('palisade'):
            palisade(mx, my, half)
        for k, spec in enumerate(style['monuments']):
            a = 2 * math.pi * (k + rng.random() * 0.4) / len(style['monuments'])
            for rad in (7.0, 8.0, 9.0):
                if place_thing(spec, LEFT + (mx + rad * math.cos(a)) * 128, BOTTOM + (my + rad * math.sin(a)) * 128):
                    break
        houses(mx, my, 6.5, half - 2.0, style['houses'], style['houses_n'])
        for k in range(10):
            a = 2 * math.pi * k / 10 + rng.uniform(-0.2, 0.2)
            light(style['light'], LEFT + (mx + 6.2 * math.cos(a)) * 128, BOTTOM + (my + 6.2 * math.sin(a)) * 128)

    # ---- towns ---------------------------------------------------------------------------------
    for name, cx, cy, building in geo.TOWNS:
        biome = geo.ZONES[T.zone_of[int(cy), int(cx)]]['biome']
        horde = name in HORDE_TOWNS
        style = TOWN_STYLES['dry' if horde else TOWN_STYLE_OF_BIOME.get(biome, 'village')]
        for dx in (0.0, 1.5, -1.5, 3.0):
            if place_thing(style['centre'], LEFT + (cx + dx) * 128.0, BOTTOM + cy * 128.0, road_clear=1.2):
                break
        # a town beside a capital or another walled town (Brill, the Booty Bay and Gadgetzan
        # markets) shares its neighbour's wall rather than raising one of its own
        alone = all(math.hypot(cx - ex, cy - ey) > reach for ex, ey, reach in enclosed)
        walled = alone and not horde and building in WALLED_TOWNS and style.get('wall')
        if alone:
            enclosed.append((cx, cy, 9.5))
        if walled:
            wall_ring(cx, cy, TOWN_WALL_SIDE, style['wall'], style.get('post'), style['light'])
        elif alone and horde:
            palisade(cx, cy, 7.0)
        elif alone and style.get('fence'):
            fence(cx, cy, 7.5, style['fence'])
        outer = TOWN_WALL_SIDE * SEGMENT / 256.0 - 1.2 if walled else 7.5
        houses(cx, cy, 2.0, outer, style['houses'], int(rng.integers(5, 9)))
        for k in range(4):
            a = 2 * math.pi * (k + 0.5) / 4
            light(style['light'], LEFT + (cx + 2.6 * math.cos(a)) * 128, BOTTOM + (cy + 2.6 * math.sin(a)) * 128)
    return walls, parts


def keep_open(T, walls, parts, rounds=10):
    """Take away wall segments and buildings beside any ground they would cut off from the rest of
    the land (a city or town must be reachable through its gateways), until none is cut off."""
    n4 = T.pathing.shape[0]

    def regions(extra):
        cells = T.pathing.copy()
        for p in extra:
            if p['box'] is not None:
                y0, y1, x0, x1 = p['box']
                cells[max(y0, 0):min(y1, n4), max(x0, 0):min(x1, n4)] = 0xCA
        walk = np.zeros((MAP_H + 1, MAP_W + 1), bool)
        walk[:-1, :-1] = ((cells.reshape(MAP_H, 4, MAP_W, 4) & 0x02) == 0).mean(axis=(1, 3)) >= 0.5
        return label_regions(walk)

    def tiles_of(p):
        y0, y1, x0, x1 = p['box']
        return slice(max(y0 // 4, 0), (y1 - 1) // 4 + 1), slice(max(x0 // 4, 0), (x1 - 1) // 4 + 1)

    base, base_sizes = regions([])
    for _ in range(rounds):
        label, sizes = regions(walls + parts)
        covered = np.zeros(base.shape, bool)
        for p in walls + parts:
            if p['box'] is not None:
                covered[tiles_of(p)] = True
        b = np.maximum(base, 0)
        cut = (base >= 0) & ~covered & (base_sizes[b] >= 150)
        cut &= (label < 0) | (sizes[np.maximum(label, 0)] < 0.9 * base_sizes[b])
        if not cut.any():
            break
        near = dilate(cut, 2)
        keep = lambda p: p['box'] is None or not near[tiles_of(p)].any()
        walls2, parts2 = [w for w in walls if keep(w)], [p for p in parts if keep(p)]
        if len(walls2) + len(parts2) == len(walls) + len(parts):
            break
        walls, parts = walls2, parts2
    return walls, parts
