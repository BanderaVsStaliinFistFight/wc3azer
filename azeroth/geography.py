"""Hand-authored layout of Azeroth on a 480 x 480 tile grid.

Coordinates are in tiles with (0, 0) at the south-west corner of the map and
y growing northwards. The playable area is x 6..474, y 4..472.
Kalimdor lies to the west and the Eastern Kingdoms to the east; both are drawn
in tile coordinates and then squashed vertically (SQUASH) to leave the top of
the map for Northrend, which follows the Wrath of the Lich King continent map
inside NORTHREND_BOX. The Maelstrom sits in the middle of the Great Sea with the
goblin isle of Kezan below it and Kul Tiras to the east.
"""
import math


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
    (372, 302), (362, 306), (356, 312), (355, 318), (352, 324), (348, 329), (343, 330), (334, 329.5), (327, 331.5),
    (328, 340.25), (334, 350), (338, 364), (336, 376), (340, 388), (348, 396), (358, 400),
    (370, 398), (382, 396), (394, 400), (404, 406), (410, 420), (414, 432),
]

# Coastline noise scale per landmass (default 1.0); traced shapes use less so they keep their outline.
COAST_NOISE = {}

# name: shape. Polygons are lists of points; ellipses are ('ellipse', cx, cy, rx, ry).
LANDMASSES = {
    'Kalimdor': KALIMDOR,
    'Eastern Kingdoms': EASTERN_KINGDOMS,
    'Teldrassil': ('ellipse', 37, 413, 15, 14),
    'Azuremyst Isle': ('ellipse', 22, 366, 8, 12),
    'Bloodmyst Isle': ('ellipse', 16, 386, 6, 6),
    "Isle of Quel'Danas": ('ellipse', 441, 455, 10, 7),
    'Echo Isles': ('ellipse', 176, 206, 4, 3),
    'Theramore Isle': ('ellipse', 179, 133, 3, 3),
    'Alcaz Island': ('ellipse', 182, 152, 4, 3),
    'Tol Barad': ('ellipse', 352, 292.1, 4, 3.75),
    'Kezan': ('ellipse', 250, 202, 9, 6),
}

# The Maelstrom: a whirlpool drawn into the sea floor as spiral arms of shallow water
# around a bottomless eye: (centre x, centre y), outer radius in tiles.
MAELSTROM = (247, 246)
MAELSTROM_RADIUS = 30

# ---------------------------------------------------------------------------
# Zones: (name, landmass, cx, cy, rx, ry, biome, extra settings)
# Zone of a land tile = nearest zone centre (ellipse-normalised) on its landmass.
# ---------------------------------------------------------------------------
Z = []


def zone(name, land, cx, cy, rx, ry, biome, **kw):
    Z.append(dict(name=name, land=land, cx=cx, cy=cy, rx=rx, ry=ry, biome=biome, **kw))


# Kalimdor
zone('Teldrassil', 'Teldrassil', 37, 413, 15, 14, 'worldtree', base=90)
zone('Azuremyst Isle', 'Azuremyst Isle', 22, 366, 8, 12, 'nightelf')
zone('Bloodmyst Isle', 'Bloodmyst Isle', 16, 386, 6, 6, 'fel')
zone('Darkshore', 'Kalimdor', 50, 348, 10, 44, 'nightelf', hills=90)
zone('Moonglade', 'Kalimdor', 88, 385, 13, 10, 'nightelf', base=110)
zone('Felwood', 'Kalimdor', 78, 340, 14, 30, 'fel')
zone('Winterspring', 'Kalimdor', 146, 380, 24, 20, 'snow', base=50, level=1)
zone('Mount Hyjal', 'Kalimdor', 136, 338, 18, 15, 'worldtree', base=60, hills=110, level=1)
zone('Azshara', 'Kalimdor', 182, 318, 16, 22, 'autumn', hills=90)
zone('Ashenvale', 'Kalimdor', 100, 290, 55, 17, 'nightelf')
zone('Stonetalon Mountains', 'Kalimdor', 46, 240, 22, 24, 'rocky', base=30, mountains=360, level=1)
zone('Northern Barrens', 'Kalimdor', 120, 232, 26, 24, 'savanna')
zone('Durotar', 'Kalimdor', 164, 238, 13, 32, 'reddesert')
zone('Desolace', 'Kalimdor', 38, 180, 22, 24, 'barren')
zone('Mulgore', 'Kalimdor', 80, 182, 18, 21, 'plains', base=80)
zone('Southern Barrens', 'Kalimdor', 124, 176, 25, 21, 'savanna')
zone('Feralas', 'Kalimdor', 42, 122, 24, 24, 'jungle', hills=120)
zone('Thousand Needles', 'Kalimdor', 98, 128, 24, 15, 'needles', base=10, hills=20)
zone('Dustwallow Marsh', 'Kalimdor', 150, 134, 18, 22, 'swamp', base=18)
zone("Un'Goro Crater", 'Kalimdor', 82, 84, 18, 18, 'jungle', base=150, hills=50, level=-1)
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
zone('Hillsbrad Foothills', 'Eastern Kingdoms', 368, 322, 15, 11, 'temperate')
zone('Alterac Mountains', 'Eastern Kingdoms', 390, 343, 12, 10, 'snow', base=40, level=1)
zone('The Hinterlands', 'Eastern Kingdoms', 434, 330, 28, 13, 'highland', base=20, level=1)
zone('Arathi Highlands', 'Eastern Kingdoms', 410, 302, 24, 13, 'farmland', base=60)
zone('Wetlands', 'Eastern Kingdoms', 394, 270, 18, 14, 'swamp', base=20)
zone('Twilight Highlands', 'Eastern Kingdoms', 452, 272, 17, 22, 'highland')
zone('Dun Morogh', 'Eastern Kingdoms', 368, 236, 18, 16, 'snow', base=40, level=1)
zone('Loch Modan', 'Eastern Kingdoms', 420, 240, 14, 13, 'highland', base=90, mountains=100)
zone('Badlands', 'Eastern Kingdoms', 434, 212, 17, 13, 'reddesert')
zone('Searing Gorge', 'Eastern Kingdoms', 392, 210, 14, 9, 'volcanic', base=20, level=1)
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
zone('Tol Barad', 'Tol Barad', 352, 292.1, 4, 3.75, 'barren')
# Northrend
# Kezan
zone('Kezan', 'Kezan', 250, 202, 9, 6, 'jungle')
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
    ([(64, 318), (66, 336), (64, 356), (66, 372)], 3, 380),                        # Darkshore's eastern range
    ([(186, 304), (192, 320), (194, 334)], 3, 340),                                # the mountains of Azshara
    ([(66, 134), (70, 118), (68, 104)], 3, 360),                                   # Feralas / Thousand Needles wall
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
    ([(440, 222), (452, 214), (458, 202)], 4, 360),                                # Badlands peaks
    ([(414, 160), (426, 156), (440, 160)], 3, 360),                                # Redridge peaks
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
    # Desolace
    (30, 170, 2.0, 1),
]

# Walls: (polyline, gate gaps) built as a one-tile raised cliff rampart, also out into shallow water.
WALLS = []

# Basins (bowls): (cx, cy, radius, depth)
BASINS = [
    (82, 84, 12, 60),        # Un'Goro crater floor (the crater itself is a sunken cliff level)
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
    (7, 'Silvermoon City', 438, 428, 'human'),
    (10, 'Boralus', 307.6, 182, 'human'),
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
    ('Stormwind Harbor', 344, 186, 'nshp'), ('Arathor', 404, 300, 'nmrk'),
    ('Aerie Peak', 422, 334, 'nmer'), ('Hammerfall', 428, 300, 'ntav'), ("Thorium Point", 390, 214, 'ngme'),
    ('Morgan\'s Vigil', 418, 190, 'ndrk'), ('Sentinel Hill', 342, 146, 'ntav'), ('Sepulcher', 346, 352, 'nmr2'),
    ('Brill', 370, 384, 'ngme'), ('Chillwind Camp', 404, 360, 'nfoh'), ('Tanaris Caverns of Time', 150, 70, 'ndrz'),
    ('Onyxia\'s Lair', 150, 106, 'ndrk'), ('Feathermoon', 26, 118, 'nshp'), ('Rut\'theran', 44, 404, 'nshp'),
    ('Splintertree Post', 140, 282, 'nmr5'), ('Razor Hill', 166, 232, 'ngme'), ('Kezan Trade', 250, 202, 'ngad'),
]

CAMPS = [
    # name, x, y, creep strength (0 weak, 1 medium, 2 strong); each gets a gold mine
    ('Northshire', 384, 178, 0), ('Jerod\'s Landing', 392, 160, 0), ('Moonbrook', 336, 136, 1), ('Jangolode Mine', 348, 160, 0),
    ('Raven Hill', 368, 136, 1), ('Karazhan', 418, 136, 2), ('Stonard', 456, 146, 1), ('Dark Portal', 446, 94, 2),
    ('Zul\'Gurub', 384, 104, 2), ('Nesingwary\'s Camp', 362, 112, 1), ('Gurubashi Arena', 360, 64, 1), ('Ruins of Jubuwal', 376, 40, 1),
    ('Stonewatch', 440, 176, 0), ('Blackrock Spire', 396, 196, 2), ('Uldaman', 426, 224, 1), ('Dun Algaz', 396, 246, 0),
    ('Kharanos', 380, 232, 0), ('Gnomeregan', 356, 246, 1), ('Grim Batol', 444, 248, 2), ('Dragonmaw Gates', 458, 262, 1),
    ('Thandol Span', 386, 290, 0), ('Stromgarde', 396, 310, 1), ('Dalaran Crater', 378, 344, 2), ('Durnholde Keep', 382, 316, 1),
    ('Shadowfang Keep', 340, 340, 1), ('Andorhal', 404, 368, 1), ('Stratholme', 448, 382, 2),
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
    ('Azuremyst Vault', 22, 362, 0), ('Bloodmyst Crash', 16, 386, 0),
    ('Kezan', 252, 200, 0), ('Tol Barad', 352, 292.1, 1),
]

# Waygates (mage portals): pairs of (name, x, y) linking far-apart lands.
PORTALS = [
    (('Stormwind Portal', 362, 180), ('Darnassus Portal', 38, 412)),
    (('Orgrimmar Portal', 152, 262), ('Undercity Portal', 356, 382)),
    (('Thunder Bluff Portal', 78, 202), ('Silvermoon Portal', 432, 420)),
    (('Stormwind Harbor Portal', 350, 190), ('Boralus Portal', 298, 192)),
    (('Ratchet Portal', 152, 206), ('Kezan Portal', 250, 202)),
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
    [(140, 282), (136, 300), (134, 318), (137, 334)],                       # Ashenvale up to Mount Hyjal
    # Eastern Kingdoms, continued
    [(428, 300), (426, 316), (422, 334), (436, 332), (446, 326)],          # Arathi up to the Hinterlands
]

# Landmark doodads: (doodad id, x, y, scale, angle radians)
LANDMARKS = [
    ('ASwt', 44, 418, 1.0, 4.71),        # Teldrassil
    ('ASwt', 138, 343, 1.0, 4.71),       # Nordrassil on Mount Hyjal
    ('YOsw', 441, 457, 0.9, 4.71),       # The Sunwell
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
]


# ---------------------------------------------------------------------------
# Squash Kalimdor and the Eastern Kingdoms towards the south edge so the top
# of the map is free for a correctly proportioned Northrend.
# ---------------------------------------------------------------------------
SQUASH_BASE, SQUASH = 14.0, 0.8
_SQUASHED_LANDS = {'Kalimdor', 'Eastern Kingdoms', 'Teldrassil', 'Azuremyst Isle', 'Bloodmyst Isle',
                   "Isle of Quel'Danas", 'Echo Isles', 'Theramore Isle', 'Alcaz Island', 'Tol Barad'}


def _sy(y):
    return round(SQUASH_BASE + (y - SQUASH_BASE) * SQUASH, 2)


def _near_squashed(x, y, margin=10.0):
    """True if (x, y), in pre-squash coordinates, lies on or near Kalimdor, the Eastern Kingdoms or their isles."""
    for name in _SQUASHED_LANDS:
        shape = LANDMASSES[name]
        if shape[0] == 'ellipse':
            _, cx, cy, rx, ry = shape
            if ((x - cx) / (rx + margin)) ** 2 + ((y - cy) / (ry + margin)) ** 2 <= 1:
                return True
            continue
        inside = False
        for (ax, ay), (bx, by) in zip(shape, shape[1:] + shape[:1]):
            if (ay > y) != (by > y) and x < ax + (y - ay) * (bx - ax) / (by - ay):
                inside = not inside
            dx, dy = bx - ax, by - ay
            t = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / float(dx * dx + dy * dy)))
            if (x - ax - t * dx) ** 2 + (y - ay - t * dy) ** 2 <= margin * margin:
                return True
        if inside:
            return True
    return False


def _squash_points(points):
    return [(x, _sy(y)) for x, y in points]


def _squash_everything():
    global RIDGES, LAKES, RIVERS, SHALLOWS, MESAS, BASINS, CAPITALS, TOWNS, CAMPS, PORTALS, ROADS
    global LANDMARKS, DESTRUCTABLE_LANDMARKS, WALLS
    near = _near_squashed
    for z in ZONES:
        if z['land'] in _SQUASHED_LANDS:
            z['cy'], z['ry'] = _sy(z['cy']), z['ry'] * SQUASH
    RIDGES = [(_squash_points(l), w, h) if near(*l[0]) else (l, w, h) for l, w, h in RIDGES]
    LAKES = [(x, _sy(y), rx, ry * SQUASH) if near(x, y) else (x, y, rx, ry) for x, y, rx, ry in LAKES]
    RIVERS = [_squash_points(l) if near(*l[0]) else l for l in RIVERS]
    SHALLOWS = [_squash_points(l) if near(*l[0]) else l for l in SHALLOWS]
    MESAS = [(x, _sy(y), r, lv) if near(x, y) else (x, y, r, lv) for x, y, r, lv in MESAS]
    BASINS = [(x, _sy(y), r * 0.9, d) if near(x, y) else (x, y, r, d) for x, y, r, d in BASINS]
    WALLS = [(_squash_points(l), _squash_points(g)) if near(*l[0]) else (l, g) for l, g in WALLS]
    CAPITALS = [(i, n, x, _sy(y), race) if near(x, y) else (i, n, x, y, race) for i, n, x, y, race in CAPITALS]
    TOWNS = [(n, x, _sy(y), b) if near(x, y) else (n, x, y, b) for n, x, y, b in TOWNS]
    CAMPS = [(n, x, _sy(y), st) if near(x, y) else (n, x, y, st) for n, x, y, st in CAMPS]
    PORTALS = [tuple((n, x, _sy(y)) if near(x, y) else (n, x, y) for n, x, y in pair) for pair in PORTALS]
    ROADS = [_squash_points(l) if near(*l[0]) else l for l in ROADS]
    LANDMARKS = [(d, x, _sy(y), sc, a) if near(x, y) else (d, x, y, sc, a) for d, x, y, sc, a in LANDMARKS]
    DESTRUCTABLE_LANDMARKS = [(d, x, _sy(y), sc) if near(x, y) else (d, x, y, sc) for d, x, y, sc in DESTRUCTABLE_LANDMARKS]
    # landmass outlines last: the membership test above needs the original shapes
    for name in _SQUASHED_LANDS:
        shape = LANDMASSES[name]
        if shape[0] == 'ellipse':
            _, cx, cy, rx, ry = shape
            LANDMASSES[name] = ('ellipse', cx, _sy(cy), rx, ry * SQUASH)
        else:
            LANDMASSES[name] = _squash_points(shape)


_squash_everything()

# ---------------------------------------------------------------------------
# Northrend, after the Wrath of the Lich King continent map.
# Authored in normalised coordinates: u = 0 west .. 1 east, v = 0 south .. 1 north.
# ---------------------------------------------------------------------------
NORTHREND_BOX = (144, 330, 386, 468)      # x0, y0, x1, y1 in tiles


def nr(u, v):
    x0, y0, x1, y1 = NORTHREND_BOX
    return round(x0 + u * (x1 - x0), 1), round(y0 + v * (y1 - y0), 1)


def nr_size(ru, rv):
    x0, y0, x1, y1 = NORTHREND_BOX
    return round(ru * (x1 - x0), 1), round(rv * (y1 - y0), 1)


NORTHREND_UV = [
    # south coast, west to east: Borean Tundra, Dragonblight's bay, Venture Bay, Howling Fjord's fjords
    (0.03, 0.22), (0.06, 0.12), (0.10, 0.06), (0.15, 0.03), (0.20, 0.05), (0.24, 0.09), (0.27, 0.15),
    (0.29, 0.10), (0.33, 0.12), (0.38, 0.16), (0.42, 0.12), (0.45, 0.17), (0.50, 0.15), (0.55, 0.18),
    (0.59, 0.16), (0.62, 0.21), (0.65, 0.14), (0.69, 0.10), (0.72, 0.04), (0.75, 0.09), (0.78, 0.01),
    (0.82, 0.06), (0.85, 0.02), (0.89, 0.07), (0.93, 0.03), (0.97, 0.09),
    # east coast: Howling Fjord, Grizzly Hills, Zul'Drak, the Storm Peaks
    (1.00, 0.17), (0.97, 0.25), (1.00, 0.31), (0.96, 0.37), (0.93, 0.44), (0.95, 0.52), (0.92, 0.60),
    (0.95, 0.70), (0.93, 0.80), (0.96, 0.88), (0.90, 0.96),
    # north coast: the Storm Peaks and the Icecrown glacier
    (0.82, 0.99), (0.72, 0.97), (0.64, 1.00), (0.56, 0.97), (0.50, 0.93), (0.44, 0.97), (0.36, 0.93),
    (0.30, 0.96), (0.24, 0.90), (0.18, 0.86), (0.10, 0.84), (0.05, 0.78),
    # west coast: Sholazar Basin, Coldarra, Borean Tundra
    (0.02, 0.70), (0.04, 0.60), (0.01, 0.52), (0.04, 0.47), (-0.02, 0.45), (-0.05, 0.39), (-0.04, 0.32),
    (0.01, 0.28),
]
LANDMASSES['Northrend'] = [nr(u, v) for u, v in NORTHREND_UV]

# Narrow sea inlets cut after the coastline noise so they stay crisp: (polyline in u/v, half-width in tiles)
SEA_INLETS = [
    ([nr(u, v) for u, v in line], w) for line, w in [
        ([(-0.07, 0.30), (0.02, 0.34), (0.04, 0.40), (0.03, 0.48)], 1.3),      # strait around Coldarra
        ([(0.28, 0.04), (0.28, 0.12), (0.30, 0.19)], 2.2),                     # bay between Borean Tundra and Dragonblight
        ([(0.46, 0.08), (0.47, 0.15), (0.49, 0.20)], 1.8),                     # Moa'ki Harbor
        ([(0.60, 0.10), (0.61, 0.18), (0.63, 0.24)], 2.4),                     # Venture Bay
        ([(0.70, -0.02), (0.71, 0.08), (0.73, 0.15)], 1.5),                    # Kamagua fjord
        ([(0.90, -0.02), (0.90, 0.10), (0.92, 0.17), (0.95, 0.21)], 1.8),      # the Howling Fjord
        ([(1.03, 0.22), (0.96, 0.26), (0.91, 0.31)], 1.5),                     # Vengeance Landing fjord
    ]
]


def _nr_zone(name, u, v, ru, rv, biome, **kw):
    cx, cy = nr(u, v)
    rx, ry = nr_size(ru, rv)
    zone(name, 'Northrend', cx, cy, rx, ry, biome, **kw)


_nr_zone('Borean Tundra', 0.13, 0.25, 0.13, 0.18, 'tundra')
_nr_zone('Sholazar Basin', 0.13, 0.64, 0.12, 0.17, 'jungle', base=30)
_nr_zone('Wintergrasp', 0.32, 0.50, 0.08, 0.09, 'snow', base=110, mountains=100)
_nr_zone('Icecrown', 0.38, 0.80, 0.17, 0.16, 'icecrown', base=40, level=1)
_nr_zone('Crystalsong Forest', 0.50, 0.52, 0.06, 0.08, 'crystal', base=90)
_nr_zone('Dragonblight', 0.43, 0.28, 0.16, 0.17, 'snow', base=60, mountains=30, density=0.06)
_nr_zone('The Storm Peaks', 0.74, 0.82, 0.20, 0.16, 'snow', base=100, mountains=460, level=1)
_nr_zone("Zul'Drak", 0.73, 0.53, 0.14, 0.10, 'tundra', base=50, hills=90, density=0.04, level=1)
_nr_zone('Grizzly Hills', 0.70, 0.30, 0.10, 0.11, 'grizzly', base=70)
_nr_zone('Howling Fjord', 0.87, 0.17, 0.12, 0.15, 'fjord', base=80)

RIDGES += [
    ([nr(0.55, 0.70), nr(0.65, 0.82), nr(0.78, 0.86), nr(0.90, 0.78)], 6, 640),       # the Storm Peaks
    ([nr(0.28, 0.88), nr(0.38, 0.90), nr(0.48, 0.86)], 5, 520),                       # Icecrown glacier
    ([nr(0.05, 0.50), nr(0.12, 0.47), nr(0.21, 0.50), nr(0.25, 0.60), nr(0.22, 0.74)], 3, 360),  # Sholazar rim
    ([nr(0.60, 0.42), nr(0.70, 0.40), nr(0.82, 0.42)], 3, 280),                       # Zul'Drak escarpment
    ([nr(0.72, 0.22), nr(0.80, 0.26), nr(0.90, 0.28)], 3, 260),                       # Howling Fjord highlands
    ([nr(0.25, 0.40), nr(0.30, 0.36), nr(0.38, 0.38)], 3, 240),                       # Wintergrasp foothills
]
LAKES += [nr(0.36, 0.24) + (3, 2), nr(0.52, 0.36) + (2.5, 2), nr(0.66, 0.26) + (3, 2)]   # Indu'le, Wyrmrest, Grizzly
RIVERS += [[nr(0.13, 0.64), nr(0.07, 0.57), nr(0.02, 0.51)]]                               # Sholazar's river
MESAS += [nr(0.68, 0.52) + (3.0, 1), nr(0.78, 0.50) + (2.6, 1), nr(0.92, 0.20) + (2.2, 1)]  # Zul'Drak, Howling Fjord
BASINS += [nr(0.13, 0.64) + (12, 70)]                                                     # Sholazar Basin

CAPITALS += [
    (6, 'Icecrown Citadel') + nr(0.34, 0.72) + ('undead',),
    (8, 'Dalaran') + nr(0.50, 0.52) + ('random',),
    (9, 'Warsong Hold') + nr(0.10, 0.28) + ('orc',),
    (11, 'Valgarde') + nr(0.80, 0.10) + ('human',),
]
CAPITALS.sort()

TOWNS += [(name,) + nr(u, v) + (building,) for name, u, v, building in [
    ('Valiance Keep', 0.20, 0.08, 'nshp'), ('Fizzcrank Airstrip', 0.18, 0.38, 'ngad'), ("River's Heart", 0.13, 0.60, 'nmoo'),
    ('Wyrmrest Temple', 0.52, 0.30, 'ndru'), ("Moa'ki Harbor", 0.42, 0.16, 'nshp'), ("Agmar's Hammer", 0.40, 0.36, 'ntav'),
    ('Amberpine Lodge', 0.70, 0.30, 'ngme'), ('K3', 0.66, 0.66, 'nmr7'), ("Zim'Torga", 0.74, 0.50, 'nfoh'),
    ('Vengeance Landing', 0.96, 0.26, 'nshp'), ('Argent Tournament Grounds', 0.50, 0.88, 'nmrk'), ('Violet Gate Market', 0.44, 0.50, 'nmr9'),
]]

CAMPS += [(name,) + nr(u, v) + (strength,) for name, u, v, strength in [
    ('Coldarra', 0.03, 0.37, 1), ('Amber Ledge', 0.06, 0.18, 0), ('Kaskala', 0.24, 0.18, 0), ("Bor'gorok Outpost", 0.18, 0.44, 0),
    ('Nesingwary Base Camp', 0.09, 0.56, 1), ('Rainspeaker Canopy', 0.18, 0.70, 1), ('Frenzyheart Hill', 0.21, 0.57, 0),
    ('Ymirheim', 0.42, 0.74, 1), ('The Shadow Vault', 0.30, 0.86, 2), ('Argent Vanguard', 0.50, 0.72, 1), ("Aldur'thar", 0.42, 0.88, 2),
    ('Wintergrasp Fortress', 0.30, 0.52, 1), ('Azjol-Nerub', 0.34, 0.30, 2), ('Naxxramas', 0.58, 0.34, 2), ("Star's Rest", 0.30, 0.20, 0),
    ('New Hearthglen', 0.56, 0.22, 1), ('Icemist Village', 0.40, 0.42, 1), ("Drak'Tharon Keep", 0.66, 0.42, 1), ('Grizzlemaw', 0.73, 0.27, 1),
    ('Camp Oneqwah', 0.78, 0.34, 0), ('Gundrak', 0.88, 0.48, 2), ("Drak'Sotra", 0.63, 0.53, 1), ('Ulduar', 0.72, 0.88, 2),
    ('Dun Niffelem', 0.84, 0.74, 1), ('Brunnhildar Village', 0.60, 0.80, 1), ('Utgarde Keep', 0.85, 0.20, 1),
    ('Utgarde Pinnacle', 0.93, 0.31, 2), ('Kamagua', 0.70, 0.08, 0), ('Westguard Keep', 0.74, 0.18, 0),
]]

PORTALS += [
    (('Ironforge Portal', 378, _sy(244)), ('Dalaran Portal',) + nr(0.57, 0.44)),
    (('Undercity Gate', 368, _sy(370)), ('Icecrown Portal',) + nr(0.40, 0.64)),
    (('Orgrimmar Gate', 166, _sy(262)), ('Warsong Hold Portal',) + nr(0.20, 0.22)),
    (('Menethil Harbor Portal', 378, _sy(280)), ('Valgarde Portal',) + nr(0.70, 0.16)),
]

ROADS += [[nr(u, v) for u, v in line] for line in [
    [(0.10, 0.28), (0.18, 0.30), (0.26, 0.36), (0.32, 0.46), (0.42, 0.50), (0.50, 0.52)],
    [(0.20, 0.08), (0.20, 0.20), (0.18, 0.30)],
    [(0.50, 0.52), (0.50, 0.40), (0.52, 0.30), (0.45, 0.20), (0.42, 0.16)],
    [(0.50, 0.52), (0.42, 0.62), (0.34, 0.72)],
    [(0.52, 0.30), (0.62, 0.30), (0.70, 0.30), (0.76, 0.22), (0.80, 0.10)],
    [(0.50, 0.52), (0.60, 0.54), (0.72, 0.52), (0.86, 0.48)],
    [(0.50, 0.52), (0.58, 0.62), (0.66, 0.66), (0.70, 0.80)],
    [(0.80, 0.10), (0.88, 0.18), (0.96, 0.26)],
]]

LANDMARKS += [('IZft',) + nr(0.28, 0.82) + (1.0, 4.71)]   # The Frozen Throne


# ---------------------------------------------------------------------------
# Gilneas, after the "City-States of Arathor" map: a compact peninsula that
# continues Lordaeron's west coast south of Silverpine, west of Southshore and
# level with Stromgarde. Its south-western lobe reaches furthest south, a
# harbour on the east side holds Gilneas City, two islets lie off the west
# coast and Baradin Bay opens to the south-east. Tile coordinates, added after
# the squash.
# ---------------------------------------------------------------------------
LANDMASSES['Gilneas'] = [
    (325.5, 271), (343, 269), (339.5, 263.5), (337, 260), (337.8, 257.5), (339.5, 255.6), (343.5, 252), (344.5, 248.5),
    (343.5, 244.5), (340, 241.5), (335.5, 240), (331, 238.5), (327, 236.5), (323, 237.5), (320, 240.5),
    (318.5, 244.5), (318, 249), (319, 253.5), (320.5, 257.5), (322.5, 261), (324.5, 264), (325.5, 266.5),
]
LANDMASSES['Gilneas Isle North'] = ('ellipse', 308.5, 248, 2.8, 2.3)
LANDMASSES['Gilneas Isle South'] = ('ellipse', 310, 241.5, 2.8, 2.3)
COAST_NOISE['Gilneas'] = 0.6
zone('Gilneas', 'Gilneas', 331, 251, 15, 16, 'darkforest', base=60)
zone('Gilneas', 'Gilneas Isle North', 308.5, 248, 2.8, 2.3, 'darkforest')
zone('Gilneas', 'Gilneas Isle South', 310, 241.5, 2.8, 2.3, 'darkforest')

SEA_INLETS += [([(347, 254.5), (341, 254.3), (338.5, 254)], 1.1)]                 # Gilneas City's harbour
RIDGES += [([(321, 243), (326, 239.5)], 1.6, 260)]                                 # hills above Tempest's Reach

# Gilneas City: a ring road around Greymane's statue, at the head of the harbour
_CITY, _CITY_R = (333.3, 253.6), 3.2
_ring = [(round(_CITY[0] + _CITY_R * math.cos(a), 1), round(_CITY[1] + _CITY_R * math.sin(a), 1))
         for a in [2 * math.pi * k / 16 for k in range(17)]]
_GATE = (333.5, 265.5)
ROADS += [
    _ring,
    [(_CITY[0], _CITY[1] + _CITY_R), _GATE, (334, 272), (346, 282.8)],   # north to the Greymane Gate and Silverpine
    [(_CITY[0] - _CITY_R, _CITY[1]), (321.5, 250)],                        # west to Duskhaven
    [(_CITY[0], _CITY[1] - _CITY_R), (329, 241.5)],                        # south to Stormglen
]
LANDMARKS += [('YOst',) + _CITY + (0.9, 4.71)]                              # Greymane's statue

# The Greymane Wall: a cliff rampart across the neck, reaching a couple of tiles past each shore.
WALLS += [([(322.5, 265.5), (345.5, 265.5)], [_GATE])]

TOWNS += [('Duskhaven', 321.5, 250, 'ntav'), ('Keel Harbor', 323.5, 259.5, 'nshp')]
CAMPS += [('The Blackwald', 339, 245, 2), ('Stormglen Village', 327, 241, 0)]

# ---------------------------------------------------------------------------
# Kul Tiras, traced from the Battle for Azeroth zone map (without Mechagon and
# Nazjatar): Stormsong Valley to the north with a mountain band along its south,
# Drustvar's peaks to the south-west, Tiragarde Sound to the south-east with
# Boralus on the harbour at its north-west tip. A strait runs south from the
# harbour between Drustvar and Tiragarde, and an inlet cuts in from the west.
# Authored in that map's pixel coordinates and fitted into KUL_TIRAS_BOX.
# ---------------------------------------------------------------------------
KUL_TIRAS_BOX = (276, 160, 320, 210)       # x0, y0, x1, y1 in tiles
_KT_PX = (470, 110, 1430, 1200)            # the zone map's islands: left, top, right, bottom


def kt(px, py):
    x0, y0, x1, y1 = KUL_TIRAS_BOX
    l, t, r, b = _KT_PX
    return round(x0 + (px - l) / (r - l) * (x1 - x0), 1), round(y0 + (b - py) / (b - t) * (y1 - y0), 1)


LANDMASSES['Kul Tiras'] = [kt(px, py) for px, py in [
    # Stormsong Valley, north coast west to east
    (690, 450), (740, 420), (800, 380), (860, 320), (900, 260), (950, 220), (1000, 170), (1070, 145), (1140, 140),
    (1190, 170), (1230, 175), (1270, 140), (1330, 150), (1390, 210), (1430, 290), (1410, 345), (1360, 365),
    (1335, 410), (1365, 470), (1380, 560), (1345, 630), (1300, 690),
    # Tiragarde Sound
    (1330, 740), (1360, 800), (1405, 850), (1425, 930), (1405, 1020), (1360, 1085), (1300, 1125), (1255, 1170),
    (1190, 1150), (1120, 1105), (1070, 1050),
    # Drustvar
    (990, 1150), (900, 1190), (800, 1205), (700, 1185), (655, 1125), (590, 1065), (510, 1035), (470, 960),
    (490, 880), (475, 810), (515, 750), (560, 690), (640, 670),
    # Stormsong's south-western lobe
    (670, 600), (665, 520),
]]
COAST_NOISE['Kul Tiras'] = 0.5
zone('Stormsong Valley', 'Kul Tiras', *kt(1120, 330), 14, 9, 'farmland', base=50)
zone('Drustvar', 'Kul Tiras', *kt(720, 940), 10, 11, 'autumn', base=20, hills=110, level=1)
zone('Tiragarde Sound', 'Kul Tiras', *kt(1230, 960), 9, 11, 'temperate')

SEA_INLETS += [([kt(px, py) for px, py in line], w) for line, w in [
    ([(1150, 680), (1090, 720), (1030, 770), (1010, 850), (1020, 950), (1030, 1060), (1040, 1180)], 1.5),  # Boralus harbour and the strait
    ([(560, 650), (660, 670), (760, 700)], 1.4),                                                          # the western inlet
    ([(1230, 160), (1232, 230), (1250, 300)], 1.0),                                                       # bay on Stormsong's north coast
]]
RIDGES += [([kt(px, py) for px, py in line], w, h) for line, w, h in [
    ([(700, 520), (850, 560), (1000, 560), (1150, 540), (1300, 500)], 2.0, 360),     # Stormsong's southern mountains
    ([(640, 780), (760, 900), (800, 1080)], 2.0, 380),                                # Drustvar's peaks
    ([(1100, 1060), (1250, 1030)], 1.5, 260),                                         # Tiragarde's southern hills
]]
TOWNS += [('Brennadam',) + kt(1050, 300) + ('ntav',)]
CAMPS += [(name,) + kt(px, py) + (strength,) for name, px, py, strength in [
    ('Shrine of the Storm', 1360, 280, 1), ('Waycrest Manor', 600, 690, 1),
]]
ROADS += [[kt(px, py) for px, py in line] for line in [
    [(1160, 720), (1200, 600), (1050, 300), (1360, 280)],          # Boralus north through Stormsong to the Shrine
    [(1160, 720), (1260, 880), (1240, 1080)],                       # Boralus south through Tiragarde
    [(1160, 720), (1180, 620), (950, 610), (850, 700), (720, 900)], # Boralus west round the harbour into Drustvar
]]

# ---------------------------------------------------------------------------
# Coasts. Shores are cliffs, as on the classic hand-made Azeroth maps; beaches
# (land sloping into shallow water) are kept where units must reach the water:
# along the wading straits and rivers, at every shipyard, all round the small
# islands, and at the spots listed in BEACHES (x, y, radius).
# ---------------------------------------------------------------------------
BEACH_ISLANDS = {'Kezan', 'Tol Barad', 'Azuremyst Isle', 'Bloodmyst Isle', 'Gilneas Isle North', 'Gilneas Isle South',
                 'Echo Isles', 'Theramore Isle', 'Alcaz Island'}
BEACHES = []

# ---------------------------------------------------------------------------
# Instances: dungeons and raids as walled, cliff-edged islands in the corners
# of the Great Sea, each reached through a waygate from its entrance on the
# continents (the camp or town named here). Inside: a pillared hall, a guard
# camp halfway and the boss on a raised dais at the far end. Tile coordinates.
# (name, (x0, y0, x1, y1), biome, entrance camp/town, side of the waygate)
# ---------------------------------------------------------------------------
INSTANCES = [
    # north-west of Kalimdor: Kalimdor's dungeons and raids, and Azjol-Nerub
    ("Onyxia's Lair", (12, 444, 34, 466), 'lava', "Onyxia's Lair", 'S'),
    ("Temple of Ahn'Qiraj", (42, 440, 72, 466), 'temple', "Ahn'Qiraj", 'S'),
    ('Caverns of Time', (80, 444, 104, 466), 'temple', 'Tanaris Caverns of Time', 'W'),
    ('Wailing Caverns', (12, 404, 34, 430), 'grotto', 'The Crossroads Oasis', 'E'),
    ('Maraudon', (42, 406, 66, 430), 'grotto', 'Maraudon', 'S'),
    ('Dire Maul', (74, 404, 96, 430), 'halls', 'Dire Maul', 'N'),
    ('Azjol-Nerub', (104, 404, 126, 428), 'frozen', 'Azjol-Nerub', 'E'),
    ("Zul'Farrak", (12, 362, 36, 386), 'temple', "Zul'Farrak", 'N'),
    ('Blackfathom Deeps', (44, 362, 68, 386), 'grotto', 'Blackfathom Deeps', 'W'),
    ('Razorfen Downs', (76, 364, 98, 386), 'grotto', 'Razorfen Kraul', 'E'),
    # north-east, beyond Quel'Danas: Lordaeron's and Northrend's
    ('Naxxramas', (388, 440, 414, 466), 'crypt', 'Naxxramas', 'S'),
    ('Ulduar', (422, 440, 450, 466), 'halls', 'Ulduar', 'W'),
    ('Icecrown Citadel', (388, 402, 412, 430), 'frozen', "Aldur'thar", 'W'),
    ('Stratholme', (420, 402, 444, 430), 'crypt', 'Stratholme', 'S'),
    ("Zul'Aman", (452, 400, 468, 432), 'troll', "Zul'Aman", 'S'),
    # south, between the continents: the southern Eastern Kingdoms and Uldum
    ('Molten Core', (208, 110, 236, 136), 'lava', 'Blackrock Spire', 'N'),
    ('Karazhan', (246, 112, 270, 138), 'halls', 'Karazhan', 'N'),
    ("Zul'Gurub", (282, 108, 308, 134), 'troll', "Zul'Gurub", 'E'),
    ('The Deadmines', (210, 66, 234, 90), 'halls', 'Moonbrook', 'E'),
    ('Sunken Temple', (246, 62, 272, 90), 'grotto', 'Stonard', 'N'),
    ('Uldaman', (284, 64, 308, 88), 'halls', 'Uldaman', 'E'),
    ('Halls of Origination', (212, 16, 238, 42), 'temple', "Lost City of the Tol'vir", 'W'),
    ('Gnomeregan', (250, 16, 272, 40), 'halls', 'Gnomeregan', 'N'),
    ('Scholomance', (284, 16, 308, 40), 'crypt', 'Andorhal', 'E'),
]

# Raised rectangles (x0, y0, x1, y1, extra cliff levels): the instances' pillars.
BLOCKS = []
# Creep camps without a gold mine: (name, x, y, strength); strength 3 is a raid boss.
DUNGEON_CAMPS = []
INSTANCE_NAMES = set()


def _instance_layout(name, box, side):
    """Outline, waygate, guard and boss positions, raised blocks and corridor of an instance.

    Laid out along the hall: `a` runs from the waygate end (0) to the far end (L),
    `c` across it. The two corners beside the waygate are cut away into a
    vestibule, pillars line the hall and the boss waits on a raised dais at
    the far end, reached by a ramp where the corridor climbs onto it.
    """
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    along_x = side in 'WE'
    L = (x1 - x0) if along_x else (y1 - y0)
    W = (y1 - y0) if along_x else (x1 - x0)

    def world(a, c):
        return {'W': (x0 + a, cy + c), 'E': (x1 - a, cy + c), 'S': (cx + c, y0 + a), 'N': (cx + c, y1 - a)}[side]

    def rect(a0, a1, c0, c1, lv):
        (ax, ay), (bx, by) = world(a0, c0), world(a1, c1)
        return (min(ax, bx), min(ay, by), max(ax, bx), max(ay, by), lv)

    h = sum(map(ord, name))
    na, nl = 4 + h % 3, 5 + (h // 3) % 3                         # vestibule notch: across, along
    outline = [world(a, c) for a, c in [(0, -W / 2 + na), (0, W / 2 - na), (nl, W / 2 - na), (nl, W / 2), (L, W / 2),
                                        (L, -W / 2), (nl, -W / 2), (nl, -W / 2 + na)]]
    gate, mid, boss = world(4.5, 0), world(L * 0.45, 0), world(L - 5, 0)
    blocks = [rect(L - 9, L - 1, -W / 2 + 3, W / 2 - 3, 1)]       # the boss's dais
    a = nl + 5
    while a <= L - 15:
        for c in (-(W / 2 - 4), W / 2 - 4):
            blocks.append(rect(a - 1, a + 1, c - 1, c + 1, 1))
        a += 5
    return outline, gate, mid, boss, blocks, [gate, boss]


def _find_site(ref):
    for n, x, y, _ in CAMPS + TOWNS:
        if n == ref:
            return x, y
    raise KeyError(ref)


for _name, _box, _biome, _ref, _side in INSTANCES:
    _x0, _y0, _x1, _y1 = _box
    _outline, _gate, _mid, _boss, _blocks, _corridor = _instance_layout(_name, _box, _side)
    LANDMASSES[_name] = _outline
    COAST_NOISE[_name] = 0.0
    INSTANCE_NAMES.add(_name)
    zone(_name, _name, (_x0 + _x1) / 2.0, (_y0 + _y1) / 2.0, (_x1 - _x0) / 2.0, (_y1 - _y0) / 2.0, _biome, instance=True)
    BLOCKS += _blocks
    ROADS.append(_corridor)
    PORTALS.append(((_name + ' Entrance',) + _find_site(_ref), (_name + ' Portal',) + _gate))
    DUNGEON_CAMPS += [(_name + ' Guards', _mid[0], _mid[1], 2), (_name, _boss[0], _boss[1], 3)]
