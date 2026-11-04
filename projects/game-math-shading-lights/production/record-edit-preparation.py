"""Record inspected edit layout and source-specific audio choices, without QA inflation."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
P=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat()
audit=read(P/'planning/footage-audit.json')
for s in audit['sources']:
    if s['id']=='FRfnXAIbA-M':
        s['audio']['policyFollowup']={'checkedAt':now,'policy':'https://rawfury.com/lets-play/','audioTeamPrimaryPortfolio':'https://www.noknokaudio.com/','credit':'Townscaper audio — NokNok Audio (Martin Kvale, Oda Tilset).','decision':'Retain synchronized native game mix with ducking and include the verified audio-team credit. No added background music.','actualListening':False}
    if s['id']=='X9UdRR_4Rog':
        s['audio']['sourceSpecificDecision']={'checkedAt':now,'policy':'https://www.xbox.com/en-US/developers/rules','decision':'Omit only this Forzavista menu audio because any third-party soundtrack is not separately identified/cleared. Preserve the unchanged native video and original source file. Keep cleared game audio for the other sources.','reason':'Current Microsoft grant does not cover third-party music. Delegated production preference chooses the local rights-safe excerpt rather than inventing a music-free track.','finalListening':False}
save(P/'planning/footage-audit.json',audit)
plan=read(P/'planning/production-plan.json')
choice={'id':'m21-caption-safe-gameplay-layout','decision':'Fit native 16:9 game image at192,48 /1536×864 inside1080p master. Source/action cropped neither spatially nor by slowdown. Top48px holds names/annotation meaning; one-clause fixed caption remains960,970.','reason':'Preserve game UI and visible annotation target while keeping final caption geometry. Original sources remain nativeFHD+.','verified':'Seven native target frames inspected. Caption text in these layout frames is provisional, not final word timing. Final encoded motion/375px review remains pending.','at':now}
plan['choices']=[c for c in plan.get('choices',[]) if c.get('id')!=choice['id']]+[choice]
save(P/'planning/production-plan.json',plan)
ledger=read(P/'production/review-ledger.json')
check={'id':'gameplay-edit-layout-v3','status':'target-frame-inspected-revisions-pending','checkedAt':now,'framesInspected':['000','007','018','027','031','049','060'],'path':'production/local/annotation-layout-v3','findings':['All seven marks point at actual named surfaces/objects.','Original UI, watermark and aspect remain visible.','Townscaper pastel wall needs dark edge around teal line.','ASS closes open arcs, producing an unwanted straight chord; changed to hollow full ellipse.','Increase small top labels to36px and use short canonical Korean game names.'],'correctionsInCode':'production/compose-lecture.py','codeSha256':sha(P/'production/compose-lecture.py'),'revisedFramesViewed':False,'captionTimingVerified':False,'motionVerified':False,'mobileVerified':False,'humanListening':False}
ledger['checks']=[c for c in ledger['checks'] if c['id']!=check['id']]+[check]
save(P/'production/review-ledger.json',ledger)
print('Recorded seven-frame layout review, corrections and source-specific audio decisions; no final review claimed.')
