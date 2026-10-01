from pathlib import Path
import json,wave,subprocess,sys,numpy as np
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).parent;SR=48000
for mode in sys.argv[1:] or ['timing','specificity','strength','honesty','placement']:
    if mode not in ['timing','specificity','strength','honesty','placement']:raise ValueError(mode)
    version='v2' if mode in ['timing','strength'] else 'v1';dest=ROOT/f'shared/assets/praise-player/playtests-{version}'
    evidence=json.loads((BASE/f'{mode}-{version}-input-log.json').read_text(encoding='utf-8'))
    audio=np.zeros((round(evidence['seconds']*SR),2),np.float32)
    for event in evidence['sounds']:
        frequency,length={'block':(690,.11),'dodge':(940,.09),'hit':(170,.15)}[event['kind']]
        time=np.arange(round(length*SR))/SR
        signal=np.sin(2*np.pi*(frequency*time+90*time*time))*np.exp(-time*16)*np.minimum(time/.008,1)*.09
        start=round(event['time']*SR);end=min(len(audio),start+len(signal));pan=[.75,.35] if event['panel']==0 else [.35,.75]
        for channel in range(2):audio[start:end,channel]+=signal[:end-start]*pan[channel]
    # Outcome sounds stay identical in the paired panels. Recognition is visual
    # only, so the timing comparison does not introduce an audio confound.
    wav=dest/f'{mode}.wav'
    with wave.open(str(wav),'wb') as stream:
        stream.setparams((2,2,SR,len(audio),'NONE','not compressed'));stream.writeframes((np.clip(audio,-.9,.9)*32767).astype('<i2').tobytes())
    output=dest/f'{mode}-sound.mp4'
    if output.exists():raise RuntimeError(f'Preserve existing {output}')
    subprocess.check_call(['ffmpeg','-v','error','-n','-i',str(dest/f'{mode}.mp4'),'-i',str(wav),'-c:v','copy','-c:a','aac','-b:a','192k','-t',str(evidence['seconds']),'-movflags','+faststart',str(output)])
    print(mode,'verified actual outcomes',len(evidence['finalState'][0]['events']))
