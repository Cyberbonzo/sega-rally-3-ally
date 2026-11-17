"""Select arcade difficulty and extend the native timer table for Very Easy."""
import hashlib
import os
import struct
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEVELS = ("Very Easy", "Easy", "Medium", "Hard")
ORIGINAL = "19cc7aa1ea2852aac2e9d5f44bef1d90a9effc0ffbb96961f1c9ac037c004399"
DATABASE = Path("game/Rally/ArcadeDatabase/arcadedatabase_xdata.sbf")

def replace(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as f:
        tmp = Path(f.name)
        try:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        except BaseException:
            tmp.unlink(missing_ok=True)
            raise
    try:
        tmp.chmod(path.stat().st_mode & 0o777 if path.exists() else 0o644)
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)

def selected(root=ROOT):
    path = root/"state/difficulty.txt"
    level = path.read_text().strip() if path.exists() else LEVELS[0]
    if level not in LEVELS:
        raise ValueError(f"Unknown SEGA Rally 3 difficulty: {level!r}")
    return level

def choose(level, root=ROOT):
    if level not in LEVELS:
        raise ValueError(level)
    replace(root/"state/difficulty.txt", (level+"\n").encode())

def extended(original):
    if hashlib.sha256(original).hexdigest() != ORIGINAL:
        raise ValueError("Unrecognized arcade database")
    data = bytearray(original)
    # The timing section has 54 event entries. Each difficulty has a lap
    # count and up to four rows of six time awards, preceded by a lap ID.
    for event in range(54):
        for difficulty in range(3):
            table = 0x18c4 + event*352 + difficulty*116
            laps, = struct.unpack_from("<I", original, table)
            if laps > 4:
                raise ValueError("Invalid lap count")
            for lap in range(laps):
                row = table + 4 + lap*28
                for split in range(6):
                    pos = row + 4 + split*4
                    seconds, = struct.unpack_from("<I", original, pos)
                    if seconds:
                        bonus = 20 if lap == 0 and split == 0 else 10
                        struct.pack_into("<I", data, pos, min(99, seconds+bonus))
    return bytes(data)

def configure(level, root=ROOT):
    if level not in LEVELS:
        raise ValueError(level)
    active = root/DATABASE
    backup = root/"saves/original/arcadedatabase_xdata.sbf"
    current = active.read_bytes()
    original = backup.read_bytes() if backup.exists() else current
    custom = extended(original)
    if current not in (original, custom):
        raise ValueError("Arcade database has other changes. Existing file preserved.")
    wanted = custom if level == "Very Easy" else original
    if wanted != current:
        if not backup.exists():
            replace(backup, original)
        replace(active, wanted)
    return "Easy" if level == "Very Easy" else level
