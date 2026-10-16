"""Natural decorations per biome: rocks, plants, logs and ambient life.

Each doodad: id -> (variations, footprint, (min scale, max scale), fixed facing or None).
footprint is the size of its pathing texture in 32-unit cells (0 = no pathing; 2, 4, 8 = a
2x2, 4x4 or 8x8 square that blocks walking and building; -4 = a 4x4 square that only
blocks building; (w, h) = a w x h block at the default facing, laid either way round).
All data from Blizzard's doodads.slk.
"""
DOODADS = {
    # Lordaeron
    'LOrb': (4, 0, (0.8, 1.2), None), 'LPcr': (1, 0, (0.8, 1.2), None),
    'LPwh': (1, 0, (0.8, 1.2), None), 'LPcw': (2, 0, (0.8, 1.2), None), 'LOfl': (1, 0, (0.8, 1.2), None),
    # Ashenvale and Felwood
    'AOhs': (1, 4, (0.8, 1.2), None), 'APbs': (1, 2, (0.8, 1.2), None), 'AObd': (1, 0, (0.8, 1.2), None),
    'COhs': (1, 4, (0.8, 1.2), None), 'CPbs': (2, 2, (0.8, 1.2), None),
    # the Barrens and the deserts
    'BObo': (10, -4, (0.8, 1.2), None), 'BPca': (10, 4, (0.8, 1.2), None), 'BPtw': (10, 4, (0.8, 1.2), None),
    'BRrp': (3, 4, (0.8, 1.2), None), 'BRgs': (3, 4, (0.8, 1.2), None),
    # the jungle and the shores
    'ZPms': (6, 2, (0.8, 1.2), 4.712389), 'ZPvp': (4, 2, (0.8, 1.2), None), 'ZPtw': (10, 4, (0.8, 1.2), None),
    'ZOsh': (10, 0, (0.8, 1.2), None),
    # Northrend and Icecrown
    'NObo': (10, -4, (0.8, 1.2), None), 'NPth': (7, 4, (0.8, 1.2), None), 'NRic': (10, 4, (0.8, 1.2), None),
    'NObt': (1, 0, (0.8, 1.2), None), 'IRic': (4, 2, (0.8, 1.2), None), 'IRcy': (9, 8, (0.8, 1.2), None),
    # volcanic and the deep places
    'OOsk': (2, 0, (0.8, 1.2), None), 'ORmk': (5, 8, (0.8, 1.2), 4.712389), 'DOlc': (4, 0, (0.8, 1.2), None),
    'DRst': (4, 4, (0.8, 1.2), None), 'DRrk': (10, 4, (0.8, 1.3), None),
    # boulders, bushes and thorns
    'LRrk': (10, 4, (0.8, 1.3), None), 'ARrk': (10, 4, (0.8, 1.3), None), 'BRrk': (10, 4, (0.8, 1.3), None),
    'CRrk': (10, 4, (0.8, 1.3), None), 'ZRrk': (10, 4, (0.8, 1.3), None), 'NRrk': (10, 4, (0.8, 1.3), None),
    'IRrs': (10, 4, (0.8, 1.3), None), 'ORrk': (10, 4, (0.8, 1.3), 4.712389), 'YPbs': (1, 2, (0.8, 1.2), None),
    'GPsh': (1, 2, (0.75, 1.4), None), 'APtv': (7, 2, (0.8, 1.2), None),
    # fallen logs, fissures, rubble and the rocks of the cold and the deep
    'AOlg': (1, (12, 6), (0.8, 1.1), 4.712389), 'COlg': (1, (12, 6), (0.8, 1.1), 4.712389), 'BRfs': (2, 8, (0.8, 1.2), None),
    'CRfs': (2, 8, (0.8, 1.2), None), 'NRfs': (2, 8, (0.8, 1.2), None), 'ORrr': (6, 4, (0.8, 1.2), None),
    'ZRbs': (4, 4, (0.8, 1.2), None), 'IRrk': (8, 4, (0.8, 1.3), None), 'GRrk': (10, 4, (0.8, 1.3), None),
    'GRst': (4, 4, (0.8, 1.2), None), 'CPct': (1, 2, (0.8, 1.2), None),
}

# Things dotted over open country: biome -> [(doodad, weight)]. All of it the land's own:
# boulders, rubble and fissures, bushes, thorns, cacti, hollow stumps, fallen logs and bones.
SCATTER = {
    'temperate': [('LRrk', 3), ('APbs', 3.5), ('AOhs', 1), ('AOlg', 1)],
    'farmland': [('LPwh', 3), ('LPcr', 1), ('APbs', 2), ('LRrk', 1.5), ('AOhs', 0.5)],
    'plains': [('LRrk', 2), ('APbs', 1.5), ('BPtw', 1), ('BRrk', 1), ('BObo', 0.3)],
    'autumn': [('LRrk', 2), ('AOhs', 1.5), ('APbs', 2.5), ('AOlg', 1), ('COhs', 0.5)],
    'darkforest': [('AOhs', 2), ('LRrk', 2), ('COlg', 1.2), ('COhs', 1), ('APtv', 1.5), ('APbs', 1)],
    'highland': [('LRrk', 3), ('ORrr', 1.5), ('AOhs', 1), ('APbs', 1.5), ('AOlg', 0.6)],
    'grizzly': [('LRrk', 2), ('AOhs', 2), ('AOlg', 1.5), ('NPth', 1), ('APbs', 1), ('NRrk', 1)],
    'fjord': [('NRrk', 2), ('AOhs', 1), ('AOlg', 1), ('NPth', 1), ('ORrr', 1), ('NObo', 0.4)],
    'nightelf': [('APbs', 3), ('ARrk', 3), ('AOhs', 2), ('AOlg', 1.5)],
    'worldtree': [('APbs', 3), ('ARrk', 2), ('AOhs', 2), ('AOlg', 1.5)],
    'crystal': [('ARrk', 2), ('IRic', 2), ('APbs', 1), ('IRrk', 1)],
    'fel': [('CPbs', 3), ('CRrk', 2), ('COhs', 2), ('APtv', 1.5), ('COlg', 1.5), ('CRfs', 0.3), ('CPct', 0.5)],
    'plague': [('LRrk', 2), ('COhs', 1.5), ('COlg', 1), ('CPbs', 1), ('APtv', 1), ('LOrb', 0.8), ('CRfs', 0.3)],
    'savanna': [('BRrk', 3), ('BPtw', 2.5), ('BObo', 0.8), ('BRrp', 0.6), ('BRgs', 0.4), ('BRfs', 0.2)],
    'reddesert': [('BRrk', 3), ('BRrp', 1.5), ('BObo', 0.8), ('BPca', 0.5), ('ORrr', 1), ('BRfs', 0.3)],
    'needles': [('BRrk', 3), ('BRrp', 2), ('BObo', 0.8), ('BPca', 0.5), ('BRfs', 0.3)],
    'barren': [('BRrk', 3), ('BRrp', 1), ('BPtw', 1), ('BObo', 0.8), ('LOrb', 0.4), ('ORrr', 1), ('BRfs', 0.4)],
    'desert': [('BPca', 3), ('BRrk', 2), ('BObo', 1), ('BRrp', 0.7), ('BRfs', 0.3)],
    'amber': [('BRrk', 2), ('BRrp', 1), ('BPca', 1), ('BObo', 0.8)],
    'jungle': [('ZPvp', 3), ('ZPms', 2), ('ZPtw', 2), ('ZRrk', 2), ('ZRbs', 1), ('AOlg', 0.6)],
    'swamp': [('ZPms', 3), ('ZPvp', 2), ('ZPtw', 1), ('ZRrk', 1), ('COlg', 0.8), ('CPct', 0.6)],
    'volcanic': [('ORrk', 3), ('DOlc', 2), ('ORmk', 1), ('ORrr', 1.5), ('OOsk', 0.2)],
    'snow': [('NRrk', 3), ('IRrs', 2), ('NPth', 1.5), ('NRic', 1), ('NObo', 0.3), ('NRfs', 0.3)],
    'tundra': [('NRrk', 3), ('NPth', 2), ('NRic', 1), ('NObo', 0.5), ('NRfs', 0.4)],
    'icecrown': [('IRrs', 2), ('IRic', 2), ('IRrk', 1.5), ('IRcy', 0.5), ('NObo', 0.3)],
    'rocky': [('LRrk', 3), ('ORrr', 2), ('BRrp', 1), ('BRfs', 0.3)],
}

# What each open-country piece is, for the place it belongs and the company it keeps (objects.py):
# rocks lie on rough ground with stones spilled downhill and a plant sheltering at their foot,
# stumps and logs lie by the woods with mushrooms on them, bushes grow in thickets, cacti stand
# apart on the flats, fissures crack rough ground with stones on their rims, thorns grow in
# tangles, and wild grass and crops grow in little stands.
KINDS = {
    'rock': {'LRrk', 'ARrk', 'BRrk', 'CRrk', 'ZRrk', 'NRrk', 'IRrs', 'ORrk', 'ORrr', 'ZRbs', 'IRrk', 'GRrk', 'DRrk'},
    'wood': {'AOhs', 'COhs', 'AOlg', 'COlg'},
    'bush': {'APbs', 'CPbs'},
    'cactus': {'BPca'},
    'bones': {'BObo', 'NObo', 'LOrb'},
    'thorns': {'NPth', 'APtv'},
    'fissure': {'BRfs', 'CRfs', 'NRfs'},
    'growth': {'BPtw', 'ZPtw', 'ZPvp', 'ZPms', 'CPct'},
    'crop': {'LPwh', 'LPcr'},
}
KIND_OF = {did: kind for kind, ids in KINDS.items() for did in ids}

# Water plants without pathing, by biome: rushes on the banks, lily pads on still water
RUSHES = {'jungle': ['ZPru', 'LPrs'], 'swamp': ['ZPru', 'APct'], 'fel': ['APct'], 'plague': ['LPrs']}
LILIES = {'nightelf': 'AWfl', 'worldtree': 'AWfl', 'crystal': 'AWfl', 'jungle': 'ZPlp', 'swamp': 'ZPlp',
          'fel': 'CPlp', 'plague': 'CPlp'}
WATER_VARIATIONS = {'ZPru': 2, 'LPrs': 4, 'APct': 1, 'AWfl': 3, 'ZPlp': 3, 'CPlp': 1, 'LPfp': 3, 'ZWsw': 5}
SEAWEED = 'ZWsw'                                      # in the shallows off warm and temperate coasts
ICE_FLOES = ['NWf1', 'NWf2', 'NWf3', 'NWf4', 'NWi3', 'NWi4']     # drifting in the cold seas

# Ambient life without pathing: where it gathers
BIRDS = 'AObd'          # over woods and shores
BATS = 'NObt'           # in the dark places
FLIES = 'LOfl'          # over the swamps
SHELLS = 'ZOsh'         # on the beaches
