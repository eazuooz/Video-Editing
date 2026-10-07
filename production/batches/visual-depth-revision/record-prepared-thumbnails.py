"""Metadata only for seven already generated and directly inspected images; no image transformation."""
from pathlib import Path
import json,hashlib,datetime
from PIL import Image
ROOT=Path(__file__).resolve().parents[3]
headlines={'motion-sickness-games':'게임 화면 왜 멀미날까?','hierarchical-game-outlines':'기획서 정리 계층형 아웃라인','game-reward-planning':'보상, 뭘 줘야 할까?','avoid-game-comparisons':'게임 비교, 왜 조심해야 할까?','making-game-sequels':'속편, 뭐가 달라져야 할까?','familiar-game-rules':'익숙한 규칙, 왜 바꿀까?'}
for slug,headline in headlines.items():
 p=ROOT/'projects'/slug/'publishing/thumbnail-depth-v1.png';dest=p.with_suffix('.json')
 if dest.exists():raise RuntimeError('Preserve existing thumbnail metadata')
 im=Image.open(p); width,height=im.size
 result=dict(status='generated-directly-reviewed-prepared-not-uploaded',path=p.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size,width=width,height=height,references=['projects/deconstruct-analyze-rebuild/publishing/thumbnail-v2.png','shared/assets/branding/yamyamcoding-cats-original.png'],method='builtin-imagegen',headlineConcept=headline,branding='얌얌코딩',review=dict(legibleHeadline=True,naturalIllustration=True,noVideoInset=True,catIdentity=True),reviewedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),gitEssentialApproved=False,uploaded=False)
 dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8');print(slug,width,height,p.stat().st_size)
folder=ROOT/'projects/familiar-game-rules/production/visual-depth-v1'
paths=['observation-guides.ko.json','observation-guides.en.json']
records=[]
for name in paths:
 p=ROOT/'projects/familiar-game-rules/narration'/name
 if not p.exists():
  matches=list((ROOT/'projects/familiar-game-rules').rglob(name))
  if len(matches)!=1:raise RuntimeError('Exact guide path required')
  p=matches[0]
 records.append(dict(role='preservedAdditionalGuideScript',path=p.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
(folder/'guide-preservation.json').write_text(json.dumps(dict(files=records,scope='Eight guide paragraphs in addition to the original 62 main paragraphs; directly read in current bilingual script review',changed=False),ensure_ascii=False,indent=2)+'\n','utf-8')
