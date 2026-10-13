"""Terrain recipes per biome: ground tiles, trees, relief and creeps."""

# The 16 ground tiles the map uses (order = draw order, later tiles overlay earlier ones).
GROUND_TILES = ['Ldrt', 'Bdrt', 'Bdsr', 'Ybtl', 'Dlvc', 'Lrok', 'Bgrr', 'Lgrs',
                'Fgrs', 'Agrs', 'Zgrs', 'Lgrd', 'Cpos', 'Wsng', 'Nsnw', 'Nice']
TILE = {t: i for i, t in enumerate(GROUND_TILES)}

# Cliff types; their ground tiles (Ldrt, Nsnw, Lgrs) are in GROUND_TILES as the game requires.
CLIFF_TILES = ['CLdi', 'CNsn', 'CLgr']
CLIFF_DIRT, CLIFF_SNOW, CLIFF_GRASS = 0, 1, 2

# Each biome:
#   tiles    - [(tile, noise threshold)] painted in order; a tile wins where noise > threshold
#   beach    - tile used on shores, seabed - tile visible under shallow water
#   rock     - tile on steep slopes, peak - tile on high ground (None = rock)
#   tree     - destructable id, density 0..1 of forest cover, clump - forest patch size (tiles)
#   floor    - ground tile under the woods (None keeps the zone's own)
#   tree2    - (destructable id, share) of a second species mixed into the woods
#   base     - ground height above sea, hills - hill amplitude, mountains - ridge amplitude
#   creeps   - (low, mid, high) creep unit ids used for camps in this biome
#   cold / blight / mm - snow on peaks, blighted ground, minimap tint (r, g, b)
#   cliff    - cliff type (index into CLIFF_TILES)
B = {}


def biome(name, **kw):
    kw.setdefault('beach', 'Bdsr')
    kw.setdefault('seabed', 'Bdsr')
    kw.setdefault('rock', 'Lrok')
    kw.setdefault('peak', None)
    kw.setdefault('tree', None)
    kw.setdefault('floor', None)
    kw.setdefault('tree2', None)
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


biome('temperate', tree2=('FTtw', 0.08), floor='Lgrd', cliff=CLIFF_GRASS, tiles=[('Lgrs', -2), ('Lgrd', 0.25), ('Ldrt', 0.55)], tree='LTlt', density=0.46,
      hills=70, creeps=(['ngno', 'nkob', 'nmrl', 'nwlt'], ['ngnb', 'nkog', 'nmrr', 'nfsp'], ['ngnv', 'nkol', 'nogm', 'nwld']),
      critters=['nder', 'nshe', 'necr'], mm=(78, 120, 52))
biome('darkforest', cliff=CLIFF_GRASS, tiles=[('Lgrd', -2), ('Ldrt', 0.45), ('Lgrs', 0.6)], tree='LTlt', density=0.70, clump=18,
      hills=80, creeps=(['nwlt', 'nspb', 'ngh1', 'nske'], ['nwlg', 'nspg', 'nskg', 'ngh1'], ['nwld', 'ngh2', 'nsgt', 'nskm']),
      critters=['nder', 'nrat'], mm=(46, 82, 40))
biome('autumn', tree2=('LTlt', 0.25), floor='Ldrt', tiles=[('Fgrs', -2), ('Lgrd', 0.35), ('Ldrt', 0.55)], tree='FTtw', density=0.52,
      hills=70, creeps=(['ngno', 'nkob', 'nmrl', 'nspr'], ['ngnb', 'nftr', 'nmrr', 'nspg'], ['ngnv', 'nftk', 'nmrm', 'nfsh']),
      critters=['nder', 'necr'], mm=(150, 118, 50))
biome('farmland', cliff=CLIFF_GRASS, tiles=[('Lgrs', -2), ('Bgrr', 0.0), ('Ldrt', 0.5)], tree='LTlt', density=0.14, clump=8,
      hills=40, creeps=(['ngna', 'nban', 'nmrl', 'nkob'], ['ngnb', 'nbrg', 'nmrr', 'nrog'], ['ngnv', 'nass', 'nenf', 'nbld']),
      critters=['nshe', 'npig', 'nech'], mm=(128, 140, 66))
biome('highland', floor='Lgrd', cliff=CLIFF_GRASS, tiles=[('Lgrs', -2), ('Lrok', 0.45), ('Ldrt', 0.3)], tree='LTlt', density=0.32,
      hills=150, mountains=170, creeps=(['nftr', 'nogr', 'nwlt', 'nhar'], ['nftb', 'nogm', 'nwlg', 'nhrr'], ['nftk', 'nogl', 'nwld', 'nhrq']),
      critters=['nder', 'nrac'], mm=(88, 116, 64))
biome('nightelf', tree2=('ATtc', 0.06), floor='Lgrd', cliff=CLIFF_GRASS, tiles=[('Agrs', -2), ('Lgrd', 0.3), ('Ldrt', 0.6)], tree='ATtr', density=0.62, clump=16,
      hills=70, creeps=(['nfrl', 'nsat', 'nwlt', 'nspg'], ['nfrs', 'nsty', 'nwlg', 'nenp'], ['nfrg', 'nsts', 'nfre', 'nstl']),
      critters=['nder', 'nrac', 'nsno'], mm=(54, 92, 98))
biome('fel', tree2=('CTtc', 0.05), tiles=[('Cpos', -2), ('Lgrd', 0.2), ('Ldrt', 0.5)], tree='CTtr', density=0.50,
      hills=70, creeps=(['nsat', 'nenc', 'nspb', 'nslm'], ['nsts', 'nenp', 'nslf', 'nfgu'], ['nstl', 'nepl', 'nsln', 'npfm']),
      critters=['nfbr', 'nrat'], mm=(86, 98, 44))
biome('plague', tiles=[('Ldrt', -2), ('Cpos', 0.0), ('Lgrd', 0.55)], tree='CTtr', density=0.20, clump=10,
      hills=60, blight=True, creeps=(['nzom', 'nske', 'ngh1', 'nska'], ['nskg', 'nskm', 'nslf', 'nfgb'], ['nsoc', 'ngh2', 'nfgl', 'nsln']),
      critters=['nrat'], mm=(92, 84, 70))
biome('savanna', tiles=[('Bdrt', -2), ('Bgrr', 0.05), ('Ldrt', 0.55)], tree='BTtw', density=0.08, clump=6,
      hills=40, creeps=(['nrzt', 'ncea', 'nhar', 'nrzs'], ['nrzb', 'ncer', 'nhrr', 'nqbh'], ['nrzm', 'ncen', 'nhrw', 'nrzg']),
      critters=['nvul', 'nskk'], mm=(158, 136, 72))
biome('plains', cliff=CLIFF_GRASS, tiles=[('Lgrs', -2), ('Bgrr', 0.3), ('Ldrt', 0.65)], tree='BTtw', density=0.10, clump=8,
      hills=50, creeps=(['nrzt', 'nqbh', 'nwlt', 'nhar'], ['nrzb', 'nwlg', 'ncer', 'nhrr'], ['nrzm', 'nwld', 'ncen', 'nhrw']),
      critters=['nder', 'necr'], mm=(110, 140, 64))
biome('reddesert', tiles=[('Bdrt', -2), ('Ldrt', 0.3), ('Lrok', 0.55)], tree='BTtw', density=0.04, clump=5,
      hills=90, creeps=(['nrzt', 'nhar', 'nsc2', 'nkob'], ['nrzb', 'nhrr', 'nsc3', 'nkog'], ['nrzg', 'nhrq', 'ntrg', 'nkol']),
      critters=['nskk', 'nvul'], mm=(150, 88, 60))
biome('barren', tiles=[('Ldrt', -2), ('Bdrt', 0.2), ('Lrok', 0.5)], tree='CTtr', density=0.05, clump=5,
      hills=80, creeps=(['ncea', 'nsat', 'nkob', 'nhar'], ['ncer', 'nsty', 'ngst', 'nhrr'], ['ncks', 'nsts', 'nggr', 'ncnk']),
      critters=['nvul'], mm=(120, 104, 84))
biome('desert', tiles=[('Bdsr', -2), ('Bdrt', 0.4), ('Ldrt', 0.65)], tree='BTtw', density=0.02, clump=4,
      hills=70, creeps=(['nscb', 'nanb', 'nsc2', 'nban'], ['nanw', 'nsc3', 'nbrg', 'nslh'], ['nano', 'nane', 'nslr', 'nbld']),
      critters=['ndwm', 'nskk', 'nvul'], mm=(200, 170, 106))
biome('jungle', tree2=('ZTtc', 0.07), floor='Lgrd', cliff=CLIFF_GRASS, tiles=[('Zgrs', -2), ('Lgrd', 0.25), ('Ldrt', 0.6)], tree='ZTtw', density=0.66, clump=16,
      hills=90, creeps=(['nftr', 'njg1', 'nmrl', 'nspg'], ['nfsp', 'njg1', 'nmrr', 'nftb'], ['nftk', 'njga', 'nmrm', 'nfsh']),
      critters=['nfro', 'nskk', 'nrac'], mm=(60, 112, 44))
biome('swamp', tree2=('ZTtc', 0.05), cliff=CLIFF_GRASS, tiles=[('Lgrd', -2), ('Zgrs', 0.15), ('Ldrt', 0.5)], tree='ZTtw', density=0.40, clump=10,
      hills=25, seabed='Ldrt', creeps=(['nmrl', 'nslm', 'nspb', 'nlpr'], ['nmrr', 'nslf', 'nltc', 'nhyh'], ['nmrm', 'nsln', 'nlds', 'nhyd']),
      critters=['nfro', 'nskk'], mm=(56, 84, 50))
biome('volcanic', tiles=[('Bdrt', -2), ('Dlvc', 0.05), ('Lrok', 0.5)], tree='CTtr', density=0.03, clump=4,
      hills=100, creeps=(['nrdk', 'nrvf', 'nkob', 'nfgu'], ['nrdk', 'nrvf', 'nkog', 'ninc'], ['nrdr', 'nrwm', 'ninf', 'nkol']),
      critters=['nskk'], mm=(110, 58, 40))
biome('snow', tree2=('NTtw', 0.3), tiles=[('Nsnw', -2), ('Wsng', 0.08), ('Lrok', 0.55)], tree='WTst', density=0.30, clump=10,
      hills=110, mountains=240, cold=True, beach='Nsnw', seabed='Ldrt', cliff=1,
      creeps=(['nitr', 'nwwf', 'nfpl', 'nkob'], ['nits', 'nwwg', 'nfps', 'nitp'], ['nitw', 'nwwd', 'nfpc', 'nith']),
      critters=['npng', 'nsea', 'nsno'], mm=(214, 222, 232))
biome('tundra', tiles=[('Wsng', -2), ('Nsnw', 0.2), ('Ldrt', 0.55)], tree='NTtw', density=0.16, clump=8,
      hills=60, cold=True, beach='Nsnw', seabed='Ldrt', cliff=1,
      creeps=(['ntkf', 'nwwf', 'nmam', 'nanb'], ['ntka', 'nwwg', 'nmit', 'ntkh'], ['ntkw', 'nmdr', 'ntks', 'ntkc']),
      critters=['nsea', 'npng'], mm=(170, 178, 160))
biome('icecrown', tiles=[('Nsnw', -2), ('Nice', 0.0), ('Lrok', 0.55)], tree='ITtw', density=0.10, clump=6,
      hills=110, mountains=260, cold=True, blight=True, beach='Nice', seabed='Nice', cliff=1,
      creeps=(['nske', 'nnwa', 'nska', 'nzom'], ['nnwl', 'nskg', 'nnws', 'nrvs'], ['nnwq', 'nsoc', 'nfgl', 'nrvi']),
      critters=['npng'], mm=(170, 184, 206))
biome('needles', tiles=[('Bdrt', -2), ('Ldrt', 0.2), ('Bdsr', 0.6)], tree='BTtw', density=0.03, clump=4,
      hills=30, creeps=(['ncea', 'nhar', 'nrzt', 'nkob'], ['ncer', 'nhrr', 'nrzb', 'nhrw'], ['ncen', 'nhrq', 'ncks', 'ncnk']),
      critters=['nvul'], mm=(176, 120, 80))
biome('rocky', tiles=[('Lrok', -2), ('Ldrt', 0.1)], hills=110, mountains=200, creeps=(['ngrk', 'nkob', 'nhar', 'nsc2'], ['ngst', 'nkog', 'nhrr', 'nsc3'], ['nggr', 'nkol', 'nhrq', 'nsgb']),
      critters=['nalb'], mm=(112, 104, 96))
biome('fjord', tree2=('LTlt', 0.2), floor='Lgrd', cliff=CLIFF_GRASS, tiles=[('Lgrs', -2), ('Fgrs', 0.25), ('Lrok', 0.6)], tree='NTtw', density=0.38, clump=12,
      hills=140, mountains=150, cold=True, beach='Ldrt', seabed='Ldrt', creeps=(['ntkf', 'nwlt', 'nmrl', 'nfrl'], ['ntka', 'nwlg', 'nmrr', 'nfrs'], ['ntkw', 'nwld', 'nmrm', 'nfrg']),
      critters=['nsea', 'nder'], mm=(90, 122, 76))
biome('grizzly', tree2=('LTlt', 0.15), floor='Lgrd', cliff=CLIFF_GRASS, tiles=[('Lgrs', -2), ('Lgrd', 0.0), ('Ldrt', 0.6)], tree='NTtw', density=0.62, clump=16,
      hills=90, cold=True, beach='Ldrt', seabed='Ldrt', creeps=(['nfrl', 'nwlt', 'ntkf', 'nftr'], ['nfrs', 'nwlg', 'nftb', 'nfrb'], ['nfrg', 'nwld', 'nfre', 'nftk']),
      critters=['nder', 'nrac'], mm=(58, 96, 52))
biome('crystal', tiles=[('Agrs', -2), ('Nsnw', 0.25), ('Lgrd', 0.55)], tree='ATtr', density=0.50, clump=14,
      hills=60, cold=True, beach='Nsnw', seabed='Ldrt', creeps=(['nadw', 'nfpl', 'nwiz', 'nwwf'], ['nadk', 'nfps', 'nwzr', 'nwwg'], ['nadr', 'nfpc', 'nwzg', 'nwzd']),
      critters=['nsno'], mm=(110, 140, 170))
biome('amber', tiles=[('Bdsr', -2), ('Cpos', 0.15), ('Bdrt', 0.5)], tree='CTtr', density=0.07, clump=6,
      hills=90, creeps=(['nanb', 'nanc', 'nspr', 'nslm'], ['nanw', 'nsc3', 'nssp', 'nslf'], ['nano', 'nane', 'nsbm', 'nsln']),
      critters=['nskk'], mm=(170, 150, 70))
biome('worldtree', tree2=('ATtc', 0.08), floor='Lgrd', cliff=CLIFF_GRASS, tiles=[('Agrs', -2), ('Lgrd', 0.2), ('Lgrs', 0.55)], tree='ATtr', density=0.66, clump=18,
      hills=90, creeps=(['nfrl', 'nsat', 'nwlt', 'nowb'], ['nfrs', 'nsty', 'nowb', 'nwlg'], ['nfrg', 'nsts', 'nowe', 'nfre']),
      critters=['nder', 'nsno'], mm=(70, 110, 96))

# Instances: flat, treeless floors of worked stone (Ybtl is the Cityscape brick).
_HALL = dict(hills=10, base=40, beach='Ldrt', seabed='Ldrt')
biome('lava', tiles=[('Dlvc', -2), ('Lrok', 0.25), ('Ybtl', 0.6)], **_HALL,
      creeps=(['nrdk', 'nrvf', 'nfgu'], ['nrdk', 'nrvf', 'ninc'], ['nrdr', 'nrwm', 'ninf']), mm=(120, 50, 30))
biome('temple', tiles=[('Bdsr', -2), ('Ybtl', 0.15), ('Bdrt', 0.6)], **_HALL,
      creeps=(['nscb', 'nanb', 'nsc2'], ['nanw', 'nsc3', 'nslh'], ['nano', 'nane', 'nslr']), mm=(196, 168, 110))
biome('halls', tiles=[('Ybtl', -2), ('Lrok', 0.3), ('Ldrt', 0.62)], **_HALL,
      creeps=(['nkob', 'ngno', 'nban'], ['nkog', 'ngnb', 'nrog'], ['nkol', 'ngnv', 'nass']), mm=(120, 110, 104))
biome('crypt', tiles=[('Ybtl', -2), ('Cpos', 0.3), ('Ldrt', 0.6)], **_HALL, blight=True,
      creeps=(['nzom', 'nske', 'ngh1'], ['nskg', 'nskm', 'nfgb'], ['nsoc', 'ngh2', 'nfgl']), mm=(96, 96, 80))
biome('frozen', tiles=[('Nice', -2), ('Ybtl', 0.2), ('Nsnw', 0.6)], **_HALL, cold=True, cliff=CLIFF_SNOW,
      creeps=(['nske', 'nnwa', 'nska'], ['nnwl', 'nskg', 'nnws'], ['nnwq', 'nsoc', 'nrvi']), mm=(170, 190, 214))
biome('grotto', tiles=[('Lgrd', -2), ('Cpos', 0.25), ('Lrok', 0.55)], **_HALL, tree='ZTtw', density=0.12, clump=6, cliff=CLIFF_GRASS,
      creeps=(['nmrl', 'nslm', 'nspb'], ['nmrr', 'nslf', 'nltc'], ['nmrm', 'nsln', 'nlds']), mm=(60, 92, 50))
biome('troll', tiles=[('Zgrs', -2), ('Ybtl', 0.2), ('Ldrt', 0.6)], **_HALL, tree='ZTtw', density=0.15, clump=6, cliff=CLIFF_GRASS,
      creeps=(['nftr', 'njg1', 'nspg'], ['nfsp', 'nftb', 'njg1'], ['nftk', 'njga', 'nfsh']), mm=(64, 116, 50))
