"""Measured original-order audio, exact 60:40 cuts and bilingual word-aligned captions."""
from pathlib import Path
import json,hashlib,math,re,difflib
import numpy as np,soundfile as sf
W=Path(__file__).resolve().parent;R=W.parents[3]
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
m=read(W/'voice.manifest.json');out=R/m['tts']['outputDir'];approval=read(W/'voice-approval.json')
assert approval['allCurrentScenesTechnicallyReviewed'] and len(approval['scenes'])==56
scripts={l:read(W/f'narration.{l}.json') for l in ['ko','en']};pron=read(W/'pronunciation-map.json')
approved={s['id']:s for s in approval['scenes']};scenes=[];manim={'08':'NodeAndTraversal','34':'InsertBetween','41':'DeleteMiddle','49':'HeadAndEmpty'}
pools={p['chapter']:p['ranges'] for p in read(W/'source-pools.json')['pools']}
connections={c['chapter']:c for c in read(W/'concept-connections.json')['chapters']}
for s in scripts['ko']['scenes']:
 sid=s['id'];wav=out/'chunks'/f'{sid}-scene.wav';digest=hashlib.sha256(wav.read_bytes()).hexdigest();assert digest==approved[sid]['audioSha256']
 pcm,rate=sf.read(wav,dtype='int16');assert rate==24000 and pcm.ndim==1
 frames=math.ceil(len(pcm)/400-1e-8)+43
 if sid in manim:frames=max(frames,25*60)
 scenes.append({'id':sid,'chapter':s['chapter'],'title':s['title'],'classification':'mixed','voiceSeconds':len(pcm)/rate,'frames':frames,'voice':wav.relative_to(R).as_posix(),'audioSha256':digest,'asr':(out/'asr'/f'{sid}.json').relative_to(R).as_posix(),'sourceReconstructed':s.get('sourceReconstructed',False)})
bodyFrames=sum(s['frames'] for s in scenes);targetActual=round(bodyFrames*.6)
# Keep at least four seconds of an independent explanation per scene. Linked-list
# process chapters and coaching have no actual-footage pool; all are explanation.
chapterCaps={ch:round(sum(r['sourceEnd']-r['sourceStart'] for r in rr)*60) for ch,rr in pools.items()}
for s in scenes:s['actualFrames']=0;s['maxActual']=min(s['frames']-240,chapterCaps[s['chapter']]) if s['id'] not in manim else 0
chapterUsed={ch:0 for ch in pools};left=targetActual
while left:
 eligible=[s for s in scenes if s['actualFrames']<s['maxActual'] and chapterUsed[s['chapter']]<chapterCaps[s['chapter']]]
 assert eligible,'Not enough concept-matched actual footage; acquire new related action instead of loops.'
 s=min(eligible,key=lambda s:s['actualFrames']/s['frames'])
 n=min(left,12,s['maxActual']-s['actualFrames'],chapterCaps[s['chapter']]-chapterUsed[s['chapter']]);s['actualFrames']+=n;chapterUsed[s['chapter']]+=n;left-=n
def norm(t):
 for a,b in pron.items():t=re.sub(re.escape(a),b,t,flags=re.I)
 for a,b in [('AI','에이아이'),('API','에이피아이'),('UI','유아이'),('C++','씨플러스플러스'),('Next','넥스트')]:t=re.sub(re.escape(a),b,t,flags=re.I)
 t=re.sub('[^a-z0-9가-힣]','',t.lower())
 return t
def sentences(t):return [v.strip() for v in re.findall(r'.+?(?:[.!?](?=\s|$)|$)',t) if v.strip()]
def split_balanced(t,n):
 for term in pron:
  if ' ' in term:t=re.sub(re.escape(term),lambda m:m.group().replace(' ','\u2060'),t,flags=re.I)
 left=t.split();n=min(n,len(left));result=[]
 for i in range(n-1):
  goal=len(' '.join(left))/(n-i);_,j=min((abs(len(' '.join(left[:j]))-goal),j) for j in range(1,len(left)-(n-i-1)+1));result.append(' '.join(left[:j]));left=left[j:]
 return [v.replace('\u2060',' ') for v in result+[' '.join(left)]]
position=120;pieces=[];entries=[];paragraphs=[];cuts=[];reelFrame=0;timing={};poolPositions={ch:[0,0] for ch in pools}
def addcut(s,kind,frames,**kw):
 assert frames>0
 t=s['startFrame']+sum(c['frames'] for c in cuts if c['scene']==s['id'])
 c={'id':str(len(cuts)+1).zfill(3),'scene':s['id'],'chapter':s['chapter'],'classification':kind,'frames':frames,'seconds':frames/60,'timelineStartFrame':t,'timelineEndFrame':t+frames,'timelineStart':t/60,'timelineEnd':(t+frames)/60,'claim':connections[s['chapter']]['claim'],'viewerFocus':connections[s['chapter']]['viewerFocus'],**kw};cuts.append(c)
def actual(s):
 ch=s['chapter'];left=s['actualFrames']
 while left:
  idx,consumed=poolPositions[ch];p=pools[ch][idx];available=round((p['sourceEnd']-p['sourceStart'])*60)-consumed;n=min(left,available,18*60)
  addcut(s,'actual',n,key=p['key'],raw=p['file'],sourceId=p['sourceId'],sourceIn=p['sourceStart']+consumed/60,sourceOut=p['sourceStart']+(consumed+n)/60,localIn=p['localStart']+consumed/60,speed=1,sourceAudioMuted=True,visualReview='pending-final-cut')
  left-=n;consumed+=n
  poolPositions[ch]=[idx+1,0] if n==available else [idx,consumed]
for s in scenes:
 sid=s['id'];s.update(startFrame=position,start=position/60,seconds=s['frames']/60);position+=s['frames'];s['explanationFrames']=s['frames']-s['actualFrames']
 pcm,rate=sf.read(R/s['voice'],dtype='int16');pieces.append(np.concatenate([pcm,np.zeros(s['frames']*400-len(pcm),dtype=np.int16)]))
 mf=1260 if sid in manim else 0;mc=s['explanationFrames']-mf;assert mc>=240
 timing[sid]=mc/60;s['reelStartFrame']=reelFrame;s['motionCanvasFrames']=mc;s['manimFrames']=mf
 def explanation():
  if mf:addcut(s,'explanation',mf,key='manim',manimClass=manim[sid],raw=f'shared/output/manim/blank-project-coding/original-restored-v2/videos/linked_list/1080p60/{manim[sid]}.mp4',localIn=0,speed=2,sourceIn=0,sourceOut=42,visualReview='pending-final-cut')
  addcut(s,'explanation',mc,key='motion-canvas',reelStartFrame=reelFrame,localIn=reelFrame/60,speed=1,visualReview='pending-final-cut')
 if int(sid)%2==0 and s['actualFrames']:actual(s);explanation()
 else:explanation();actual(s)
 reelFrame+=mc
 ko=next(x['lines'] for x in scripts['ko']['scenes'] if x['id']==sid);en=next(x['lines'] for x in scripts['en']['scenes'] if x['id']==sid);assert len(ko)==len(en)
 asr=read(R/s['asr']);assert asr['audio_sha256']==s['audioSha256'];words=asr['words'];expected=norm(''.join(ko));recognized='';times=[]
 for wi,w in enumerate(words):
  a,b=w['timestamp'];a=float(a if a is not None else (times[-1][1] if times else 0));b=float(b if b is not None else next((v['timestamp'][0] for v in words[wi+1:] if v['timestamp'][0] is not None),s['voiceSeconds']));b=min(max(a,b),s['voiceSeconds']);chars=norm(w['text'])
  for j,ch in enumerate(chars):recognized+=ch;times.append((a+(b-a)*j/max(len(chars),1),a+(b-a)*(j+1)/max(len(chars),1)))
 match=difflib.SequenceMatcher(None,expected,recognized,autojunk=False);assert match.ratio()>.92,(sid,match.ratio())
 mapping={block.a+j:block.b+j for block in match.get_matching_blocks() for j in range(block.size)};mapkeys=sorted(mapping)
 def mapped(i):return mapping[i] if i in mapping else int(round(float(np.interp(i,mapkeys,[mapping[k] for k in mapkeys]))))
 char_pos=0;scene_rows=[]
 for pi,(k,e) in enumerate(zip(ko,en)):
  ks=sentences(k);es=sentences(e)
  if len(ks)!=len(es):ks=[k];es=[e]
  pairs=[]
  for ksent,esent in zip(ks,es):
   n=min(max(math.ceil(len(ksent)/29),math.ceil(len(esent)/105),1),len(ksent.split()),len(esent.split()));pairs+=list(zip(split_balanced(ksent,n),split_balanced(esent,n)))
  pa=times[mapped(char_pos)][0]
  for kc,ec in pairs:
   n=len(norm(kc));a=times[mapped(char_pos)][0];b=times[mapped(char_pos+n-1)][1];char_pos+=n
   scene_rows.append({'scene':sid,'paragraph':pi+1,'start':s['start']+a,'end':min(s['start']+b+.07,s['start']+s['voiceSeconds']),'ko':kc,'en':ec})
  paragraphs.append({'scene':sid,'paragraph':pi+1,'start':s['start']+pa,'end':scene_rows[-1]['end'],'ko':k,'en':e})
 assert char_pos==len(expected),(sid,char_pos,len(expected),scene_rows)
 for i,c in enumerate(scene_rows):
  if i<len(scene_rows)-1:c['end']=min(c['end'],scene_rows[i+1]['start']-.015)
  assert c['end']>c['start'],(sid,c)
 entries+=scene_rows;s['wordMatch']=match.ratio()
assert sum(c['frames'] for c in cuts)==bodyFrames
plan={'revision':'original-restored-v2','fps':60,'introFrames':120,'introSeconds':2,'outroFrames':600,'bodyFrames':bodyFrames,'bodySeconds':bodyFrames/60,'bodyEnd':position/60,'seconds':(position+600)/60,'totalFrames':position+600,'actualFrames':targetActual,'explanationFrames':bodyFrames-targetActual,'gameplaySeconds':targetActual/60,'explanationSeconds':(bodyFrames-targetActual)/60,'gameplayShare':targetActual/bodyFrames,'ratioErrorFrames':abs(targetActual-.6*bodyFrames),'explanationReelFrames':reelFrame,'manimExplanationFrames':5040,'scenes':scenes,'paragraphs':paragraphs,'cuts':cuts,'humanListening':'pending','sourceRights':'CC source records verified; full human rights review and Nimbus original acquisition pending'}
write(W/'plan.json',plan);write(R/'motion-canvas/src/projects/blank-project-coding/restored-v2/timing.json',timing);write(W/'caption-alignment.json',{'entries':entries,'cues':len(entries),'kind':'Current-hash Whisper words aligned to original Korean and complete English paragraphs','humanListening':'pending'})
bodyWav=out/'blank-project-coding-original-restored-v2-body.wav';sf.write(bodyWav,np.concatenate(pieces),24000,subtype='PCM_16')
def stamp(t):
 n=round(t*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
for lang in ['ko','en']:
 (W/f'captions.{lang}.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(c["start"])} --> {stamp(c["end"])}\n'+ ('\n'.join(split_balanced(c[lang],2)) if lang=='en' and len(c[lang])>80 else c[lang]) for i,c in enumerate(entries))+'\n',encoding='utf-8')
original=''.join(x for s in scripts['ko']['scenes'] for x in s['lines']);caption=''.join(c['ko'] for c in entries);assert re.sub(r'\s','',original)==re.sub(r'\s','',caption),'Caption word loss'
m['paths'].update(narration=bodyWav.relative_to(R).as_posix(),script=(W/'narration.ko.json').relative_to(R).as_posix(),scriptEn=(W/'narration.en.json').relative_to(R).as_posix(),captionsKo=(W/'captions.ko.srt').relative_to(R).as_posix(),captionsEn=(W/'captions.en.srt').relative_to(R).as_posix(),audioMix='shared/output/narration/blank-project-coding/original-restored-v2/final-mix.m4a',editorAudioMix='shared/output/narration/blank-project-coding/original-restored-v2/final-mix.wav',videoClean='shared/output/motion-canvas/blank-project-coding-original-restored-v2.mp4',videoBurnedCaptions='shared/output/motion-canvas/blank-project-coding-original-restored-v2-subtitled.mp4')
rel=lambda f:(W/f).relative_to(R).as_posix()
m['paths'].update(timeline=rel('plan.json'),footageCuts=rel('footage-cuts.json'),sources=rel('sources.json'),storyboard=rel('plan.json'),sourceMap=rel('original-preservation-audit.json'),scriptReview=rel('narration.review.txt'),ttsScript=rel('narration.tts.ko.json'),publishingKo=rel('publishing/description.ko.txt'),publishingEn=rel('publishing/description.en.txt'),audioReport=rel('mix-settings.json'),motionCanvasProject='motion-canvas/src/projects/blank-project-coding/restored-v2/full/project.ts',explanationProject='motion-canvas/src/projects/blank-project-coding/restored-v2/project.ts',manimProject='manim/projects/blank-project-coding/linked_list.py')
m['editing'].update(actualGameplaySeconds=plan['gameplaySeconds'],actualExplanationSeconds=plan['explanationSeconds'],actualGameplayShare=plan['gameplayShare'],actualCommercialGameplaySeconds=sum(c['seconds'] for c in cuts if c['key']=='tetris'),actualDevelopmentFootageSeconds=sum(c['seconds'] for c in cuts if c['classification']=='actual' and c['key']!='tetris'),actualManimExplanationSeconds=84,scenePlan=rel('plan.json'),timingStatus='measured-original-narration-final-cuts-pending-render')
m['editing']['exampleInterleaving'].update(planningPath=rel('concept-connections.json'),storyboard=rel('plan.json'),reviewStatus='candidate-source-review-complete; exact-final-cut-review-pending')
m['editing'].update(plannedBodySeconds=plan['bodySeconds'],plannedActualSeconds=plan['gameplaySeconds'],plannedExplanationSeconds=plan['explanationSeconds'])
m['editing']['coaching'].update(sceneId='56',placement='after-original-conclusion-before-membership-outro')
m['editing']['channelIntro'].update(status='preserved-baseline-pending-new-assembly',appliedToFinal=False)
m['editing']['exampleExpansion']={'method':'Restore the entire initial script in its original order under the latest explicit request. Interleave newly selected actual external footage; retain rejected v1 baseline separately.','preserveOriginalWordingAndOrder':True,'baseline':rel('baseline.json'),'latestUserEvidence':'처음준 대본 순서대로 내용 그대로 만들어줘 영상'}
m['video']['durationSeconds']=plan['seconds'];m['titles']=dict(ko=scripts['ko']['title'],en=scripts['en']['title']);m['scriptRevision']=2;m['status']='original-restored-v2-render-pending';m['delivery']['gitEvidence']=rel('git-delivery.json');m['membershipOutro']['appliedToFinal']=False
m['video'].update(targetDurationSeconds=plan['seconds'],durationEstimateRangeSeconds=[plan['seconds'],plan['seconds']],durationEstimateStatus='measured-current56-voice-timeline')
m['engines']=['motion-canvas','manim'];m['tts']['sceneGapSeconds']=43/60
m['audio'].update(mixStatus='current-original56-scene-mix-pending',sourceAudioMuted=True)
m['approvals'].update(fullNarration='56-current-scene-hashes-ASR-and-endings-technically-reviewed; human-listening-pending',translation='56-scenes118-paragraphs-complete-original-meaning; aligned-KO-EN-cues',broll='fresh-CC-source-candidate-review-complete; final-cut-review-pending',rights='external-CC-notices-and-attributions-recorded; human-full-rights-and-Nimbus-original-bytes-review-pending',render='pending',scriptEvidence='처음준 대본 순서대로 내용 그대로 만들어줘 영상')
m['publishing']={'status':'pending-new-private-revision-upload','defaultPrivacyStatus':'private','publicPublicationOrSchedulingAuthorized':False,'receipt':'projects/blank-project-coding/publishing/youtube-upload-original-restored-v2.json','coachingEndingLinkRequired':True,'pinnedCoachingCommentRequired':True,'defaults':'shared/publishing/youtube-defaults.json','pinnedCommentStatus':'pending-video-publication','previousPrivateVideoId':'kcZL02MXtvI','previousReceiptPreserved':'projects/blank-project-coding/publishing/youtube-upload.json'}
m['production']={'currentStage':'measured-original-script-timeline-ready','ttsGenerated':True,'rendered':False,'collected':False,'uploaded':False};m['audio'].pop('finalMeasurement',None)
m['finalRender']={'revision':'original-restored-v2','seconds':plan['seconds'],'technicalQa':rel('qa.json'),'mixAlignmentReview':rel('mix-alignment-review.json'),'humanListening':'pending','knownIssues':[],'openItems':['Full human listening pending','Nimbus restored bytes used; original acquisition verification pending','Original membership identities retained; truncated handles not guessed','External media backup location is not configured','Private review only; user controls public publication']}
write(W/'final.manifest.json',m)
print(json.dumps({'seconds':plan['seconds'],'actual':plan['gameplaySeconds'],'explanation':plan['explanationSeconds'],'manimSeconds':84,'cues':len(entries),'cuts':len(cuts),'originalCaptionWordsPreserved':True},ensure_ascii=False))
