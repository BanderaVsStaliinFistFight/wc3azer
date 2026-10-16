"""Renders overview images of the generated map (for the repo and the minimap)."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from . import geography as geo
from .biomes import GROUND_TILES

TILE_COLOURS = {
    'Ldrt': (128, 100, 68), 'Bdrt': (156, 98, 62), 'Bdsr': (206, 176, 116), 'Ybtl': (112, 108, 112),
    'Dlvc': (118, 48, 28), 'Lrok': (118, 112, 104), 'Ldrg': (108, 112, 68), 'Vcbp': (128, 114, 96), 'Lgrs': (84, 132, 52),
    'Fgrs': (174, 132, 54), 'Vgrt': (48, 100, 72), 'Lgrd': (46, 86, 40),
    'Ldro': (112, 92, 66), 'Wsng': (188, 198, 186), 'Wsnw': (236, 240, 246), 'Wrok': (150, 152, 156),
}
TREE_COLOURS = {'LTlt': (30, 70, 28), 'FTtw': (150, 80, 26), 'ATtr': (40, 60, 90), 'CTtr': (60, 70, 30), 'BTtw': (100, 110, 40),
                'ZTtw': (24, 80, 20), 'WTst': (200, 214, 220), 'NTtw': (50, 80, 60), 'ITtw': (120, 140, 170),
                'WTtw': (52, 76, 58), 'JTtw': (62, 64, 36), 'YTct': (44, 96, 32), 'YTft': (176, 104, 34), 'YTst': (214, 222, 228),
                'ATtc': (50, 84, 104), 'BTtc': (124, 122, 52), 'CTtc': (74, 86, 36), 'ITtc': (140, 160, 192), 'NTtc': (64, 96, 74),
                'ZTtc': (34, 98, 30), 'KTtw': (112, 74, 140), 'DTsh': (146, 96, 112), 'GTsh': (92, 112, 134),
                'VTlt': (40, 82, 34), 'OTtw': (96, 70, 120), 'JTct': (70, 84, 40), 'YTwt': (186, 196, 204)}


def colour_map(T):
    pal = np.array([TILE_COLOURS[t] for t in GROUND_TILES], dtype=np.float64)
    rgb = pal[T.tex]
    # hill shading from the final ground heights
    g = T.ground_z
    gx = np.zeros_like(g); gy = np.zeros_like(g)
    gx[:, 1:-1] = g[:, 2:] - g[:, :-2]
    gy[1:-1, :] = g[2:, :] - g[:-2, :]
    shade = np.clip(1.0 + (-gx + gy) / 600.0, 0.55, 1.4)
    rgb = rgb * shade[..., None]
    depth = -89.6 - g
    wet = T.water_flag & (depth > 0)
    shallow = np.array([70, 140, 170.0]); deep = np.array([16, 44, 92.0])
    t = np.clip(depth / 250.0, 0, 1)[..., None]
    water_rgb = shallow * (1 - t) + deep * t
    rgb = np.where(wet[..., None], water_rgb * 0.85 + rgb * 0.15, rgb)
    cliff = np.zeros(g.shape, bool)
    cliff[:-1, :-1] = T.cliff_tile
    cliff &= ~(wet & (depth > 60))                 # sunken cliffs vanish in deep water
    rgb = np.where(cliff[..., None], rgb * 0.55, rgb)
    rgb = np.where(T.edge[..., None], rgb * 0.25, rgb)
    return np.clip(rgb, 0, 255).astype(np.uint8)


def render(T, path, scale=3, objects=None, labels=True):
    rgb = colour_map(T)
    img = Image.fromarray(rgb[::-1], 'RGB').resize((rgb.shape[1] * scale, rgb.shape[0] * scale), Image.NEAREST)
    draw = ImageDraw.Draw(img)
    H = rgb.shape[0]

    def px(x, y):
        return x * scale, (H - 1 - y) * scale

    if objects:
        for d in objects.get('trees', []):
            x, y = px(d['tx'], d['ty'])
            draw.point((x, y), fill=TREE_COLOURS.get(d['id'], (0, 60, 0)))
    try:
        font = ImageFont.truetype('DejaVuSans.ttf', 4 * scale)
        big = ImageFont.truetype('DejaVuSans-Bold.ttf', 5 * scale)
    except OSError:
        font = big = ImageFont.load_default()
    if labels:
        seen = set()
        for z in geo.ZONES:
            if z['name'] in seen:
                continue
            seen.add(z['name'])
            x, y = px(z['cx'], z['cy'])
            draw.text((x, y), z['name'], fill=(255, 255, 255), font=font, anchor='mm', stroke_width=1, stroke_fill=(0, 0, 0))
        for idx, name, cx, cy, race in geo.CAPITALS:
            x, y = px(cx, cy)
            draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=(255, 40, 40), outline=(255, 255, 255))
            draw.text((x, y + 10), name, fill=(255, 230, 120), font=big, anchor='mt', stroke_width=1, stroke_fill=(0, 0, 0))
    img.save(path)
    return img


def minimap_rgb(T, size=256):
    """Image for war3mapMap.blp: the playable area, north up."""
    from .terrain import MARGIN_L, MARGIN_R, MARGIN_B, MARGIN_T, MAP_W, MAP_H
    rgb = colour_map(T)[MARGIN_B:MAP_H - MARGIN_T + 1, MARGIN_L:MAP_W - MARGIN_R + 1]
    img = Image.fromarray(rgb[::-1], 'RGB').resize((size, size), Image.LANCZOS)
    return np.asarray(img)
