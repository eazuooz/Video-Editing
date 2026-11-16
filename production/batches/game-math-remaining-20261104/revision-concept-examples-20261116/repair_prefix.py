"""Remove an unclear leading fragment from our NEW bridge, at its aligned word boundary."""
import os,shutil
from prepare import *
def main():
 import numpy as np,soundfile as sf
 p=HERE/'local/voice/raw/M23-01.wav';receipt=HERE/'voice-prefix-edit.json'
 if receipt.exists() and read(receipt)['newRawSha256']==sha(p):return
 rec=read(HERE/'local/asr/M23-01.json');assert rec['sha256']==sha(p)
 start=next(w['timestamp'][0] for w in rec['words'] if w['text'].strip()=='실제')
 x,sr=sf.read(p,dtype='float32');oldsha=sha(p);backup=HERE/'local/voice/history'/('M23-01-prefix-source-'+oldsha[:16]+'.wav');shutil.copy2(p,backup)
 x=x[round(start*sr):].copy();n=round(sr*.006);x[:n]*=np.linspace(0,1,n,dtype='float32');temp=p.with_name('M23-01-cropped.wav');sf.write(temp,x,sr,subtype='PCM_16');os.replace(temp,p)
 choices=read(HERE/'selections.json');choices['M23-01']['ko'][0]='실제 게임에서 보겠습니다.';choices['M23-01']['en'][0]="Let's look at an actual game.";save(HERE/'selections.json',choices)
 texts=read(HERE/'local/voice/take-texts.json');texts['M23-01'].update(text=' '.join(choices['M23-01']['ko']),sha256=sha(p),editing='Leading unclear fragment removed at aligned start of 실제;6ms edge fade; no speech tempo change.');save(HERE/'local/voice/take-texts.json',texts)
 save(receipt,dict(originalRawSha256=oldsha,retainedSource=str(backup),trimStartSeconds=start,edgeFadeSeconds=.006,newRawSha256=sha(p),newFirstSentence=choices['M23-01']['ko'][0],originalLectureVoiceUntouched=True))
 print('New bridge prefix repaired at',start,'s; main lecture untouched')
if __name__=='__main__':main()
