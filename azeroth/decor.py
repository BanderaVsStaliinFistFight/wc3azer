"""Decorations: props, ruins, village clutter and ambient life, per biome.

Each doodad: id -> (variations, footprint, (min scale, max scale), fixed facing or None).
footprint is the size of its pathing texture in 32-unit cells (0 = no pathing; 2, 4, 8 = a
2x2, 4x4 or 8x8 square that blocks walking and building; -4 = a 4x4 square that only
blocks building; (w, h) = a w x h block at the default facing, laid either way round).
All data from Blizzard's doodads.slk.
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
    # boulders, bushes and thorns
    'LRrk': (10, 4, (0.8, 1.3), None), 'ARrk': (10, 4, (0.8, 1.3), None), 'BRrk': (10, 4, (0.8, 1.3), None),
    'CRrk': (10, 4, (0.8, 1.3), None), 'ZRrk': (10, 4, (0.8, 1.3), None), 'NRrk': (10, 4, (0.8, 1.3), None),
    'IRrs': (10, 4, (0.8, 1.3), None), 'ORrk': (10, 4, (0.8, 1.3), 4.712389),
    'YPbs': (1, 2, (0.8, 1.2), None), 'GPsh': (1, 2, (0.75, 1.4), None), 'APtv': (7, 2, (0.8, 1.2), None),
    # fallen logs, fissures, rubble and the rocks of the cold and the deep
    'AOlg': (1, (12, 6), (0.8, 1.1), 4.712389), 'COlg': (1, (12, 6), (0.8, 1.1), 4.712389),
    'BRfs': (2, 8, (0.8, 1.2), None), 'CRfs': (2, 8, (0.8, 1.2), None), 'NRfs': (2, 8, (0.8, 1.2), None),
    'ORrr': (6, 4, (0.8, 1.2), None), 'ZRbs': (4, 4, (0.8, 1.2), None), 'IRrk': (8, 4, (0.8, 1.3), None),
    'GRrk': (10, 4, (0.8, 1.3), None), 'GRst': (4, 4, (0.8, 1.2), None), 'CPct': (1, 2, (0.8, 1.2), None),
}

# Things dotted over open country: biome -> [(doodad, weight)]. All of it the land's own:
# boulders, rubble and fissures, bushes, thorns, cacti, hollow stumps, fallen logs and bones.
SCATTER = {
    'temperate': [('LRrk', 3), ('YPbs', 2.5), ('AOhs', 1), ('AOlg', 1), ('APbs', 1), ('LPwh', 1)],
    'farmland': [('LPwh', 3), ('LPcr', 1), ('YPbs', 2), ('LRrk', 1.5), ('AOhs', 0.5), ('LOhc', 0.5)],
    'plains': [('LRrk', 2), ('LPwh', 2), ('YPbs', 1.5), ('BPtw', 1), ('BRrk', 1), ('BObo', 0.3)],
    'autumn': [('LRrk', 2), ('AOhs', 1.5), ('YPbs', 1.5), ('AOlg', 1), ('COhs', 0.5), ('APbs', 1)],
    'darkforest': [('AOhs', 2), ('LRrk', 2), ('COlg', 1.2), ('COhs', 1), ('GPsh', 1), ('APtv', 1), ('YPbs', 1)],
    'highland': [('LRrk', 3), ('ORrr', 1.5), ('AOhs', 1), ('YPbs', 1.5), ('AOlg', 0.6), ('NRfs', 0.2)],
    'grizzly': [('LRrk', 2), ('AOhs', 2), ('AOlg', 1.5), ('NPth', 1), ('YPbs', 1), ('NRrk', 1)],
    'fjord': [('NRrk', 2), ('AOhs', 1), ('AOlg', 1), ('NPth', 1), ('ORrr', 1), ('NObo', 0.4)],
    'nightelf': [('APbs', 3), ('ARrk', 3), ('AOhs', 2), ('AOlg', 1.5), ('GPsh', 0.5)],
    'worldtree': [('APbs', 3), ('ARrk', 2), ('AOhs', 2), ('AOlg', 1.5)],
    'crystal': [('ARrk', 2), ('IRic', 2), ('APbs', 1), ('IRrk', 1)],
    'fel': [('CPbs', 3), ('CRrk', 2), ('COhs', 2), ('APtv', 1.5), ('COlg', 1.5), ('CRfs', 0.3), ('CPct', 0.5)],
    'plague': [('LRrk', 2), ('COhs', 1.5), ('COlg', 1), ('CPbs', 1), ('APtv', 1), ('LOrb', 0.8), ('CRfs', 0.3)],
    'savanna': [('BRrk', 3), ('BPtw', 2.5), ('LPwh', 1.5), ('BObo', 0.8), ('BRrp', 0.6), ('BRgs', 0.4), ('BRfs', 0.2)],
    'reddesert': [('BRrk', 3), ('BRrp', 1.5), ('BObo', 0.8), ('BPca', 0.5), ('ORrr', 1), ('BRfs', 0.3)],
    'needles': [('BRrk', 3), ('BRrp', 2), ('BObo', 0.8), ('BPca', 0.5), ('BRfs', 0.3)],
    'barren': [('BRrk', 3), ('BRrp', 1), ('BPtw', 1), ('BObo', 0.8), ('LOrb', 0.4), ('ORrr', 1), ('BRfs', 0.4)],
    'desert': [('BPca', 3), ('BRrk', 2), ('BObo', 1), ('BRrp', 0.7), ('BRfs', 0.3)],
    'amber': [('BRrk', 2), ('BRrp', 1), ('BPca', 1), ('BObo', 0.8)],
    'jungle': [('ZPvp', 3), ('ZPms', 2), ('ZPtw', 2), ('ZRrk', 2), ('ZRbs', 1), ('AOlg', 0.6)],
    'swamp': [('ZPms', 3), ('ZPvp', 2), ('ZPtw', 1), ('ZRrk', 1), ('GPsh', 1), ('COlg', 0.8), ('CPct', 0.6)],
    'troll': [('ZPvp', 2), ('ZRrk', 1), ('ZPms', 1), ('ZRbs', 1), ('ZOrp', 0.3)],
    'grotto': [('ZPms', 2), ('GPsh', 2), ('ZPvp', 1), ('GRst', 1), ('GRrk', 1)],
    'volcanic': [('ORrk', 3), ('DOlc', 2), ('ORmk', 1), ('ORrr', 1.5), ('OOsk', 0.2)],
    'lava': [('DOlc', 3), ('ORrk', 1), ('ORmk', 0.5), ('ORrr', 1)],
    'snow': [('NRrk', 3), ('IRrs', 2), ('NPth', 1.5), ('NRic', 1), ('NObo', 0.3), ('NRfs', 0.3)],
    'tundra': [('NRrk', 3), ('NPth', 2), ('NRic', 1), ('NObo', 0.5), ('NRfs', 0.4)],
    'icecrown': [('IRrs', 2), ('IRic', 2), ('IRrk', 1.5), ('IRcy', 0.5), ('NObo', 0.3)],
    'frozen': [('IRic', 1), ('IOpr', 1), ('ISrb', 1), ('IOst', 1)],
    'rocky': [('LRrk', 3), ('ORrr', 2), ('NRrk', 1), ('BRrp', 1), ('BRfs', 0.3)],
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

# Water plants without pathing, by biome: rushes on the banks, lily pads on still water
RUSHES = {'jungle': ['ZPru', 'LPrs'], 'swamp': ['ZPru', 'APct'], 'troll': ['ZPru'], 'grotto': ['ZPru', 'APct'],
          'fel': ['APct'], 'plague': ['LPrs']}
LILIES = {'nightelf': 'AWfl', 'worldtree': 'AWfl', 'crystal': 'AWfl', 'jungle': 'ZPlp', 'swamp': 'ZPlp', 'troll': 'ZPlp',
          'grotto': 'ZPlp', 'fel': 'CPlp', 'plague': 'CPlp'}
WATER_VARIATIONS = {'ZPru': 2, 'LPrs': 4, 'APct': 1, 'AWfl': 3, 'ZPlp': 3, 'CPlp': 1, 'LPfp': 3, 'ZWsw': 5}
SEAWEED = 'ZWsw'                                      # in the shallows off warm and temperate coasts
ICE_FLOES = ['NWf1', 'NWf2', 'NWf3', 'NWf4', 'NWi3', 'NWi4']     # drifting in the cold seas

# Ambient life without pathing: where it gathers
BIRDS = 'AObd'          # over woods and shores
BATS = 'NObt'           # in the dark places
FLIES = 'LOfl'          # over the swamps
SHELLS = 'ZOsh'         # on the beaches
SIGNPOST = 'LOsp'       # at the forks in the roads
