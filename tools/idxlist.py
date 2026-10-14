"""idxlist.py <IDXFILES.IDX> <IDXFILES.IMG> [outdir]: list (and optionally dump) the entries of the Ducati World archive.
Index = 16-byte records {u32 offset, u32 stored size, u32 unpacked size, u32 flags}; flags 3 = compressed (dumped as-is).
"""
import os, struct, sys

idx = open(sys.argv[1], 'rb').read()
img = open(sys.argv[2], 'rb')
out = sys.argv[3] if len(sys.argv) > 3 else None
if out: os.makedirs(out, exist_ok=True)
for i in range(len(idx) // 16):
    off, st, un, fl = struct.unpack_from('<4I', idx, i * 16)
    if st == 0 and off == 0 and i: continue
    img.seek(off); head = img.read(min(st, 16))
    tag = head[:8].decode('latin1') if head[:8].isascii() and head[:4].isalnum() else head[:8].hex()
    print('%3d %08x %8x %8x %d %s' % (i, off, st, un, fl, tag))
    if out:
        img.seek(off)
        open(os.path.join(out, '%03d%s.bin' % (i, '_z' if fl else '')), 'wb').write(img.read(st))
