"""Replace only the source-mismatched08p2; preserve every other current sample."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil
import numpy as np,soundfile as sf
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;WORK=BASE/'repair2'
read=lambda p:json.loads(p.read_text(encoding='utf8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
req=read(WORK/'request.json');report=read(WORK/'asr/asr.json');candidate=ROOT/report['rows'][0]['source'];assert report['rows'][0]['text'].strip().replace(',','')==req['ko'].replace(',','')
assert sha(candidate)==report['rows'][0]['sourceSha256']
write(WORK/'direct-review.json',{'reviewedAt':datetime.now(timezone.utc).isoformat(),'candidate':req['ko'],'candidateSha256':sha(candidate),'allFullClausesDirectlyCompared':True,'endingContext':'Complete 바꾼 뒤→서로 다른 복장→움직이는 장면을 보세요 present. The crop starts3.1 within 의상과3.02–3.46 and reads 이상과; full candidate supplies the complete 의상과. Preserve both readbacks.','sourceClaim':'The native ROBES and MASKS changes were read directly; hat selection was not shown. Only 모자→의상 and hats→clothing are changed.','sourceEvidence':req['sourceFrames'],'decision':'content-readback-pass','endingHeuristicUsedAsApproval':False,'humanWholeListening':'pending','pronunciationApproval':'pending'})
v2=ROOT/req['originalWavDirectory'];v3=ROOT/'shared/output/narration/game-reward-planning/qwen3-1.7b-balanced-v3';assert not v3.exists();(v3/'chunks').mkdir(parents=True);(v3/'asr').mkdir()
for sid,h in req['originalWavLocks'].items():assert sha(v2/(sid+'-scene.wav'))==h
a=223656;b=409272;rows=[]
for sid in [f'{n:02}' for n in range(1,14)]:
 source=v2/(sid+'-scene.wav');dest=v3/'chunks'/source.name
 if sid!='08':
  shutil.copy2(source,dest);shutil.copy2(v2.parent/'asr'/(sid+'.json'),v3/'asr'/(sid+'.json'));assert sha(source)==sha(dest);rows.append({'scene':sid,'wholeWavByteIdentical':True,'sha256':sha(dest)});continue
 old,sr=sf.read(source,dtype='int16');patch,pr=sf.read(candidate,dtype='int16');assert sr==pr==24000
 # a is the retained original p1 endpoint from repair1; b is the directly
 # measured quiet gap before p3. Candidate ends with its natural silence.
 composite=np.concatenate([old[:a],patch,old[b:]]);sf.write(dest,composite,24000,subtype='PCM_16');decoded,_=sf.read(dest,dtype='int16')
 assert np.array_equal(decoded[:a],old[:a]) and np.array_equal(decoded[a+len(patch):],old[b:])
 rows.append({'scene':sid,'wholeWavByteIdentical':False,'sha256':sha(dest),'samples':len(composite),'sourceRemovedSamples':[a,b],'candidateSamples':len(patch),'retainedBeforeSamples':a,'retainedAfterSamples':len(old)-b,'retained51ParagraphsPcmVerified':True,'allSamplesOfOther08ParagraphsPreserved':True,'joinSilenceNotAdded':True})
ko=read(WORK/'baseline/narration.ko.json');en=read(WORK/'baseline/narration.en.json')
for lang,obj,line in [('ko',ko,req['ko']),('en',en,req['en'])]:
 s=next(s for s in obj['scenes'] if s['id']=='08');assert s['lines'][1]==req['previousKo' if lang=='ko' else 'previousEn'];s['lines'][1]=line;write(WORK/('v3.narration.'+lang+'.json'),obj)
mf=read(WORK/'baseline/project.json');mf['tts'].update(outputDir=v3.relative_to(ROOT).as_posix(),filenameStem='game-reward-planning-qwen3-1.7b-balanced-v3');mf['paths'].update(script=(WORK/'v3.narration.ko.json').relative_to(ROOT).as_posix(),scriptEn=(WORK/'v3.narration.en.json').relative_to(ROOT).as_posix())
for field,ext in [('narration','.wav'),('captionsKo','.srt'),('captionsEn','.en.srt')]:mf['paths'][field]=(v3/(mf['tts']['filenameStem']+ext)).relative_to(ROOT).as_posix()
write(WORK/'v3.manifest.json',mf);write(WORK/'v3-composite-proof.json',{'createdAt':datetime.now(timezone.utc).isoformat(),'status':'current08-full-ASR-and-seams-pending','scenes':rows,'original13V2WavsPreserved':True,'all7ExplanationWholeWavsByteIdentical':True,'unchangedFromV2Paragraphs':51,'sourceClaimCorrectionOnly':['08p2'],'finalTimingApproved':False,'humanWholeListening':'pending'})
print(json.dumps({'v3Scene08Seconds':sf.info(v3/'chunks/08-scene.wav').duration,'remaining12ByteIdentical':True}))
