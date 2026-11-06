"""CPU-only, exact03.02 voice/ASR -> frame timeline and plain KO/EN captions.

No recognition, synthesis, model, engine, encode or platform work is started.
Internal boundaries come from literal authored text against blind ASR words,
never paragraph-length ratios or phonetic aliases. Raw discrepancies remain QA.
"""
from __future__ import annotations
import argparse, copy, difflib, hashlib, importlib.util, json, math, re, sys
from pathlib import Path
from PIL import ImageFont
from initialize import HERE, ROOT, MEDIA, read, save

sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('first_timeline_asr',HERE/'run-first-asr.py')
asr=importlib.util.module_from_spec(spec);spec.loader.exec_module(asr)
PROJECT=ROOT/'projects/shorts-leveldesign-03-02'
FPS=60;A='tf2-black-knight-0248-0295';B='tf2-black-knight-2138-2226'


class Pending(RuntimeError):pass


# Semantic English phrase boundaries are authored here; every supplied KO/EN
# paragraph must be retained exactly except whitespace when concatenated.
CLAUSES=[
 ('P1a','이 수레 옆에서 싸우는 사람들을 보세요.','Watch the players fighting beside this cart.'),
 ('P1b','팀 포트리스 2의 수레 밀기 모드에서',"In Team Fortress 2's Payload mode,"),
 ('P1b','공격팀은 폭탄 수레를 상대 진영까지 보내야 이깁니다.','the attacking team must escort a bomb cart into the enemy base.'),
 ('P1c','그래서 수레가 지나갈 길만 있으면 될 것 같죠.','A path wide enough for the cart might sound sufficient.'),
 ('P1d','그런데 초기 설계에서는','Yet in the early design,'),
 ('P1d','사람도 멀쩡히 다니던 터널에 수레를 넣자,','adding the cart to a tunnel that players could use'),
 ('P1d','오히려 사람이 막히는 문제가 생겼습니다.','created a new problem: the players were getting blocked.'),
 ('P2a','배드워터 베이슨이라는 맵의 초기 시제품에서는,','Early prototypes of the map Badwater Basin'),
 ('P2a','다른 맵에서 쓰던 기본 터널 폭을 그대로 가져왔습니다.','reused the standard tunnel width from other maps.'),
 ('P2b','수레 자체는 들어갔지만,','The cart fit,'),
 ('P2b','곁에서 움직여야 하는 플레이어의 공간이 부족했던 거예요.','but players did not have enough space to move alongside it.'),
 ('P2c','수레가 통과한다는 검사와,','Checking whether a cart can pass'),
 ('P2c','수레 옆에서 사람이 이동할 수 있다는 검사는','and checking whether a person can move beside that cart'),
 ('P2c','달랐던 겁니다.','are two different tests.'),
 ('P3a','위에서 보면 차이가 분명해집니다.','The difference becomes clear from above.'),
 ('P3b','터널 한가운데 수레가 서면,','With a cart in the middle,'),
 ('P3b','사람이 쓸 수 있는 길은 양옆에 남은 틈입니다.',"the player's routes are the gaps on either side."),
 ('P3c','수레를 제외한 폭이','The width left after the cart is removed'),
 ('P3c','두 옆으로 나뉘는 거죠.','is divided between those sides.'),
 ('P3d','이 틈보다 사람의 충돌 영역이 넓으면,',"If a gap is narrower than the player's collision volume,"),
 ('P3d','화면에 빈틈이 보여도 몸은 지나가지 못합니다.','a visible opening still will not let the body through.'),
 ('P3e','지금 둘러 그린 선은','The outline now shows'),
 ('P3e','우리 실험 속 충돌 캡슐의 범위입니다.','the bounds of our experiment’s collision capsule.'),
 ('P3e','위쪽 카메라로 내려다본 모습을 표시한 거예요.','It marks how that capsule looks from the overhead camera.'),
 ('P4a','이번에는 수레도, 사람도, 이동 속도도 그대로 두고','Now we keep the cart, player and movement speed unchanged,'),
 ('P4a','양옆 벽만 벌려 볼게요.','and move only the two walls apart.'),
 ('P4b','같은 이동 입력을 받던 사람이','The player receiving the same movement commands'),
 ('P4b','이제는 수레 옆을 지나갑니다.','can now pass beside the cart.'),
 ('P4c','수레의 폭을 재는 것에서 끝내지 않고,','Instead of measuring only the cart,'),
 ('P4c','그 옆에서 사람이 해야 할 행동까지 함께 검사한 거예요.','we test the action a player must perform alongside it.'),
 ('P4d','실제 배드워터 베이슨도 플레이테스트를 거쳐',"Badwater Basin's developers likewise"),
 ('P4d','이 통행 공간을 넓혔습니다.','widened this circulation space after playtesting.'),
 ('P5a','이처럼 캐릭터의 몸집과 이동 방식에 맞춰','The reference dimensions used to fit spaces'),
 ('P5a','공간을 정할 때 쓰는 기준 치수를',"to a character's body and movement"),
 ('P5a','게임플레이 메트릭스라고 부릅니다.','are called gameplay metrics.'),
 ('P5b-door','문을 통과하는 몸의 크기,','They include the body that must fit through a doorway,'),
 ('P5b-jump','점프가 닿는 범위,','the reach of a jump,'),
 ('P5b-cart','다른 물체와 함께 쓸 공간을 먼저 확인하는 겁니다.','and the space required alongside another object.'),
 ('P5c','게임마다 몸집과 이동 방식이 다르니,','Bodies and movement differ between games,'),
 ('P5c','이 기준도 그 게임에서 다시 확인해야 합니다.','so these metrics must be checked in the game being designed.'),
 ('P6a','그렇다고 모든 통로를 넓히면 좋은 건 아닙니다.','This does not mean every corridor should be wider.'),
 ('P6b','공포 게임에서는 좁은 복도가','In a horror game, a narrow corridor'),
 ('P6b','적 한 마리를 큰 위협으로 만들기도 하죠.','can make a single enemy a serious threat.'),
 ('P6c','중요한 건 이 레벨에서 어떤 행동을 시키려는가입니다.','What matters is the action the level is meant to support.'),
 ('P6d','수레를 밀며 싸우게 하려면,','Fighting while escorting a cart required a tunnel'),
 ('P6d','수레가 들어가는 터널보다','that lets people move alongside it,'),
 ('P6d','사람이 그 옆에서 움직일 수 있는 터널이 필요했던 거예요.','beyond simply letting the cart fit inside.'),
]


def text_identity(text):return re.sub(r'\s+','',text)
def frame(seconds):return int(math.floor(seconds*FPS+.5))


def fonts():
    path=Path('C:/Windows/Fonts/NotoSansKR-VF.ttf')
    if not path.is_file():raise Pending('Exact shared NotoSansKR variable caption font is missing')
    normal=ImageFont.truetype(str(path),48);normal.set_variation_by_axes([500])
    bold=ImageFont.truetype(str(path),48);bold.set_variation_by_axes([700])
    return normal,bold,[path]


def wrap(text,normal,bold,width=800):
    rows=[];line=''
    for word in text.split():
        candidate=(line+' '+word).strip()
        if max(normal.getlength(candidate),bold.getlength(candidate))>width:
            if not line:raise Pending('Single caption word exceeds fixed48px width: '+word)
            rows.append(line);line=word
        else:line=candidate
    if line:rows.append(line)
    if len(rows)>2:raise Pending('Authored caption clause needs a semantic split, not a smaller font: '+text)
    return rows


def align_literal(expected,record,entry):
    """Map exact expected characters to blind-ASR word intervals, preserving errors."""
    assert record['task']['expected']==expected and record['text']==record['rawRecognition']['text']
    assert record['comparison']==asr.comparison(expected,record['text'])
    words=record['globalWords'];assert words,'Blind ASR has no words'
    recognized='';char_words=[];previous=-1.0
    for index,w in enumerate(words):
        start,end=w['timestamp']
        if start is None or end is None:raise Pending('Blind ASR word timestamp missing; explicit alignment required')
        if end<start or start<entry['start']-.08 or end>entry['end']+.08:raise Pending('Blind ASR word lies outside exact paragraph PCM')
        if start<previous-.08:raise Pending('Blind ASR word clock moves backwards')
        previous=start;chars=asr.folded(w['text']);recognized+=chars;char_words.extend([index]*len(chars))
    a=asr.folded(expected);matcher=difflib.SequenceMatcher(None,a,recognized,autojunk=False)
    mapping={};differences=[]
    for tag,i,j,k,l in matcher.get_opcodes():
        if tag=='equal':mapping.update((i+q,k+q) for q in range(j-i))
        else:differences.append(dict(kind=tag,expected=a[i:j],recognized=recognized[k:l],expectedRange=[i,j],recognizedRange=[k,l]))
    if not mapping:raise Pending('No literal word anchors; never substitute pronunciation aliases')
    diagnostics=[]
    def boundary(position):
        if position==0:return max(entry['start'],words[char_words[min(mapping.values())]]['timestamp'][0])
        if position==len(a):return min(entry['end'],words[char_words[max(mapping.values())]]['timestamp'][1])
        left=max((i for i in mapping if i<position),default=None);right=min((i for i in mapping if i>=position),default=None)
        if left is None or right is None or position-1-left>12 or right-position>12:
            raise Pending('Caption boundary lacks nearby literal ASR anchors')
        lw=char_words[mapping[left]];rw=char_words[mapping[right]]
        if lw==rw:
            # A whitespace/punctuation boundary inside one recognized word is
            # a marked interpolation, never a claimed phoneme measurement.
            indices=[i for i,v in enumerate(char_words) if v==lw]
            fraction=(mapping[left]+1-indices[0])/len(indices)
            start,end=words[lw]['timestamp'];value=start+(end-start)*fraction
            diagnostics.append(dict(expectedBoundary=position,method='within-recognized-word-interpolation',word=words[lw],humanTimingReviewRequired=True))
        else:
            value=(words[lw]['timestamp'][1]+words[rw]['timestamp'][0])/2
            if right-left>1:diagnostics.append(dict(expectedBoundary=position,method='neighboring-literal-anchors-across-ASR-difference',leftWord=lw,rightWord=rw,humanTimingReviewRequired=True))
        return max(entry['start'],min(entry['end'],value))
    def span(begin,end):
        mapped=[char_words[v] for k,v in mapping.items() if begin<=k<end]
        indices=list(range(min(mapped),max(mapped)+1)) if mapped else []
        return dict(expectedNormalizedCharacterRange=[begin,end],recognizedWordIndices=indices,
            recognizedLiteral=' '.join(words[i]['text'] for i in indices),
            rawRecognitionSHA256=asr.digest(record['rawRecognition']),
            sourceAudioSHA256=record['task'].get('audioSHA256'),asrTaskKey=record['task'].get('key'),
            aliasesApplied=False,normalization='NFC/punctuation/spacing/Latin case only; no phonetic replacements',
            humanListening=False,automaticSpeechPass=False)
    boundary.span=span
    return boundary,dict(expectedLiteral=expected,recognizedLiteral=record['text'],comparison=record['comparison'],
        wordTextMatchesRawLiteral=asr.folded(record['text'])==recognized,alignmentDifferences=differences,
        boundaryDiagnostics=diagnostics,aliasesApplied=False,automaticSpeechPass=False,humanListening=False)


def emphasis(ko,en):
    pairs=[('게임플레이 메트릭스','gameplay metrics','term'),('충돌 영역','collision volume','term'),
           ('충돌 캡슐','collision capsule','term'),('지나가지 못합니다','will not let','problem'),
           ('막히는','blocked','problem'),('지나갑니다','pass','result')]
    result={'ko':[],'en':[]}
    for k,e,role in pairs:
        if k not in ko:continue
        result['ko']=[dict(start=ko.index(k),end=ko.index(k)+len(k),role=role)]
        match=re.search(re.escape(e),en,re.I)
        if match:result['en']=[dict(start=match.start(),end=match.end(),role=role)]
        break
    return result


def one_line_emphasis(text,lines,spans):
    if not spans:return []
    span=copy.deepcopy(spans[0]);positions=[];cursor=0
    for line in lines:
        start=text.find(line,cursor)
        assert start>=0,'Wrapped caption line is not a literal substring'
        positions.append((start,start+len(line)));cursor=start+len(line)
    if not any(a<=span['start']<span['end']<=b for a,b in positions):
        # Keep one useful exact word if the complete phrase straddles lines.
        # The authored display/speech remains unchanged; this is color only.
        word=text[span['start']:span['end']].split()[-1]
        start=text.rfind(word,span['start'],span['end']);span.update(start=start,end=start+len(word))
        assert any(a<=span['start']<span['end']<=b for a,b in positions),'Highlight still crosses wrapped lines'
    return [span]


def caption_and_beat_frames(narration,plan,timing,paragraphs,normal,bold):
    cues=[];beats=[];paragraph_frames=[];reviews=[]
    for pnum,(ko,en,pp,entry,record) in enumerate(zip(narration['narrationKo'],narration['paragraphsEn'],plan['paragraphPlans'],timing['entries'],paragraphs),1):
        rows=[row for row in CLAUSES if row[0].startswith('P'+str(pnum))]
        assert text_identity(' '.join(row[1] for row in rows))==text_identity(ko),'KO authored clauses stale'
        assert text_identity(' '.join(row[2] for row in rows))==text_identity(en),'EN authored clauses stale'
        assert text_identity(' '.join(b['speechCue'] for b in pp['subbeats']))==text_identity(ko),'25-beat plan is stale'
        get_boundary,review=align_literal(ko,record,entry);reviews.append(dict(paragraph=pnum,**review))
        cursor=0;caption_ids=[];local=[]
        for bid,k,e in rows:
            begin=cursor;start=get_boundary(cursor);cursor+=len(asr.folded(k));end=get_boundary(cursor)
            sf,ef=frame(start),frame(end)
            if ef<=sf:raise Pending('Caption has no positive frame duration: '+k)
            cue=dict(id=f'c{len(cues)+1:03}',paragraph=pnum,beatId=bid,startFrame=sf,endFrameExclusive=ef,
                ko=k,en=e,koLines=wrap(k,normal,bold),enLines=wrap(e,normal,bold),emphasis=emphasis(k,e),
                literalDisplayAlignment=dict(displayLiteral=k,**get_boundary.span(begin,cursor)))
            for lang in ['ko','en']:cue['emphasis'][lang]=one_line_emphasis(cue[lang],cue[lang+'Lines'],cue['emphasis'][lang])
            if pnum==5 and '메트릭스' in k and '매트릭스' in cue['literalDisplayAlignment']['recognizedLiteral']:
                cue['literalDisplayAlignment']['canonicalDisplayReview']=dict(
                    scope='This exact cue only; canonical Gameplay Metrics display retains 메트릭스 while raw blind ASR spells 매트릭스.',
                    authority='Root explicit content-review instruction; unchanged approved PCM and raw ASR remain pinned.',
                    audioPronunciationVerified=False,humanListening=False,automaticSpeechPass=False,
                    retainRawDiscrepancyInQA=True,globalReplacementApplied=False)
            cues.append(cue);local.append(cue);caption_ids.append(cue['id'])
        pstart=frame(entry['start']);pend=frame(entry['end'])
        for i,b in enumerate(pp['subbeats']):
            assigned=[c for c in local if c['beatId']==b['id']];assert assigned,'No captions for authored subbeat'
            start=pstart if i==0 else assigned[0]['startFrame']
            end=pend if i==len(pp['subbeats'])-1 else next(c['startFrame'] for c in local if c['beatId']==pp['subbeats'][i+1]['id'])
            if end<=start:raise Pending('Subbeat has no positive frame duration')
            beats.append(dict(id=b['id'],paragraph=pnum,startFrame=start,endFrameExclusive=end,captionIds=[c['id'] for c in assigned],plan=copy.deepcopy(b)))
        paragraph_frames.append(dict(paragraph=pnum,startFrame=pstart,endFrameExclusive=pend,captionIds=caption_ids))
    for left,right in zip(cues,cues[1:]):assert left['endFrameExclusive']<=right['startFrame'],'Captions overlap'
    return cues,beats,paragraph_frames,reviews


class SourcePool:
    def __init__(self,windows):
        # Windows are decoded native30fps frame bounds. A fresh cut may skip
        # half a native frame after an odd60fps duration; it never repeats it.
        self.windows=[dict(sourceId=s,begin=round(a*30),end=round(b*30),cursor=round(a*30)) for s,a,b in windows]
    def take(self,count):
        result=[]
        for w in self.windows:
            available=(w['end']-w['cursor'])*2
            if not available:continue
            n=min(count,available);start=w['cursor'];w['cursor']+=math.ceil(n/2)
            result.append(dict(sourceId=w['sourceId'],sourceLocalInPts=start/30,sourceStartFrame=start,frameCount=n,rate=1))
            count-=n
            if count==0:return result
        raise Pending('Inspected matching native-speed footage budget exhausted; select a meaningful new range rather than loop/slow/pad')


def pools():
    return {name:SourcePool(windows) for name,windows in {
        'p1':[(A,25,26+25/30),(B,40,51)],  # root full-frame reviewed opening, max26.8333
        'p2':[(B,5.8,11.2),(B,15,18.5)],
        'p4':[(B,58,69)],'p5a':[(A,35.8,46.8)],
        'door':[(A,4.2,6.7)],'jump':[(A,8.6,11.2)],'cart':[(B,32,37)],'p5c':[(B,69,74.9)],
        'route':[(B,18.5,25.5),(B,27.5,31)],
        'close-prefix':[(A,11.2,19.2)],'close-end':[(B,75,81)]}.items()}


def term_for(bid,glossary):
    name=None;presentation='chip'
    if bid in ['P1b','P1c','P1d','P2a','P2b','P2c']:name='Payload';presentation='definition' if bid=='P1b' else 'chip'
    if bid in ['P3d','P3e','P4a','P4b','P4c','P4d']:name='Collision Volume';presentation='definition' if bid=='P3d' else 'chip'
    if bid.startswith('P5') or bid.startswith('P6'):name='Gameplay Metrics';presentation='definition' if bid=='P5a' else 'chip'
    if not name:return []
    term=next(g for g in glossary if g['english']==name)
    return [dict(english=term['english'],korean=term['korean'],meaning=term['meaning'],presentation=presentation)]


def make_sections(beats,captions,sources,glossary):
    by_beat={b['id']:b for b in beats};bank=pools();out=[]
    plays=[]
    for mode,last,first in [('narrow','P2b','P2a'),('wide','P4b','P4a')]:
        end=by_beat[last]['endFrameExclusive'];start=end-270
        if start<by_beat[first]['startFrame']:raise Pending('Actual speech leaves less than4.5s for the complete native trial')
        plays.append(dict(mode=mode,start=start,end=end))
    for b in beats:
        bid=b['id'];plan=b['plan'];start=b['startFrame'];end=b['endFrameExclusive'];pieces=[]
        if plan['pictureRole']=='independent-gameplay':
            groups=[]
            if bid=='P6d':
                cs=[c for c in captions if c['beatId']==bid];boundary=cs[-1]['startFrame']
                groups=[('close-prefix',start,boundary),('close-end',boundary,end)]
            else:
                key='p1' if bid.startswith('P1') else 'p2' if bid=='P2c' else 'p4' if bid.startswith('P4') else {'P5a':'p5a','P5b-door':'door','P5b-jump':'jump','P5b-cart':'cart','P5c':'p5c','P6a':'route','P6c':'route'}[bid]
                groups=[(key,start,end)]
            for key,gs,ge in groups:
                pos=gs
                for segment in bank[key].take(ge-gs):
                    n=segment.pop('frameCount');pieces.append(dict(kind='gameplay',startFrame=pos,endFrameExclusive=pos+n,**segment));pos+=n
        else:
            splits=sorted({start,end,*[v for play in plays for v in [play['start'],play['end']] if start<v<end]})
            for sf,ef in zip(splits,splits[1:]):
                play=next((p for p in plays if p['start']<=sf<ef<=p['end']),None)
                mode=play['mode'] if play else ('wide' if bid.startswith('P4') else 'narrow')
                layout='dual' if bid.startswith('P3') or play else 'single-observer'
                if play:
                    native=dict(mode=mode,layout=layout,startNativeFrame=sf-play['start'],frameCount=ef-sf,playbackRate=1,holdPolicy=None)
                else:
                    held=0 if bid in ['P2a','P4a','P6b'] else 269
                    native=dict(mode=mode,layout=layout,startNativeFrame=held,frameCount=1,playbackRate=1,
                        holdPolicy=dict(frame=held,reason=plan['action'],activeExplanation=[plan['before'],plan['action'],plan['result']],notGameplay=True))
                pieces.append(dict(kind='illustration' if bid=='P6b' else 'native',startFrame=sf,endFrameExclusive=ef,native=native))
        for piece in pieces:
            piece.update(id=f'section{len(out)+1:03}',beatId=bid,paragraph=b['paragraph'],pictureRole=plan['pictureRole'],catPose=None,
                termChips=term_for(bid,glossary),annotationCues=[],semanticAnnotationIntent=dict(speechCue=plan['speechCue'],before=plan['before'],action=plan['action'],result=plan['result'],planAnnotationIds=plan.get('annotations',[])))
            if piece['kind']=='gameplay':
                source=sources[piece['sourceId']];piece.update(sourcePath=source['path'],sourceSHA256=source['sha256'],sourceNativeFps=30,aspectPolicy='full16:9 contain; no crop/stretch',originalAudio=False)
                if piece['sourceId']==A and 25<=piece['sourceLocalInPts']<26+25/30:
                    piece['annotationCues']=[dict(kind='opening-tracks',startFrame=piece['startFrame'],endFrameExclusive=piece['endFrameExclusive'])]
            elif bid in ['P3b','P3c','P3d','P3e','P4a','P4b']:
                # Reveal the relationship before its technical collision term.
                # The saved engine pixels/thin lines remain untouched.
                parts=['clearance']
                if bid in ['P3d','P3e','P4a','P4b']:parts.append('footprint')
                if bid=='P4b':parts.append('input')  # first spoken same-input statement
                piece['annotationCues']=[dict(kind='native-guides',startFrame=piece['startFrame'],endFrameExclusive=piece['endFrameExclusive'],guideParts=parts)]
            if bid=='P6b':piece['illustrationIntent']='One clearly labeled opponent/pictogram restricts route in our own corridor; not a commercial horror-game or simulated enemy result.'
            out.append(piece)
    assert out and out[0]['startFrame']==0
    for left,right in zip(out,out[1:]):assert left['endFrameExclusive']==right['startFrame'],'Timeline has a hole/overlap'
    used={sid:[] for sid in sources}
    for s in out:
        if s['kind']=='gameplay':used[s['sourceId']].append([s['sourceStartFrame'],s['sourceStartFrame']+math.ceil((s['endFrameExclusive']-s['startFrame'])/2)])
    for ranges in used.values():
        ranges.sort()
        for left,right in zip(ranges,ranges[1:]):assert left[1]<=right[0],'An actual source frame was repeated'
    for mode in ['narrow','wide']:
        moving=[s for s in out if s.get('native',{}).get('mode')==mode and s['native']['holdPolicy'] is None]
        frames=[f for s in moving for f in range(s['native']['startNativeFrame'],s['native']['startNativeFrame']+s['native']['frameCount'])]
        assert frames==list(range(270)),f'{mode} trial must play exactly once at1x'
    return out


def srt(captions,language):
    def stamp(f):
        ms=round(f*1000/FPS);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
        return f'{h:02}:{m:02}:{s:02},{ms:03}'
    return ''.join(f"{i}\n{stamp(c['startFrame'])} --> {stamp(c['endFrameExclusive'])}\n{chr(10).join(c[language+'Lines'])}\n\n" for i,c in enumerate(captions,1))


def pin(role,path):return dict(role=role,path=str(Path(path).resolve()),sha256=asr.voice.sha(path))


def mix_info(path):
    # The existing audio processor writes IEEE-float WAV. stdlib wave only
    # accepts integer PCM on supported Python versions; soundfile reads both.
    import soundfile as sf
    path=Path(path).resolve();info=sf.info(path)
    if info.format!='WAV' or info.frames<=0:raise Pending('Final mix must be the exact completed WAV')
    return dict(path=str(path),sha256=asr.voice.sha(path),sampleRate=info.samplerate,channels=info.channels,
                frames=info.frames,durationSeconds=info.frames/info.samplerate,subtype=info.subtype)


def load_exact(asr_job):
    output,evidence,timing=asr.exact_voice();path=Path(asr_job).resolve();job=read(path)
    assert path==(output/'review/independent-asr-v1'/job['fingerprint'][:24]/'job.json').resolve()
    assert asr.digest(job['identity'])==job['fingerprint'] and job['identity']['profile']==asr.PROFILE
    assert job['identity']['voiceFingerprint']==evidence['fingerprint']
    assert job['identity']['aggregateSHA256']==evidence['aggregateWav']['sha256'] and job['identity']['timingSHA256']==evidence['timing']['sha256']
    review_path=path.parent/'review.json'
    if not review_path.exists():raise Pending('Exact completed blind ASR review is not available')
    review=read(review_path);records=[asr.read_cache(job,t) for t in job['identity']['tasks']]
    if any(r is None for r in records):raise Pending('Blind ASR still lacks paragraphs or join windows')
    paragraphs=[r for r in records if r['task']['kind']=='paragraph'];joins=[r for r in records if r['task']['kind']=='boundary']
    assert len(paragraphs)==6 and len(joins)==5
    assert review['fingerprint']==job['fingerprint'] and review['paragraphs']==paragraphs and review['boundaryWindows']==joins
    for record in records:
        task=record['task'];words,flags=asr.words_from_raw(record['rawRecognition'],task)
        assert record['globalWords']==words and record['boundaryFlags']==flags
        assert record['expectedPrompt'] is None and record['aliasesApplied'] is False and record['pcmModified'] is False
    for entry,record,chunk in zip(timing['entries'],paragraphs,evidence['sceneWavs']):
        assert record['task']['sceneId']==entry['scene_id'] and record['task']['expected']==entry['text']
        assert record['task']['audioSHA256']==chunk['sha256'] and record['task']['offsetSeconds']==entry['start']
    return output,evidence,timing,job,review,paragraphs,[path,review_path,*[path.parent/(t['key']+'.json') for t in job['identity']['tasks']]]


def prepare(asr_job,mix=None):
    _,evidence,timing,job,review,paragraphs,asr_paths=load_exact(asr_job)
    paths=dict(narration=PROJECT/'narration-voice-v1.json',editorial=PROJECT/'narration-editorial-v1.json',draft=PROJECT/'narration-draft.json',editPlan=PROJECT/'edit-plan-v1.json',layout=PROJECT/'visual-layout-v1.json',sources=PROJECT/'source-footage.json')
    docs={k:read(p) for k,p in paths.items()};n=docs['editorial'];plan=docs['editPlan'];layout=docs['layout']
    assert [e['text'] for e in timing['entries']]==n['narrationKo']==docs['draft']['narrationKo']
    assert [' '.join(s['lines']) for s in docs['narration']['scenes']]==n['narrationKo']
    assert layout['caption']['fontPx']==48 and layout['caption']['maxLines']==2 and layout['caption']['textMaxWidthPx']==800
    normal,bold,font_paths=fonts();cues,beats,paragraph_frames,alignment=caption_and_beat_frames(n,plan,timing,paragraphs,normal,bold)
    for cue in cues:
        cache_path=Path(job['output'])/('paragraph-s'+str(cue['paragraph']).zfill(2)+'.json')
        cue['literalDisplayAlignment'].update(asrCachePath=str(cache_path),asrCacheSHA256=asr.voice.sha(cache_path))
    selected={s['id']:s for s in docs['sources']['sources'] if s['id'] in [A,B]}
    for source in selected.values():
        assert source['rightsReviewed'] and source['width']>=1920 and source['height']>=1080
        assert source['editorialRole']=='independent-gameplay' and asr.voice.sha(source['path'])==source['sha256']
    total=math.ceil(evidence['aggregateWav']['frames']*FPS/evidence['aggregateWav']['sampleRate'])
    beats[-1]['endFrameExclusive']=total;paragraph_frames[-1]['endFrameExclusive']=total
    sections=make_sections(beats,cues,selected,n['glossary'])
    inputs=[pin(role,p) for role,p in paths.items()]
    inputs += [pin('voice-evidence',asr.PROOF),pin('voice-timing',evidence['timing']['path']),pin('voice-aggregate',evidence['aggregateWav']['path']),pin('voice',evidence['aggregateWav']['path']),pin('asr',asr_paths[1]),pin('timeline-helper',__file__)]
    inputs += [pin('blind-asr-evidence',p) for p in asr_paths]+[pin('caption-font',p) for p in font_paths]
    for role,path in [('native-helper',PROJECT/'production/composite-native-frame.py'),
                      ('game-helper',PROJECT/'production/composite-game-frame.py'),
                      ('tracking',PROJECT/'opening-cart-tracking-v2.json'),
                      ('native-evidence',HERE/'first-native-evidence.json'),
                      ('render-helper',HERE/'render-first-film.py')]:
        if not path.is_file():raise Pending('Required current compositor evidence missing: '+str(path))
        inputs.append(pin(role,path))
    voice=copy.deepcopy(evidence['aggregateWav']);audio=dict(voice=voice,mix=None)
    if mix:
        info=mix_info(mix)
        if abs(info['durationSeconds']-voice['durationSeconds'])>1/max(info['sampleRate'],voice['sampleRate']):raise Pending('Final mix duration differs from untouched voice')
        audio['mix']=info;inputs.append(pin('final-audio-mix',mix))
    actual=sum(s['endFrameExclusive']-s['startFrame'] for s in sections if s['kind']=='gameplay')
    result=dict(schemaVersion='03-02-final-timeline-v1',topicId='03.02',status='final-asr-aligned',format=dict(width=1080,height=1920,fps=FPS),
        totalFrames=total,voiceFingerprint=evidence['fingerprint'],asrFingerprint=job['fingerprint'],audio=audio,inputs=inputs,
        paragraphFrames=paragraph_frames,sections=sections,captions=cues,captionStyle=layout['caption'],
        alignmentReview=dict(paragraphs=alignment,boundaryObservations=review['boundaryObservations'],
            literalDiscrepanciesPreserved=True,aliasesApplied=False,canonicalDisplayFromAuthoredText=True,
            newRetakeLiteralDifferences=[dict(paragraph=r['paragraph'],expectedLiteral=r['expectedLiteral'],recognizedLiteral=r['recognizedLiteral'],
                differences=r['comparison']['characterDifferences'],contentAndListeningReviewRequired=True)
                for r in alignment if r['paragraph'] in [2,3] and r['comparison']['characterDifferences']],
            requiredHumanListening=[dict(scene='s05',issue='Gameplay Metrics 메트릭스/매트릭스 ae/e orthography or actual pronunciation must remain a listening question; canonical display is not evidence that speech is correct.')],
            automaticSpeechPass=False,humanListening=False,finalApproval=False),
        sourcePolicy=dict(nativeSpeed=True,loops=False,fixedActualRatioRequired=False,actualFrames=actual,explanationFrames=total-actual,
            sourceTimebase='Local presentation PTS, discarded preroll excluded; native30fps duplicated at60fps, no optical flow.',
            sourceRangeAdjustment='Actual word/phrase-bound timing consumes inspected nonoverlapping windows; no whole-lesson proportional allocation.',
            opening='Root frame review selectedA25.0–26.8333 cart+whole players, thenB40+; annotation visibility still enforced by tracking helper.'),
        productionReadiness=dict(timelineTechnicallyAligned=True,audioMixPresent=audio['mix'] is not None,
            nativeAndEncodedMotionReview=False,mobileReview=False,fullListening=False,humanFinalReview=False,
            pending=['Actual final encoded/motion/mobile/playback and full mix listening','s05 literal ASR discrepancy / pronunciation human listening','P5 jump clip is partial airborne example, not verified maximum reachable range','P6b one-enemy purpose illustration must be visibly implemented rather than only a held scene']))
    # Cat timing is separate from a section's background; never cover a dual view.
    result['catCues']=[]
    for bid,pose in [('P1d','puzzled'),('P4c','relief'),('P6d','realize')]:
        beat=next(b for b in beats if b['id']==bid);end=beat['endFrameExclusive'];start=max(beat['startFrame'],end-90)
        if bid=='P4c':start=beat['startFrame'];end=min(beat['endFrameExclusive'],start+90)
        # Only a single-view/gameplay interval is allowed. Dual native comparison stays clear.
        valid=[s for s in sections if s['startFrame']<=start<end<=s['endFrameExclusive'] and s.get('native',{}).get('layout')!='dual']
        if valid:result['catCues'].append(dict(pose=pose,startFrame=start,endFrameExclusive=end,easeInFrames=7,easeOutFrames=9,clipToLayout=True))
    for section in sections:
        section['catCues']=[dict(cue,startFrame=max(cue['startFrame'],section['startFrame']),endFrameExclusive=min(cue['endFrameExclusive'],section['endFrameExclusive']))
            for cue in result['catCues'] if cue['startFrame']<section['endFrameExclusive'] and cue['endFrameExclusive']>section['startFrame']]
        if section.get('native',{}).get('layout')=='dual':assert not section['catCues']
        if section['beatId']=='P6b':section['illustrationOverlay']=dict(kind='purpose-contrast',heading='목적 비교 그림',routeLabel='좁은 복도',enemyLabel='적 한 마리',resultLabel='목적에 따라 달라짐',
            narrowPurposeLabel='좁은 길 · 긴장',widePurposeLabel='넓은 길 · 호위',narrowActionLabel='한 방향 접근',wideActionLabel='곁에서 이동',pictureLabel='설명용 도식')
    result['fingerprintScope']='all fields except fingerprint and subtitles (subtitle bytes derive from the already-bound caption cues)'
    result['fingerprint']=asr.digest(result)
    return result


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--asr-job',required=True);ap.add_argument('--mix');ap.add_argument('--execute',action='store_true');args=ap.parse_args()
    try:timeline=prepare(args.asr_job,args.mix)
    except (Pending,asr.Pending) as error:
        print(json.dumps(dict(ready=False,reason=str(error),modelLoaded=False,outputWritten=False),ensure_ascii=False));return
    if not args.execute:
        print(json.dumps(dict(ready=True,fingerprint=timeline['fingerprint'],frames=timeline['totalFrames'],sections=len(timeline['sections']),captions=len(timeline['captions']),mixReady=timeline['audio']['mix'] is not None,outputWritten=False),ensure_ascii=False));return
    folder=MEDIA/'shorts-leveldesign-03-02/film-timeline'/timeline['fingerprint'][:24]
    tracks={}
    for language in ['ko','en']:
        path=folder/('narration.'+language+'.srt');data=srt(timeline['captions'],language)
        if path.exists():assert path.read_text(encoding='utf-8')==data,'Preserve different subtitle output'
        else:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(data,encoding='utf-8')
        tracks[language]=dict(path=str(path),sha256=asr.voice.sha(path))
    timeline['subtitles']=tracks;path=folder/'final-timeline.json'
    if path.exists():assert read(path)==timeline,'Preserve different timeline output'
    else:save(path,timeline)
    print(json.dumps(dict(ready=True,timeline=str(path),sha256=asr.voice.sha(path),subtitleFiles=tracks,modelLoaded=False),ensure_ascii=False))


if __name__=='__main__':main()
