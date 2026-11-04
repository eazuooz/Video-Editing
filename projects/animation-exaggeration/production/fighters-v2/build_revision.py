"""Bind preserved A02 speech/Unity with inspected fighters; produce no platform mutation."""
from pathlib import Path
import json,hashlib,math,copy,subprocess
import numpy as np,soundfile as sf
import audio_pipeline as ap,video_pipeline as vp,caption_pipeline as cp
H=Path(__file__).resolve().parent;R=H.parents[3];L=H.parent/'local/fighters-v2';O=H.parent/'local/grid-v1';OH=H.parent/'grid-v1'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,j):ap.save(p,j)
def rel(p):return p.relative_to(R).as_posix()
def artifact(p):return {'path':rel(p),'sha256':ap.sha(p)}
def main():
 ap.require_authorized('mix');(L/'edit').mkdir(parents=True,exist_ok=True)
 baseline=load(OH/'edit-plan.json');raw,sr=sf.read(L/'voice/additional-sample-b.wav',dtype='float32');assert sr==48000
 words=load(L/'voice/additional-asr.json')['result']['chunks']
 # Measured silent gaps: paragraph1 ends26.28, paragraph2 begins27.10;
 # paragraph2 ends52.54, paragraph3 begins52.96. Cuts lie inside those gaps.
 bounds=[0,1601,3165,math.ceil(len(raw)/800)]
 insert_at=[2737,3941,12231];offset=0;inserts=[]
 for n,old in enumerate(insert_at):
  a,b=bounds[n]*800,min(bounds[n+1]*800,len(raw));frames=bounds[n+1]-bounds[n]
  data=np.pad(raw[a:b],(0,frames*800-(b-a)))
  f=L/f'voice/addition-{n+1:02}.wav';sf.write(f,data,sr,subtype='PCM_24')
  inserts.append({'id':f'add{n+1}','originalAtFrame':old,'startFrame':old+offset,'frames':frames,'sourceStartFrame':bounds[n],'sourceEndFrame':bounds[n+1],'audio':artifact(f)})
  offset+=frames
 total=baseline['totalFrames']+offset;body=total-720
 def shift(t):return t+sum(x['frames']/60 for x in inserts if t>=x['originalAtFrame']/60-.008)
 save(H/'narration-insert-map.json',{'inserts':inserts,'additionalSource':artifact(L/'voice/additional-sample-b.wav'),'oldNarrationStem':artifact(O/'edit/narration-stem.wav'),'oldBodySpeechRetained':True,'newBodyFrames':body,'totalFrames':total,'splitInObservedSilence':True})
 # Authored bilingual clauses aligned to the actual additional speech.
 paras=(H/'additional-narration.ko.txt').read_text(encoding='utf-8').strip().split('\n\n')
 units=load(H/'additional-caption-units.json');alltext=' '.join(paras)
 aliases={'킹오프파이터스15':'킹오브파이터즈피프틴','쏠도':'솔도'}
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
 # Actual gameplay and retained exact native implementation captures.
 sources={}
 for name,url,label,publisher in [('kof-ralf','https://www.youtube.com/watch?v=fjEe1S7aNJs','THE KING OF FIGHTERS XV','Cykioh'),('gg-sol','https://www.youtube.com/watch?v=Pe1CZN7txe8','GUILTY GEAR -STRIVE-','Chaos Productions Inc')]:
  f=L/f'sources/{name}.mp4';info=vp.video_stream(f);assert (info['width'],info['height'])==(1920,1080)
  sources[name]={'sourceFile':rel(f),'sourceSha256':ap.sha(f),'sourceUrl':url,'sourceAttribution':{'publisher':publisher,'url':url,'game':label},'gameLabel':label,'sourceNativeFps':60,'sourceVideoDimensions':[1920,1080],'sourceAudioEnabled':False}
 def actual(cid,scene,start,frames,src,ss,purpose):
  return {'id':cid,'scene':scene,'startFrame':start,'endFrame':start+frames,'frames':frames,'kind':'independent-gameplay',**sources[src],'sourceStart':ss,'sourceEndExclusive':ss+frames/60,'viewport':[160,90,1600,792],'pictureLabel':'실제 게임 영상','playbackSpeed':1,'loop':False,'marks':[],'teachingPurpose':purpose,'rightsFinalized':False,'recordingReusePermissionVerified':False,'creditPlacement':'description-bottom'}
 keep={'A02-'+x for x in ['E004','E005','E006','E011','E013','E014','E015','E021','E022','E024','E025','E026','E027']}
 mapping={'E001':('kof-ralf',55.3),'E002':('kof-ralf',57.9),'E002B':('kof-ralf',59.7666667),'E003':('gg-sol',104.0),'E007':('gg-sol',131.0),'E008':('kof-ralf',62.0),'E009':('kof-ralf',177.0),'E010':('kof-ralf',173.2),'E012':('kof-ralf',81.2),'E016':('kof-ralf',103.1),'E017':('kof-ralf',104.4833333),'E018':('kof-ralf',108.3),'E019':('gg-sol',313.1),'E020':('kof-ralf',133.8),'E028':('kof-ralf',194.0),'E029':('kof-ralf',200.3666667),'E030':('kof-ralf',203.6166667)}
 cuts=[];offset=0
 for old in baseline['cuts']:
  ins=next((x for x in inserts if x['originalAtFrame']==old['startFrame']),None)
  if ins:
   idx=inserts.index(ins);cursor=ins['startFrame'];remain=ins['frames']
   chunks=[[(720,'kof-ralf',41.0),(None,'kof-ralf',54.0)],[(240,'gg-sol',91.0),(392,'gg-sol',315.5),(300,'gg-sol',108.0),(None,'gg-sol',131.0)],[(288,'kof-ralf',220.0),(432,'kof-ralf',227.6),(360,'kof-ralf',154.0),(None,'kof-ralf',163.0)]][idx]
   for j,(count,src,ss) in enumerate(chunks):
    n=count if count is not None else remain
    cuts.append(actual(f'A02-F{idx+1}{j+1}',f'fighter-{idx+1}',cursor,n,src,ss,['Compare short punch with broad wind-up, torso turn, attack and return.','Read Sol sword silhouette and horizontal/rising attack direction at native speed.','Observe Ralf preparation, driven punch and recovery as one motion.'][idx]));cursor+=n;remain-=n
   assert remain==0;offset+=ins['frames']
  if old['id'] in keep or old['id']=='A02-E023':
   c=copy.deepcopy(old);c['startFrame']+=offset;c['endFrame']+=offset
  else:
   src,ss=mapping[old['id'][4:]];c=actual(old['id'],old['scene'],old['startFrame']+offset,old['frames'],src,ss,old['teachingPurpose'])
  cuts.append(c)
 # Carry Kirby's second live Needle activation into the shape passage before
 # the existing editable Unity comparison; no loop, speed change or extra silence.
 gameplay=sum(c['frames'] for c in cuts if c['kind']=='independent-gameplay');extend=round(.6*body)-gameplay
 assert 0<extend<150,extend
 kirby=next(c for c in cuts if c['id']=='A02-E023');kirby['frames']+=extend;kirby['endFrame']+=extend;kirby['sourceEndExclusive']=kirby['sourceStart']+kirby['frames']/60
 shape=next(c for c in cuts if c['id']=='A02-E024');shape['startFrame']+=extend;shape['frames']-=extend;shape['renderedStartFrame']=extend
 shape['reuseReason']='Continue the actual Needle activation through the first shape sentence, then enter the unchanged comparison at the same original speech moment.'
 p={'episode':'A02','slug':'animation-exaggeration','revision':'fighters-v2','fps':60,'width':1920,'height':1080,'totalFrames':total,'bodyFrames':body,'introFrames':120,'outroFrames':600,'cuts':cuts,'expectedGameplayShare':sum(c['frames'] for c in cuts if c['kind']=='independent-gameplay')/body,'ratioToleranceFrames':1,'outputDir':rel(L/'edit'),'outputStem':'animation-exaggeration','captionsAss':rel(L/'edit/captions.ko.ass'),'mixFile':rel(L/'edit/final-mix.wav'),'captionProtectedRect':[150,892,1784,1060],'baseline':artifact(OH/'edit-plan.json'),'insertionMap':artifact(H/'narration-insert-map.json'),'nativeSourceClosure':artifact(OH/'saved-scene-source-manifest.json'),'baselinePreserved':True,'humanFinalReview':False,'platformMutation':False}
 vp.validate_plan(p);save(H/'edit-plan.json',p)
 save(H/'source-review.json',{'sources':sources,'sourceKind':'independent-gameplay','researchLessonFootageIncluded':False,'reviewedContacts':[artifact(x) for x in (L/'source-review').glob('*.jpg')],'publisherPolicies':['https://www.arcsystemworks.com/video-policy/','https://www.snk-corp.co.jp/guide/terms/','https://www.snk-corp.co.jp/faq/'],'publisherPolicyReviewed':'2026-11-04','rightsAssessment':'Publisher policies allow qualifying commentary/gameplay uses; they do not license a recorder\'s distinct contribution. Metadata has no explicit reusable recording license. Local analytical excerpts only, no platform upload authorized or performed; final public reuse basis remains to resolve.','recordingReusePermissionVerified':False,'audioDecision':'New source audio muted; source music not detached/reused. Existing licensed Nimbus background retained.','primaryGames':['The King of Fighters XV','Guilty Gear -Strive-',"Kirby\'s Adventure"],'nintendoExampleCount':{'numerator':1,'denominator':3,'basis':'Kirby Nintendo basis retained from grid-v1 source records'},'genreChoiceReason':'User specifically selected fighting games to show exaggerated articulated attack movement; Kirby preserves contrasting shape overshoot.'})
 save(H/'checkpoint.json',{'episode':'A02','revision':'fighters-v2','status':'source-bound-captions-and-audio-prepared','durationSeconds':total/60,'gameplayShare':p['expectedGameplayShare'],'additionalVoiceSeconds':offset/60,'nextAction':'Render annotated actual footage and native reuse, encode pair, inspect final captions/motion/audio.','baselinePreserved':True,'humanFinalReview':False})
 print(json.dumps({'seconds':total/60,'cuts':len(cuts),'cues':len(out),'actualShare':p['expectedGameplayShare'],'extendKirbyFrames':extend,'newVoiceGain':gain,'masterGain':master_gain,'alignment':align['matchingCharacterCoverage']}))
if __name__=='__main__':main()
