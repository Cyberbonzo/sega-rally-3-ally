"""Back up the game's own local high-score files without changing their records."""
from pathlib import Path
import hashlib,os,time,struct,json,zlib
ROOT=Path(__file__).resolve().parents[1]
FILES=('Rally/HighScoreData.txt','ShellData/HighScoreData.txt','ShellData/HighScoreCounter.txt')
TABLE=0x789f98
TABLE_SIZE=0x36e0
CHECKPOINT=ROOT/'state/score-table.bin'
def valid_scores(data):
    return len(data)>=TABLE_SIZE+8 and data[:4]==struct.pack('<I',5) and data[4:8]==struct.pack('<I',1) and zlib.crc32(data[4:4+TABLE_SIZE])==struct.unpack_from('<I',data,4+TABLE_SIZE)[0]
def atomic(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_name(path.name+'.tmp');temp.write_bytes(data);os.replace(temp,path)
def backup():
    for name in FILES:
        path=ROOT/'game'/name
        if not path.exists():continue
        before=path.stat();data=path.read_bytes();after=path.stat()
        if not data or before.st_mtime_ns!=after.st_mtime_ns or path.read_bytes()!=data:continue
        if name=='ShellData/HighScoreData.txt' and not valid_scores(data):continue
        if name=='ShellData/HighScoreCounter.txt' and len(data)!=4:continue
        target=ROOT/'saves/latest'/name
        if target.exists() and target.read_bytes()==data:continue
        history=ROOT/'saves/history'/name
        atomic(history/(hashlib.sha256(data).hexdigest()[:16]+'.bin'),data)
        atomic(target,data)
        for old in sorted(history.glob('*.bin'),key=lambda p:p.stat().st_mtime,reverse=True)[20:]:old.unlink()
def restore_missing():
    for name in FILES:
        path=ROOT/'game'/name;saved=ROOT/'saves/latest'/name
        if not path.exists() and saved.exists():
            data=saved.read_bytes()
            if name=='ShellData/HighScoreData.txt' and not valid_scores(data):continue
            atomic(path,data)

def prepare():
    restore_missing()
    # The game file-system root is '.', with Rally as its working directory.
    # Its native '.\\ShellData' must resolve to the supplied sibling folder.
    alias=ROOT/'game/Rally/ShellData';target=ROOT/'game/ShellData'
    if not target.is_dir():raise RuntimeError('Missing game/ShellData')
    if alias.is_symlink():
        if alias.resolve()!=target.resolve():raise RuntimeError('Unexpected ShellData link')
    elif alias.exists():
        raise RuntimeError('Rally/ShellData already exists; merge saves before setup')
    else:alias.symlink_to(Path('../ShellData'),target_is_directory=True)
    scores=target/'HighScoreData.txt'
    checkpoint=CHECKPOINT.read_bytes() if CHECKPOINT.exists() else b''
    if valid_scores(checkpoint) and (not scores.exists() or not valid_scores(scores.read_bytes()) or CHECKPOINT.stat().st_mtime_ns>scores.stat().st_mtime_ns):
        atomic(scores,checkpoint)
    backup()

class Runtime:
    """Persist only the pointer-free table consumed by the native v5 reader."""
    def __init__(self):self.pid=None;self.ready=False;self.last=0;self.digest=None
    def tick(self,pids):
        now=time.monotonic()
        if now-self.last<2:return
        self.last=now
        pid=pids[0] if pids else None
        if pid!=self.pid:self.pid=pid;self.ready=False;self.digest=None
        if pid is None:return
        fd=os.open(f'/proc/{pid}/mem',os.O_RDONLY)
        try:
            phase=struct.unpack('<I',os.pread(fd,4,0x7ece10))[0]
            if phase in (39,40):self.ready=True
            if not self.ready:return
            data=os.pread(fd,TABLE_SIZE,TABLE)
            if len(data)!=TABLE_SIZE or data[:4]!=struct.pack('<I',1) or os.pread(fd,TABLE_SIZE,TABLE)!=data:return
            # Ignore merge serial changes; only record changes need checkpoints.
            digest=hashlib.sha256(data[8:]).hexdigest()
            if digest==self.digest:return
            native=struct.pack('<I',5)+data+struct.pack('<I',zlib.crc32(data))
            assert valid_scores(native)
            atomic(CHECKPOINT,native)
            atomic(ROOT/'state/progress.json',json.dumps({'schema':1,'records_sha256':digest,'saved_at':time.time(),'kind':'native high-score table: names, cars, transmissions, times'},indent=2).encode())
            self.digest=digest
            print('Native records checkpoint saved',flush=True)
        finally:os.close(fd)
