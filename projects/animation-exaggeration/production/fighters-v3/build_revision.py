"""Bind preserved A02 speech/Unity with inspected fighters; produce no platform mutation."""
from pathlib import Path
import json,hashlib,math,copy,subprocess
import numpy as np,soundfile as sf
import audio_pipeline as ap,video_pipeline as vp,caption_pipeline as cp
H=Path(__file__).resolve().parent;R=H.parents[3];L=H.parent/'local/fighters-v3';O=H.parent/'local/grid-v1';OH=H.parent/'grid-v1'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,j):ap.save(p,j)
def rel(p):return p.relative_to(R).as_posix()
def artifact(p):return {'path':rel(p),'sha256':ap.sha(p)}
def main():
 ap.require_authorized('mix');(L/'edit').mkdir(parents=True,exist_ok=True)
 baseline=load(OH/'edit-plan.json');raw,sr=sf.read(L/'voice/additional-qwen.wav',dtype='float32');assert sr==48000
 words=load(L/'voice/additional-asr.json')['result']['chunks']
 bounds=load(H/'qwen-voice-record.json')['boundsFrames']
 insert_at=[2737,3941,12231];offset=0;inserts=[]
 for n,old in enumerate(insert_at):
  a,b=bounds[n]*800,min(bounds[n+1]*800,len(raw));frames=bounds[n+1]-bounds[n]
  data=np.pad(raw[a:b],(0,frames*800-(b-a)))
  f=L/f'voice/addition-{n+1:02}.wav';sf.write(f,data,sr,subtype='PCM_24')
  inserts.append({'id':f'add{n+1}','originalAtFrame':old,'startFrame':old+offset,'frames':frames,'sourceStartFrame':bounds[n],'sourceEndFrame':bounds[n+1],'audio':artifact(f)})
  offset+=frames
 total=baseline['totalFrames']+offset;body=total-720
 def shift(t):return t+sum(x['frames']/60 for x in inserts if t>=x['originalAtFrame']/60-.008)
 save(H/'narration-insert-map.json',{'inserts':inserts,'additionalSource':artifact(L/'voice/additional-qwen.wav'),'oldNarrationStem':artifact(O/'edit/narration-stem.wav'),'oldBodySpeechRetained':True,'newBodyFrames':body,'totalFrames':total,'splitInObservedSilence':True})
 # Authored bilingual clauses aligned to the actual additional speech.
 paras=(H/'additional-narration.ko.txt').read_text(encoding='utf-8').strip().split('\n\n')
 units=load(H/'additional-caption-units.json');alltext=' '.join(paras)
 aliases={'킹오브파이터즈15':'킹오브파이터즈피프틴','킹오브파이터스15':'킹오브파이터즈피프틴','길티기어스트라이브':'길티기어스트라이브','셜미':'셸미','쉘미':'셸미'}
 starts,ends,align=cp.align_characters(alltext,words,len(raw)/sr,aliases,.96)
 cues=load(O/'edit/captions.json')['cues'];out=[]
 for c in cues:
  c=copy.deepcopy(c);c['start']=shift(c['start']);c['end']=shift(c['end']-.00001)+.00001
  # Existing endpoints may differ from the original frame join by a few ms.
  for ins in inserts:
   end=ins['startFrame']/60
   if c['start']<end<c['end'] and c['end']-end<.02:c['end']=end
  out.append(c)
 pos=0
 for i,(paragraph,rows) in enumerate(zip(paras,units)):
  assert cp.normalized(paragraph,{})==cp.normalized(' '.join(x[0] for x in rows),{})
  ins=inserts[i];origin=ins['startFrame']/60-ins['sourceStartFrame']/60
  for j,(ko,en) in enumerate(rows):
   size=len(cp.normalized(ko,aliases));start=starts[pos]+origin;end=ends[pos+size-1]+origin
   out.append({'paragraph':ins['id'],'scene':f'fighter-{i+1}','line':j,'start':start,'end':end,'ko':ko,'en':en,'emphasis':{'ko':None,'en':None},'twoLineReason':None});pos+=size
 out.sort(key=lambda c:c['start'])
 fontfile=Path('C:/Windows/Fonts/NotoSansKR-VF.ttf');font=cp.measured_font(fontfile,500);bold=cp.measured_font(fontfile,700)
 layouts=[]
 for lang in ('ko','en'):
  ass=cp.ass_header('Noto Sans KR');srt=[]
  for n,c in enumerate(out,1):
   c['cue']=n
   if n>1:assert c['start']>=out[n-2]['end']-.02,(n,c,out[n-2])
   wrapped=cp.wrap(c[lang],font);assert wrapped is not None
   g=cp.geometry('\n'.join(wrapped),font,bold,c.get('emphasis',{}).get(lang));ass+=cp.ass_events(c,g,lang)
   srt.append(f'{n}\n{cp.srt_stamp(c["start"])} --> {cp.srt_stamp(c["end"])}\n'+ '\n'.join(wrapped)+'\n')
   layouts.append({'cue':n,'language':lang,**g})
  (L/f'edit/captions.{lang}.ass').write_text(ass,encoding='utf-8');(L/f'edit/captions.{lang}.srt').write_text('\n'.join(srt),encoding='utf-8')
 save(L/'edit/captions.json',{'style':'boxed-white-forest-v1','cuePolicy':'caption-clause-keyword-v1','cues':out})
 save(L/'edit/caption-layout.json',{'font':artifact(fontfile) if fontfile.is_relative_to(R) else {'path':str(fontfile),'sha256':ap.sha(fontfile)},'size':48,'center':[960,970],'cues':layouts})
 save(H/'additional-speech-alignment-review.json',{'asr':artifact(L/'voice/additional-asr.json'),'alignment':align,'allThreeParagraphsRead':True,'minorOrthographyAliases':aliases,'actualListeningPerformed':False})
 # Every old voice sample is copied, not time-stretched or regenerated.
 oldvoice,rate=sf.read(O/'edit/narration-stem.wav',dtype='float32',always_2d=True);assert rate==sr
 voice=np.zeros((total*800,2),np.float32);previous=0;cursor=0;proof=[]
 oldrms=np.sqrt(np.mean(oldvoice[abs(oldvoice).max(axis=1)>.025]**2));newrms=np.sqrt(np.mean(raw[abs(raw)>.025]**2));gain=float(oldrms/newrms)
 for ins in inserts:
  at=ins['originalAtFrame']*800;n=at-previous;voice[cursor:cursor+n]=oldvoice[previous:at];cursor+=n
  data,_=sf.read(R/ins['audio']['path'],dtype='float32');voice[cursor:cursor+len(data)]=data[:,None]*gain
  proof.append({'oldStartSample':previous,'oldEndSample':at,'newStartSample':cursor-n,'exactSampleEquality':bool(np.array_equal(voice[cursor-n:cursor],oldvoice[previous:at]))});cursor+=len(data);previous=at
 tail=oldvoice[previous:];voice[cursor:cursor+len(tail)]=tail;assert cursor+len(tail)==len(voice)
 sf.write(L/'edit/narration-stem.wav',voice,sr,subtype='PCM_24')
 music_source=R/'shared/assets/music/youtube-audio-library/Nimbus-Eveningland.mp3'
 subprocess.run(['ffmpeg','-y','-v','error','-stream_loop','-1','-i',str(music_source),'-t',str(total/60),'-ar','48000','-ac','2','-c:a','pcm_s24le',str(L/'edit/music-decoded.wav')],check=True)
 music,_=sf.read(L/'edit/music-decoded.wav',dtype='float32',always_2d=True);music=music[:len(voice)]
 if len(music)<len(voice):music=np.pad(music,((0,len(voice)-len(music)),(0,0)))
 music*=10**(-28/20)/max(1e-9,float(np.sqrt(np.mean(music**2))))
 fade=np.minimum(np.arange(len(music))/48000,(len(music)-1-np.arange(len(music)))/96000).clip(0,1);music*=fade[:,None]
 sf.write(L/'edit/music-stem.wav',music,sr,subtype='PCM_24')
 mixed=voice+music;peak=float(np.max(abs(mixed)));master_gain=min(1,10**(-2.4/20)/peak);mixed*=master_gain
 sf.write(L/'edit/final-mix.wav',mixed,sr,subtype='PCM_24')
 save(L/'edit/audio-build.json',{'duration':total/60,'outputs':[artifact(L/'edit/final-mix.wav')],'voiceGainForNewInserts':gain,'masterGain':master_gain,'oldPcmSegmentEquality':proof,'oldVoiceSpeed':1,'gameTrack':'New sources muted; do not attach old Tekken/VF audio to different games. Nimbus bed retained continuously.','music':artifact(music_source),'humanListening':False})
 from build_cut_plan import build
 build(baseline,inserts,total,body,out)
 print('Assembly prepared',total/60,'seconds',len(out),'caption cues')
if __name__=='__main__':main()
