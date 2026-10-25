"""Record the user's approval of the delivered seventh Short, without other scope."""
import datetime, hashlib, json
from pathlib import Path
P = Path(__file__).resolve().parents[1]
R = P.parents[1]
def read(p): return json.loads(p.read_text(encoding='utf8'))
def save(p, x): p.write_text(json.dumps(x, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
d = read(P/'production/delivery.json')
master = d['files']['captioned']
assert hashlib.sha256(Path(master['path']).read_bytes()).hexdigest() == master['sha256']
assert master['sha256'] == 'e9a3b57c7836d2226b7efc2a2f6d20b82028ed342af3648214bf4ae3fa61fef3'
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
approval = {'status':'accepted-for-upload', 'recordedAt':now,
 'userEvidence':'응 기존꺼내리고수정영상으로 업로드해줘',
 'kind':'explicit-upload-request-after-full-local-delivery',
 'masterSha256':master['sha256'], 'version':d['masterVersion'],
 'wholeListeningExplicitlyConfirmed':False,
 'scope':'Upload seventh revised master privately and complete available settings. No new schedule inferred when no seventh baseline exists. Preserve distinct fifth Portal-recursion video.',
 'baselineDiscovery':{'studioSearch':'반쯤','resultCount':0,'ledger':'not-uploaded',
 'differentVideoPreserved':{'videoId':'bHr-JtyI4rs','title':'포털 속 포털, 컴퓨터는 무한히 그릴까?｜재귀 렌더링 #게임개발','order':5,'state':'scheduled'},
 'conclusion':'No prior seventh upload identified. No deletion or unpublishing performed.'}}
save(P/'publishing/upload-approval.json', approval)
for rel in ['production/delivery.json','production/checkpoint.json','production/review-ledger.json']:
 x=read(P/rel);x['humanReview']='accepted-for-upload';x['actualHumanReview']=approval
 if rel.endswith('checkpoint.json'):x.update(status='upload-authorized', next='Upload approved v5 once; retain exact new ID and finish available settings.',updatedAt=now)
 save(P/rel,x)
cpath=R/'shared/publishing/video-production-control.json';c=read(cpath)
c['portalTraversalShortsAuthorization']['currentRevision']['uploadAuthorization']=approval
for x in c['portalTraversalShortsAuthorization']['deliveries']:
 if x['slug']==P.name:x['humanReview']='accepted-for-upload'
save(cpath,c)
print('Approved master verified; only seventh upload authorized.')
