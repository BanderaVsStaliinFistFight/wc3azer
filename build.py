#!/usr/bin/env python3
"""Builds dist/(12)Azeroth.w3x - a 480x480 Warcraft III map of Azeroth.

Usage: python3 build.py [--seed N] [--out PATH] [--preview PATH]
Requires Python 3.9+, numpy and Pillow.
"""
import argparse
import os
import time

from azeroth import formats, jass, mpq, objects, preview, terrain
from azeroth import geography as geo
from azeroth.biomes import CLIFF_TILES, GROUND_TILES
from azeroth.terrain import LEFT, BOTTOM, MAP_W, MAP_H, MARGIN_L, MARGIN_R, MARGIN_B, MARGIN_T

MAP_NAME = 'Azeroth'
AUTHOR = 'Azeroth map generator (wc3azer)'
DESCRIPTION = ('The world of Azeroth on the largest map Warcraft III allows (480x480): Kalimdor, the Eastern Kingdoms, '
               'a vast Northrend, Kul Tiras, Kezan and the Maelstrom, with cliff coasts, terraced highlands and 24 '
               'dungeon and raid instances. Twelve capitals, mage portals between the continents, goblin shipyards '
               'and zeppelins.')
PLAYER_COLOURS = [(255, 3, 3), (0, 66, 255), (28, 230, 185), (84, 0, 129), (255, 252, 0), (254, 138, 14),
                  (32, 192, 0), (229, 91, 176), (149, 150, 151), (126, 191, 241), (16, 98, 70), (78, 42, 4)]
RACE_ID = {'human': 1, 'orc': 2, 'undead': 3, 'nightelf': 4, 'random': 0}


def minimap_pos(x, y):
    left, bottom, right, top = jass.playable_bounds()
    px = int((x - left) / (right - left) * 256)
    py = int((top - y) / (top - bottom) * 256)
    return min(max(px, 0), 255), min(max(py, 0), 255)


def build(seed, out_path, preview_path):
    t0 = time.time()
    T = terrain.build(seed)
    O = objects.place(T, seed + 6)
    print('terrain + objects: %.1fs' % (time.time() - t0))

    left, bottom, right, top = jass.playable_bounds()
    cam = [left + 512, bottom + 256, right - 512, top - 256, left + 512, top - 256, right - 512, bottom + 256]
    prio = jass.ally_priorities(O.starts)
    players = []
    for idx, name, sx, sy, race in sorted(O.starts):
        players.append(dict(index=idx, race=RACE_ID[race], name=name, x=LEFT + sx * 128.0, y=BOTTOM + sy * 128.0))
    w3i = formats.write_w3i(MAP_NAME, AUTHOR, DESCRIPTION, '1 - 12', cam, (MARGIN_L, MARGIN_R, MARGIN_B, MARGIN_T),
                            MAP_W - MARGIN_L - MARGIN_R, MAP_H - MARGIN_B - MARGIN_T, 'L', players,
                            loading_title='Azeroth', loading_subtitle='The World of Warcraft', loading_text=DESCRIPTION)
    # w3i ally priority masks mirror InitAllyPriorities in the script
    w3i = patch_ally_masks(w3i, players, prio)

    w3e = formats.write_w3e('L', GROUND_TILES, CLIFF_TILES, LEFT, BOTTOM, T.height_raw, terrain.WATER_RAW,
                            T.edge, T.tex, T.flags, T.variation, T.cliff_tex, T.layer)
    wpm = formats.write_wpm(T.pathing)
    shd = formats.write_shd(MAP_W, MAP_H)
    doo = formats.write_doodads(O.doodads)
    units_doo = formats.write_units(O.units)
    icons = []
    for u in O.units:
        if u['kind'] == 'start':
            icons.append((formats.ICON_START,) + minimap_pos(u['x'], u['y']) + (PLAYER_COLOURS[u['owner']],))
        elif u['kind'] == 'mine':
            icons.append((formats.ICON_GOLDMINE,) + minimap_pos(u['x'], u['y']) + ((255, 255, 255),))
        elif u['kind'] in ('shop', 'waygate'):
            icons.append((formats.ICON_NEUTRAL,) + minimap_pos(u['x'], u['y']) + ((255, 255, 255),))
    mmp = formats.write_mmp(icons)
    blp = formats.write_blp_paletted(preview.minimap_rgb(T))
    info = dict(name=MAP_NAME, author=AUTHOR, description=DESCRIPTION, ally_priorities=prio)
    script = jass.generate(info, O)

    files = [
        ('war3map.w3i', w3i), ('war3map.w3e', w3e), ('war3map.wpm', wpm), ('war3map.shd', shd),
        ('war3map.doo', doo), ('war3mapUnits.doo', units_doo), ('war3map.j', script), ('war3map.mmp', mmp),
        ('war3mapMap.blp', blp), ('war3map.w3r', formats.write_w3r(O.regions)), ('war3map.w3c', formats.write_w3c()),
        ('war3map.wtg', formats.write_wtg()), ('war3map.wct', formats.write_wct()),
    ]
    flags = formats.MAP_FLAGS
    data = mpq.build_map(MAP_NAME, flags, len(players), files)
    os.makedirs(os.path.dirname(out_path) or '.', exist_ok=True)
    with open(out_path, 'wb') as fh:
        fh.write(data)
    if preview_path:
        links = O.portals[:len(O.portals) - len(geo.INSTANCES)]   # instance waygates are left unlinked
        preview.render(T, preview_path, scale=2, objects=dict(trees=O.trees, mines=O.mines, creeps=O.creeps,
                                                              shops=O.shops, portals=links))
    print('wrote %s (%.1f MB) in %.1fs' % (out_path, len(data) / 1e6, time.time() - t0))
    print('  trees: %d, other doodads: %d, units: %d (creeps %d, gold mines %d, shops %d, waygates %d, critters %d)' % (
        len(O.trees), len(O.doodads) - len(O.trees), len(O.units),
        sum(u['kind'] == 'creep' for u in O.units), sum(u['kind'] == 'mine' for u in O.units),
        sum(u['kind'] == 'shop' for u in O.units), sum(u['kind'] == 'waygate' for u in O.units),
        sum(u['kind'] == 'critter' for u in O.units)))
    return T, O, dict(files)


def patch_ally_masks(w3i, players, prio):
    """Rewrite each player's ally-low-priority mask to match the script's start location priorities."""
    import struct
    out = bytearray(w3i)
    for p in players:
        marker = struct.pack('<iiii', p['index'], 1, p['race'], 0) + p['name'].encode('utf-8') + b'\0'
        pos = out.index(marker) + len(marker) + 8
        mask = sum(1 << o for o in prio[p['index']])
        out[pos:pos + 4] = struct.pack('<i', mask)
    return bytes(out)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--out', default=os.path.join('dist', '(12)Azeroth.w3x'))
    ap.add_argument('--preview', default=os.path.join('dist', 'preview.png'))
    args = ap.parse_args()
    build(args.seed, args.out, args.preview)
