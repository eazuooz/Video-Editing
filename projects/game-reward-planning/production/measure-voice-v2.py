"""Measure current PCM/word/paragraph boundaries without creating a mix or final timing."""
from pathlib import Path
from datetime import datetime,timezone
import difflib,hashlib,json,math,re
import numpy as np,soundfile as sf
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
norm=lambda t:re.sub(r'[^a-z0-9가-힣]','',t.lower())
dest=BASE/'measured-voice-v2.json';assert not dest.exists(),'Preserve measured evidence.'
mf=read(BASE.parent/'project.json');script=read(ROOT/mf['paths']['script']);en=read(ROOT/mf['paths']['scriptEn']);gate=read(BASE/'voice-approval-v2.json');assert gate['allCurrentScenesTechnicallyReviewed']
OUT=ROOT/mf['tts']['outputDir'];rows=[]
contexts=read(BASE/'speech-v2/contexts.json');opening=read(BASE/'speech-v2/opening-context/asr.json')
for s in script['scenes']:
 sid=s['id'];file=OUT/'chunks'/f'{sid}-scene.wav';x,rate=sf.read(file,dtype='float32');assert rate==24000 and x.ndim==1
 asr=read(OUT/'asr'/f'{sid}.json');assert asr['audio_sha256']==sha(file)
 words=asr['words'];annotation=None
 if sid=='02':
  c=next(z for z in contexts['rows'] if z['id']=='02-opening');assert c['sourceSha256']==sha(file)
  words=c['chunks']+[z for z in words if z['timestamp'][0]>=3.3];annotation='Use directly read independent current opening timestamps; preserve the original full ASR with inferred 자.'
 if sid=='08':
  c=next(z for z in opening['rows'] if z['id']=='08-title');assert c['sourceSha256']==sha(file)
  words=c['chunks']+[z for z in words if z['timestamp'][0]>=2.42];annotation='Use directly read current0–2.42 Korean title timestamps; preserve longer unstable Ascult transliteration.'
 text='';times=[]
 for w in words:
  t=norm(w['text']);a,b=w['timestamp'];assert a is not None and b is not None and 0<=a<=b<=len(x)/rate+.03
  for j,ch in enumerate(t):text+=ch;times.append((a+(b-a)*j/max(1,len(t)),a+(b-a)*(j+1)/max(1,len(t))))
 expected=''.join(norm(z) for z in s['lines']);matcher=difflib.SequenceMatcher(None,expected,text,autojunk=False);mapped={};matched=set()
 for tag,a,b,c,d in matcher.get_opcodes():
  if tag=='equal':
   for j in range(b-a):mapped[a+j]=times[c+j];matched.add(a+j)
  elif b>a and d>c:
   for j in range(b-a):mapped[a+j]=times[c+min(d-c-1,math.floor(j*(d-c)/(b-a))) ]
  elif b>a:
   prior=times[max(0,c-1)][1];later=times[min(c,len(times)-1)][0]
   for j in range(b-a):mapped[a+j]=(prior,later)
 paragraphs=[];offset=0
 english=next(z for z in en['scenes'] if z['id']==sid)['lines'];assert len(english)==len(s['lines'])
 for i,line in enumerate(s['lines']):
  count=len(norm(line));vals=[mapped[k] for k in range(offset,offset+count)];coverage=len(matched.intersection(range(offset,offset+count)))/count
  paragraphs.append({'paragraph':i+1,'ko':line,'en':english[i],'speechStart':vals[0][0],'speechEnd':vals[-1][1],'normalizedCharacterMatch':coverage});offset+=count
 boundaries=[0];quiet=[]
 for left,right in zip(paragraphs,paragraphs[1:]):
  lo=max(0,round((left['speechEnd']-.045)*rate));hi=min(len(x),round((right['speechStart']+.015)*rate));overlap=right['speechStart']<left['speechEnd']
  if hi<=lo:
   midpoint=(left['speechEnd']+right['speechStart'])/2
   lo=max(0,round((midpoint-.2)*rate));hi=min(len(x),round((midpoint+.2)*rate))
  win=round(.016*rate);center=(lo+hi)//2;proposed=[]
  for k in range(lo,hi,24):
   samples=x[max(0,k-win//2):min(len(x),k+win//2)];rms=float(np.sqrt(np.mean(samples*samples)));proposed.append((rms+abs(k-center)/rate*.0004,k,rms,float(np.max(np.abs(samples)))))
  _,point,rms,peak=min(proposed);boundaries.append(point);quiet.append({'afterParagraph':left['paragraph'],'sample':point,'seconds':point/rate,'rms16ms':rms,'peak16ms':peak,'asrTimestampOverlap':overlap,'preserveAllPcm':True,'newTimingJoinReviewRequired':True})
 boundaries.append(len(x))
 for i,p in enumerate(paragraphs):p.update(pcmFromSample=boundaries[i],pcmToSample=boundaries[i+1],pcmSeconds=(boundaries[i+1]-boundaries[i])/rate)
 classification='explanation' if int(sid)%2 else 'actual'
 rows.append({'id':sid,'title':s['title'],'classification':classification,'audio':file.relative_to(ROOT).as_posix(),'audioSha256':sha(file),'samples':len(x),'sampleRate':rate,'speechSeconds':len(x)/rate,'minimumSpeechFrames':math.ceil(len(x)*60/rate),'referenceTailGapFrames':43,'paragraphs':paragraphs,'quietBoundaries':quiet,'timingEvidenceAnnotation':annotation,'allPcmUnchanged':True})
 explanation_frames=sum(z['minimumSpeechFrames']+43 for z in rows if z['classification']=='explanation');actual_target=round(explanation_frames*1.5)
result={'schemaVersion':1,'status':'current-PCM-measured-word-and-paragraph-evidence-not-final-edit','measuredAt':datetime.now(timezone.utc).isoformat(),'voiceApproval':'projects/game-reward-planning/production/voice-approval-v2.json','voiceApprovalSha256':sha(BASE/'voice-approval-v2.json'),'scriptKoSha256':sha(ROOT/mf['paths']['script']),'scriptEnSha256':sha(ROOT/mf['paths']['scriptEn']),'scenes':rows,'proposedMinimumExplanationFrames':explanation_frames,'proposedActualTargetFrames':actual_target,'proposedBodyFrames':explanation_frames+actual_target,'proposedBrandingFrames':120,'proposedMembershipFrames':600,'proposedFinalFrames':explanation_frames+actual_target+720,'bodyRatioRoundingErrorFrames':actual_target-1.5*explanation_frames,'finalSourceTimingApproved':False,'fixedCaptionApproval':False,'finalMixBuilt':False,'humanListening':'pending'}
dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'measuredScenes':len(rows),'paragraphs':sum(len(z['paragraphs']) for z in rows),'proposedExplanationSeconds':explanation_frames/60,'proposedActualSeconds':actual_target/60,'proposedFinalSeconds':result['proposedFinalFrames']/60,'finalApproval':False,'paragraphWindows':[{'scene':z['id'],'windows':[[p['paragraph'],round(p['speechStart'],3),round(p['speechEnd'],3)] for p in z['paragraphs']]} for z in rows]},ensure_ascii=False))
