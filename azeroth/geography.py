"""Hand-authored layout of Azeroth on a 480 x 480 tile grid.

Coordinates are in tiles with (0, 0) at the south-west corner of the map and
y growing northwards. The playable area is x 6..474, y 4..472.
Kalimdor lies to the west, the Eastern Kingdoms to the east, Northrend to the
north, the Maelstrom in the middle of the Great Sea, Pandaria to the south and
the Broken Isles, Kul Tiras and Zandalar around the Maelstrom.
"""

# ---------------------------------------------------------------------------
# Landmasses: polygons (clockwise or not, doesn't matter) or ellipses.
# ---------------------------------------------------------------------------
KALIMDOR = [
    (52, 394), (60, 400), (74, 398), (86, 396), (98, 401), (110, 406), (124, 409), (138, 407), (150, 404),
    (160, 398), (168, 390), (173, 378), (170, 366), (174, 356), (180, 348), (190, 345), (200, 342), (208, 336),
    (206, 328), (198, 324), (194, 318), (200, 312), (204, 304), (196, 298), (186, 294), (180, 286), (182, 276),
    (180, 264), (184, 254), (182, 240), (178, 228), (174, 216), (168, 208), (162, 202), (156, 198), (154, 190),
    (158, 182), (156, 172), (160, 164), (154, 158), (158, 150), (166, 148), (172, 142), (176, 134), (172, 124),
    (166, 116), (168, 106), (172, 96), (176, 84), (174, 72), (168, 60), (162, 50), (154, 42), (144, 36),
    (132, 30), (120, 24), (108, 20), (96, 16), (84, 14), (72, 15), (60, 19), (48, 24), (38, 30), (30, 40),
    (26, 52), (23, 66), (24, 80), (20, 92), (22, 104), (16, 116), (19, 128), (14, 140), (18, 150), (13, 162),
    (16, 174), (11, 186), (15, 198), (18, 208), (22, 220), (18, 232), (24, 244), (26, 256), (32, 266), (28, 278),
    (34, 286), (30, 294), (36, 302), (38, 314), (41, 328), (38, 342), (42, 356), (44, 370), (47, 384),
]

EASTERN_KINGDOMS = [
    (418, 440), (432, 444), (448, 442), (460, 436), (468, 424), (470, 408), (466, 394), (470, 382), (472, 366),
    (468, 350), (464, 338), (466, 322), (470, 306), (472, 290), (470, 272), (466, 256), (458, 246), (452, 236),
    (448, 222), (452, 208), (458, 196), (462, 180), (466, 164), (468, 148), (466, 134), (468, 118), (466, 104),
    (462, 90), (454, 80), (444, 76), (432, 78), (420, 74), (408, 66), (398, 56), (390, 44), (382, 32), (374, 22),
    (366, 15), (354, 18), (346, 26), (342, 40), (338, 56), (336, 72), (334, 88), (332, 104), (330, 118),
    (326, 130), (324, 144), (326, 158), (330, 170), (338, 176), (342, 186), (344, 200), (346, 214), (344, 228),
    (346, 242), (350, 254), (360, 262), (368, 268), (372, 276), (366, 284), (378, 288), (390, 291), (382, 296),
    (370, 300), (362, 302), (354, 308), (346, 309), (340, 302), (332, 294), (324, 290), (319, 298), (318, 310),
    (322, 322), (330, 328), (336, 336), (334, 350), (338, 364), (336, 376), (340, 388), (348, 396), (358, 400),
    (370, 398), (382, 396), (394, 400), (404, 406), (410, 420), (414, 432),
]

NORTHREND = [
    (190, 394), (194, 404), (188, 414), (192, 424), (187, 436), (191, 448), (198, 458), (208, 464), (224, 469),
    (244, 470), (264, 470), (282, 469), (298, 466), (308, 460), (315, 450), (316, 438), (319, 426), (316, 414),
    (319, 402), (316, 392), (310, 384), (304, 380), (298, 385), (294, 392), (290, 385), (282, 384), (276, 388),
    (268, 384), (260, 380), (250, 381), (242, 386), (236, 392), (230, 388), (226, 380), (218, 378), (208, 380),
    (200, 384),
]

PANDARIA = [
    (200, 64), (198, 80), (204, 94), (214, 104), (228, 112), (244, 116), (260, 116), (274, 112), (286, 104),
    (296, 96), (304, 84), (308, 70), (306, 56), (300, 44), (292, 34), (280, 26), (266, 20), (250, 18),
    (236, 20), (224, 26), (214, 34), (206, 44), (202, 54),
]

BROKEN_ISLES = [
    (258, 318), (253, 330), (256, 342), (260, 352), (268, 358), (278, 362), (290, 360), (298, 352), (304, 342),
    (306, 330), (302, 318), (296, 310), (288, 307), (282, 302), (274, 300), (266, 304), (260, 310),
]

KUL_TIRAS = [
    (276, 200), (278, 214), (286, 224), (298, 228), (310, 226), (318, 216), (318, 202), (312, 192), (304, 186),
    (300, 192), (294, 183), (284, 184), (278, 190),
]

ZANDALAR = [
    (196, 160), (198, 172), (206, 180), (218, 182), (230, 178), (236, 168), (234, 156), (230, 146), (222, 140),
    (212, 138), (204, 142), (198, 150),
]

# name: shape. Polygons are lists of points; ellipses are ('ellipse', cx, cy, rx, ry).
LANDMASSES = {
    'Kalimdor': KALIMDOR,
    'Eastern Kingdoms': EASTERN_KINGDOMS,
    'Northrend': NORTHREND,
    'Pandaria': PANDARIA,
    'Broken Isles': BROKEN_ISLES,
    'Kul Tiras': KUL_TIRAS,
    'Zandalar': ZANDALAR,
    'Teldrassil': ('ellipse', 37, 413, 13, 11),
    'Azuremyst Isle': ('ellipse', 22, 366, 8, 12),
    'Bloodmyst Isle': ('ellipse', 18, 392, 7, 7),
    "Isle of Quel'Danas": ('ellipse', 441, 455, 10, 7),
    'Echo Isles': ('ellipse', 176, 206, 4, 3),
    'Theramore Isle': ('ellipse', 179, 133, 3, 3),
    'Alcaz Island': ('ellipse', 182, 152, 4, 3),
    'Tol Barad': ('ellipse', 338, 274, 5, 4),
    'Broken Shore': ('ellipse', 292, 293, 9, 5),
    'Kezan': ('ellipse', 258, 210, 6, 5),
    'Lost Isles': ('ellipse', 230, 226, 6, 5),
    'Timeless Isle': ('ellipse', 316, 26, 5, 4),
    'Isle of Thunder': ('ellipse', 194, 114, 6, 5),
}

# The Maelstrom: a ring of jagged rocks around a bottomless whirlpool.
MAELSTROM = (252, 246)
MAELSTROM_ROCKS = [(252, 268, 3), (268, 262, 3), (275, 247, 3), (268, 231, 3), (252, 224, 3),
                   (236, 230, 3), (229, 246, 3), (236, 262, 3), (260, 256, 2), (244, 238, 2)]
for i, (x, y, r) in enumerate(MAELSTROM_ROCKS):
    LANDMASSES['Maelstrom Rock %d' % i] = ('ellipse', x, y, r, r)

# ---------------------------------------------------------------------------
# Zones: (name, landmass, cx, cy, rx, ry, biome, extra settings)
# Zone of a land tile = nearest zone centre (ellipse-normalised) on its landmass.
# ---------------------------------------------------------------------------
Z = []


def zone(name, land, cx, cy, rx, ry, biome, **kw):
    Z.append(dict(name=name, land=land, cx=cx, cy=cy, rx=rx, ry=ry, biome=biome, **kw))


# Kalimdor
zone('Teldrassil', 'Teldrassil', 37, 413, 13, 11, 'worldtree', base=90)
zone('Azuremyst Isle', 'Azuremyst Isle', 22, 366, 8, 12, 'nightelf')
zone('Bloodmyst Isle', 'Bloodmyst Isle', 18, 392, 7, 7, 'fel')
zone('Darkshore', 'Kalimdor', 50, 348, 10, 44, 'nightelf', hills=90)
zone('Moonglade', 'Kalimdor', 88, 385, 13, 10, 'nightelf', base=110)
zone('Felwood', 'Kalimdor', 78, 340, 14, 30, 'fel')
zone('Winterspring', 'Kalimdor', 146, 380, 24, 20, 'snow', base=160)
zone('Mount Hyjal', 'Kalimdor', 136, 338, 18, 15, 'worldtree', base=180, hills=150)
zone('Azshara', 'Kalimdor', 182, 318, 16, 22, 'autumn', hills=90)
zone('Ashenvale', 'Kalimdor', 100, 290, 55, 17, 'nightelf')
zone('Stonetalon Mountains', 'Kalimdor', 46, 240, 22, 24, 'rocky', base=120, mountains=260)
zone('Northern Barrens', 'Kalimdor', 120, 232, 26, 24, 'savanna')
zone('Durotar', 'Kalimdor', 164, 238, 13, 32, 'reddesert')
zone('Desolace', 'Kalimdor', 38, 180, 22, 24, 'barren')
zone('Mulgore', 'Kalimdor', 80, 182, 18, 21, 'plains', base=80)
zone('Southern Barrens', 'Kalimdor', 124, 176, 25, 21, 'savanna')
zone('Feralas', 'Kalimdor', 42, 122, 24, 24, 'jungle', hills=120)
zone('Thousand Needles', 'Kalimdor', 98, 128, 24, 15, 'needles', base=10, hills=20)
zone('Dustwallow Marsh', 'Kalimdor', 150, 134, 18, 22, 'swamp', base=18)
zone("Un'Goro Crater", 'Kalimdor', 82, 84, 18, 18, 'jungle', base=0, hills=60)
zone('Tanaris', 'Kalimdor', 134, 72, 28, 30, 'desert')
zone('Silithus', 'Kalimdor', 42, 72, 20, 22, 'desert', hills=50)
zone('Uldum', 'Kalimdor', 82, 36, 42, 17, 'desert', hills=40)
zone('Echo Isles', 'Echo Isles', 176, 206, 4, 3, 'jungle')
zone('Theramore Isle', 'Theramore Isle', 179, 133, 3, 3, 'swamp')
zone('Alcaz Island', 'Alcaz Island', 182, 152, 4, 3, 'swamp')
# Eastern Kingdoms
zone("Isle of Quel'Danas", "Isle of Quel'Danas", 441, 455, 10, 7, 'autumn')
zone('Eversong Woods', 'Eastern Kingdoms', 434, 424, 22, 13, 'autumn')
zone('Ghostlands', 'Eastern Kingdoms', 442, 398, 20, 10, 'fel')
zone('Tirisfal Glades', 'Eastern Kingdoms', 362, 382, 22, 14, 'autumn', density=0.30)
zone('Western Plaguelands', 'Eastern Kingdoms', 398, 372, 15, 17, 'plague')
zone('Eastern Plaguelands', 'Eastern Kingdoms', 442, 368, 26, 17, 'plague')
zone('Silverpine Forest', 'Eastern Kingdoms', 346, 346, 9, 20, 'darkforest')
zone('Gilneas', 'Eastern Kingdoms', 330, 306, 11, 13, 'darkforest', base=70)
zone('Hillsbrad Foothills', 'Eastern Kingdoms', 368, 322, 15, 11, 'temperate')
zone('Alterac Mountains', 'Eastern Kingdoms', 390, 343, 12, 10, 'snow', base=140)
zone('The Hinterlands', 'Eastern Kingdoms', 434, 330, 28, 13, 'highland')
zone('Arathi Highlands', 'Eastern Kingdoms', 410, 302, 24, 13, 'farmland', base=60)
zone('Wetlands', 'Eastern Kingdoms', 394, 270, 18, 14, 'swamp', base=20)
zone('Twilight Highlands', 'Eastern Kingdoms', 452, 272, 17, 22, 'highland')
zone('Dun Morogh', 'Eastern Kingdoms', 368, 236, 18, 16, 'snow', base=150)
zone('Loch Modan', 'Eastern Kingdoms', 420, 240, 14, 13, 'highland', base=90, mountains=60)
zone('Badlands', 'Eastern Kingdoms', 434, 212, 17, 13, 'reddesert')
zone('Searing Gorge', 'Eastern Kingdoms', 392, 210, 14, 9, 'volcanic', base=110)
zone('Burning Steppes', 'Eastern Kingdoms', 404, 191, 22, 8, 'volcanic', base=90)
zone('Redridge Mountains', 'Eastern Kingdoms', 434, 172, 17, 10, 'highland', base=70)
zone('Elwynn Forest', 'Eastern Kingdoms', 378, 170, 22, 10, 'temperate')
zone('Westfall', 'Eastern Kingdoms', 342, 146, 14, 18, 'farmland')
zone('Duskwood', 'Eastern Kingdoms', 382, 141, 22, 11, 'darkforest')
zone('Deadwind Pass', 'Eastern Kingdoms', 418, 140, 9, 9, 'rocky', base=100)
zone('Swamp of Sorrows', 'Eastern Kingdoms', 448, 150, 15, 12, 'swamp')
zone('Blasted Lands', 'Eastern Kingdoms', 446, 104, 18, 22, 'volcanic', base=40)
zone('Northern Stranglethorn', 'Eastern Kingdoms', 366, 98, 26, 20, 'jungle')
zone('Cape of Stranglethorn', 'Eastern Kingdoms', 364, 50, 22, 26, 'jungle')
zone('Tol Barad', 'Tol Barad', 338, 274, 5, 4, 'barren')
# Northrend
zone('Borean Tundra', 'Northrend', 208, 398, 16, 14, 'tundra')
zone('Sholazar Basin', 'Northrend', 204, 436, 14, 16, 'jungle', base=30)
zone('Icecrown', 'Northrend', 236, 452, 24, 14, 'icecrown', base=150)
zone('Wintergrasp', 'Northrend', 232, 422, 10, 10, 'snow', base=110, mountains=60)
zone('Dragonblight', 'Northrend', 252, 398, 22, 13, 'snow', base=60, mountains=40, density=0.06)
zone('Crystalsong Forest', 'Northrend', 262, 425, 8, 8, 'crystal', base=90)
zone('The Storm Peaks', 'Northrend', 282, 452, 26, 14, 'snow', base=220, mountains=320)
zone("Zul'Drak", 'Northrend', 294, 424, 18, 12, 'tundra', base=170, hills=90, density=0.04)
zone('Grizzly Hills', 'Northrend', 288, 398, 14, 10, 'grizzly', base=70)
zone('Howling Fjord', 'Northrend', 308, 396, 11, 14, 'fjord', base=80)
# Pandaria
zone('The Dread Wastes', 'Pandaria', 214, 56, 12, 18, 'amber')
zone('Townlong Steppes', 'Pandaria', 218, 92, 14, 12, 'savanna', base=90)
zone('Kun-Lai Summit', 'Pandaria', 254, 102, 26, 12, 'snow', base=180, mountains=280)
zone('The Jade Forest', 'Pandaria', 290, 72, 14, 26, 'jungle', hills=110)
zone('Vale of Eternal Blossoms', 'Pandaria', 256, 70, 14, 11, 'autumn', base=90, density=0.25)
zone('Valley of the Four Winds', 'Pandaria', 244, 44, 18, 11, 'farmland')
zone('Krasarang Wilds', 'Pandaria', 262, 26, 26, 8, 'jungle')
zone('Timeless Isle', 'Timeless Isle', 316, 26, 5, 4, 'jungle')
zone('Isle of Thunder', 'Isle of Thunder', 194, 114, 6, 5, 'swamp')
# Broken Isles
zone('Azsuna', 'Broken Isles', 264, 312, 10, 10, 'autumn')
zone("Val'sharah", 'Broken Isles', 262, 336, 10, 11, 'nightelf')
zone('Highmountain', 'Broken Isles', 280, 353, 14, 9, 'highland', base=120, mountains=160)
zone('Stormheim', 'Broken Isles', 298, 336, 9, 15, 'tundra', base=80, hills=120)
zone('Suramar', 'Broken Isles', 282, 324, 11, 9, 'nightelf', base=60)
zone('Broken Shore', 'Broken Shore', 292, 293, 9, 5, 'volcanic')
# Kul Tiras, Zandalar, the Maelstrom
zone('Drustvar', 'Kul Tiras', 284, 207, 10, 11, 'autumn', base=110, hills=110)
zone('Stormsong Valley', 'Kul Tiras', 306, 219, 11, 9, 'farmland', base=50)
zone('Tiragarde Sound', 'Kul Tiras', 302, 195, 10, 9, 'temperate')
zone("Vol'dun", 'Zandalar', 204, 162, 9, 12, 'desert')
zone('Nazmir', 'Zandalar', 224, 172, 10, 9, 'swamp')
zone('Zuldazar', 'Zandalar', 220, 150, 12, 11, 'jungle', base=60, hills=110)
zone('Kezan', 'Kezan', 258, 210, 6, 5, 'jungle')
zone('Lost Isles', 'Lost Isles', 230, 226, 6, 5, 'jungle')
zone('The Maelstrom', 'Maelstrom Rock 0', 252, 246, 30, 30, 'rocky')
for i in range(1, len(MAELSTROM_ROCKS)):
    zone('The Maelstrom', 'Maelstrom Rock %d' % i, 252, 246, 30, 30, 'rocky')
ZONES = Z

# ---------------------------------------------------------------------------
# Relief features
# ---------------------------------------------------------------------------
# Ridges: polyline, half-width (tiles), crest height (world units). Steep ones are impassable.
RIDGES = [
    # Kalimdor
    ([(60, 360), (66, 380), (78, 392), (100, 394), (106, 380)], 4, 420),          # Moonglade ring (north)
    ([(108, 372), (112, 360), (116, 340), (112, 320)], 4, 380),                    # Felwood / Hyjal wall
    ([(122, 344), (134, 348), (146, 342)], 6, 520),                                # Hyjal summit
    ([(118, 368), (130, 392), (150, 396), (164, 384)], 5, 460),                    # Winterspring peaks
    ([(30, 258), (40, 250), (50, 236), (56, 222), (64, 210)], 6, 560),             # Stonetalon peaks
    ([(66, 210), (74, 200), (70, 186), (64, 170), (72, 162), (88, 160), (98, 168), (100, 182)], 3, 320),  # Mulgore rim
    ([(98, 196), (96, 206), (84, 208)], 3, 300),
    ([(152, 252), (158, 262), (170, 268)], 3, 260),                                # Orgrimmar ridge
    ([(30, 150), (50, 148), (70, 144)], 4, 300),                                   # Feralas / Desolace hills
    ([(70, 104), (84, 104), (98, 98), (100, 84), (96, 68), (82, 64), (68, 70), (64, 86), (70, 104)], 4, 380),  # Un'Goro rim
    ([(138, 112), (150, 104), (160, 112)], 4, 300),                                # Onyxia's lair hills
    ([(26, 96), (40, 92), (60, 96)], 3, 220),                                      # Silithus / Feralas border
    # Eastern Kingdoms
    ([(376, 336), (384, 346), (394, 352), (404, 346)], 5, 560),                    # Alterac Mountains
    ([(408, 318), (420, 322), (432, 318)], 4, 300),                                # Hinterland hills
    ([(352, 250), (360, 244), (370, 248), (380, 246), (388, 236)], 5, 520),        # Khaz Mountains (Ironforge)
    ([(388, 258), (396, 250), (404, 248)], 4, 360),                                # Dun Algaz
    ([(380, 220), (394, 222), (408, 220)], 4, 420),                                # Searing Gorge rim
    ([(388, 202), (396, 200)], 6, 520),                                            # Blackrock Mountain
    ([(372, 182), (390, 182), (414, 183), (428, 182)], 3, 360),                    # Redridge / Burning Steppes wall
    ([(446, 180), (452, 168), (446, 160)], 3, 300),                                # Redridge east
    ([(408, 150), (416, 140), (424, 132)], 4, 420),                                # Deadwind peaks
    ([(426, 122), (430, 110), (432, 96), (428, 84)], 4, 400),                      # Blasted Lands wall
    ([(382, 120), (396, 116), (410, 120)], 3, 260),                                # Duskwood / STV ridge
    ([(368, 70), (376, 80), (388, 84)], 3, 220),                                   # STV hills
    ([(430, 256), (440, 248), (448, 236)], 3, 280),                                # Grim Batol hills
    # Northrend
    ([(220, 470), (232, 460), (246, 462), (258, 468)], 6, 520),                    # Icecrown glacier
    ([(262, 446), (276, 458), (296, 462), (310, 452)], 7, 640),                    # Storm Peaks
    ([(192, 424), (204, 422), (214, 428)], 3, 320),                                # Sholazar rim
    ([(272, 436), (284, 436), (300, 440)], 3, 300),                                # Zul'Drak cliffs
    # Pandaria
    ([(226, 104), (246, 108), (268, 104), (280, 98)], 6, 600),                     # Kun-Lai peaks
    ([(236, 84), (248, 90), (262, 88), (272, 80)], 3, 300),                        # Vale wall
    ([(222, 74), (226, 62), (226, 48)], 3, 260),                                   # Serpent's Spine (west)
    # Broken Isles / Kul Tiras / Zandalar
    ([(266, 350), (278, 358), (292, 354)], 5, 480),                                # Highmountain
    ([(300, 348), (302, 334), (298, 322)], 3, 300),                                # Stormheim
    ([(280, 212), (286, 202), (284, 192)], 3, 300),                                # Drustvar
    ([(214, 152), (220, 156), (226, 152)], 3, 280),                                # Dazar'alor hill
]

# Lakes: (cx, cy, rx, ry) or polygon.
LAKES = [
    (91, 384, 4, 3),         # Lake Elune'ara (Moonglade)
    (104, 280, 4, 3),        # Lake Falathim region (Ashenvale)
    (70, 290, 3, 2),         # Mystral lake
    (138, 132, 5, 4),        # Dustwallow pools
    (148, 146, 4, 3),
    (366, 344, 9, 9),        # Lordamere Lake
    (398, 356, 4, 3),        # Darrowmere Lake
    (414, 242, 5, 7),        # Loch Modan
    (424, 168, 4, 3),        # Lake Everstill (Redridge)
    (372, 172, 2, 2),        # Crystal Lake (Elwynn)
    (402, 270, 4, 3),        # Wetlands marsh
    (390, 276, 3, 2),
    (446, 152, 4, 3),        # Swamp of Sorrows
    (226, 176, 4, 3),        # Nazmir marsh
    (246, 400, 3, 2),        # Dragonblight lake
    (208, 432, 3, 3),        # Sholazar lake
    (254, 54, 3, 2),         # Valley of Four Winds pond
]

# Rivers: polyline, half-width. Rivers are shallow (walkable) water.
RIVERS = [
    [(102, 296), (96, 288), (84, 284), (66, 280), (52, 276), (34, 274)],     # Falfarren River (Ashenvale)
    [(120, 236), (130, 224), (142, 214), (152, 204), (158, 198)],            # Southfury tributary to Ratchet
    [(174, 266), (166, 250), (160, 232), (158, 214), (160, 202)],            # Southfury River (Durotar border)
    [(110, 48), (100, 40), (88, 34), (74, 30), (60, 28), (50, 24)],          # Uldum's river
    [(366, 336), (368, 322), (360, 312)],                                    # Lordamere to Southshore
    [(398, 352), (404, 362), (420, 372), (440, 374), (458, 372)],            # Thondroril / Darrowmere
    [(414, 234), (420, 226), (430, 218)],                                    # Loch Modan outflow
    [(380, 176), (372, 168), (360, 166), (344, 170)],                        # Elwynn river
    [(232, 52), (244, 56), (256, 54), (270, 44), (282, 34)],                 # Pandaria river
    [(216, 168), (224, 172), (232, 176)],                                    # Nazmir
]

# Shallow straits that ground units can wade across: polyline, half-width.
SHALLOWS = [
    [(38, 410), (46, 400), (54, 392)],   # Teldrassil to Darkshore
    [(170, 210), (174, 206)],        # Echo Isles to Durotar
    [(173, 134), (178, 133)],        # Theramore
    [(436, 448), (434, 440)],        # Quel'Danas to Eversong
]

# Cliff plateaus (mesas): (cx, cy, radius, extra cliff levels).
MESAS = [
    # Thunder Bluff
    (78, 192, 3.2, 2), (73, 186, 2.6, 2), (83, 185, 2.4, 2),
    # Thousand Needles
    (82, 132, 2.6, 2), (88, 122, 2.2, 1), (96, 134, 2.8, 2), (104, 124, 2.4, 2), (110, 134, 2.2, 1),
    (116, 122, 2.6, 2), (92, 116, 2.0, 1), (100, 140, 1.8, 1), (120, 132, 2.0, 2), (86, 140, 2.0, 1),
    # Durotar / Badlands buttes
    (170, 226, 1.8, 1), (156, 218, 1.6, 1), (440, 206, 2.4, 1), (426, 218, 2.0, 1),
    # Howling Fjord cliffs, Zul'Drak plateau, Kun-Lai shelves
    (314, 404, 2.5, 1), (300, 428, 3.0, 1), (286, 420, 2.6, 1),
    # Desolace
    (30, 170, 2.0, 1),
]

# Basins (bowls): (cx, cy, radius, depth)
BASINS = [
    (82, 84, 12, 180),       # Un'Goro crater floor
    (204, 436, 9, 60),       # Sholazar basin
    (254, 70, 8, 40),        # Vale
]

# ---------------------------------------------------------------------------
# Settlements and points of interest (tile coordinates)
# kind: 'capital' (player start), 'town' (neutral shop), 'camp' (expansion: gold mine + creeps)
# ---------------------------------------------------------------------------
CAPITALS = [
    # (start index, name, x, y, preferred race, faction colour hint)
    (0, 'Stormwind', 356, 172, 'human'),
    (1, 'Orgrimmar', 160, 256, 'orc'),
    (2, 'Undercity', 362, 376, 'undead'),
    (3, 'Darnassus', 33, 418, 'nightelf'),
    (4, 'Ironforge', 372, 236, 'human'),
    (5, 'Thunder Bluff', 86, 196, 'orc'),
    (6, 'Icecrown Citadel', 238, 446, 'undead'),
    (7, 'Silvermoon City', 438, 428, 'human'),
    (8, 'Shrine of Seven Stars', 258, 68, 'random'),
    (9, 'Suramar City', 284, 324, 'nightelf'),
    (10, 'Boralus', 300, 196, 'human'),
    (11, "Dazar'alor", 220, 150, 'orc'),
]

TOWNS = [
    # name, x, y, building
    ('Goldshire', 372, 166, 'ntav'), ('Booty Bay', 360, 24, 'nshp'), ('Booty Bay Market', 364, 28, 'ngme'),
    ('Ratchet', 156, 200, 'nshp'), ('Gadgetzan', 134, 76, 'ngad'), ('Everlook', 142, 382, 'ngad'),
    ('Theramore', 179, 133, 'nshp'), ('Menethil Harbor', 372, 272, 'nshp'), ('Auberdine', 44, 344, 'nshp'),
    ('Crossroads', 120, 230, 'ntav'), ('Astranaar', 96, 288, 'nmr5'), ('Lakeshire', 426, 172, 'nmer'),
    ('Darkshire', 394, 140, 'nmr2'), ('Southshore', 360, 314, 'nmrk'), ('Tarren Mill', 380, 326, 'ngme'),
    ('Thelsamar', 412, 232, 'ntav'), ('Kargath', 424, 214, 'nmr4'), ("Light's Hope Chapel", 458, 374, 'nfoh'),
    ('Tranquillien', 440, 396, 'nmr6'), ("Grom'gol", 348, 100, 'ngad'), ('Nethergarde Keep', 452, 120, 'nmrk'),
    ('Gadgetzan Market', 130, 72, 'ngme'), ('Cenarion Hold', 44, 72, 'nmoo'), ("Marshal's Refuge", 86, 92, 'nfoh'),
    ('Freewind Post', 100, 128, 'nmr4'), ('Camp Mojache', 58, 126, 'ntav'), ("Nijel's Point", 40, 198, 'ngme'),
    ('Sun Rock Retreat', 52, 230, 'nmer'), ('Camp Taurajo', 114, 182, 'nmr4'), ('Ramkahen', 78, 40, 'nmrk'),
    ('Valiance Keep', 206, 390, 'nshp'), ('Warsong Hold', 198, 404, 'ngad'), ('Dalaran', 262, 426, 'nmr7'),
    ('Wyrmrest Temple', 252, 402, 'ndru'), ('Valgarde', 306, 388, 'nshp'), ("K3", 288, 452, 'nmr7'),
    ('Shrine of Two Moons', 252, 74, 'ntav'), ('Halfhill', 240, 46, 'nmrk'), ('Dawn\'s Blossom', 288, 74, 'nmrc'),
    ('Dalaran (Broken Isles)', 270, 326, 'nmr9'), ('Stormwind Harbor', 344, 186, 'nshp'),
    ('Port of Zandalar', 228, 146, 'nshp'), ('Brennadam', 306, 220, 'ntav'), ('Arathor', 404, 300, 'nmrk'),
    ('Aerie Peak', 422, 334, 'nmer'), ('Hammerfall', 428, 300, 'ntav'), ("Thorium Point", 390, 214, 'ngme'),
    ('Morgan\'s Vigil', 418, 190, 'ndrk'), ('Sentinel Hill', 342, 146, 'ntav'), ('Sepulcher', 346, 352, 'nmr2'),
    ('Brill', 370, 384, 'ngme'), ('Chillwind Camp', 404, 360, 'nfoh'), ('Tanaris Caverns of Time', 150, 70, 'ndrz'),
    ('Onyxia\'s Lair', 150, 106, 'ndrk'), ('Feathermoon', 26, 118, 'nshp'), ('Rut\'theran', 44, 404, 'nshp'),
    ('Splintertree Post', 140, 282, 'nmr5'), ('Razor Hill', 166, 232, 'ngme'), ('Kezan Trade', 258, 210, 'ngad'),
]

CAMPS = [
    # name, x, y, creep strength (0 weak, 1 medium, 2 strong); each gets a gold mine
    ('Northshire', 384, 178, 0), ('Jerod\'s Landing', 392, 160, 0), ('Moonbrook', 336, 136, 1), ('Jangolode Mine', 348, 160, 0),
    ('Raven Hill', 368, 136, 1), ('Karazhan', 418, 136, 2), ('Stonard', 456, 146, 1), ('Dark Portal', 446, 94, 2),
    ('Zul\'Gurub', 384, 104, 2), ('Nesingwary\'s Camp', 362, 112, 1), ('Gurubashi Arena', 360, 64, 1), ('Ruins of Jubuwal', 376, 40, 1),
    ('Stonewatch', 440, 176, 0), ('Blackrock Spire', 396, 196, 2), ('Uldaman', 426, 224, 1), ('Dun Algaz', 396, 246, 0),
    ('Kharanos', 380, 232, 0), ('Gnomeregan', 356, 246, 1), ('Grim Batol', 444, 248, 2), ('Dragonmaw Gates', 458, 262, 1),
    ('Thandol Span', 386, 290, 0), ('Stromgarde', 396, 310, 1), ('Dalaran Crater', 378, 344, 2), ('Durnholde Keep', 382, 316, 1),
    ('Shadowfang Keep', 340, 340, 1), ('Gilneas City', 332, 308, 1), ('Andorhal', 404, 368, 1), ('Stratholme', 448, 382, 2),
    ('Zul\'Aman', 456, 408, 2), ('Sunwell Plateau', 442, 456, 2), ('Jintha\'Alor', 446, 326, 2), ('Scarlet Monastery', 378, 390, 1),
    ('Naxxramas Shadow', 432, 362, 2), ('Highbank', 462, 290, 1), ('Ruins of Lordaeron', 364, 366, 0),
    ('Shadowglen', 38, 420, 0), ('Ruins of Mathystra', 58, 384, 1), ('Bashal\'Aran', 50, 330, 0), ('Felwood Jaedenar', 76, 322, 1),
    ('Timbermaw Hold', 104, 352, 1), ('Nordrassil', 138, 342, 2), ('Mazthoril', 150, 372, 2), ('Ruins of Eldarath', 176, 316, 1),
    ('Warsong Lumber Camp', 136, 300, 1), ('Raynewood Retreat', 112, 286, 0), ('Blackfathom Deeps', 40, 290, 1),
    ('Stonetalon Peak', 40, 252, 2), ('Windshear Crag', 62, 236, 1), ('The Crossroads Oasis', 106, 240, 0), ('Far Watch Post', 150, 236, 0),
    ('Valley of Trials', 164, 220, 0), ('Kodo Graveyard', 36, 176, 1), ('Maraudon', 22, 186, 2), ('Bloodhoof Village', 82, 172, 0),
    ('Razorfen Kraul', 112, 156, 1), ('Bael Modan', 132, 168, 1), ('Dire Maul', 50, 132, 2), ('Twin Colossals', 34, 108, 1),
    ('Shimmering Flats', 116, 116, 1), ('Brackenwall Village', 140, 150, 1), ('Fire Plume Ridge', 82, 82, 2), ('Ahn\'Qiraj', 30, 56, 2),
    ('Zul\'Farrak', 120, 92, 2), ('Lost City of the Tol\'vir', 96, 32, 2), ('Steamwheedle Port', 160, 90, 0), ('Ruins of Ahn\'Qiraj', 46, 52, 1),
    ('Azuremyst Vault', 22, 362, 0), ('Bloodmyst Crash', 18, 392, 0),
    ('Coldarra', 196, 412, 1), ('Naxxramas', 270, 410, 2), ('Ulduar', 296, 458, 2), ('Gundrak', 306, 428, 2), ('Utgarde Keep', 312, 402, 1),
    ('Drak\'Tharon', 280, 412, 1), ('Wintergrasp Fortress', 232, 424, 1), ('Nesingwary Base Camp', 210, 440, 1), ('Azjol-Nerub', 240, 396, 2),
    ('Amber Ledge', 216, 392, 0), ('Pinnacle of Naxx', 222, 450, 2),
    ('Temple of the Jade Serpent', 296, 66, 1), ('Mogu\'shan Palace', 252, 62, 2), ('Niuzao Temple', 214, 98, 1), ('Klaxxi\'vess', 212, 56, 1),
    ('Temple of the White Tiger', 268, 102, 2), ('Zhu\'s Watch', 270, 24, 0), ('Stormstout Brewery', 236, 40, 0),
    ('Black Rook Hold', 262, 342, 1), ('Thunder Totem', 282, 350, 1), ('Halls of Valor', 300, 340, 2), ('Nar\'thalas', 266, 312, 1),
    ('Tomb of Sargeras', 292, 293, 2), ('Waycrest Manor', 284, 210, 1), ('Shrine of the Storm', 312, 220, 1), ('Freehold', 290, 188, 1),
    ('Atal\'Dazar', 214, 156, 1), ('Temple of Sethraliss', 204, 166, 1), ('The Underrot', 224, 174, 1),
    ('Maelstrom Rock', 252, 268, 2), ('Kezan', 260, 212, 0), ('Lost Isles', 230, 226, 1),
    ('Isle of Thunder', 194, 114, 2), ('Timeless Isle', 316, 26, 2), ('Tol Barad', 338, 274, 1),
]

# Waygates (mage portals): pairs of (name, x, y) linking far-apart lands.
PORTALS = [
    (('Stormwind Portal', 362, 180), ('Darnassus Portal', 38, 412)),
    (('Orgrimmar Portal', 152, 262), ('Undercity Portal', 356, 382)),
    (('Ironforge Portal', 378, 244), ('Dalaran Portal (Northrend)', 266, 430)),
    (('Thunder Bluff Portal', 78, 202), ('Silvermoon Portal', 432, 420)),
    (('Stormwind Harbor Portal', 350, 190), ('Boralus Portal', 306, 202)),
    (('Orgrimmar Gate', 166, 262), ("Dazar'alor Portal", 214, 146)),
    (('Ratchet Portal', 152, 206), ('Shrine Portal', 262, 76)),
    (('Undercity Gate', 368, 370), ('Icecrown Portal', 230, 440)),
    (('Silvermoon Gate', 444, 432), ('Suramar Portal', 278, 318)),
]

# Roads (polylines of tiles). Painted as dirt paths and kept free of trees.
ROADS = [
    # Eastern Kingdoms
    [(356, 172), (372, 166), (394, 170), (412, 172), (426, 172), (444, 176), (456, 166)],
    [(372, 166), (360, 156), (346, 146), (336, 132), (340, 116), (350, 104), (360, 88), (362, 64), (360, 40), (360, 24)],
    [(372, 166), (384, 150), (394, 140), (412, 140), (430, 146), (450, 146), (452, 130), (452, 120), (446, 100)],
    [(372, 236), (384, 236), (398, 238), (412, 232), (424, 220), (424, 214)],
    [(398, 238), (396, 252), (392, 264), (380, 272), (372, 274)],
    [(392, 264), (390, 280), (390, 292), (404, 300), (416, 304), (428, 300)],
    [(390, 292), (376, 304), (360, 314), (370, 322), (380, 326), (392, 334), (404, 346), (404, 360), (420, 368), (440, 372), (458, 374)],
    [(360, 314), (352, 330), (346, 350), (352, 366), (362, 376), (370, 384)],
    [(440, 372), (442, 386), (440, 396), (436, 410), (438, 428)],
    [(424, 214), (404, 212), (392, 212), (396, 196), (412, 190), (426, 186), (440, 176)],
    # Kalimdor
    [(160, 256), (164, 240), (166, 232), (154, 230), (138, 230), (120, 230), (106, 238), (96, 254), (96, 270), (96, 288)],
    [(120, 230), (138, 214), (152, 204), (156, 200)],
    [(120, 230), (118, 206), (114, 182), (100, 186), (86, 196)],
    [(114, 182), (116, 166), (110, 150), (102, 136), (100, 128), (112, 112), (124, 96), (134, 76)],
    [(134, 76), (150, 70)], [(134, 76), (112, 82), (90, 92), (70, 92), (50, 80), (44, 72)],
    [(96, 288), (120, 286), (140, 282), (160, 286), (176, 300)],
    [(96, 288), (78, 298), (60, 310), (50, 330), (44, 344), (46, 366), (52, 386)],
    [(96, 288), (84, 312), (80, 330), (88, 352), (110, 366), (128, 376), (142, 382)],
    [(96, 254), (70, 246), (52, 230), (44, 210), (40, 198), (36, 176), (46, 150), (58, 126)],
    [(140, 150), (150, 140), (166, 134), (176, 133)],
    [(118, 206), (130, 196), (140, 170), (140, 150)],
    # Northrend, Pandaria, isles
    [(206, 390), (208, 400), (198, 404)], [(206, 396), (228, 396), (252, 402), (270, 410), (288, 404), (306, 390)],
    [(252, 402), (260, 414), (262, 426)], [(262, 426), (250, 438), (238, 446)], [(262, 426), (278, 436), (288, 452)],
    [(258, 68), (252, 74), (240, 82), (226, 92)], [(258, 68), (276, 72), (288, 74)], [(258, 68), (248, 56), (240, 46), (262, 30)],
    [(284, 324), (270, 326), (264, 336)], [(284, 324), (290, 340), (282, 350)], [(284, 324), (268, 312)],
    [(300, 196), (290, 206), (306, 220)], [(220, 150), (206, 162)], [(220, 150), (224, 172)],
]

# Landmark doodads: (doodad id, x, y, scale, angle radians)
LANDMARKS = [
    ('ASwt', 37, 414, 1.0, 4.71),        # Teldrassil
    ('ASwt', 138, 343, 1.0, 4.71),       # Nordrassil on Mount Hyjal
    ('YOsw', 441, 457, 0.9, 4.71),       # The Sunwell
    ('IZft', 240, 450, 1.0, 4.71),       # The Frozen Throne
    ('ZOvr', 378, 344, 0.9, 4.71),       # Ruined Violet Citadel (Dalaran crater)
    ('OZsp', 446, 92, 1.0, 4.71),        # The Dark Portal
    ('LZth', 162, 246, 1.0, 4.71),       # Thrall's hut
    ('DOas', 184, 312, 1.0, 3.14),       # Statue of Azshara
    ('ZZys', 444, 268, 1.0, 4.71),       # Eye of Sargeras (Twilight Highlands)
    ('BOth', 156, 258, 0.95, 4.71),      # Hellscream's throne
    ('YOst', 360, 180, 0.95, 4.71),      # Stormwind statue
    ('AOgs', 40, 406, 1.0, 4.71),        # Sentinel statue
]
# Destructable landmarks (volcanoes etc.): (id, x, y, scale)
DESTRUCTABLE_LANDMARKS = [
    ('Volc', 82, 82, 1.0),      # Fire Plume Ridge
    ('Volc', 392, 202, 1.1),    # Blackrock Mountain
    ('Volc', 290, 296, 0.8),    # Broken Shore
]
