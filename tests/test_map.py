"""End-to-end checks of the generated map. Run: python3 -m unittest discover tests"""
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import build  # noqa: E402
from game_ids import DESTRUCTABLE_IDS, DOODAD_IDS, UNIT_IDS  # noqa: E402
from readers import MPQ, read_doodads, read_units, read_w3e, read_w3i  # noqa: E402

EXPECTED_FILES = {'war3map.w3i', 'war3map.w3e', 'war3map.wpm', 'war3map.shd', 'war3map.doo', 'war3mapUnits.doo',
                  'war3map.j', 'war3map.mmp', 'war3mapMap.blp', 'war3map.w3r', 'war3map.w3c', 'war3map.wtg', 'war3map.wct'}


class MapTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.path = os.path.join(cls.tmp, 'Azeroth.w3x')
        build.build(1, cls.path, None)
        with open(cls.path, 'rb') as fh:
            cls.raw = fh.read()
        cls.mpq = MPQ(cls.raw)
        cls.files = {n: cls.mpq.read(n) for n in cls.mpq.names()}

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def test_archive(self):
        self.assertEqual(self.raw[:4], b'HM3W')
        self.assertTrue(EXPECTED_FILES <= set(self.files))
        for name, data in self.files.items():
            self.assertIsNotNone(data, name)

    def test_info(self):
        info = read_w3i(self.files['war3map.w3i'])
        self.assertEqual(info['version'], 25)
        self.assertEqual((info['pw'], info['ph']), (468, 468))
        self.assertEqual(len(info['players']), 12)
        self.assertFalse(info['flags'] & 0x4, 'a custom scenario, not a melee map')

    def test_terrain(self):
        w = read_w3e(self.files['war3map.w3e'])
        self.assertEqual((w['w'], w['h']), (481, 481))   # 480 x 480 tiles, the maximum map size
        self.assertLessEqual(len(w['tiles']), 16)
        self.assertLessEqual(len(w['cliffs']), 3)
        pts = np.frombuffer(w['data'], dtype=np.dtype([('h', '<u2'), ('w', '<u2'), ('t', 'u1'), ('v', 'u1'), ('c', 'u1')]))
        pts = pts.reshape(w['h'], w['w'])
        self.assertLess(int((pts['t'] & 15).max()), len(w['tiles']))
        cliff = pts['c'] >> 4
        self.assertTrue(((cliff < len(w['cliffs'])) | (cliff == 15)).all())
        layer = (pts['c'] & 15).astype(int)
        corners = [layer[:-1, :-1], layer[1:, :-1], layer[:-1, 1:], layer[1:, 1:]]
        spread = np.maximum.reduce(corners) - np.minimum.reduce(corners)
        self.assertLessEqual(int(spread.max()), 2, 'a tile needs a cliff model that does not exist')
        self.assertTrue((pts['h'] < 0x4000).all())

    def test_cliff_ground(self):
        """Beside every cliff the game draws the cliff type's own ground; it must suit the land around it."""
        w = read_w3e(self.files['war3map.w3e'])
        pts = np.frombuffer(w['data'], dtype=np.dtype([('h', '<u2'), ('w', '<u2'), ('t', 'u1'), ('v', 'u1'), ('c', 'u1')]))
        pts = pts.reshape(w['h'], w['w'])
        layer = (pts['c'] & 15).astype(int)
        cliff_type = (pts['c'] >> 4).astype(int)
        tex = (pts['t'] & 15).astype(int)
        ramp = (pts['t'] & 0x10) != 0
        tile = np.zeros_like(ramp)
        tile[:-1, :-1] = (layer[:-1, :-1] != layer[:-1, 1:]) | (layer[:-1, :-1] != layer[1:, :-1]) | (layer[:-1, :-1] != layer[1:, 1:])
        beside = tile.copy()
        beside[1:, :] |= tile[:-1, :]
        beside[:, 1:] |= tile[:, :-1]
        beside[1:, 1:] |= tile[:-1, :-1]
        beside &= ~ramp
        ground = {'CLdi': 'Ldrt', 'CWsn': 'Wsnw', 'CLgr': 'Lgrs'}
        cliff_ground = np.array([w['tiles'].index(ground[c]) for c in w['cliffs']])
        self.assertTrue((tex[beside] == cliff_ground[cliff_type[beside]]).all(), 'painted ground differs from what the game draws')
        # grass cliffs stand in grass: most open ground near them is grassy (roads, beaches and the
        # odd rock patch make up the rest; with one cliff type per zone it was only about half)
        grassy = np.isin(tex, [w['tiles'].index(t) for t in ('Lgrs', 'Lgrd', 'Fgrs', 'Agrs', 'Zgrs') if t in w['tiles']])
        open_ground = ~beside & ((pts['t'] & 0x40) == 0)
        near_grass_cliff = np.zeros_like(ramp)
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                near_grass_cliff |= np.roll(np.roll(beside & (cliff_type == w['cliffs'].index('CLgr')), dy, 0), dx, 1)
        sel = near_grass_cliff & open_ground
        self.assertGreater(float(grassy[sel].mean()), 0.68, 'grass cliffs on snow or rock')

    def test_ramps(self):
        """Ramps follow the World Editor's layout and their slope is walkable."""
        w = read_w3e(self.files['war3map.w3e'])
        pts = np.frombuffer(w['data'], dtype=np.dtype([('h', '<u2'), ('w', '<u2'), ('t', 'u1'), ('v', 'u1'), ('c', 'u1')]))
        pts = pts.reshape(w['h'], w['w'])
        ramp = (pts['t'] & 0x10) != 0
        layer = (pts['c'] & 15).astype(int)
        self.assertGreater(int(ramp.sum()), 100)
        # each flagged corner lies on a straight run of three: the upper corner and two lower ones
        for y, x in np.argwhere(ramp):
            ok = False
            for dx, dy in ((1, 0), (0, 1)):
                for start in (0, -1, -2):
                    run = [(y + (start + k) * dy, x + (start + k) * dx) for k in range(3)]
                    if all(0 <= a < w['h'] and 0 <= b < w['w'] and ramp[a, b] for a, b in run):
                        lv = [layer[a, b] for a, b in run]
                        ok |= lv in ([lv[0], lv[0] - 1, lv[0] - 1], [lv[2] - 1, lv[2] - 1, lv[2]])
            self.assertTrue(ok, (x, y))
        # the sloped tiles of every ramp are walkable
        cells = np.frombuffer(self.files['war3map.wpm'][16:], dtype=np.uint8).reshape(1920, 1920)
        c = [ramp[:-1, :-1], ramp[1:, :-1], ramp[:-1, 1:], ramp[1:, 1:]]
        lc = [layer[:-1, :-1], layer[1:, :-1], layer[:-1, 1:], layer[1:, 1:]]
        slope = np.logical_and.reduce(c) & (np.maximum.reduce(lc) != np.minimum.reduce(lc))
        self.assertGreater(int(slope.sum()), 40)
        for ty, tx in np.argwhere(slope):
            self.assertFalse((cells[ty * 4:ty * 4 + 4, tx * 4:tx * 4 + 4] & 0x02).any(), (tx, ty))

    def test_pathing_and_shadow(self):
        wpm = self.files['war3map.wpm']
        self.assertEqual(wpm[:4], b'MP3W')
        self.assertEqual(struct.unpack_from('<iii', wpm, 4), (0, 1920, 1920))
        self.assertEqual(len(wpm), 16 + 1920 * 1920)
        self.assertEqual(len(self.files['war3map.shd']), 1920 * 1920)

    def test_objects_exist_in_game_data(self):
        _, _, doodads, special = read_doodads(self.files['war3map.doo'])
        self.assertGreater(len(doodads), 15000)
        for d in doodads:
            self.assertIn(d['id'], DESTRUCTABLE_IDS | DOODAD_IDS)
            self.assertTrue(-29952 < d['x'] < 29952 and -30208 < d['y'] < 29696)
        _, _, units = read_units(self.files['war3mapUnits.doo'])
        for u in units:
            self.assertTrue(u['id'] == 'sloc' or u['id'] in UNIT_IDS, u['id'])
        script = self.files['war3map.j'].decode('utf-8')
        for uid in set(re.findall(r"CreateUnit\(p, '(\w{4})'", script)):
            self.assertIn(uid, UNIT_IDS)
        self.assertEqual(sum(u['id'] == 'sloc' for u in units), 12)

    def test_no_melee_content(self):
        """Terrain only: no gold mines, creeps, shops or item drops, and no melee setup."""
        _, _, units = read_units(self.files['war3mapUnits.doo'])
        ids = {u['id'] for u in units}
        self.assertNotIn('ngol', ids)
        self.assertEqual(ids - {'sloc', 'nwgt'}, {u['id'] for u in units if u['owner'] == 15 and u['id'] != 'nwgt'})
        self.assertFalse([u for u in units if u['owner'] == 12], 'no neutral hostile units')
        script = self.files['war3map.j'].decode('utf-8')
        self.assertNotIn('Melee', script)
        self.assertNotIn('ngol', script)
        self.assertNotIn('PLAYER_NEUTRAL_AGGRESSIVE', script)
        self.assertNotIn('DropItem', script)
        wtg = self.files['war3map.wtg']
        self.assertEqual(struct.unpack_from('<i', wtg, len(wtg) - 4)[0], 0, 'no triggers')

    def test_script_structure(self):
        script = self.files['war3map.j'].decode('utf-8')
        defined = set(re.findall(r'^function (\w+) takes', script, re.M))
        self.assertTrue({'main', 'config'} <= defined)
        for name in re.findall(r'call (\w+)\(', script):
            if name.startswith(('Create', 'Init', 'Unit_', 'Trig_')) and name not in ('CreateUnit', 'CreateTrigger', 'InitBlizzard', 'InitGenericPlayerSlots'):
                self.assertIn(name, defined, name)
        self.assertEqual(script.count('\nfunction '), script.count('\nendfunction'))

    @unittest.skipUnless(os.environ.get('PJASS') and os.environ.get('COMMON_J') and os.environ.get('BLIZZARD_J'),
                         'set PJASS, COMMON_J and BLIZZARD_J to run the JASS syntax checker')
    def test_pjass(self):
        path = os.path.join(self.tmp, 'war3map.j')
        with open(path, 'wb') as fh:
            fh.write(self.files['war3map.j'])
        res = subprocess.run([os.environ['PJASS'], os.environ['COMMON_J'], os.environ['BLIZZARD_J'], path],
                             capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)


if __name__ == '__main__':
    unittest.main()
