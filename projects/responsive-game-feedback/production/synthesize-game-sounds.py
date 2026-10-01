from pathlib import Path
import json,wave,subprocess,sys,numpy as np
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).parent;SR=48000
for mode in [v for v in sys.argv[1:] if not v.startswith('--')] or ['receipt','blocked','menu','cutscene','pending','context']:
    version='v4' if mode=='blocked' else 'v3' if mode in ['receipt','context'] else 'v2' if mode in ['menu','pending'] else 'v1'
    dest=ROOT/f'shared/assets/responsive-game-feedback/playtests-{version}'
    evidence=json.loads((BASE/f'{mode}-{version}-input-log.json').read_text(encoding='utf-8'))
    if not evidence['assertions'].startswith('passed'):raise ValueError('Actual input evidence required')
    audio=np.zeros((round(evidence['seconds']*SR),2),np.float32)
    for event in evidence['sounds']:
        frequency,length={'received':(510,.075),'refusal':(260,.10),'complete':(780,.14)}[event['kind']]
        time=np.arange(round(length*SR))/SR
        signal=np.sin(2*np.pi*(frequency*time+60*time*time))*np.exp(-time*18)*np.minimum(time/.008,1)*.08
        start=round(event['t']*SR);end=min(len(audio),start+len(signal));pan=[.75,.35] if event['panel']==0 else [.35,.75]
        for channel in range(2):audio[start:end,channel]+=signal[:end-start]*pan[channel]
    wav=dest/f'{mode}.wav'
    with wave.open(str(wav),'wb') as stream:
        stream.setparams((2,2,SR,len(audio),'NONE','not compressed'));stream.writeframes((np.clip(audio,-.9,.9)*32767).astype('<i2').tobytes())
    output=dest/f'{mode}-sound.mp4'
    if output.exists():raise RuntimeError(f'Preserve existing {output}')
    subprocess.check_call(['ffmpeg','-v','error','-n','-i',str(dest/f'{mode}.mp4'),'-i',str(wav),'-c:v','copy','-c:a','aac','-b:a','192k','-t',str(evidence['seconds']),'-movflags','+faststart',str(output)])
    print(mode,'actual event audio',len(evidence['sounds']))
