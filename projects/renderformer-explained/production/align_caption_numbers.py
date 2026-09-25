"""Improve number/English pronunciation alignment without changing audio or page durations."""
from pathlib import Path
import difflib,json,re,shutil,sys
from prepare_full import stamp
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'projects/renderformer-explained/production/body-review'
CACHE=ROOT/'shared/output/narration/renderformer-explained/qwen3-1.7b-balanced-v1/asr'
terms={'attention is all you need':'어텐션이즈올유니드','how are you':'하우아유','i am fine':'아이앰파인',
 'self-attention':'셀프어텐션','attention':'어텐션','renderformer':'렌더포머','transformer':'트랜스포머',
 'softmax':'소프트맥스','rms':'알엠에스','dpt':'디피티','hdr':'에이치디알','psnr':'피에스엔알',
 'ssim':'에스에스아이엠','lp ips':'엘피아이피에스','lpips':'엘피아이피에스',
 '칠백육십팔':'768','이천사십팔':'2048','이천십칠':'2017','이천이십오':'2025','오백십이':'512',
 '백구십이':'192','백이십팔':'128','예순네':'64','육십사':'64','쉰네':'54','백팔':'108',
 '열여섯':'16','열한':'11','열두':'12','여덟':'8','여섯':'6','아홉':'9','스무':'20',
 '삼차원':'3차원','이차원':'2차원','일차원':'1차원'}
def norm(t):
    t=t.lower()
    for a,b in terms.items():t=t.replace(a,b)
    for a,b in [('q','큐'),('k','케이'),('v','브이')]:t=t.replace(a,b)
    return re.sub('[^a-z0-9가-힣]','',t)
data=json.loads((BASE/'timing.json').read_text(encoding='utf-8'))
changes=[]
for scene in data['scenes']:
    page=scene['sourcePage']
    raw=json.loads((BASE/'page22-asr-v2.json' if page==22 else CACHE/f'page{page:02}.json').read_text(encoding='utf-8'))
    words=raw['chunks'] if page==22 else raw['words']
    expected=''.join(norm(c.get('spokenKo',c['ko'])) for c in scene['cues'])
    observed=''.join(norm(w['text']) for w in words)
    mapping={};times=[]
    for b in difflib.SequenceMatcher(None,expected,observed,autojunk=False).get_matching_blocks():
        mapping.update({b.a+k:b.b+k for k in range(b.size)})
    for w in words:
        a,b=w['timestamp'];times.extend([(0 if a is None else a,scene['duration']-1.15 if b is None else b)]*len(norm(w['text'])))
    keys=sorted(mapping)
    def at(i,end=False):
        if i in mapping:j=mapping[i]
        else:
            before=max((k for k in keys if k<i),default=None)
            after=min((k for k in keys if k>i),default=None)
            if before is None:j=0
            elif after is None:j=len(times)-1
            else:j=round(mapping[before]+(mapping[after]-mapping[before])*(i-before)/(after-before))
        return times[max(0,min(len(times)-1,j))][int(end)]
    cursor=0;local=[]
    for cue in scene['cues']:
        n=len(norm(cue.get('spokenKo',cue['ko'])));a=max(.35,at(cursor)+.31);b=min(scene['duration']-.2,at(cursor+n-1,True)+.41)
        if local:
            a=max(a,local[-1]['start']+.08);local[-1]['end']=min(local[-1]['end'],a)
        if b<=a:raise ValueError(f'Invalid cue {page}: {cue}')
        local.append({**cue,'start':a,'end':b});cursor+=n
    for i,(old,new) in enumerate(zip(scene['cues'],local)):
        if abs(old['start']-new['start'])>.019 or abs(old['end']-new['end'])>.019:
            changes.append({'page':page,'cue':i,'old':[old['start'],old['end']],'new':[new['start'],new['end']],'text':old['ko']})
    scene['cues']=local
data['captions']=[{**c,'start':c['start']+s['firstFrame']/60,'end':c['end']+s['firstFrame']/60,'page':s['sourcePage']} for s in data['scenes'] for c in s['cues']]
data['englishStatus']='translated-needs-timecode-regeneration'
(BASE/'timing.number-aligned.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
(BASE/'alignment-changes.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(changes,ensure_ascii=False,indent=2))
if '--apply' in sys.argv:
    # The only timed slide animations are on pages 14 and 48. Their cues must
    # remain unchanged, or the clean master must be rendered again as well.
    assert not any(c['page'] in [14,48] for c in changes)
    backup=BASE/'timing.before-number-alignment.json'
    if backup.exists():raise FileExistsError(backup)
    shutil.copy2(BASE/'timing.json',backup)
    shutil.copy2(BASE/'timing.number-aligned.json',BASE/'timing.json')
    shutil.copy2(BASE/'timing.json',ROOT/'motion-canvas/src/projects/renderformer-explained/full/narrated/timing.generated.json')
    (BASE/'renderformer.ko.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(c["start"])} --> {stamp(c["end"])}\n{c["ko"]}' for i,c in enumerate(data['captions']))+'\n',encoding='utf-8')
