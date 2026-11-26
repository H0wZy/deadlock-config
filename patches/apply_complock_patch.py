"""Inject patches/complock_mirage_minimap.css into CompLock (addons/pak01_dir.vpk).

The rules go at the end of panorama/styles/clean_minimap.vcss_c inside the VPK (v2, data inline).
Running it again replaces the previous injection, so: edit the .css, run this, open the game.
Run it with Deadlock closed: the game reads the VPK only at startup.

Usage: py patches/apply_complock_patch.py [path/to/pak01_dir.vpk]
"""
import hashlib, os, re, struct, subprocess, sys, zlib

HERE = os.path.dirname(os.path.abspath(__file__))
VPK = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'addons', 'pak01_dir.vpk')
CSS = os.path.join(HERE, 'complock_mirage_minimap.css')
TARGET = (b'vcss_c', b'panorama/styles', b'clean_minimap')
BEGIN, END = b'/* mirage-minimap-fix:begin */', b'/* mirage-minimap-fix:end */'
LEGACY = b'/* fix-mirage-minimap'  # first version of this patch: appended at the end, no end marker
HDR = 28  # VPK v2 header


def game_running():
    try:
        out = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq deadlock.exe'], capture_output=True).stdout
    except OSError:
        return False
    return b'deadlock.exe' in out.lower()


def find_entry(f):
    """Offset of TARGET's 18-byte directory entry (tree: extension / path / name)."""
    def cstr(j):
        k = f.index(b'\0', j)
        return bytes(f[j:k]), k + 1
    j = HDR
    while True:
        ext, j = cstr(j)
        if not ext:
            break
        while True:
            path, j = cstr(j)
            if not path:
                break
            while True:
                name, j = cstr(j)
                if not name:
                    break
                if (ext, path, name) == TARGET:
                    return j
                j += 18 + struct.unpack('<H', f[j + 4:j + 6])[0]
    sys.exit('clean_minimap.vcss_c not found: is this the CompLock VPK?')


def header(f):
    sig, ver, tree, data, amd5, omd5, sigsz = struct.unpack('<7I', f[:HDR])
    if (sig, ver, amd5, omd5, sigsz) != (0x55AA1234, 2, 0, 48, 0) or len(f) != HDR + tree + data + omd5:
        sys.exit('Unexpected VPK layout (not a CompLock pak01_dir.vpk?)')
    return tree, data


def entry_data(f, tree, e):
    crc, pre, idx, off, ln, term = struct.unpack('<IHHIIH', f[e:e + 18])
    assert idx == 0x7FFF and term == 0xFFFF and pre == 0, 'file data is not inline'
    res = bytes(f[HDR + tree + off:HDR + tree + off + ln])
    assert zlib.crc32(res) == crc, 'CRC mismatch in the VPK'
    return res, off, ln


def new_css():
    text = open(CSS, encoding='utf-8-sig').read()
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.S)        # comments stay in the .css only
    rules = re.sub(r'\s+', ' ', text).strip().replace('} ', '}\n')
    return b'\n' + BEGIN + b'\n' + rules.encode() + b'\n' + END + b'\n', rules


def strip_old(css):
    i = css.find(BEGIN)
    if i >= 0:
        k = css.find(END, i)
        css = css[:i] + (css[k + len(END):] if k >= 0 else b'')
    i = css.find(LEGACY)
    if i >= 0:
        css = css[:i]
    return css.rstrip(b'\n') + b'\n'


def main():
    if game_running():
        sys.exit('Close Deadlock first: the game reads the VPK only at startup.')
    f = bytearray(open(VPK, 'rb').read())
    tree, data = header(f)
    e = find_entry(f)
    res, off, ln = entry_data(f, tree, e)

    # resource: 16-byte header, block table, DATA last = crc32(css) + u16 0 + css text
    assert struct.unpack('<I', res[8:12])[0] == 8
    bc = struct.unpack('<I', res[12:16])[0]
    dpos = 16 + 12 * (bc - 1)
    assert res[dpos:dpos + 4] == b'DATA'
    dstart = dpos + 4 + struct.unpack('<I', res[dpos + 4:dpos + 8])[0]
    assert dstart + struct.unpack('<I', res[dpos + 8:dpos + 12])[0] == len(res)
    block, rules = new_css()
    css = strip_old(res[dstart + 6:]) + block
    new = bytearray(res[:dstart] + struct.pack('<IH', zlib.crc32(css), 0) + css)
    struct.pack_into('<I', new, 0, len(new))                 # resource size
    struct.pack_into('<I', new, dpos + 8, len(new) - dstart)  # DATA block size

    # our previous copy is the last thing in the data section: overwrite it, else append
    at = off if off + ln == data else data
    body = f[:HDR + tree + at] + new
    struct.pack_into('<IHHIIH', body, e, zlib.crc32(new), 0, 0x7FFF, at, len(new), 0xFFFF)
    struct.pack_into('<I', body, 12, at + len(new))          # header: data section size
    om = hashlib.md5(body[HDR:HDR + tree]).digest() + hashlib.md5(b'').digest()
    om += hashlib.md5(bytes(body) + om).digest()
    tmp = VPK + '.tmp'
    with open(tmp, 'wb') as out:
        out.write(bytes(body) + om)
    os.replace(tmp, VPK)

    # check what was written
    g = open(VPK, 'rb').read()
    tree2, _ = header(g)
    got, _, _ = entry_data(g, tree2, find_entry(g))
    assert got == bytes(new) and hashlib.md5(g[:-16]).digest() == g[-16:]
    scale = re.search(r'ui-scale:\s*([\d.]+%)', rules)
    print('CompLock patched: clean_minimap.vcss_c', ln, '->', len(new), 'bytes; centered map ui-scale',
          scale.group(1) if scale else '?')


if __name__ == '__main__':
    main()
