from pathlib import Path
import json,wave,subprocess,sys,numpy as np
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).parent;VERSION='v2' if '--v2' in sys.argv else 'v1';DEST=ROOT/f'shared/assets/meaningful-quests/playtests-{VERSION}';SR=48000
for mode in ['comparison','delivery','shortcut']:
    log=BASE/f'{mode}-{VERSION}-input-log.json'
    if not log.exists():log=BASE/f'{mode}-input-log.json'
    e=json.loads(log.read_text(encoding='utf-8'));audio=np.zeros((round(e['seconds']*SR),2),np.float32)
    settings={'pickup':(620,.13),'blocked':(170,.08),'bridge-open':(880,.3),'delivery':(730,.22),'drop-items':(310,.11),'new-area-reached':(990,.25)}
    for v in e['sounds']:
        f,d=settings[v['kind']];t=np.arange(round(d*SR))/SR;signal=np.sin(2*np.pi*(f*t-50*t*t))*np.exp(-t*15)*np.minimum(t/.008,1)*.11
        a=round(v['time']*SR);b=min(len(audio),a+len(signal));pan=[.75,.4] if v['lane']==0 else [.4,.75]
        for k in range(2):audio[a:b,k]+=signal[:b-a]*pan[k]
    wav=DEST/f'{mode}.wav'
    with wave.open(str(wav),'wb') as w:w.setparams((2,2,SR,len(audio),'NONE','not compressed'));w.writeframes((np.clip(audio,-.9,.9)*32767).astype('<i2').tobytes())
    out=DEST/f'{mode}-sound.mp4'
    if out.exists():raise RuntimeError(f'Preserve existing {out}')
    subprocess.check_call(['ffmpeg','-v','error','-n','-i',str(DEST/f'{mode}.mp4'),'-i',str(wav),'-c:v','copy','-c:a','aac','-b:a','192k','-t',str(e['seconds']),'-movflags','+faststart',str(out)])
    print(mode,'events',len(e['outcomes']),'final',e['finalState'])
