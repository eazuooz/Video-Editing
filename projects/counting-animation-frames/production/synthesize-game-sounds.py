"""Export only original input/hit events from actual capture logs as game SFX."""
from pathlib import Path
import json,wave,subprocess,sys,numpy as np
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).parent
VERSION='v3' if '--v3' in sys.argv else 'v2'
DEST=ROOT/f'shared/assets/counting-animation-frames/playtests-{VERSION}';SR=48000
selected=next((a for a in sys.argv[1:] if not a.startswith('--')),None)
for mode in ([selected] if selected else ['rate','interval','poses','pause','render']):
    e=json.loads((BASE/f'{mode}-{VERSION}-input-log.json').read_text(encoding='utf-8'))
    assert all(e['assertions'].values()), 'Executable mechanics assertion missing'
    audio=np.zeros((round(e['seconds']*SR),2),np.float32)
    for event in e['sounds']:
        f,d=(310,.06) if event['kind']=='input' else (620,.14)
        t=np.arange(round(d*SR))/SR
        signal=np.sin(2*np.pi*(f*t-65*t*t))*np.exp(-t*23)*np.minimum(t/.008,1)*.09
        a=round(event['time']*SR);b=min(len(audio),a+len(signal))
        for ch in range(2):audio[a:b,ch]+=signal[:b-a]
    wav=DEST/f'{mode}.wav'
    with wave.open(str(wav),'wb') as w:
        w.setparams((2,2,SR,len(audio),'NONE','not compressed'))
        w.writeframes((np.clip(audio,-.9,.9)*32767).astype('<i2').tobytes())
    target=DEST/f'{mode}-sound.mp4'
    if target.exists():raise RuntimeError(f'Preserve existing {target}')
    subprocess.check_call(['ffmpeg','-v','error','-n','-i',str(DEST/f'{mode}.mp4'),'-i',str(wav),'-c:v','copy','-c:a','aac','-b:a','192k','-t',str(e['seconds']),'-movflags','+faststart',str(target)])
    print(mode, 'verified input/hit sound events',len(e['sounds']))
