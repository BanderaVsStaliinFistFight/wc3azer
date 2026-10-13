"""Writers for the Warcraft III map files that go inside a .w3x archive.

Layouts follow the classic Frozen Throne formats (war3map.w3i version 25,
doodad/unit files version 8 subversion 11, war3map.w3e version 11), which
every game patch from 1.29 (480x480 maps) up to Reforged still loads.
Coordinates are WC3 world units; arrays are indexed [y, x] with y = 0 at
the bottom (south) edge, which is the order the files store them in.
"""
import struct

import numpy as np


def cstr(text):
    return text.encode('utf-8') + b'\0'


def rawcode(code):
    assert len(code) == 4, code
    return code.encode('latin1')


# --------------------------------------------------------------------------
# Terrain: war3map.w3e
# --------------------------------------------------------------------------
TILEPOINT = np.dtype([('height', '<u2'), ('water', '<u2'), ('tex', 'u1'), ('var', 'u1'), ('cliff', 'u1')])

FLAG_RAMP, FLAG_BLIGHT, FLAG_WATER, FLAG_BOUNDARY = 0x10, 0x20, 0x40, 0x80


def write_w3e(main_tileset, ground_tiles, cliff_tiles, left, bottom, height, water, edge,
              ground, flags, variation, cliff_tex, layer):
    """All per-tilepoint arrays have shape (rows, cols) = (map_h + 1, map_w + 1)."""
    assert len(ground_tiles) <= 16 and len(cliff_tiles) <= 15
    rows, cols = height.shape
    assert ground.max() < len(ground_tiles)
    pts = np.zeros((rows, cols), TILEPOINT)
    pts['height'] = np.clip(height, 0, 0x3FFF)
    pts['water'] = (np.clip(water, 0, 0x3FFF) | np.where(edge, 0x4000, 0)).astype('<u2')
    pts['tex'] = (ground & 0x0F) | (flags & 0xF0)
    pts['var'] = variation
    pts['cliff'] = ((cliff_tex & 0x0F) << 4) | (layer & 0x0F)
    head = b'W3E!' + struct.pack('<i', 11) + main_tileset.encode('latin1') + struct.pack('<i', 1)
    head += struct.pack('<i', len(ground_tiles)) + b''.join(rawcode(t) for t in ground_tiles)
    head += struct.pack('<i', len(cliff_tiles)) + b''.join(rawcode(t) for t in cliff_tiles)
    head += struct.pack('<iiff', cols, rows, left, bottom)
    return head + pts.tobytes()


# --------------------------------------------------------------------------
# Pathing (war3map.wpm) and shadows (war3map.shd)
# --------------------------------------------------------------------------
PATH_NOWALK, PATH_NOFLY, PATH_NOBUILD, PATH_BLIGHT, PATH_NOWATER, PATH_UNK = 0x02, 0x04, 0x08, 0x20, 0x40, 0x80


def write_wpm(cells):
    """cells: uint8 array of shape (map_h * 4, map_w * 4)."""
    h, w = cells.shape
    return b'MP3W' + struct.pack('<iii', 0, w, h) + cells.astype('u1').tobytes()


def write_shd(map_w, map_h):
    return bytes(map_w * 4 * map_h * 4)


# --------------------------------------------------------------------------
# Doodads (war3map.doo) and pre-placed units (war3mapUnits.doo)
# --------------------------------------------------------------------------
def write_doodads(doodads):
    """doodads: list of dicts with id, var, x, y, z, angle, scale, state, life."""
    out = [b'W3do', struct.pack('<iii', 8, 11, len(doodads))]
    for num, d in enumerate(doodads):
        s = d.get('scale', 1.0)
        out.append(rawcode(d['id']) + struct.pack('<i7f', d.get('var', 0), d['x'], d['y'], d['z'], d.get('angle', 4.712389), s, s, s))
        out.append(struct.pack('<BBiii', d.get('state', 2), d.get('life', 100), -1, 0, num))
    out.append(struct.pack('<ii', 0, 0))   # special doodad format version, special doodad count
    return b''.join(out)


def write_units(units):
    """units: list of dicts (id, x, y, z, angle, owner, ...). Player indices use the
    pre-1.31 numbering (12 = neutral hostile, 15 = neutral passive)."""
    out = [b'W3do', struct.pack('<iii', 8, 11, len(units))]
    for num, u in enumerate(units):
        out.append(rawcode(u['id']) + struct.pack('<i7f', u.get('var', 0), u['x'], u['y'], u['z'], u.get('angle', 4.712389), 1.0, 1.0, 1.0))
        out.append(struct.pack('<BiBBii', 2, u['owner'], 0, 0, -1, -1))
        out.append(struct.pack('<i', -1))                      # map item table
        drops = u.get('drops', [])                              # list of item sets, each [(item, chance)]
        out.append(struct.pack('<i', len(drops)))
        for item_set in drops:
            out.append(struct.pack('<i', len(item_set)))
            for item, chance in item_set:
                out.append(rawcode(item) + struct.pack('<i', chance))
        is_start = u['id'] == 'sloc'
        out.append(struct.pack('<ifi', u.get('gold', 0 if is_start else 12500), 0.0 if is_start else u.get('acquire', -1.0),
                               0 if is_start else 1))
        out.append(struct.pack('<iii', 0, 0, 0))              # hero str/agi/int
        out.append(struct.pack('<ii', 0, 0))                    # inventory items, modified abilities
        out.append(struct.pack('<iBBBB', 0, 1, 0, 0, 0))        # random unit flag 0 + level/class bytes
        out.append(struct.pack('<iii', -1, u.get('waygate', -1), num))
    return b''.join(out)


# --------------------------------------------------------------------------
# Map info (war3map.w3i, format 25)
# --------------------------------------------------------------------------
MAP_FLAGS = (0x0002    # modify ally priorities
             | 0x0008  # playable map size was large
             | 0x0010  # masked areas are partially visible
             | 0x0400  # map properties menu opened
             | 0x0800  # water waves on cliff shores
             | 0x1000  # water waves on rolling shores
             | 0x4000  # requires The Frozen Throne
             | 0x8000)  # item classification system


def write_w3i(name, author, description, players_text, camera_bounds, margins, playable_w, playable_h,
              tileset, players, flags=MAP_FLAGS, loading_title='', loading_subtitle='', loading_text=''):
    out = [struct.pack('<iii', 25, 1, 6072), cstr(name), cstr(author), cstr(description), cstr(players_text)]
    out.append(struct.pack('<8f', *camera_bounds))
    out.append(struct.pack('<4i', *margins))
    out.append(struct.pack('<iii', playable_w, playable_h, flags))
    out.append(tileset.encode('latin1'))
    out.append(struct.pack('<i', -1) + cstr(''))                        # loading screen: default
    out.append(cstr(loading_text) + cstr(loading_title) + cstr(loading_subtitle))
    out.append(struct.pack('<i', 0) + cstr(''))                         # game data set, prologue path
    out.append(cstr('') + cstr('') + cstr(''))                          # prologue text, title, subtitle
    out.append(struct.pack('<ifff', 0, 3000.0, 5000.0, 0.5) + bytes([0, 0, 0, 255]))   # no terrain fog
    out.append(struct.pack('<i', 0) + cstr('') + b'\0')                 # weather, sound env, light env
    out.append(bytes([255, 255, 255, 255]))                              # water tint (BGRA)
    out.append(struct.pack('<i', len(players)))
    for p in players:
        out.append(struct.pack('<iiii', p['index'], 1, p['race'], 0) + cstr(p['name']) + struct.pack('<ffii', p['x'], p['y'], 0, 0))
    out.append(struct.pack('<i', 1))                                     # one force with everyone
    out.append(struct.pack('<ii', 0, (1 << len(players)) - 1) + cstr('Force 1'))
    out.append(struct.pack('<iiii', 0, 0, 0, 0))                         # upgrades, tech, unit tables, item tables
    return b''.join(out)


# --------------------------------------------------------------------------
# Minimap preview icons (war3map.mmp) and minimap image (war3mapMap.blp)
# --------------------------------------------------------------------------
ICON_NEUTRAL, ICON_START = 1, 2


def write_mmp(icons):
    """icons: list of (type, px, py, (r, g, b)) with px/py in 0..255 minimap space."""
    out = [struct.pack('<ii', 0, len(icons))]
    for kind, px, py, (r, g, b) in icons:
        out.append(struct.pack('<iii', kind, px, py) + bytes([b, g, r, 255]))
    return b''.join(out)


def write_blp_paletted(rgb):
    """BLP1, palettised, no alpha, single mip level. rgb: uint8 (h, w, 3) image."""
    from PIL import Image
    h, w, _ = rgb.shape
    img = Image.fromarray(rgb, 'RGB').quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    pal = img.getpalette()[:768]
    pal += [0] * (768 - len(pal))
    indices = np.asarray(img, dtype=np.uint8).tobytes()
    header_size = 4 + 4 * 6 + 64 + 64
    offset = header_size + 1024
    offsets = [offset] + [0] * 15
    lengths = [len(indices)] + [0] * 15
    out = [b'BLP1', struct.pack('<6I', 1, 0, w, h, 5, 0), struct.pack('<16I', *offsets), struct.pack('<16I', *lengths)]
    out.append(b''.join(bytes([pal[3 * i + 2], pal[3 * i + 1], pal[3 * i], 255]) for i in range(256)))
    out.append(indices)
    return b''.join(out)


# --------------------------------------------------------------------------
# Editor-side files: regions, cameras, triggers, custom text
# --------------------------------------------------------------------------
def write_w3r(regions):
    """regions: list of dicts with left, bottom, right, top, name, index, color (r, g, b)."""
    out = [struct.pack('<ii', 5, len(regions))]
    for r in regions:
        out.append(struct.pack('<4f', r['left'], r['bottom'], r['right'], r['top']) + cstr(r['name']))
        red, green, blue = r.get('color', (255, 128, 128))
        out.append(struct.pack('<i', r['index']) + bytes(4) + cstr('') + bytes([blue, green, red, 255]))
    return b''.join(out)


def write_w3c():
    return struct.pack('<ii', 0, 0)


def write_wtg():
    """Trigger data (TFT format 7): the 'Initialization' category and no triggers."""
    out = [b'WTG!', struct.pack('<ii', 7, 1), struct.pack('<i', 0), cstr('Initialization'), struct.pack('<i', 0)]
    out.append(struct.pack('<ii', 2, 0))                        # unknown (always 2), variable count
    out.append(struct.pack('<i', 0))                            # trigger count
    return b''.join(out)


def write_wct():
    comment = ('Enter map-specific custom script code below.  This text will be included in the map script '
               'after variables are declared and before any trigger code.')
    return struct.pack('<i', 1) + cstr(comment) + struct.pack('<ii', 0, 0)     # no custom code, no triggers
