"""Record the user's finite visual-only revision without changing other scopes."""
from pathlib import Path
import json, hashlib, datetime
R=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
SLUGS=['limited-color-world','computer-controlled-players','in-game-cutscenes','start-with-climax','kind-to-beginners','respect-player-time']
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def main():
 out=HERE/'authorization.json'
 if out.exists():print('Existing scoped authorization preserved');return
 now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
 auth=dict(id=HERE.name,requestedOnKst='2026-10-28',recordedAt=now,userEvidence='전반적으로 잘만들었어 이야기 구성이나 순서는 / 설명 ppt 부분이 조금 글로만 되어있어서 공감이 잘안되 / 비디오에디팅 유니티 켜뒀어 에셋 안에 졸라많이 넣었으니까 잘 골라서 설명 ppt 부분 보완해주고 다시 만들어줘~ 영상전부',slugs=SLUGS,episodeIds=['D'+str(i) for i in range(25,31)],scope='All six just-delivered D25–D30 videos: improve explanation visuals with contextual imported Unity assets; preserve liked story, order, useful explanation, exact narration/mixed audio, captions, gameplay cuts and clocks.',boundary='Six complete local four-output versions, visual delta QA, updated joint review table and selective Git',localProductionAuthorized=True,fullSixBeforeReview=True,newTts=False,platformMutation=False,automaticOutsideBatch=False,preserveOldVersions=True,status='active-visual-revision',completed=0,total=6)
 baseline=[]
 for s in SLUGS:
  p=read(R/'projects'/s/'project.json')
  files={k:dict(path=p['paths'][k],sha256=sha(R/p['paths'][k]),bytes=(R/p['paths'][k]).stat().st_size) for k in ['videoBurnedCaptions','videoClean','captionsKo','captionsEn']}
  baseline.append(dict(slug=s,episode=p.get('episode'),files=files,manifestSha256=sha(R/'projects'/s/'project.json')))
 auth['baseline']=baseline
 write(out,auth)
 write(HERE/'checkpoint.json',dict(status='asset-selection-and-scene-design',updatedAt=now,completed=0,total=6,authorization='authorization.json',next='Build and inspect meaningful Unity actor/object actions; preserve baseline audio and timeline'))
 control=R/'shared/publishing/video-production-control.json';c=read(control)
 c.setdefault('finiteBatchAuthorizations',{})[HERE.name]={k:v for k,v in auth.items() if k!='baseline'}
 write(control,c)
 print(json.dumps(dict(status='authorized',baselineFiles=24,scope=SLUGS),ensure_ascii=False))
if __name__=='__main__':main()
