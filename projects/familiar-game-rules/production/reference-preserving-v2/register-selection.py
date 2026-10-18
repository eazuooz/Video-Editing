"""Register this user-selected D20 revision without changing another task's leases."""
from pathlib import Path
import datetime, hashlib, json, subprocess

ROOT=Path(__file__).resolve().parents[4]
P=ROOT/'projects/familiar-game-rules'
NOW=datetime.datetime.now(datetime.timezone.utc).isoformat()

def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

authorization={
 'schemaVersion':1,'revision':'reference-preserving-v2','slug':P.name,
 'selectedAt':NOW,'fullRevisionAuthorized':True,
 'scope':'familiar-game-rules only through complete Google Drive final review',
 'userEvidence':'다음 게임디자인 영상도 새로운 규칙 적용해서 영상 제작해줘~',
 'selectionReason':'D19 making-game-sequels already delivered for review; D20 is the next game-design item.',
 'voice':{'provider':'ElevenLabs','voiceId':'jIRSnF8OWAsWEChVwCuK',
   'model':'Eleven v4','approvedSample':'B','settings':{'stability':0.5,'similarity':0.75,'speed':1},
   'userEvidence':'ElevenLabs 샘플 B로 진행',
   'meaning':'Same approved own clone/model/settings; sampleB is not a deterministic preset.'},
 'preserveYouTubeIds':['WpCmlV8KyOc','NLEHMC0XMtg'],
 'youtubeUploadAuthorized':False,'automaticNextVideo':False,
 'resourcePolicy':'Cloud voice; no foreign GPU/process/queue/control-selection mutations.'}
write(P/'production/reference-preserving-v2/authorization.json',authorization)
manifest=read(P/'project.json')
manifest['activeRevision']='reference-preserving-v2'
manifest['status']='selected-reference-preserving-v2-preproduction'
manifest['currentRevision']={'id':'reference-preserving-v2','authorization':'production/reference-preserving-v2/authorization.json',
 'plan':'planning/chapter-plan.json#currentRevision','reviewLedger':'production/review-ledger.json',
 'status':'source-reconstruction-and-independent-footage-selection','baselinePreserved':True,
 'baselineVideoId':'WpCmlV8KyOc','voice':'ElevenLabs own clone / sample B settings'}
write(P/'project.json',manifest)
plan=read(P/'planning/chapter-plan.json')
plan['currentRevision']={'id':'reference-preserving-v2','updatedAt':NOW,
 'status':'full-reference-reconstructed-independent-footage-pending',
 'authorization':'production/reference-preserving-v2/authorization.json',
 'reference':{'url':'https://www.youtube.com/watch?v=ANerCiyfJjo',
   'title':"It's Easier If They Already Know [Planning & Game Design]",
   'classification':'research-reference-only','productionUse':False,
   'fullContentAudit':'production/reference-preserving-v2/reference-audit.json'},
 'backbone':['Shared FPS controls','Originality through immersion/world/story','Support newcomers; shorten only familiar explanations',
   'Genre conventions across actual FPS examples','De facto standards and human-computer interaction',
   'Remapping and individual preferences','Functional limits: D-pad versus analog stick',
   'Unchangeable inputs and alternatives','Unexpected assignments can produce distinctive play; avoid overstandardization'],
 'screenRole':{'actual':0.6,'explanation':0.4,'excludedSeconds':12,'roundingFrames':1,
   'noLoopsSlowdownOrPadding':True,'sourceMinimum':[1920,1080],'master':[1920,1080,60]},
 'renderer':'Motion Canvas','rendererReason':'Input/action relations, controller comparisons and inspected screenshots benefit from editable2D diagrams and progressive paths.',
 'visualStyle':'research-black-v1','uiPolicy':'yamyam-video-ui-v1',
 'visualEvidencePolicy':'explanation-visual-evidence-v1','footageAnnotationPolicy':'footage-focus-annotations-v1',
 'captions':{'style':'boxed-white-forest-v1','center':[960,970],'fontSize':48,'maxLines':2},
 'voice':authorization['voice'],'humanFinalReview':'pending-complete-Drive-version',
 'youtubeUploadAuthorized':False,'automaticNextVideo':False}
write(P/'planning/chapter-plan.json',plan)
checkpoint=P/'production/latest-checkpoint.json'
old_hash=hashlib.sha256(checkpoint.read_bytes()).hexdigest()
old_blob=subprocess.check_output(['git','hash-object',str(checkpoint)],cwd=ROOT,text=True).strip()
write(checkpoint,{'schemaVersion':2,'slug':P.name,'updatedAt':NOW,'revision':'reference-preserving-v2',
 'stage':'reference-and-footage-preproduction','authorization':'production/reference-preserving-v2/authorization.json',
 'plan':'planning/chapter-plan.json#currentRevision','reviewLedger':'production/review-ledger.json',
 'historicalCheckpoint':{'sha256':old_hash,'gitBlob':old_blob,'source':'prior committed latest-checkpoint.json; historical media QA remains in final-v1 and visual-depth-v1'},
 'nextAction':'Inspect independent native-FHD examples, finish paired narration and all scene designs, then generate approved ElevenLabs voice.',
 'baselineVideoId':'WpCmlV8KyOc','baselinePreserved':True,'newMediaComplete':False,'driveFinalReview':'pending',
 'automaticNextVideo':False,'foreignWork':'Preserve M04 and all other task processes, GPU leases and control selection.'})
ledger=P/'production/review-ledger.json'
d=read(ledger) if ledger.exists() else {'schemaVersion':1,'slug':P.name,'checks':[]}
d.update(revision='reference-preserving-v2',updatedAt=NOW,
 referenceAudit='production/reference-preserving-v2/reference-audit.json',
 selectedScope='D20 through Drive final review; no YouTube replacement or next item',
 humanWholeListening='pending')
write(ledger,d)
work=ROOT/'shared/publishing/video-worklist.json';d=read(work)
r=next(x for x in d['rows'] if x.get('slug')==P.name)
r.update(executionStatus='선택 개정 제작 중 · 원강의 구성·독립 FHD 자료 검토',
 reviewStatus='새 규칙 개정본 제작 중 / 최종 Drive 검수 전',
 humanApproval='이번 편 제작·ElevenLabs 샘플B 승인 / 새 완성본 검수 전',
 notes='D20 한 편만 새 규칙 개정. 기존 비공개 업로드 보존. 참고 구성·사례 복원, 그림/PPT·움직이는 표식·내 목소리 샘플B·1080p60. 완성본 Drive 선검수.')
r['activeRevision']='reference-preserving-v2'
write(work,d)
subprocess.run([__import__('sys').executable,str(ROOT/'scripts/render-video-worklist.py')],cwd=ROOT,check=True)
print('D20 one-video authorization and current records registered; foreign selection/leases untouched')
