"""Terrain recipes per biome: ground tiles, trees, relief and wildlife."""

# The 16 ground tiles the map uses (order = draw order, later tiles overlay earlier ones).
GROUND_TILES = ['Ldrt', 'Ldro', 'Bdrt', 'Bdsr', 'Ybtl', 'Dlvc', 'Lrok', 'Bgrr',
                'Lgrs', 'Fgrs', 'Agrs', 'Zgrs', 'Lgrd', 'Wsng', 'Wsnw', 'Wrok']
TILE = {t: i for i, t in enumerate(GROUND_TILES)}

# Cliff types (Lordaeron dirt, Lordaeron Winter snow, Lordaeron grass); their ground tiles
# (Ldrt, Wsnw, Lgrs) are in GROUND_TILES as the game requires.
CLIFF_TILES = ['CLdi', 'CWsn', 'CLgr']
CLIFF_DIRT, CLIFF_SNOW, CLIFF_GRASS = 0, 1, 2

# Each biome:
#   tiles    - [(tile, noise threshold)] painted in order; a tile wins where noise > threshold
#   beach    - tile used on shores, seabed - tile visible under shallow water
#   rock     - tile on steep slopes, peak - tile on high ground (None = rock)
#   trees    - [(destructable id, weight)] species mix of the woods; each species gathers in its own
#              stands, so a wood shifts from one kind of tree to another instead of being uniform
#   density  - 0..1 share of the land under forest, clump - forest patch size (tiles)
#   floor    - ground tile under the woods (None keeps the zone's own)
#   base     - ground height above sea, hills - hill amplitude, mountains - ridge amplitude
#   critters - neutral wildlife ids
#   cold / blight / mm - snow on peaks, blighted ground, minimap tint (r, g, b)
#   cliff    - cliff type (index into CLIFF_TILES)
B = {}


def biome(name, **kw):
    kw.setdefault('beach', 'Bdsr')
    kw.setdefault('seabed', 'Bdsr')
    kw.setdefault('rock', 'Lrok')
    kw.setdefault('peak', None)
    kw.setdefault('trees', [])
    kw.setdefault('floor', None)
    kw.setdefault('density', 0.0)
    kw.setdefault('clump', 14)
    kw.setdefault('base', 40)
    kw.setdefault('hills', 60)
    kw.setdefault('mountains', 0)
    kw.setdefault('cold', False)
    kw.setdefault('blight', False)
    kw.setdefault('cliff', CLIFF_DIRT)
    kw.setdefault('critters', [])
    B[name] = kw


biome('temperate', floor='Lgrd', cliff=CLIFF_GRASS, tiles=[('Lgrs', -2), ('Lgrd', 0.25), ('Ldrt', 0.55)], trees=[('LTlt', 50), ('FTtw', 12), ('WTtw', 12), ('JTtw', 8), ('YTct', 10), ('YTft', 8)], density=0.46,
      hills=70,
      critters=['nder', 'nshe', 'necr'], mm=(78, 120, 52))
biome('darkforest', cliff=CLIFF_GRASS, tiles=[('Lgrd', -2), ('Ldrt', 0.45), ('Lgrs', 0.6)], trees=[('JTtw', 36), ('LTlt', 22), ('WTtw', 22), ('NTtw', 12), ('GTsh', 8)], density=0.70, clump=18,
      hills=80,
      critters=['nder', 'nrat'], mm=(46, 82, 40))
biome('autumn', floor='Ldrt', tiles=[('Fgrs', -2), ('Lgrd', 0.35), ('Ldrt', 0.55)], trees=[('FTtw', 50), ('LTlt', 18), ('YTft', 14), ('JTtw', 10), ('WTtw', 8)], density=0.52,
      hills=70,
      critters=['nder', 'necr'], mm=(150, 118, 50))
biome('farmland', cliff=CLIFF_GRASS, tiles=[('Lgrs', -2), ('Bgrr', 0.0), ('Ldrt', 0.5)], trees=[('LTlt', 36), ('YTct', 24), ('FTtw', 16), ('YTft', 14), ('BTtw', 10)], density=0.14, clump=8,
      hills=40,
      critters=['nshe', 'npig', 'nech'], mm=(128, 140, 66))
biome('highland', floor='Lgrd', cliff=CLIFF_GRASS, tiles=[('Lgrs', -2), ('Lrok', 0.45), ('Ldrt', 0.3)], trees=[('LTlt', 36), ('NTtw', 26), ('WTtw', 20), ('FTtw', 10), ('JTtw', 8)], density=0.32,
      hills=150, mountains=170,
      critters=['nder', 'nrac'], mm=(88, 116, 64))
biome('nightelf', floor='Lgrd', cliff=CLIFF_GRASS, tiles=[('Agrs', -2), ('Lgrd', 0.3), ('Ldrt', 0.6)], trees=[('ATtr', 52), ('ATtc', 22), ('LTlt', 10), ('WTtw', 8), ('JTtw', 8)], density=0.62, clump=16,
      hills=70,
      critters=['nder', 'nrac', 'nsno'], mm=(54, 92, 98))
biome('fel', tiles=[('Lgrd', -2), ('Fgrs', 0.25), ('Ldro', 0.55)], trees=[('CTtr', 50), ('CTtc', 24), ('JTtw', 18), ('GTsh', 8)], density=0.50,
      hills=70,
      critters=['nfbr', 'nrat'], mm=(86, 98, 44))
biome('plague', tiles=[('Ldrt', -2), ('Ldro', 0.0), ('Lgrd', 0.55)], trees=[('JTtw', 34), ('CTtr', 30), ('WTtw', 18), ('CTtc', 10), ('GTsh', 8)], density=0.20, clump=10,
      hills=60, blight=True,
      critters=['nrat'], mm=(92, 84, 70))
biome('savanna', tiles=[('Bdrt', -2), ('Bgrr', 0.05), ('Ldrt', 0.55)], trees=[('BTtw', 68), ('BTtc', 32)], density=0.08, clump=6,
      hills=40,
      critters=['nvul', 'nskk'], mm=(158, 136, 72))
biome('plains', cliff=CLIFF_GRASS, tiles=[('Lgrs', -2), ('Bgrr', 0.3), ('Ldrt', 0.65)], trees=[('BTtw', 40), ('BTtc', 20), ('LTlt', 24), ('FTtw', 16)], density=0.10, clump=8,
      hills=50,
      critters=['nder', 'necr'], mm=(110, 140, 64))
biome('reddesert', tiles=[('Bdrt', -2), ('Ldrt', 0.3), ('Lrok', 0.55)], trees=[('BTtw', 66), ('BTtc', 22), ('CTtr', 12)], density=0.04, clump=5,
      hills=90,
      critters=['nskk', 'nvul'], mm=(150, 88, 60))
biome('barren', tiles=[('Ldrt', -2), ('Bdrt', 0.2), ('Lrok', 0.5)], trees=[('CTtr', 40), ('BTtw', 36), ('JTtw', 24)], density=0.05, clump=5,
      hills=80,
      critters=['nvul'], mm=(120, 104, 84))
biome('desert', tiles=[('Bdsr', -2), ('Bdrt', 0.4), ('Ldrt', 0.65)], trees=[('BTtw', 60), ('ZTtw', 40)], density=0.02, clump=4,
      hills=70,
      critters=['ndwm', 'nskk', 'nvul'], mm=(200, 170, 106))
biome('jungle', floor='Lgrd', cliff=CLIFF_GRASS, tiles=[('Zgrs', -2), ('Lgrd', 0.25), ('Ldrt', 0.6)], trees=[('ZTtw', 52), ('ZTtc', 26), ('LTlt', 10), ('KTtw', 3), ('DTsh', 3)], density=0.66, clump=16,
      hills=90,
      critters=['nfro', 'nskk', 'nrac'], mm=(60, 112, 44))
biome('swamp', cliff=CLIFF_GRASS, tiles=[('Lgrd', -2), ('Zgrs', 0.15), ('Ldrt', 0.5)], trees=[('ZTtw', 30), ('JTtw', 26), ('ZTtc', 16), ('CTtc', 10), ('GTsh', 6), ('KTtw', 4)], density=0.40, clump=10,
      hills=25, seabed='Ldrt',
      critters=['nfro', 'nskk'], mm=(56, 84, 50))
biome('volcanic', tiles=[('Bdrt', -2), ('Dlvc', 0.05), ('Lrok', 0.5)], trees=[('CTtr', 56), ('JTtw', 28), ('CTtc', 16)], density=0.03, clump=4,
      hills=100,
      critters=['nskk'], mm=(110, 58, 40))
biome('snow', tiles=[('Wsnw', -2), ('Wsng', 0.08), ('Wrok', 0.55)], rock='Wrok', trees=[('WTst', 44), ('NTtw', 30), ('WTtw', 18), ('YTst', 8)], density=0.30, clump=10,
      hills=110, mountains=240, cold=True, beach='Wsnw', seabed='Ldrt', cliff=1,
      critters=['npng', 'nsea', 'nsno'], mm=(214, 222, 232))
biome('tundra', tiles=[('Wsng', -2), ('Wsnw', 0.2), ('Wrok', 0.55)], rock='Wrok', trees=[('NTtw', 48), ('WTst', 24), ('NTtc', 16), ('WTtw', 12)], density=0.16, clump=8,
      hills=60, cold=True, beach='Wsnw', seabed='Ldrt', cliff=1,
      critters=['nsea', 'npng'], mm=(170, 178, 160))
biome('icecrown', tiles=[('Wsnw', -2), ('Wrok', 0.5)], rock='Wrok', trees=[('ITtw', 52), ('ITtc', 26), ('WTst', 22)], density=0.10, clump=6,
      hills=110, mountains=260, cold=True, beach='Wsnw', seabed='Ldrt', cliff=1,
      critters=['npng'], mm=(170, 184, 206))
biome('needles', tiles=[('Bdrt', -2), ('Ldrt', 0.2), ('Bdsr', 0.6)], trees=[('BTtw', 60), ('BTtc', 20), ('ZTtw', 20)], density=0.03, clump=4,
      hills=30,
      critters=['nvul'], mm=(176, 120, 80))
biome('rocky', tiles=[('Lrok', -2), ('Ldrt', 0.1)], hills=110, mountains=200,
      critters=['nalb'], mm=(112, 104, 96))
biome('fjord', floor='Lgrd', cliff=CLIFF_GRASS, tiles=[('Lgrs', -2), ('Fgrs', 0.25), ('Lrok', 0.6)], trees=[('NTtw', 42), ('LTlt', 20), ('NTtc', 16), ('WTtw', 14), ('FTtw', 8)], density=0.38, clump=12,
      hills=140, mountains=150, cold=True, beach='Ldrt', seabed='Ldrt',
      critters=['nsea', 'nder'], mm=(90, 122, 76))
biome('grizzly', floor='Lgrd', cliff=CLIFF_GRASS, tiles=[('Lgrs', -2), ('Lgrd', 0.0), ('Ldrt', 0.6)], trees=[('NTtw', 46), ('WTtw', 20), ('LTlt', 16), ('NTtc', 12), ('FTtw', 6)], density=0.62, clump=16,
      hills=90, cold=True, beach='Ldrt', seabed='Ldrt',
      critters=['nder', 'nrac'], mm=(58, 96, 52))
biome('crystal', tiles=[('Agrs', -2), ('Wsnw', 0.25), ('Lgrd', 0.55)], rock='Wrok', trees=[('ATtr', 42), ('ITtw', 30), ('ATtc', 16), ('ITtc', 12)], density=0.50, clump=14,
      hills=60, cold=True, beach='Wsnw', seabed='Ldrt',
      critters=['nsno'], mm=(110, 140, 170))
biome('amber', tiles=[('Bdsr', -2), ('Ldro', 0.15), ('Bdrt', 0.5)], trees=[('CTtr', 48), ('BTtw', 32), ('ZTtw', 20)], density=0.07, clump=6,
      hills=90,
      critters=['nskk'], mm=(170, 150, 70))
biome('worldtree', floor='Lgrd', cliff=CLIFF_GRASS, tiles=[('Agrs', -2), ('Lgrd', 0.2), ('Lgrs', 0.55)], trees=[('ATtr', 50), ('ATtc', 30), ('LTlt', 10), ('WTtw', 10)], density=0.66, clump=18,
      hills=90,
      critters=['nder', 'nsno'], mm=(70, 110, 96))

# Instances: flat, treeless floors of worked stone (Ybtl is the Cityscape brick).
_HALL = dict(hills=10, base=40, beach='Ldrt', seabed='Ldrt')
biome('lava', tiles=[('Dlvc', -2), ('Lrok', 0.25), ('Ybtl', 0.6)], **_HALL, mm=(120, 50, 30))
biome('temple', tiles=[('Bdsr', -2), ('Ybtl', 0.15), ('Bdrt', 0.6)], **_HALL, mm=(196, 168, 110))
biome('halls', tiles=[('Ybtl', -2), ('Lrok', 0.3), ('Ldrt', 0.62)], **_HALL, mm=(120, 110, 104))
biome('crypt', tiles=[('Ybtl', -2), ('Ldro', 0.3), ('Ldrt', 0.6)], **_HALL, blight=True, mm=(96, 96, 80))
biome('frozen', tiles=[('Wsnw', -2), ('Ybtl', 0.2), ('Wrok', 0.6)], **_HALL, cold=True, cliff=CLIFF_SNOW, mm=(170, 190, 214))
biome('grotto', tiles=[('Lgrd', -2), ('Ldro', 0.25), ('Lrok', 0.55)], **_HALL, trees=[('ZTtw', 40), ('GTsh', 30), ('DTsh', 20), ('KTtw', 10)], density=0.12, clump=6, cliff=CLIFF_GRASS, mm=(60, 92, 50))
biome('troll', tiles=[('Zgrs', -2), ('Ybtl', 0.2), ('Ldrt', 0.6)], **_HALL, trees=[('ZTtw', 60), ('ZTtc', 30), ('DTsh', 10)], density=0.15, clump=6, cliff=CLIFF_GRASS, mm=(64, 116, 50))
