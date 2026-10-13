# Historical research-only preparation, superseded by the user's source clarification.
# Direct/stage/reference footage must never enter the production cut list.
raise SystemExit('Superseded research helper. Use final-timeline-v1.json and independent source reviews; do not run this historical preparation.')
from pathlib import Path
import os,json,hashlib
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[4]
N=Path(__file__).resolve().parent
raw=ROOT/'shared/assets/presenting-game-scores/raw'
media=ROOT/'shared/assets/game-footage/hierarchical-game-outlines-smash'
for src,name in [('fccgHnBQ0YM-features.mp4','hierarchy-smash-features.mp4'),('4PRS0UHXJt4-help.mkv','hierarchy-smash-live.mkv')]:
 target=raw/name
 if not target.exists():os.link(media/src,target)
html='''<!doctype html><meta charset="utf-8"><title>계층형 디자인 원본 구간 검수</title><style>body{background:#15191e;color:white;font:20px sans-serif;max-width:1400px;margin:auto}video{width:100%;max-height:780px}button{font:20px sans-serif;margin:6px;padding:12px}pre{white-space:pre-wrap}</style><h1>Smash Ultimate · 원본 메뉴 구간</h1><button onclick="start('hierarchy-smash-features.mp4',8,250)">Direct 8–250초 · 1× 무음</button><button onclick="start('hierarchy-smash-live.mkv',90,170)">Live 도움말 90–170초 · 1× 무음</button><button onclick="v.pause()">일시정지</button><video id="v" controls muted></video><pre id="s">준비</pre><script>const v=document.querySelector('video');let end=0;function start(src,a,b){end=b;v.src=src;v.onloadedmetadata=()=>{v.currentTime=a;v.playbackRate=1;v.muted=true;v.play();};}v.ontimeupdate=()=>{if(v.currentTime>=end)v.pause();document.querySelector('#s').textContent=JSON.stringify({file:v.currentSrc,time:v.currentTime,end,paused:v.paused,rate:v.playbackRate,muted:v.muted,width:v.videoWidth,height:v.videoHeight});};</script>'''
(raw/'hierarchy-smash-review.html').write_text(html,encoding='utf-8')
record={'at':datetime.now(timezone.utc).isoformat(),'liveDownload':{'session':6776,'outerExit':0,'completionChunk':'c19251','sha256':hashlib.sha256((media/'4PRS0UHXJt4-help.mkv').read_bytes()).hexdigest(),'containerDuration':189.987,'socketDemuxWarning':True,'scope':'Only decoded and directly reviewed selected ranges may be used; full download completeness not claimed'},'staticReview':{'directBoards':5,'directSamples':50,'liveBoards':4,'liveSamples':38,'allBoardsDirectlyRead':True,'fullResolutionOrContinuousApproval':False},'candidateRanges':{'direct':[[9,25],[54,76],[94,115],[131,151],[176,190],[209,226],[236,250]],'live':[[90,122],[160,170]]},'candidateMeaning':'main menu / nested help / Records categories / Options levels / per-fighter settings and guide; exclude summoning/shop/reward/title scenes and unrelated combat','normalPlayback':'pending','captionPlan':'Aspect-preserving native image reduced into 1600x900 top center with same-frame background fill; own fixed caption below; inspect all essential native UI and lower source text.'}
(N/'source-review.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Created review helper, exact hardlinks and bounded source review record')
