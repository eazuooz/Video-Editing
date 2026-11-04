from pathlib import Path
import sys,time,json,math
import numpy as np,soundfile as sf
from scipy.signal import resample_poly
import audio_pipeline as ap
H=Path(__file__).resolve().parent;L=H.parent/'local/fighters-v3';R=H.parents[3]
def main():
 ap.require_authorized('mix')
 final=L/'voice/qwen/additional-qwen.timing.json'
 if '--wait' in sys.argv:
  while not final.exists():time.sleep(5)
 assert final.is_file()
 chunks=[];bounds=[0];records=[]
 for i in range(1,4):
  source=L/f'voice/qwen/chunks/F{i:02d}-scene.wav';y,sr=sf.read(source,dtype='float32')
  if y.ndim>1:y=y.mean(axis=1)
  g=math.gcd(sr,48000);y=resample_poly(y,48000//g,sr//g)
  size=2400;a=y[:len(y)//size*size].reshape(-1,size);db=20*np.log10(np.sqrt(np.mean(a*a,axis=1))+1e-10)
  active=db[db>max(db.max()-25,-60)];before=float(np.median(active));gain=10**(np.clip(-22-before,-12,12)/20)
  y*=gain
  frames=math.ceil((len(y)+9600)/800);y=np.pad(y,(0,frames*800-len(y)))
  out=L/f'voice/addition-{i:02d}.wav';sf.write(out,y,48000,subtype='PCM_24');chunks.append(y);bounds.append(bounds[-1]+frames)
  records.append({'paragraph':i,'source':ap.artifact(source),'frames':frames,'activeMedianDbfsBefore':before,'gainDb':20*math.log10(gain),'noSpeedChange':True,'tailPaddingSeconds':(frames*800-len(y)+9600)/48000})
 sf.write(L/'voice/additional-qwen.wav',np.concatenate(chunks),48000,subtype='PCM_24')
 ap.save(H/'qwen-voice-record.json',{'model':'Qwen3-TTS-12Hz-1.7B-Base','reference':'shared/voice-reference/reference-15-35s.wav','boundsFrames':bounds,'paragraphs':records,'source':ap.artifact(L/'voice/additional-qwen.wav'),'actualListening':False,'latestUserInstruction':'일래븐랩스 말고 tts 로 만들면돼'})
 print(bounds,flush=True)
if __name__=='__main__':main()
