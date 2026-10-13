"""Minimal MPQ (format v0) archive writer, as used by Warcraft III maps.

Files are stored sector-compressed with zlib (compression mask 0x02),
unencrypted. Hash and block tables are encrypted as the format requires.
A 512-byte HM3W map header is prepended when writing a .w3x/.w3m map.
"""
import struct
import zlib

MPQ_FILE_COMPRESS = 0x00000200
MPQ_FILE_EXISTS = 0x80000000
SECTOR_SHIFT = 3                      # sector size = 512 << 3 = 4096
SECTOR_SIZE = 512 << SECTOR_SHIFT
MASK = 0xFFFFFFFF


def _build_crypt_table():
    table = [0] * 0x500
    seed = 0x00100001
    for index1 in range(0x100):
        index2 = index1
        for _ in range(5):
            seed = (seed * 125 + 3) % 0x2AAAAB
            temp1 = (seed & 0xFFFF) << 0x10
            seed = (seed * 125 + 3) % 0x2AAAAB
            temp2 = seed & 0xFFFF
            table[index2] = temp1 | temp2
            index2 += 0x100
    return table


CRYPT_TABLE = _build_crypt_table()
HASH_OFFSET, HASH_A, HASH_B, HASH_KEY = 0, 1, 2, 3


def hash_string(name, hash_type):
    seed1, seed2 = 0x7FED7FED, 0xEEEEEEEE
    for ch in name.upper().replace('/', '\\').encode('latin1'):
        seed1 = (CRYPT_TABLE[(hash_type << 8) + ch] ^ (seed1 + seed2)) & MASK
        seed2 = (ch + seed1 + seed2 + (seed2 << 5) + 3) & MASK
    return seed1


def encrypt(words, key):
    seed = 0xEEEEEEEE
    out = []
    for value in words:
        seed = (seed + CRYPT_TABLE[0x400 + (key & 0xFF)]) & MASK
        out.append((value ^ (key + seed)) & MASK)
        key = ((((~key) << 0x15) + 0x11111111) | (key >> 0x0B)) & MASK
        seed = (value + seed + (seed << 5) + 3) & MASK
    return out


def decrypt(words, key):
    seed = 0xEEEEEEEE
    out = []
    for value in words:
        seed = (seed + CRYPT_TABLE[0x400 + (key & 0xFF)]) & MASK
        plain = (value ^ (key + seed)) & MASK
        out.append(plain)
        key = ((((~key) << 0x15) + 0x11111111) | (key >> 0x0B)) & MASK
        seed = (plain + seed + (seed << 5) + 3) & MASK
    return out


def _compress_file(data):
    """Return (stored bytes, compressed size) for a sector-compressed file."""
    sectors = [data[i:i + SECTOR_SIZE] for i in range(0, len(data), SECTOR_SIZE)] or [b'']
    blobs = []
    for sector in sectors:
        packed = zlib.compress(sector, 9)
        # A sector is stored raw whenever compression does not shrink it.
        blobs.append(b'\x02' + packed if len(packed) + 1 < len(sector) else sector)
    offsets = [4 * (len(blobs) + 1)]
    for blob in blobs:
        offsets.append(offsets[-1] + len(blob))
    stored = struct.pack('<%dI' % len(offsets), *offsets) + b''.join(blobs)
    return stored


def build_mpq(files):
    """files: list of (archive name, bytes). Returns the MPQ archive bytes."""
    names = [n for n, _ in files]
    if '(listfile)' not in names:
        listfile = '\r\n'.join(names + ['(listfile)']).encode('latin1') + b'\r\n'
        files = list(files) + [('(listfile)', listfile)]

    hash_size = 16
    while hash_size < len(files) * 2:
        hash_size *= 2

    body = bytearray()
    blocks = []
    header_size = 32
    for name, data in files:
        stored = _compress_file(data)
        offset = header_size + len(body)
        body += stored
        blocks.append((offset, len(stored), len(data), MPQ_FILE_EXISTS | MPQ_FILE_COMPRESS))

    hash_table = [(0xFFFFFFFF, 0xFFFFFFFF, 0xFFFF, 0xFFFF, 0xFFFFFFFF)] * hash_size
    for block_index, (name, _) in enumerate(files):
        slot = hash_string(name, HASH_OFFSET) & (hash_size - 1)
        while hash_table[slot][4] != 0xFFFFFFFF:
            slot = (slot + 1) & (hash_size - 1)
        hash_table[slot] = (hash_string(name, HASH_A), hash_string(name, HASH_B), 0, 0, block_index)

    hash_words = []
    for a, b, locale, platform, block_index in hash_table:
        hash_words += [a, b, locale | (platform << 16), block_index]
    block_words = []
    for entry in blocks:
        block_words += list(entry)

    hash_bytes = struct.pack('<%dI' % len(hash_words), *encrypt(hash_words, hash_string('(hash table)', HASH_KEY)))
    block_bytes = struct.pack('<%dI' % len(block_words), *encrypt(block_words, hash_string('(block table)', HASH_KEY)))

    hash_pos = header_size + len(body)
    block_pos = hash_pos + len(hash_bytes)
    archive_size = block_pos + len(block_bytes)
    header = struct.pack('<4sIIHHIIII', b'MPQ\x1a', header_size, archive_size, 0, SECTOR_SHIFT,
                         hash_pos, block_pos, hash_size, len(blocks))
    return header + bytes(body) + hash_bytes + block_bytes


def map_header(name, flags, max_players):
    """The 512-byte HM3W block that precedes the MPQ in .w3m/.w3x files."""
    head = b'HM3W' + struct.pack('<i', 0) + name.encode('utf-8') + b'\0' + struct.pack('<ii', flags, max_players)
    return head.ljust(512, b'\0')


def build_map(name, flags, max_players, files):
    return map_header(name, flags, max_players) + build_mpq(files)
