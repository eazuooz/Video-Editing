"""Record the user's scoped revision without changing the delivered video."""
from pathlib import Path
import json, hashlib, datetime
P=Path(__file__).resolve().parent; ROOT=P.parents[3]
PREV=P.parent/'reference-preserving-v1'; H=P.parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
assert not (P/'revision-request.json').exists()
request='자막이랑 tts 에서 사쿠라이는 없는거야 관련내용은 제거해주고 다른설명으로 대체해줘 그리고 영상 초반에 왜 계층형 정보가 필요한지 예시랑 설명을 예시로 하나 만들어줘 포켓몬 초기작 기획문서 예시가 좋을꺼같아'
write(P/'revision-request.json',dict(at=now,userMessage=request,scope='same selected video through new private upload; preserve both prior uploads and reservations',removeFrom=['narration','KO captions','EN captions','public explanatory metadata'],retainedResearchAttribution=True,pokemon='User-selected early-generation planning-document illustration; original developer document not claimed',changedVoiceScenes=['01','01a','02','07','08'],unchangedVoiceScenes=['03','04','05','06'],existingPrivateVideoId='JoHXz7YtEPw',scheduledBaselineId='jBRt3xatdPk',automaticNextVideo=False))
preserved=[H/'project.json',PREV/'latest-checkpoint.json',PREV/'final-timeline-v1.json',PREV/'final-direct-review-v2.json',PREV/'narration.ko.json',PREV/'narration.en.json',PREV/'publishing/completion-v1.json']
write(P/'preservation.json',dict(at=now,files=[dict(path=x.relative_to(ROOT).as_posix(),sha256=sha(x)) for x in preserved]))
(P/'delivered-main-backup-local.json').write_bytes((H/'project.json').read_bytes())
cp=dict(updatedAt=now,stage='pokemon-source-and-opening-design',previousCompletedCheckpoint=(PREV/'latest-checkpoint.json').relative_to(ROOT).as_posix(),request='revision-request.json',worker=None,sourceApproved=False,scriptFinalized=False,newPcm=False,finalPair=False,privateUpload=False,gitDelivered=False,next='Verify one independently recorded early Pokémon example and its usage terms, then finalize the changed narration and opening document design.',automaticNextVideo=False)
write(P/'latest-checkpoint.json',cp)
plan=read(H/'planning/production-plan.json')
(P/'previous-production-plan-local.json').write_bytes((H/'planning/production-plan.json').read_bytes())
plan.update(updatedAt=now,status=cp['stage'],currentRevision=P.relative_to(ROOT).as_posix(),latestCheckpoint=(P/'latest-checkpoint.json').relative_to(ROOT).as_posix(),nextAction=cp['next'])
plan['userRevision']=dict(message=request,publicNarrationHasPersonalAttribution=False,personalExperienceRemovedRatherThanReattributed=True,additionalGame='Pokémon Red (early generation explicitly requested)',documentType='independently authored illustrative planning document')
write(H/'planning/production-plan.json',plan)
print(json.dumps(cp,ensure_ascii=False))
