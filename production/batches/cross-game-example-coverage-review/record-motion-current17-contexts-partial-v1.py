"""Record only the first 21 full expected/recognized pairs actually read by the reviewer."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ids=['00a-p01','00a-p02','00a-p03','00a-p04','01-p01','01-p02','01-p03','01-p04','01-p05','01-p06','02-p01','02-p02','02-p03','02-p04','03-p01','03-p02','03-p03','03-p04','03-p05','03-p06','04-p01']
notes={
 '00a-p03':'Independent 관찰의 versus expected 관찰을; whole00a recovers 관찰을. Full sentence present; human pronunciation remains pending.',
 '01-p03':'Independent 에임모드 recovers whole A 모드 alternative. Spacing is not a missing word.',
 '01-p04':'Independent 조종 versus expected 조준; whole01 recovers 조준. Whole 이동에 versus expected 이동이 is recovered independently. Human pronunciation remains pending.',
 '01-p05':'2022 is the numeric transcription of 이천이십이 년; same source-year claim and complete limitation.',
 '03-p04':'Independent 배경에 versus expected 배경의; whole03 recovers 배경의. Full observation and conclusion retained; human pronunciation remains pending.'
}
out=R/'current17-mixed-contexts-partial-direct-review-v1.json'
assert not out.exists()
state=read(R/'current17-mixed-contexts-asr-execution-v3.json')
rows=[]
for cid in ids:
 p=R/f'current17-mixed-contexts-asr-v3/{cid}.json';v=read(p)
 assert v['id']==cid and v['sourceSha256']==state['decodedAacSha256'] and v['exactSourceStereoPcmBytesMatched']
 rows.append(dict(id=cid,resultPath=p.relative_to(ROOT).as_posix(),resultSha256=sha(p),expectedKo=v['expectedKo'],recognizedKo=v['text'],fullExpectedAndRecognizedTextsDirectlyRead=True,noMissingCompleteSentenceObserved=True,reviewNote=notes.get(cid,'Full expected sentence(s) and recognized sentence(s) agree apart from punctuation/spacing.'),humanPronunciationApproved=False))
whole=R/'current17-mixed-whole-asr-v3/asr.json'
out.write_text(json.dumps(dict(schemaVersion=1,reviewedAt=datetime.now(timezone.utc).isoformat(),partialCount=21,totalCount=81,rows=rows,wholeResultPath=whole.relative_to(ROOT).as_posix(),wholeResultSha256=sha(whole),mixAacSha256=state['mixAacSha256'],decodedAacSha256=state['decodedAacSha256'],currentMixedContentReviewPassed=False,all81Reviewed=False,humanListeningApproved=False,humanPronunciationApproved=False,scope='Full text comparison only; final waveform/captions/pixels remain pending. Remaining60 have not been directly read.'),ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(partialDirectRead=21,total=81,all81Approved=False)))
