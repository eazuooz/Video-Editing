"""Restore the preferred v2 narration, removing only source-creator passages."""
from pathlib import Path
import json,hashlib,datetime,copy,subprocess,sys
import numpy as np,soundfile as sf
R=Path(__file__).resolve().parents[4];P=R/'projects/game-reward-planning';D=P/'production/reference-preserving-v2';B=P/'production/local/reference-preserving-v2/edit';O=B/'original-deletion-v4';O.mkdir(exist_ok=True);S=P/'script/original-deletion-v4';S.mkdir(exist_ok=True)
sys.path.insert(0,str(R/'qwen3-tts'))
from build_translated_srt import timestamp
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
assert sha(B/'game-reward-planning-v2-captioned.mp4')=='b45ea859ee2fbd2e344c4f68ffc814cf69ffb3eac7cfdbb7a89827d4e741cf9d'
assert sha(B/'game-reward-planning-v2-clean.mp4')=='4a44ccb6e3e3e29052cec0bc0747e732c9728893eb0ad16c981a59505ec84472'
deletions=[{'scene':'04','line':8,'startFrame':9685,'endFrame':9965,'scope':'whole-source-commentary-sentence'},
 {'scene':'05','line':7,'startFrame':13322,'endFrame':13511,'scope':'whole-source-commentary-sentence'},
 {'scene':'08','line':10,'startFrame':23071,'endFrame':23393,'scope':'whole-source-commentary-sentence'},
 {'scene':'09','line':2,'startFrame':24708,'endFrame':24744,'scope':'creator-name-prefix-only; keep Kirby Air Ride factual example and existing voice'}]
oldplan=load(D/'edit-plan.json');total=oldplan['totalFrames'];kept=[];cursor=0;dest=0
for x in deletions:
 n=x['startFrame']-cursor;kept.append({'sourceStartFrame':cursor,'sourceEndFrame':x['startFrame'],'startFrame':dest,'endFrame':dest+n});dest+=n;cursor=x['endFrame'];x['removedFrames']=x['endFrame']-x['startFrame'];x['newJoinFrame']=dest
kept.append({'sourceStartFrame':cursor,'sourceEndFrame':total,'startFrame':dest,'endFrame':dest+total-cursor});frames=kept[-1]['endFrame']
def mapframe(f):return f-sum(max(0,min(f,x['endFrame'])-x['startFrame']) for x in deletions)
def maptime(t):return t-sum(max(0,min(t,x['endFrame']/60)-x['startFrame']/60) for x in deletions)
removed={(x['scene'],x['line']) for x in deletions if x['scope'].startswith('whole')}
for name in ['narration.ko.json','narration.tts.ko.json','narration.en.json']:
 original=load(B/'standalone-v3'/name);d=copy.deepcopy(original);d['revision']='original-deletion-v4'
 for scene in d['scenes']:
  out=[]
  for i,line in enumerate(scene['lines'],1):
   if (scene['id'],i) in removed:continue
   if (scene['id'],i)==('09',2):
    line=line.replace('사쿠라이는 ','') if name!='narration.en.json' else 'Kirby Air Ride included a board resembling the achievement systems that later became familiar on consoles.'
   out.append(line)
  scene['lines']=out
 assert not any(term in ' '.join(l for s in d['scenes'] for l in s['lines']) for term in ['사쿠라이','Sakurai'])
 save(S/name,d)
rows=[]
for r in load(B/'caption-tracks.json'):
 key=(r['scene'],r['line'])
 if key in removed:continue
 r=copy.deepcopy(r)
 if key==('09',2) and '사쿠라이' in r['ko']:
  r['ko']=r['ko'].replace('사쿠라이는 ','');r['en']='Kirby Air Ride included a board resembling the';r['start']=24744/60
 r['sourceStart']=r['start'];r['sourceEnd']=r['end'];r['start']=maptime(r['start']);r['end']=maptime(r['end']);r['sourceLine']=r['line'];r['line']-=sum(s==r['scene'] and n<r['line'] for s,n in removed);rows.append(r)
for lang in ['ko','en']:
 previous=0;blocks=[]
 for i,r in enumerate(rows,1):
  assert r['start']>=previous-.002 and r['end']>r['start'];previous=r['end'];blocks.append(f"{i}\n{timestamp(r['start'])} --> {timestamp(r['end'])}\n{r[lang]}")
 (O/f'captions.{lang}.srt').write_text('\n\n'.join(blocks)+'\n',encoding='utf8')
save(O/'caption-tracks.json',rows)
plan=copy.deepcopy(oldplan);plan.update(revision='original-deletion-v4',totalFrames=frames,bodyFrames=frames-720,explanationFrames=oldplan['explanationFrames']-(total-frames),actualShare=oldplan['actualFrames']/(frames-720),sourcePlan='production/reference-preserving-v2/edit-plan.json',deletions=deletions,retainedSourceRanges=kept,sourceMaster=(B/'game-reward-planning-v2-clean.mp4').relative_to(R).as_posix(),narrationTiming='production/reference-preserving-v2/original-deletion-v4-plan.json#retainedSourceRanges')
for c in plan['cuts']:
 c['originalStartFrame']=c['startFrame'];c['originalEndFrame']=c['endFrame'];c['startFrame']=mapframe(c['startFrame']);c['endFrame']=mapframe(c['endFrame']);c['frames']=c['endFrame']-c['startFrame']
save(D/'original-deletion-v4-plan.json',plan)
# Copy decoded baseline samples in frame-aligned ranges. Only millisecond join fades
# alter retained samples; do not normalize, remix, time-stretch or synthesize speech.
audio=[]
for name in ['narration-stem.wav','final-mix.wav']:
 baseline,sr=sf.read(B/name,dtype='float32',always_2d=True);assert sr==48000
 pad=total*800-len(baseline);assert 0<=pad<=4800
 if pad:baseline=np.pad(baseline,((0,pad),(0,0)))
 pieces=[baseline[x['sourceStartFrame']*800:x['sourceEndFrame']*800].copy() for x in kept];joined=np.concatenate(pieces);assert len(joined)==frames*800;originalJoined=joined.copy();fadeMask=np.zeros(len(joined),bool)
 for x in deletions:
  center=x['newJoinFrame']*800;fade=48 if x['scope'].startswith('creator') else 240
  joined[center-fade:center]*=np.linspace(1,0,fade,dtype=np.float32)[:,None];joined[center:center+fade]*=np.linspace(0,1,fade,dtype=np.float32)[:,None];fadeMask[center-fade:center+fade]=True
 sf.write(O/name,joined,sr,subtype='PCM_24');back,_=sf.read(O/name,dtype='float32',always_2d=True);assert np.array_equal(back[~fadeMask],originalJoined[~fadeMask]);audio.append({'file':name,'baselineSha256':sha(B/name),'outputSha256':sha(O/name),'retainedSamplesIdenticalOutsideJoinFades':True,'fadesSecondsEachSide':[.005,.005,.005,.001],'sampleRate':sr,'samples':len(joined),'endPaddingSamples':pad,'gainNormalization':False,'newTts':False})
evidence={'revision':'original-deletion-v4','preferredBaseline':'reference-preserving-v2 before standalone-v3','baselineCaptionedSha256':'b45ea859ee2fbd2e344c4f68ffc814cf69ffb3eac7cfdbb7a89827d4e741cf9d','baselineCleanSha256':'4a44ccb6e3e3e29052cec0bc0747e732c9728893eb0ad16c981a59505ec84472','removedFrames':total-frames,'totalFrames':frames,'duration':frames/60,'newTtsGenerated':False,'v3ReplacementSpeechUsed':False,'deletions':deletions,'retainedRanges':kept,'audio':audio,'captionCount':len(rows),'internalJoinReview':'pending','humanListening':'pending'};save(O/'deletion-evidence.json',evidence)
s=(D/'build-caption-layout.py').read_text(encoding='utf8').replace("P/'production/local/reference-preserving-v2/edit'","P/'production/local/reference-preserving-v2/edit/original-deletion-v4'");exec(compile(s,str(D/'build-caption-layout.py'),'exec'),{'__file__':str(D/'build-caption-layout.py')})
control=load(R/'shared/publishing/video-production-control.json');control['updatedAt']=stamp;control['selectedRevisionCorrection']={'slug':'game-reward-planning','id':'original-deletion-v4','userMessage':'이전것이 더 나은거 같은데 이전영상에서 사쿠라이 관련 대본만 빼서 만들어줘','scope':'Restore prior v2 voice/edit, remove three source-commentary sentences and only the creator-name prefix from the Kirby Air Ride example. No new TTS, no visual redesign. Ripple matching video/captions; preserve old deliveries.','authorizedAt':stamp,'status':'render-and-join-review'};save(R/'shared/publishing/video-production-control.json',control)
design=load(P/'planning/reference-preserving-v2.json');design['selectedCorrection']={'id':'original-deletion-v4','userPreference':'Prior v2 voice and edit preferred over standalone-v3 replacement takes','plan':'production/reference-preserving-v2/original-deletion-v4-plan.json','deletedSourceClaims':'04 challenger frequency commentary;05 redundant production-burden attribution;08 subsequent-games historical attribution. User specifically selected removal.','retainedGameExample':'09 original Kirby Air Ride factual example retained, removing only 사쿠라이는; no first-person biography introduced.','boundaryLinks':['Locked character restriction→balance wait and new encounters','Model/UI/text/checking tasks→work grows with reward count','Locked music inconveniences listeners→plan what to lock/provide','Checklist reveals conditions→Kirby Air Ride board→Clear Getter/Checklist names and rules'],'newTts':False};save(P/'planning/reference-preserving-v2.json',design)
ledger=load(P/'production/script-source-review.json');ledger['currentRevision']['originalDeletionCorrection']={'status':'script-and-lossless-audio-selection-complete','plan':'production/reference-preserving-v2/original-deletion-v4-plan.json','evidence':(O/'deletion-evidence.json').relative_to(R).as_posix(),'scriptContinuity':'Affected predecessor/successor pairs directly read; no replacement prose or voice generated','internalQa':'pending output/join checks','humanListening':'pending'};save(P/'production/script-source-review.json',ledger)
cp=load(P/'production/latest-checkpoint.json');cp.update(stage='original-v2-source-commentary-removal',status='active',updatedAt=stamp,finalVideoComplete=False,gitDeliveryComplete=False,nextAction='Render retained original v2 frames with the deletion-only audio and captions; check four joins/current encoded audio; collect four files and commit. Existing Drive quota blocker remains unresolved.');cp['currentRevision']['originalDeletionCorrection']=ledger['currentRevision']['originalDeletionCorrection'];save(P/'production/latest-checkpoint.json',cp)
print(json.dumps({'frames':frames,'duration':frames/60,'removedSeconds':(total-frames)/60,'captionCues':len(rows),'newTts':False}))
