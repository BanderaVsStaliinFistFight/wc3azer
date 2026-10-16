"""Terrain recipes per biome: ground tiles, trees, relief and wildlife."""

# The 16 ground tiles the map uses (order = draw order, later tiles overlay earlier ones).
GROUND_TILES = ['Ldrt', 'Ldro', 'Bdrt', 'Bdsr', 'Vcbp', 'Ybtl', 'Dlvc', 'Lrok',
                'Ldrg', 'Fgrs', 'Lgrs', 'Lgrd', 'Vgrt', 'Wsng', 'Wsnw', 'Wrok']
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
#   road     - the roads' surface: cobbles in the old human lands, earth elsewhere
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
    kw.setdefault('road', 'Ldrt')
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


biome('temperate', floor='Vgrt', cliff=CLIFF_GRASS, road='Vcbp', tiles=[('Ldrg', -2), ('Vgrt', 0.25), ('Ldro', 0.55)], trees=[('LTlt', 26), ('VTlt', 18), ('FTtw', 12), ('WTtw', 10), ('YTct', 10), ('JTtw', 8), ('YTft', 8), ('JTct', 8)], density=0.46,
      hills=70,
      critters=['nder', 'nshe', 'necr'], mm=(78, 120, 52))
biome('darkforest', floor='Vgrt', cliff=CLIFF_GRASS, road='Vcbp', tiles=[('Ldrg', -2), ('Vgrt', 0.2), ('Ldro', 0.45)], trees=[('JTtw', 26), ('LTlt', 16), ('WTtw', 16), ('NTtw', 12), ('VTlt', 10), ('JTct', 8), ('GTsh', 6), ('CTtc', 6)], density=0.70, clump=18,
      hills=80,
      critters=['nder', 'nrat'], mm=(46, 82, 40))
biome('autumn', floor='Ldrt', road='Vcbp', tiles=[('Fgrs', -2), ('Lgrd', 0.35), ('Ldrt', 0.55)], trees=[('FTtw', 32), ('YTft', 14), ('LTlt', 12), ('VTlt', 10), ('JTtw', 10), ('WTtw', 8), ('JTct', 8), ('YTct', 6)], density=0.52,
      hills=70,
      critters=['nder', 'necr'], mm=(150, 118, 50))
biome('farmland', cliff=CLIFF_GRASS, road='Vcbp', tiles=[('Lgrs', -2), ('Ldrg', 0.0), ('Ldrt', 0.5)], trees=[('LTlt', 26), ('YTct', 18), ('VTlt', 16), ('FTtw', 12), ('YTft', 12), ('BTtw', 8), ('JTct', 8)], density=0.14, clump=8,
      hills=40,
      critters=['nshe', 'npig', 'nech'], mm=(128, 140, 66))
biome('highland', floor='Lgrd', cliff=CLIFF_GRASS, road='Vcbp', tiles=[('Lgrs', -2), ('Vgrt', 0.25), ('Ldrg', 0.3)], trees=[('LTlt', 24), ('NTtw', 20), ('WTtw', 16), ('VTlt', 12), ('FTtw', 10), ('JTtw', 8), ('YTwt', 6), ('NTtc', 4)], density=0.32,
      hills=150, mountains=170,
      critters=['nder', 'nrac'], mm=(88, 116, 64))
biome('nightelf', floor='Lgrd', cliff=CLIFF_GRASS, tiles=[('Lgrd', -2), ('Vgrt', 0.15), ('Ldrt', 0.6)], trees=[('ATtr', 36), ('ATtc', 22), ('LTlt', 10), ('VTlt', 10), ('WTtw', 8), ('JTtw', 8), ('BTtc', 6)], density=0.62, clump=16,
      hills=70,
      critters=['nder', 'nrac', 'nsno'], mm=(54, 92, 98))
biome('fel', tiles=[('Lgrd', -2), ('Fgrs', 0.25), ('Ldro', 0.55)], trees=[('CTtr', 38), ('CTtc', 22), ('JTtw', 16), ('GTsh', 8), ('OTtw', 8), ('KTtw', 8)], density=0.50,
      hills=70,
      critters=['nfbr', 'nrat'], mm=(86, 98, 44))
biome('plague', road='Vcbp', tiles=[('Ldrt', -2), ('Ldro', 0.0), ('Lgrd', 0.55)], trees=[('JTtw', 28), ('CTtr', 24), ('WTtw', 14), ('CTtc', 10), ('GTsh', 8), ('YTwt', 8), ('JTct', 8)], density=0.20, clump=10,
      hills=60, blight=True,
      critters=['nrat'], mm=(92, 84, 70))
biome('savanna', tiles=[('Bdrt', -2), ('Fgrs', 0.05), ('Ldrt', 0.55)], trees=[('BTtw', 52), ('BTtc', 26), ('CTtr', 12), ('ZTtw', 10)], density=0.08, clump=6,
      hills=40,
      critters=['nvul', 'nskk'], mm=(158, 136, 72))
biome('plains', cliff=CLIFF_GRASS, tiles=[('Lgrs', -2), ('Ldrg', 0.3), ('Ldrt', 0.65)], trees=[('BTtw', 30), ('LTlt', 20), ('BTtc', 16), ('FTtw', 14), ('VTlt', 12), ('YTct', 8)], density=0.10, clump=8,
      hills=50,
      critters=['nder', 'necr'], mm=(110, 140, 64))
biome('reddesert', tiles=[('Bdrt', -2), ('Ldrt', 0.3), ('Lrok', 0.55)], trees=[('BTtw', 56), ('BTtc', 22), ('CTtr', 12), ('ZTtw', 10)], density=0.04, clump=5,
      hills=90,
      critters=['nskk', 'nvul'], mm=(150, 88, 60))
biome('barren', tiles=[('Ldrt', -2), ('Bdrt', 0.2), ('Lrok', 0.5)], trees=[('CTtr', 34), ('BTtw', 30), ('JTtw', 20), ('YTwt', 8), ('OTtw', 8)], density=0.05, clump=5,
      hills=80,
      critters=['nvul'], mm=(120, 104, 84))
biome('desert', tiles=[('Bdsr', -2), ('Bdrt', 0.4), ('Ldrt', 0.65)], trees=[('BTtw', 50), ('ZTtw', 36), ('BTtc', 14)], density=0.02, clump=4,
      hills=70,
      critters=['ndwm', 'nskk', 'nvul'], mm=(200, 170, 106))
biome('jungle', floor='Lgrd', cliff=CLIFF_GRASS, tiles=[('Vgrt', -2), ('Lgrd', 0.25), ('Ldrt', 0.6)], trees=[('ZTtw', 40), ('ZTtc', 22), ('LTlt', 10), ('VTlt', 8), ('ATtc', 8), ('KTtw', 4), ('OTtw', 4), ('DTsh', 4)], density=0.66, clump=16,
      hills=90,
      critters=['nfro', 'nskk', 'nrac'], mm=(60, 112, 44))
biome('swamp', cliff=CLIFF_GRASS, tiles=[('Lgrd', -2), ('Vgrt', 0.15), ('Ldrt', 0.5)], trees=[('ZTtw', 24), ('JTtw', 20), ('ZTtc', 14), ('CTtc', 10), ('GTsh', 8), ('KTtw', 6), ('OTtw', 6), ('JTct', 6), ('VTlt', 6)], density=0.40, clump=10,
      hills=25, seabed='Ldrt',
      critters=['nfro', 'nskk'], mm=(56, 84, 50))
biome('volcanic', tiles=[('Bdrt', -2), ('Dlvc', 0.05), ('Lrok', 0.5)], trees=[('CTtr', 50), ('JTtw', 26), ('CTtc', 14), ('OTtw', 10)], density=0.03, clump=4,
      hills=100,
      critters=['nskk'], mm=(110, 58, 40))
biome('snow', tiles=[('Wsnw', -2), ('Wsng', 0.08), ('Wrok', 0.55)], rock='Wrok', trees=[('WTst', 34), ('NTtw', 26), ('WTtw', 14), ('YTst', 10), ('YTwt', 10), ('NTtc', 6)], density=0.30, clump=10,
      hills=110, mountains=240, cold=True, beach='Wsnw', seabed='Ldrt', cliff=1,
      critters=['npng', 'nsea', 'nsno'], mm=(214, 222, 232))
biome('tundra', tiles=[('Wsng', -2), ('Wsnw', 0.2), ('Wrok', 0.55)], rock='Wrok', trees=[('NTtw', 38), ('WTst', 20), ('NTtc', 14), ('WTtw', 10), ('YTwt', 10), ('YTst', 8)], density=0.16, clump=8,
      hills=60, cold=True, beach='Wsnw', seabed='Ldrt', cliff=1,
      critters=['nsea', 'npng'], mm=(170, 178, 160))
biome('icecrown', tiles=[('Wsnw', -2), ('Wrok', 0.5)], rock='Wrok', trees=[('ITtw', 46), ('ITtc', 24), ('WTst', 18), ('YTst', 12)], density=0.10, clump=6,
      hills=110, mountains=260, cold=True, beach='Wsnw', seabed='Ldrt', cliff=1,
      critters=['npng'], mm=(170, 184, 206))
biome('needles', tiles=[('Bdrt', -2), ('Ldrt', 0.2), ('Bdsr', 0.6)], trees=[('BTtw', 50), ('BTtc', 20), ('ZTtw', 18), ('CTtr', 12)], density=0.03, clump=4,
      hills=30,
      critters=['nvul'], mm=(176, 120, 80))
biome('rocky', tiles=[('Lrok', -2), ('Ldrt', 0.1)], hills=110, mountains=200,
      critters=['nalb'], mm=(112, 104, 96))
biome('fjord', floor='Vgrt', cliff=CLIFF_GRASS, road='Vcbp', tiles=[('Ldrg', -2), ('Vgrt', 0.15), ('Lrok', 0.6)], trees=[('NTtw', 32), ('LTlt', 16), ('NTtc', 14), ('WTtw', 12), ('VTlt', 10), ('FTtw', 8), ('YTwt', 8)], density=0.38, clump=12,
      hills=140, mountains=150, cold=True, beach='Ldrt', seabed='Ldrt',
      critters=['nsea', 'nder'], mm=(90, 122, 76))
biome('grizzly', floor='Lgrd', cliff=CLIFF_GRASS, tiles=[('Lgrs', -2), ('Vgrt', 0.1), ('Ldrg', 0.45)], trees=[('NTtw', 34), ('WTtw', 16), ('LTlt', 14), ('NTtc', 12), ('VTlt', 10), ('FTtw', 8), ('YTwt', 6)], density=0.62, clump=16,
      hills=90, cold=True, beach='Ldrt', seabed='Ldrt',
      critters=['nder', 'nrac'], mm=(58, 96, 52))
biome('crystal', tiles=[('Lgrd', -2), ('Wsnw', 0.25), ('Vgrt', 0.55)], rock='Wrok', trees=[('ATtr', 34), ('ITtw', 26), ('ATtc', 16), ('ITtc', 12), ('YTst', 12)], density=0.50, clump=14,
      hills=60, cold=True, beach='Wsnw', seabed='Ldrt',
      critters=['nsno'], mm=(110, 140, 170))
biome('amber', tiles=[('Bdsr', -2), ('Ldro', 0.15), ('Bdrt', 0.5)], trees=[('CTtr', 40), ('BTtw', 30), ('ZTtw', 18), ('BTtc', 12)], density=0.07, clump=6,
      hills=90,
      critters=['nskk'], mm=(170, 150, 70))
biome('worldtree', floor='Lgrd', cliff=CLIFF_GRASS, tiles=[('Lgrd', -2), ('Vgrt', 0.1), ('Lgrs', 0.55)], trees=[('ATtr', 40), ('ATtc', 26), ('LTlt', 10), ('VTlt', 10), ('WTtw', 8), ('CTtc', 6)], density=0.66, clump=18,
      hills=90,
      critters=['nder', 'nsno'], mm=(70, 110, 96))
