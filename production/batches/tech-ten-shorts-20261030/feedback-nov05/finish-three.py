"""Finite, local-only continuation for exactly 2, 6 and 8 as the voice renderer seals each pair."""
from build import *
import sys,time
for n in (2,6,8):
    pin=WORK/f'{n:02}-r2'/'voice-files.json';pin.parent.mkdir(exist_ok=True)
    if not pin.exists():
        paths={}
        while True:
            for j in (1,2):
                candidates=[(WORK/'gpu-voice.log',ROOT/f'shared/output/tech-ten-feedback-nov05/gpu/chunks/{n:02}-{j:02}-scene.wav',f'{n:02}-{j:02}-scene'),(WORK/'voice.log',ROOT/f'shared/output/tech-ten-feedback-nov05/extra-speech/chunks/{n:02}-{j:02}.wav',f'{n:02}-{j:02}')]
                for log,p,key in candidates:
                    if log.exists():
                        raw=log.read_bytes();txt=raw.decode('utf-16' if raw.startswith(b'\xff\xfe') else 'utf-8',errors='replace')
                        if f'Rendered {key} (' in txt and p.is_file():
                            paths[str(j)]=dict(path=str(p),sha256=sha(p));break
            if len(paths)==2:break
            time.sleep(4)
        save(pin,paths)
    build(n)
    run([sys.executable,'-X','utf8','-u',str(HERE/'check.py'),str(n)])
