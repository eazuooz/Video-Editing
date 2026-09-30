"""The prototype's own collision/input sound effects, from recorded event times."""
from pathlib import Path
import json, wave, subprocess, sys
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).parent
DEST=ROOT/'shared/assets/deconstruct-analyze-rebuild/playtests-v3'
SR=48000
for mode in (sys.argv[1:] or ['landing','retry','variants','observe']):
    evidence=json.loads((BASE/f'{mode}-v3-input-log.json').read_text(encoding='utf-8'))
    audio=np.zeros((45*SR,2),dtype=np.float32)
    settings={'jump':(500,0.09),'land':(170,0.055),'fail':(140,0.16),'success':(740,0.17)}
    for event in evidence['sounds']:
        f,d=settings[event['kind']];t=np.arange(int(d*SR))/SR
        wavelet=np.sin(2*np.pi*(f*t+(220 if event['kind']=='jump' else -60)*t*t))*np.exp(-t*27)
        wavelet*=np.minimum(t/0.006,1)*.14
        start=int(event['time']*SR);end=min(len(audio),start+len(wavelet))
        if end<=start:continue
        pan=[.8,.35] if event['lane']==0 else [.35,.8]
        for channel in range(2):audio[start:end,channel]+=wavelet[:end-start]*pan[channel]
    audio=np.clip(audio,-.9,.9)
    wav=DEST/f'{mode}.wav'
    with wave.open(str(wav),'wb') as w:
        w.setparams((2,2,SR,len(audio),'NONE','not compressed'));w.writeframes((audio*32767).astype('<i2').tobytes())
    out=DEST/f'{mode}-sound.mp4'
    if out.exists():raise RuntimeError(f'Preserve existing output {out}')
    subprocess.check_call(['ffmpeg','-v','error','-n','-i',str(DEST/f'{mode}.mp4'),'-i',str(wav),'-c:v','copy','-c:a','aac','-b:a','192k','-t','45','-movflags','+faststart',str(out)])
    print(mode,len(evidence['input']),len(evidence['sounds']),len(evidence['outcomes']))
