"""Selected15 gameplay/diagram revisions, with A06 retained byte-for-byte."""
import json,hashlib,subprocess,re
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
HERE=Path(__file__).resolve().parent;BATCH=HERE.parent;ROOT=HERE.parents[3]
WORK=Path('C:/Users/1/Videos/YamyamProduction/animation-gameplay-v8')
OUTPUT=Path('C:/Users/1/Videos/YamyamCoding/animation-gameplay-v8')
BASE=Path('C:/Users/1/Videos/YamyamCoding/animation-overview-v7')
KEY='animationGameplayRevision20261115'
SCOPE=[f'A{i:02}' for i in range(3,19) if i!=6]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,d):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def stamp():return datetime.now(ZoneInfo('Asia/Seoul')).isoformat()
def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()
def run(args,capture=False):
    r=subprocess.run([str(a) for a in args],stdout=subprocess.PIPE if capture else subprocess.DEVNULL,stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS)
    if r.returncode:raise RuntimeError(r.stderr.decode('utf-8','replace')[-6000:])
    return r.stdout
def ff(*args,capture=False):return run(['ffmpeg','-nostdin','-v','error','-y','-filter_complex_threads','2',*args],capture)
def srt(p):
    def sec(v):
        h,m,s=v.replace(',','.').split(':');return int(h)*3600+int(m)*60+float(s)
    out=[]
    for b in re.split(r'\n\s*\n',Path(p).read_text(encoding='utf-8-sig').strip()):
        lines=b.splitlines()
        if len(lines)>2:
            a,z=lines[1].split(' --> ');out.append(dict(start=sec(a),end=sec(z),text='\n'.join(lines[2:])))
    return out
def initialize():
    old=read(BATCH/'overview-v7/plan.json');audit=read(BATCH/'footage-substitution-audit-20261115/report.json')
    motion={e['id']:e for e in read(BATCH/'native-clips-v6/motion-audit.json')['episodes']}
    rows=[]
    for prior in old['episodes']:
        ep=prior['id'];d=read(BASE/ep/'delivery.json');proposal=next(r for r in audit['episodes'] if r['id']==ep)
        files={r['kind']:r for r in d['files']};cues=srt(files['ko.srt']['path'])
        rows.append(dict(id=ep,title=prior['title'],status='preserve-exactly' if ep=='A06' else 'shot-and-narration-planning',
            baselineReceipt=str(BASE/ep/'delivery.json'),baselineFiles=d['files'],baselineFrames=d['frames'],
            opening=prior,summaryAt=d['summaryAt'],recapFrames=600,proposal=proposal,
            candidateIntervals=motion[ep].get('intervals',[]),bodyNarrationCues=cues,
            audio='Original approved voice/BGM outside explicitly rewritten speech; preserve overview and recap speech',
            sourceReferenceMap=str(BATCH/'research'/ep/'research-map.json'),
            boundary='Keep original teaching order and bridges; replace demonstration-specific wording with inspected game observation or labeled principle diagram.'))
    save(HERE/'plan.json',dict(revision='gameplay-v8',requestedAt=stamp(),scope=SCOPE,preserved=['A06'],excludedUploaded=['A01','A02'],episodes=rows,
        userEvidence='추천한 방식으로 전부 수정. A06 그대로. 나머지 실제 게임 영상/필요 원리 도식.대본도 화면에 맞게,개론/마지막정리 유지.통합검수본.',
        policy='15 finite local revisions. Existing reference learning order/depth and original versions preserved. No platform mutation or automatic next batch.',
        resources='CPU4 bounded, costly jobs serialized; no editor capture. Preserve other applications; GPU voice remains blocked while local screen sharing is active.'))
    save(HERE/'checkpoint.json',dict(stage='shot-and-narration-planning',scope=SCOPE,preserved=['A06'],completed=[],humanReviewed=False,platformChanged=False,updatedAt=stamp()))
    print('Planned15 revisions;A06 exact preservation.')
def targets():
    tokens=['마네킹','우리 시연','우리 격자','같은 카메라','고정하고','바꾸겠습니다','조정하','열두 프레임','두 버전']
    for e in read(HERE/'plan.json')['episodes']:
        if e['id']=='A06':continue
        print('\n'+e['id'])
        for i,r in enumerate(e['bodyNarrationCues']):
            t=r['text'].replace('\n',' ')
            if any(w in t for w in tokens):print(i,round(r['start'],2),round(r['end'],2),t)
if __name__=='__main__':
    import sys
    if '--targets' in sys.argv:targets()
    else:initialize()
