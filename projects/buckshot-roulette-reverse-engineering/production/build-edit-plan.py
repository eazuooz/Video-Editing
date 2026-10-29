"""Build the selected documentary edit from measured narration and inspected media."""
from pathlib import Path
import hashlib,json,math
P=Path(__file__).resolve().parents[1]
def load(p):return json.loads((P/p).read_text(encoding='utf-8-sig'))
def digest(p):
    h=hashlib.sha256()
    with (P/p).open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
    return h.hexdigest()
def main():
    voice=load('production/local/audio-v1/narration.timing.json');rows=voice['entries']
    frames=[round(x['start']*60) for x in rows]+[math.ceil(voice['duration_seconds']*60)]
    spans={(r['scene_id'],r['paragraph']):(frames[i],frames[i+1]-frames[i]) for i,r in enumerate(rows)}
    plan=load('production/timeline.template.json')
    for k in list(plan):
        if k.startswith('_'):del plan[k]
    plan.update(editReady=True,note='Measured narration; inspected original actions and separate authored runtime experiments. Native-speed cuts; existing voice breathing retained.',encoder='libx264')
    plan['narration'].update(wav='production/local/audio-v1/narration.wav',sha256=digest('production/local/audio-v1/narration.wav'),
        koSrt='production/local/audio-v1/narration.ko.clauses.srt',enSrt='production/local/audio-v1/narration.en.clauses.srt',gainDb=3.5,timingReviewed=True)
    sources=plan['sources'];beats=plan['beats'];audit=load('planning/original-footage-audit.json')
    for s in audit['sources']:
        sources[s['id']]={'file':s['path'],'sha256':s['sha256'],'kind':'actual-gameplay','motionReviewed':True,
            'evidence':'planning/original-footage-audit.json; original live UI actions observed by root, decoded before/action/result frames and exact source PTS verified. Final cut/frame inspection is separate.'}
    for name,path in [('prototype','production/local/documentary-capture/all-v1.avi'),('prototype-intro','captures/prototype-demo-fhd.avi')]:
        sources[name]={'file':path,'sha256':digest(path),'kind':'prototype','motionReviewed':True,
            'evidence':'production/local/documentary-capture/all-v1-events.json and capture QA; independently authored implementation, distinct from commercial gameplay.' if name=='prototype' else 'production/local/test-evidence/prototype-demo-fhd-capture.json; actual FHD demo'}
    events=load('production/local/documentary-capture/all-v1-events.json')
    assert events['complete'] and events['passed'] and not events['headless_only']
    starts={e['scenario']:e['capture_seconds_at_60fps'] for e in events['events'] if e['kind']=='scenario_start'}
    for r in load('production/local/evidence-diagrams/index.json')['paragraphs']:
        assert r['rendered']
        path=f"production/local/evidence-diagrams/{r['id']}/{r['id']}.mp4"
        sources[r['id']]={'file':path,'sha256':digest(path),'kind':'analysis-visualization','motionReviewed':True,
            'evidence':f"production/local/evidence-diagrams/{r['id']}/receipt.json; source-backed authored diagram, synchronized to actual voice anchors; final encoded QA separate"}
    def add(scene,paragraph,source,start,frames_count,label,action,audio=False,gain=0,viewport=1080,overlays=None):
        assert frames_count>0
        beats.append({'id':f'b{len(beats)+1:02d}-{scene}-p{paragraph:02d}', 'source':source,'sourceInSeconds':start,'frames':frames_count,
            'observedAction':action,'narrationConnection':f"{scene}/{paragraph}: "+label,'sourceAudio':audio,'sourceAudioGainDb':gain,
            'speed':1,'loop':False,'freeze':False,'viewportHeight':viewport,'pictureLabel':'' if source=='prototype' or '-p' in source else ('자체 구현 · NEON CHAMBER' if source=='prototype-intro' else '벅샷 룰렛 · 직접 플레이'),
            'protectedRects':[],'overlays':overlays or []})
    def diagram(s,p,offset=0,count=None):
        n=spans[(s,p)][1]-round(offset*60) if count is None else count
        add(s,p,f'{s}-p{p:02d}',offset,n,'해당 문단의 실제 발화에 맞춘 원리와 결과','Cue-aligned progressive state diagram; labels describe our analysis/implementation, not hidden measured original state.')
    def text(t,a,b,x,y,color='focus',size=52):return {'type':'text','text':t,'start':a,'end':b,'x':x,'y':y,'role':color,'fontSize':size}
    def choice_marks():
        return [{'type':'ellipse','x':874.05,'y':603.592,'w':171.9,'h':165.63,'start':1.8,'end':4.8,'stroke':7,'role':'focus'},
                {'type':'arrow','points':[[617.792,557.407],[884.396,656.944]],'start':1.8,'end':4.8,'stroke':7,'role':'focus','revealSeconds':.3},
                text('다시 내 선택',1.8,4.8,371,486)]
    # Opening: an actual input/result, next choice, then the new implementation.
    add('01',1,'second',13,420,'자기 공포탄은 피해 없이 복귀','Original self-target blank shot and shell ejection; charge display unchanged.',True,12,860)
    add('01',1,'second',37,300,'다음 선택을 다시 받음','Player YOU/DEALER selector returns; idle gap removed.',True,12,860,choice_marks())
    add('01',1,'prototype-intro',0,spans[('01',1)][1]-720,'파일 조사부터 새 구현까지의 개요','Own prototype magnifier selection and self-blank animation in real native motion.',True,4.5,860)
    diagram('02',1);diagram('02',2)
    add('03',1,'first',404,360,'장전 때 탄환 구성을 공개','One live/two blank tray is revealed then loaded; order itself is not inferred from the tray.',True,12,860,
        [text('이번 장전: 실탄 1 · 공포탄 2',.3,5.8,320,100,'heading')])
    diagram('03',1,6);diagram('03',2);diagram('03',3)
    diagram('04',1,0,358)
    add('04',1,'prototype',20.2,188,'자신에게 공포탄: 내 차례 유지','Controlled self-target blank shot and unchanged health; next-actor result is visible.',True,4.5)
    add('04',1,'prototype',31.2333333333,228,'상대에게 공포탄: 딜러 차례','Same fixed blank condition aimed at dealer; next actor changes.',True,4.5)
    diagram('04',1,774/60)
    add('04',2,'second',392,360,'수갑의 다음 턴 건너뛰기','Original cuff application animation.',True,9.2,860)
    diagram('04',2,6)
    add('04',3,'second',415,168,'톱이 바꾸는 다음 사격','Active original saw cut through shortened barrel, trimmed from inspected413–419s action.',True,12,860)
    hp=[{'type':'contour','points':[[617.792,301],[767.408,342.407],[761.042,429.204],[614.608,384.611],[617.792,301]],'start':2.6,'end':3.6,'stroke':7,'role':'result'},
        text('딜러 체력 4 → 2',2.6,3.6,252,163,'result')]
    add('04',3,'second',442.2,216,'실탄 피해 2와 실제 체력 감소','Actual live shot/recoil and four-to-two health update, ending before rapid camera pullback.',True,8.8,860,hp)
    diagram('04',3,6.4)
    diagram('05',1,0,436)
    add('05',1,'prototype',72.8833333333,160,'확인한 실탄은 플레이어에게','Known-live dealer aims at player, fires and shows damage1.',True,4.5)
    add('05',1,'prototype',64.8166666667,spans[('05',1)][1]-596,'확인한 공포탄은 자신에게','Known-blank dealer self-targets, fires and shows damage0.',True,4.5)
    diagram('05',2);diagram('06',1);diagram('06',2)
    add('07',1,'prototype',starts['assets'],spans[('07',1)][1],'독립적으로 만든 모델과 움직이는 부품','Native camera/model tour of original Blender-generated geometry in our Godot stage.',True,4.5)
    # Detailed reprise of the overview objects, now matched to measured speech clauses.
    add('07',2,'prototype',96.1833333333,126,'판단하는 머리의 움직임','Articulated dealer thinking, revisited specifically for the animation explanation.',True,4.5)
    add('07',2,'prototype',109.3166666667,215,'선택한 도구가 앞으로 나옴','Camera approaches the tool, then actual magnifier pickup/use and return; stops before unrelated healing fixture.',True,4.5)
    add('07',2,'prototype',11.5,305,'발사 순간 효과음과 판정','Gun pickup, live shot, and actual synchronized own-game result.',True,4.5)
    add('07',2,'prototype',2.8,470,'확인과 배출은 다른 변화','Full magnifier reveal followed by discharge; queue/health show the observed difference.',True,4.5)
    add('07',2,'prototype',114.1166666667,spans[('07',2)][1]-1116,'규칙과 실제 장면을 연결','Purposeful final model tour and implemented state remain visible together.',True,4.5)
    add('08',1,'prototype',starts['damage'],spans[('08',1)][1],'핵심 규칙을 새로운 외형으로 구현한 결과','Controlled cuffs/saw/live-versus-blank damage experiment, identified as our prototype.',True,4.5)
    diagram('08',2)
    assert sum(b['frames'] for b in beats)==frames[-1]
    plan['bodyFrameCount']=frames[-1];plan['humanReview']=False
    plan['annotationEvidence']='planning/original-footage-callouts.json'
    plan['audioDecision']='Original source gains from audio-source-audit; own demo provisional+4.5dB, final mix measured; voiceconstant+3.5dB and float headroom until limiter.'
    (P/'production/timeline.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'beats':len(beats),'bodyFrames':frames[-1],'bodySeconds':frames[-1]/60,'totalSeconds':frames[-1]/60+12}))
if __name__=='__main__':main()
