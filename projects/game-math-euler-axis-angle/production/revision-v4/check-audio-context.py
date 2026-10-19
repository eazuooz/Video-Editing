"""Resolve the isolated voice projection flag against its actual mixed background."""
from pathlib import Path
import json,hashlib,subprocess,sys
import numpy as np
import soundfile as sf
P=Path(__file__).resolve().parents[2];O=P/'production/local/revision-v4';Q=O/'qa'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
qa=read(Q/'audio-continuity.json'); rows=qa['flaggedVoiceTransferWindows'];results=[]
FF=r'C:\Users\1\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0-full_build\bin\ffmpeg.exe'
for r in rows:
 a=max(0,r['time']-3);duration=6.4
 # Three seconds of pre-roll establishes the original compressor state.
 bg=Q/('context-'+r['scene']+'-ducked-game.wav')
 if '--use-extracted-context' not in sys.argv:
  subprocess.run([FF,'-v','error','-y','-ss',str(a),'-i',str(O/'narration-stem.wav'),'-ss',str(a),'-i',str(O/'game-stem.wav'),'-filter_complex','[1:a][0:a]sidechaincompress=threshold=0.08:ratio=2.2:attack=15:release=280:makeup=1[out]','-map','[out]','-t',str(duration),'-ar','24000','-ac','1','-c:a','pcm_f32le',str(bg)],check=True)
 game,sr=sf.read(bg);voice,_=sf.read(Q/'stem-mono.wav',start=round(a*sr),frames=len(game));encoded,_=sf.read(Q/'encoded-mono.wav',start=round(a*sr),frames=len(game))
 i=round((r['time']-a)*sr);j=i+round(.4*sr)
 X=np.column_stack([voice[i:j],game[i:j]])
 # Solve the two-component regression explicitly, avoiding platform BLAS
 # thread-pool initialization for this tiny diagnostic calculation.
 v,g=X.T;z=encoded[i:j];vv=np.sum(v*v);gg=np.sum(g*g);vg=np.sum(v*g);vz=np.sum(v*z);gz=np.sum(g*z);det=vv*gg-vg*vg
 beta=[(vz*gg-gz*vg)/det,(gz*vv-vz*vg)/det]
 db=lambda x:float(20*np.log10(max(abs(x),1e-12)))
 vc=v-v.mean();gc=g-g.mean();corr=float(np.sum(vc*gc)/np.sqrt(np.sum(vc*vc)*np.sum(gc*gc)))
 value=dict(scene=r['scene'],start=r['time'],end=r['time']+.4,originalProjectionDb=r['estimatedVoiceTransferDb'],contextStart=a,contextSeconds=duration,voiceCoefficientDb=db(beta[0]),gameCoefficientDb=db(beta[1]),voiceGameCorrelation=corr,method='Two-component least squares using actual source voice and ordinary ducked original game sound, 3-second pre-roll; background correlation separated from voice gain.',humanListening='pending')
 value['technicalVoiceTransferPassed']=abs(value['voiceCoefficientDb'])<1
 results.append(value)
out=dict(flags=results,allTechnicalVoiceTransferPassed=all(r['technicalVoiceTransferPassed'] for r in results),noHumanListeningClaimed=True)
(Q/'flag-context-review.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(out,ensure_ascii=False))
