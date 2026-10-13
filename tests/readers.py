"""Independent readers for WC3 map files (used to validate the generator's output)."""
import struct

class R:
    def __init__(self, d): self.d, self.p = d, 0
    def i(self): v, = struct.unpack_from('<i', self.d, self.p); self.p += 4; return v
    def f(self): v, = struct.unpack_from('<f', self.d, self.p); self.p += 4; return v
    def b(self): v = self.d[self.p]; self.p += 1; return v
    def id(self): v = self.d[self.p:self.p+4].decode('latin1'); self.p += 4; return v
    def s(self):
        e = self.d.index(b'\0', self.p); v = self.d[self.p:e].decode('utf-8'); self.p = e + 1; return v
    def done(self): return self.p == len(self.d)

def read_units(d):
    r = R(d); assert r.id() == 'W3do'; ver, sub, n = r.i(), r.i(), r.i()
    out = []
    for _ in range(n):
        u = dict(id=r.id(), var=r.i(), x=r.f(), y=r.f(), z=r.f(), ang=r.f(), sx=r.f(), sy=r.f(), sz=r.f(), flags=r.b(), owner=r.i(), u1=r.b(), u2=r.b(), hp=r.i(), mp=r.i(), itemtable=r.i())
        sets = []
        for _ in range(r.i()):
            sets.append([(r.id(), r.i()) for _ in range(r.i())])
        u['sets'] = sets
        u.update(gold=r.i(), acq=r.f(), level=r.i(), stra=r.i(), agi=r.i(), intel=r.i())
        u['inv'] = [(r.i(), r.id()) for _ in range(r.i())]
        u['abil'] = [(r.id(), r.i(), r.i()) for _ in range(r.i())]
        rt = r.i(); u['rtype'] = rt
        if rt == 0: u['rand'] = (r.b(), r.b(), r.b(), r.b())
        elif rt == 1: u['rand'] = (r.i(), r.i())
        elif rt == 2: u['rand'] = [(r.id(), r.i()) for _ in range(r.i())]
        u.update(color=r.i(), waygate=r.i(), num=r.i())
        out.append(u)
    assert r.done(), (r.p, len(d))
    return ver, sub, out

def read_doodads(d):
    r = R(d); assert r.id() == 'W3do'; ver, sub, n = r.i(), r.i(), r.i()
    out = []
    for _ in range(n):
        o = dict(id=r.id(), var=r.i(), x=r.f(), y=r.f(), z=r.f(), ang=r.f(), sx=r.f(), sy=r.f(), sz=r.f(), state=r.b(), life=r.b())
        if ver >= 8:
            o['itemtable'] = r.i()
            o['sets'] = [[(r.id(), r.i()) for _ in range(r.i())] for _ in range(r.i())]
        o['num'] = r.i()
        out.append(o)
    sver = r.i(); sn = r.i()
    special = [(r.id(), r.i(), r.i(), r.i()) for _ in range(sn)]
    assert r.done(), (r.p, len(d))
    return ver, sub, out, special

def read_w3i(d):
    r = R(d); info = {}
    v = info['version'] = r.i(); assert v in (25, 26), v
    info.update(saves=r.i(), editor=r.i(), name=r.s(), author=r.s(), desc=r.s(), players_rec=r.s())
    info['bounds'] = [r.f() for _ in range(8)]; info['compl'] = [r.i() for _ in range(4)]
    info.update(pw=r.i(), ph=r.i(), flags=r.i(), tileset=chr(r.b()), ls_num=r.i(), ls_model=r.s(), ls_text=r.s(), ls_title=r.s(), ls_sub=r.s(), gamedata=r.i(),
                pro_path=r.s(), pro_text=r.s(), pro_title=r.s(), pro_sub=r.s(), fog=r.i(), fog_s=r.f(), fog_e=r.f(), fog_d=r.f(), fog_c=(r.b(), r.b(), r.b(), r.b()),
                weather=r.i(), sound=r.s(), light=r.b(), water=(r.b(), r.b(), r.b(), r.b()))
    players = []
    for _ in range(r.i()):
        players.append(dict(num=r.i(), type=r.i(), race=r.i(), fixed=r.i(), name=r.s(), x=r.f(), y=r.f(), allylo=r.i(), allyhi=r.i()))
    forces = [dict(flags=r.i(), mask=r.i(), name=r.s()) for _ in range(r.i())]
    info['players'], info['forces'] = players, forces
    nup = r.i(); assert nup == 0; ntech = r.i(); assert ntech == 0
    nut = r.i(); assert nut == 0; nit = r.i(); assert nit == 0
    if v == 26: assert r.i() == 0
    assert r.done(), (r.p, len(d))
    return info

def read_w3e(d):
    r = R(d); assert r.id() == 'W3E!'; ver = r.i(); ts = chr(r.b()); custom = r.i()
    tiles = [r.id() for _ in range(r.i())]; cliffs = [r.id() for _ in range(r.i())]
    w, h = r.i(), r.i(); ox, oy = r.f(), r.f()
    assert len(d) - r.p == w * h * 7, (len(d) - r.p, w * h * 7)
    return dict(version=ver, tileset=ts, custom=custom, tiles=tiles, cliffs=cliffs, w=w, h=h, ox=ox, oy=oy, data=d[r.p:])


# ---------------------------------------------------------------------------
# A small MPQ reader written separately from azeroth/mpq.py's writer.
# ---------------------------------------------------------------------------
import zlib


def _crypt_table():
    table, seed = [0] * 0x500, 0x00100001
    for i in range(256):
        idx = i
        for _ in range(5):
            seed = (seed * 125 + 3) % 0x2AAAAB
            hi = (seed & 0xFFFF) << 16
            seed = (seed * 125 + 3) % 0x2AAAAB
            table[idx] = hi | (seed & 0xFFFF)
            idx += 256
    return table


_CT = _crypt_table()


def _hash(name, kind):
    s1, s2 = 0x7FED7FED, 0xEEEEEEEE
    for c in name.upper().replace('/', '\\').encode('latin1'):
        s1 = (_CT[kind * 256 + c] ^ (s1 + s2)) & 0xFFFFFFFF
        s2 = (c + s1 + s2 + (s2 << 5) + 3) & 0xFFFFFFFF
    return s1


def _decrypt(words, key):
    seed, out = 0xEEEEEEEE, []
    for v in words:
        seed = (seed + _CT[0x400 + (key & 0xFF)]) & 0xFFFFFFFF
        p = (v ^ (key + seed)) & 0xFFFFFFFF
        out.append(p)
        key = ((((~key) << 21) + 0x11111111) | (key >> 11)) & 0xFFFFFFFF
        seed = (p + seed + (seed << 5) + 3) & 0xFFFFFFFF
    return out


class MPQ:
    def __init__(self, data):
        self.base = 0
        while data[self.base:self.base + 4] != b'MPQ\x1a':
            self.base += 512
            assert self.base < len(data), 'no MPQ header'
        self.d = data
        (_, hsize, asize, ver, shift, hpos, bpos, hcount, bcount) = struct.unpack_from('<4sIIHHIIII', data, self.base)
        self.sector = 512 << shift
        hw = _decrypt(struct.unpack_from('<%dI' % (hcount * 4), data, self.base + hpos), _hash('(hash table)', 3))
        bw = _decrypt(struct.unpack_from('<%dI' % (bcount * 4), data, self.base + bpos), _hash('(block table)', 3))
        self.hashes = [hw[i:i + 4] for i in range(0, len(hw), 4)]
        self.blocks = [bw[i:i + 4] for i in range(0, len(bw), 4)]

    def read(self, name):
        n = len(self.hashes)
        i = _hash(name, 0) % n
        a, b = _hash(name, 1), _hash(name, 2)
        for _ in range(n):
            ha, hb, _, block = self.hashes[i]
            if block == 0xFFFFFFFF:
                return None
            if ha == a and hb == b:
                return self._read_block(*self.blocks[block])
            i = (i + 1) % n
        return None

    def _read_block(self, offset, csize, fsize, flags):
        assert flags & 0x80000000, 'file deleted'
        assert not flags & 0x00010000, 'encrypted files are not supported'
        start = self.base + offset
        if not flags & 0x00000200:
            return self.d[start:start + fsize]
        count = (fsize + self.sector - 1) // self.sector
        offs = struct.unpack_from('<%dI' % (count + 1), self.d, start)
        out = bytearray()
        for k in range(count):
            chunk = self.d[start + offs[k]:start + offs[k + 1]]
            expect = min(self.sector, fsize - k * self.sector)
            if len(chunk) < expect:
                assert chunk[0] == 0x02, 'unsupported compression %x' % chunk[0]
                chunk = zlib.decompress(chunk[1:])
            assert len(chunk) == expect
            out += chunk
        return bytes(out)

    def names(self):
        return [n for n in self.read('(listfile)').decode('latin1').split('\r\n') if n]
