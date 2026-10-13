"""Decorations: props, ruins, village clutter and ambient life, per biome.

Each doodad: id -> (variations, footprint, (min scale, max scale), fixed facing or None).
footprint is the size of its pathing texture in 32-unit cells (0 = no pathing; 2, 4, 8 = a
2x2, 4x4 or 8x8 square that blocks walking and building; -4 = a 4x4 square that only
blocks building). All data from Blizzard's doodads.slk.
"""
DOODADS = {
    # Lordaeron and villages
    'LOhb': (5, 4, (0.8, 1.2), None), 'LOrh': (5, 4, (0.8, 1.2), None), 'LOhc': (1, 0, (0.8, 1.2), None),
    'LOsw': (1, 4, (0.8, 1.2), None), 'LOlp': (2, 2, (0.8, 1.2), None), 'LOsp': (1, 0, (0.9, 1.1), None),
    'LOgr': (1, 2, (0.8, 1.2), None), 'LOpg': (3, 2, (0.8, 1.1), None), 'LOsk': (4, 4, (0.8, 1.2), None),
    'LOss': (6, 2, (0.8, 1.2), None), 'LOsh': (3, 2, (0.8, 1.2), None), 'LOrb': (4, 0, (0.8, 1.2), None),
    'LOwr': (1, 4, (0.8, 1.2), None), 'LOcb': (1, 4, (0.8, 1.2), None), 'LSwl': (1, 4, (1.0, 1.2), None),
    'LObr': (1, 2, (0.8, 1.2), None), 'LOam': (1, 2, (0.9, 1.2), None), 'LOwp': (1, 2, (0.9, 1.2), None),
    'LOhp': (1, 2, (0.8, 1.2), None), 'LOt1': (1, 4, (0.8, 1.2), None), 'LPcr': (1, 0, (0.8, 1.2), None),
    'LPwh': (1, 0, (0.8, 1.2), None), 'LPcw': (2, 0, (0.8, 1.2), None), 'LOfl': (1, 0, (0.8, 1.2), None),
    # Ashenvale and Felwood
    'ASbc': (2, 4, (0.8, 1.2), None), 'ASbr': (3, 4, (0.8, 1.2), None), 'AObo': (2, 4, (0.8, 1.2), None),
    'AOob': (3, 4, (0.8, 1.2), None), 'AOhs': (1, 4, (0.8, 1.2), None), 'APbs': (1, 2, (0.8, 1.2), None),
    'AOsr': (3, 0, (0.8, 1.2), None), 'AOnt': (3, 2, (0.8, 1.2), None), 'AObd': (1, 0, (0.8, 1.2), None),
    'CSbc': (2, 4, (0.8, 1.2), None), 'CObo': (2, 4, (0.8, 1.2), None), 'COhs': (1, 4, (0.8, 1.2), None),
    'CPbs': (2, 2, (0.8, 1.2), None), 'CSbr': (3, 4, (0.8, 1.2), None), 'CObl': (1, 0, (0.8, 1.2), None),
    # the Barrens and the deserts
    'BObo': (10, -4, (0.8, 1.2), None), 'BOct': (3, 2, (0.8, 1.2), None), 'BOtt': (2, 2, (0.8, 1.2), None),
    'BPca': (10, 4, (0.8, 1.2), None), 'BPtw': (10, 4, (0.8, 1.2), None), 'BSrc': (2, 4, (0.8, 1.2), None),
    'BRrp': (3, 4, (0.8, 1.2), None), 'BRgs': (3, 4, (0.8, 1.2), None), 'BSar': (3, 4, (0.8, 1.2), None),
    'BSrw': (1, 4, (0.8, 1.2), None),
    # ruins and jungle
    'ZOrp': (5, 2, (0.8, 1.2), None), 'ZOss': (4, 4, (1.0, 1.6), None), 'ZOsb': (2, 4, (0.9, 1.0), None),
    'ZOob': (2, 4, (0.8, 1.2), None), 'ZOst': (2, 4, (0.9, 1.0), None), 'ZPms': (6, 2, (0.8, 1.2), 4.712389),
    'ZPvp': (4, 2, (0.8, 1.2), None), 'ZPtw': (10, 4, (0.8, 1.2), None), 'ZOsh': (10, 0, (0.8, 1.2), None),
    'ZOtr': (2, 2, (0.8, 1.2), None),
    # Northrend and Icecrown
    'NObc': (2, 4, (0.8, 1.2), None), 'NObk': (1, 4, (0.8, 1.2), None), 'NOok': (1, 4, (0.8, 1.2), None),
    'NOtb': (3, 4, (0.8, 1.2), None), 'NObo': (10, -4, (0.8, 1.2), None), 'NPth': (7, 4, (0.8, 1.2), None),
    'NRic': (10, 4, (0.8, 1.2), None), 'NOfp': (1, 4, (0.8, 1.2), None), 'NSrb': (3, 4, (0.8, 1.2), None),
    'NObt': (1, 0, (0.8, 1.2), None),
    'IOob': (3, 4, (0.8, 1.2), None), 'IOpr': (3, 4, (0.8, 1.2), None), 'ISrb': (3, 4, (0.8, 1.2), None),
    'IRic': (4, 2, (0.8, 1.2), None), 'IRcy': (9, 8, (0.8, 1.2), None), 'IOst': (1, 2, (0.8, 1.2), None),
    # volcanic and the deep places
    'OOob': (5, 4, (0.8, 1.2), None), 'OOst': (2, 2, (0.8, 1.2), None), 'OOsk': (2, 0, (0.8, 1.2), None),
    'ORmk': (5, 8, (0.8, 1.2), 4.712389), 'DOlc': (4, 0, (0.8, 1.2), None),
    'DOtp': (2, 4, (0.8, 1.2), None), 'DOjp': (2, 4, (0.8, 1.2), None), 'DRst': (4, 4, (0.8, 1.2), None),
}

# Props dotted over open country: biome -> [(doodad, weight)]
SCATTER = {
    'temperate': [('LOhc', 3), ('ZOss', 1), ('LOsw', 1), ('LOwr', 0.4), ('LOt1', 0.3), ('LOgr', 0.3)],
    'farmland': [('LPwh', 3), ('LPcr', 2), ('LOhb', 2), ('LOhc', 2), ('LOcb', 1), ('LOsw', 0.6), ('LSwl', 0.3)],
    'plains': [('LOhc', 2), ('ZOss', 1.5), ('BOtt', 0.6), ('BPtw', 1), ('LOsw', 0.5)],
    'autumn': [('LOrh', 2), ('LOhc', 2), ('LOsw', 1), ('COhs', 1), ('ZOss', 1)],
    'darkforest': [('LOgr', 1.5), ('LOpg', 1.5), ('LOsw', 1), ('COhs', 1), ('LOss', 0.5), ('AOsr', 1), ('LOrb', 1)],
    'highland': [('ZOss', 2), ('LOsw', 1), ('AOhs', 1), ('LOhc', 1), ('NOfp', 0.3)],
    'grizzly': [('ZOss', 2), ('AOhs', 1.5), ('LOsw', 0.6), ('NOfp', 0.3)],
    'fjord': [('ZOss', 2), ('NOfp', 0.5), ('LOsw', 0.6), ('NObo', 1)],
    'nightelf': [('ASbc', 1.5), ('ASbr', 1.5), ('AObo', 1), ('AOob', 0.7), ('AOhs', 1.5), ('APbs', 2), ('AOnt', 0.5)],
    'worldtree': [('ASbc', 1), ('ASbr', 1), ('AOob', 0.7), ('AOhs', 1.5), ('APbs', 2)],
    'crystal': [('ASbr', 1), ('AOob', 1), ('IRic', 1.5), ('APbs', 1)],
    'fel': [('CSbc', 1), ('CObo', 1), ('COhs', 1.5), ('CPbs', 2), ('CSbr', 1), ('CObl', 2), ('LOrb', 1)],
    'plague': [('LOgr', 2), ('LOpg', 2), ('LOss', 1), ('LOsh', 1), ('LOsk', 1), ('LOrb', 2), ('CObl', 2), ('LOsw', 1), ('AOsr', 1)],
    'savanna': [('BObo', 2), ('BOct', 1), ('BOtt', 1), ('BPtw', 2), ('BRrp', 0.7), ('BRgs', 0.5), ('BSrc', 0.7)],
    'reddesert': [('BObo', 2), ('BRrp', 1.5), ('BOct', 1), ('BSrc', 1), ('BSrw', 0.5), ('BRgs', 0.5)],
    'needles': [('BObo', 2), ('BRrp', 2), ('BOct', 1), ('BSrc', 0.7)],
    'barren': [('BObo', 2), ('BRrp', 1), ('BOct', 1), ('BSrc', 1), ('BSrw', 0.5), ('LOrb', 1)],
    'desert': [('BObo', 3), ('BPca', 3), ('BSrc', 1), ('BSar', 0.5), ('ZOsb', 0.5), ('ZOrp', 0.7), ('BRrp', 1)],
    'amber': [('BObo', 2), ('BPca', 1), ('ZOrp', 1), ('ZOsb', 0.5), ('BRrp', 1)],
    'jungle': [('ZOrp', 1.5), ('ZOss', 1), ('ZOsb', 0.7), ('ZOob', 0.5), ('ZPms', 2), ('ZPvp', 2), ('ZPtw', 2), ('ZOtr', 0.5)],
    'swamp': [('ZPms', 2), ('ZPvp', 2), ('ZPtw', 1), ('ZOrp', 0.7), ('LOrb', 1)],
    'troll': [('ZOrp', 1.5), ('ZOss', 1), ('ZPms', 1), ('ZPvp', 1), ('ZOob', 0.5)],
    'grotto': [('ZPms', 2), ('ZPvp', 1), ('DRst', 1)],
    'volcanic': [('OOob', 2), ('OOst', 1), ('OOsk', 2), ('LOsk', 1), ('ORmk', 1), ('DOlc', 2)],
    'lava': [('DOlc', 3), ('OOob', 1), ('OOsk', 1), ('ORmk', 0.5)],
    'snow': [('NObc', 1), ('NObk', 0.5), ('NOok', 0.5), ('NOtb', 1), ('NObo', 2), ('NPth', 2), ('NRic', 1.5), ('NSrb', 1)],
    'tundra': [('NObo', 2), ('NPth', 2), ('NRic', 1), ('NSrb', 1), ('NOtb', 0.5), ('NOfp', 0.3)],
    'icecrown': [('IOob', 1), ('IOpr', 1), ('ISrb', 1.5), ('IRic', 2), ('NObo', 1), ('IRcy', 0.5)],
    'frozen': [('IOpr', 1), ('ISrb', 1), ('IRic', 1), ('IOst', 1)],
    'rocky': [('ZOss', 2), ('LOsw', 1), ('NSrb', 1), ('BRrp', 1)],
    'halls': [('DOjp', 1), ('DRst', 1), ('ZOrp', 1), ('LObr', 1)],
    'crypt': [('LOgr', 1), ('LOss', 1), ('LOsk', 1), ('DOjp', 1)],
    'temple': [('ZOrp', 2), ('ZOsb', 1), ('BObo', 1)],
}

# Ruins left at the named sites: biome group -> doodads
_RUINS_LORDAERON = ['LOsw', 'ZOss', 'ZOrp', 'ZOsb', 'LOt1', 'LObr']
RUINS = {b: _RUINS_LORDAERON for b in ('temperate', 'farmland', 'plains', 'autumn', 'darkforest', 'highland', 'plague',
                                       'fjord', 'grizzly', 'rocky')}
RUINS.update({b: ['ASbc', 'ASbr', 'AObo', 'AOob'] for b in ('nightelf', 'worldtree', 'crystal')})
RUINS.update({'fel': ['CSbc', 'CSbr', 'CObo']})
RUINS.update({b: ['BSrc', 'BSar', 'BSrw', 'BOct', 'BObo'] for b in ('savanna', 'reddesert', 'needles', 'barren', 'desert', 'amber')})
RUINS.update({b: ['ZOrp', 'ZOss', 'ZOsb', 'ZOob', 'ZOst'] for b in ('jungle', 'swamp', 'troll', 'grotto')})
RUINS.update({b: ['NObc', 'NObk', 'NOok', 'NSrb', 'NOtb'] for b in ('snow', 'tundra')})
RUINS.update({b: ['IOob', 'IOpr', 'ISrb'] for b in ('icecrown', 'frozen')})
RUINS.update({b: ['OOob', 'OOst', 'LOsk', 'OOsk'] for b in ('volcanic', 'lava')})
RUINS.update({b: ['DOjp', 'ZOrp', 'DRst'] for b in ('halls', 'crypt', 'temple')})

# Clutter round the town sites
VILLAGE = ['LOhb', 'LOhc', 'LOlp', 'LOcb', 'LOwr', 'LOam', 'LOwp', 'LOhp', 'LObr', 'LOt1']
VILLAGE_COLD = ['NOfp', 'LOhc', 'LOlp', 'LOam', 'LOwp', 'LObr', 'NObo']
VILLAGE_DRY = ['BOtt', 'BOct', 'LOhc', 'LObr', 'LOam', 'LOwp', 'BObo']

# Ambient life without pathing: where it gathers
BIRDS = 'AObd'          # over woods and shores
BATS = 'NObt'           # in the dark places
FLIES = 'LOfl'          # over the swamps
SHELLS = 'ZOsh'         # on the beaches
SIGNPOST = 'LOsp'       # at the forks in the roads
