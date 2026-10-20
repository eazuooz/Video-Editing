"""Canonical KO/EN names beside the continuing controlled explanation.

The model/diagram defines the term in context; this compact persistent name
does not reset the scene or interrupt speech. All cues use actual word times.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json
from PIL import ImageFont
H=Path(__file__).resolve().parent;R=H.parents[3];P=R/'projects/game-math-euler-axis-angle';O=P/'production/local/revision-v7-part1/terms'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def rel(p):return Path(p).resolve().relative_to(R).as_posix()
def module(name,p):
    sp=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
DEFAULTS={1:'3차원 회전 · 3D Rotation',2:'위치와 자세',3:'오일러 각 · Euler Angles',4:'첫 번째 회전 · 헤딩',5:'두 번째 회전 · 피치',6:'세 번째 회전 · 뱅크',7:'관찰 방향 바꾸기',8:'앞 방향과 비틀림',9:'축 · 부호 · 적용 순서',10:'물체 축과 고정 축',11:'서로 다른 동작 · 같은 끝',12:'기울어진 축과 수직 기준',13:'축을 적용하는 단계',14:'같은 자세를 다른 규약으로',15:'사람이 편집하는 손잡이',16:'각도를 기록하는 값',17:'회전 표현의 유효성',18:'숫자와 마지막 자세',19:'여러 숫자 중 대표 고르기',20:'겹치는 조절 방향',21:'끝 자세와 중간 경로'}
ADDITIONAL=[dict(ko='행벡터',en='Row Vector',firstScene='v7-a14'),dict(ko='회전 행렬',en='Rotation Matrix',firstScene='v7-a14'),dict(ko='쿼터니언',en='Quaternion',firstScene='v7-a17'),dict(ko='정규형',en='Canonical Form',firstScene='v7-a19'),
    dict(ko='오일러 각',en='Euler Angles',firstScene='v7-a01',role='overview mention; detailed definition remainsa03'),
    dict(ko='짐벌 락',en='Gimbal Lock',firstScene='v7-a19',role='first observed phenomenon name; detailed explanation remainsa20')]
def definition_plan():
    glossary=[g for g in read(P/'planning/revision-v7-two-part/production-plan.json')['glossary']if g['introducedInPart']==1]
    source={s['id']:s for s in read(P/'script/revision-v7-two-part/part-01.ko.json')['scenes']};rows=[]
    for term in glossary+ADDITIONAL:
        sid=term['firstScene'];alternatives=[term['ko'],term['ko'].replace('–',' ')]
        if term['ko']=='중복 표현':alternatives+=['중복표현','에일리어싱']
        found=[]
        for number,line in enumerate(source[sid]['lines'],1):
            for phrase in alternatives:
                if phrase in line:found.append((number,line.index(phrase),phrase))
        assert found,('Canonical first-definition phrase must exist in approved narration',term)
        line,offset,phrase=min(found);label=term['ko']+' · '+term['en']
        rows.append(dict(ko=term['ko'],en=term['en'],scene=sid,line=line,sourceKoOffset=offset,literal=phrase,label=label,
            contextMeaning=term.get('displayMeaning'),firstSourceTextSha256=hashlib.sha256(source[sid]['lines'][line-1].encode('utf8')).hexdigest()))
    return rows
def ts(frame):
    value=round(frame*100/60);h,value=divmod(value,360000);m,value=divmod(value,6000);s,cs=divmod(value,100);return f'{h}:{m:02}:{s:02}.{cs:02}'
HEADER='''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Term,Malgun Gothic,44,&H00F5F5F5,&H00F5F5F5,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,4,0,0,0,1
[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
'''
def event(a,b,text,x,size=44,c='F5F5F5'):
    return f'Dialogue: 5,{ts(a)},{ts(b)},Term,,0,0,0,,{{\\an4\\pos({x},145)\\fs{size}\\1c&H{c}&}}{text}\n'
def build(plan_only=False):
    terms=definition_plan();font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',44)
    for text in list(DEFAULTS.values())+[t['label']for t in terms]:assert font.getlength(text)<=792,(text,font.getlength(text))
    if plan_only:print(json.dumps(dict(canonicalTerms=len({t['ko']for t in terms}),spokenNameCues=len(terms),maximumLabelPixels=max(font.getlength(t['label'])for t in terms),bodyTextUnchanged=True)));return
    T=module('v7_current_terms_clock',H/'timing.py');T.authorized();clock=T.Clock();O.mkdir(parents=True,exist_ok=True);scenes={}
    for scene in clock.timeline['scenes']:
        sid=scene['id'];events={0:DEFAULTS[int(sid[4:6])]};bindings=[]
        for term in terms:
            if term['scene']!=sid:continue
            frame=clock.frame(sid,term['line'],term['sourceKoOffset'])-scene['startFrame'];events[frame]=term['label'];bindings.append(dict(term,cueFrame=scene['startFrame']+frame))
        points=sorted(events);body=HEADER+event(0,scene['frames'],'모형',990,40)
        body+=event(0,scene['frames'],'|',1070,40,'83CFE8')
        for i,at in enumerate(points):
            end=points[i+1]if i+1<len(points)else scene['frames']
            if end>at:body+=event(at,end,events[at],1088)
        dest=O/(sid+'.ass');dest.write_text(body,encoding='utf8');scenes[sid]=dict(file=rel(dest),sha256=sha(dest),bindings=bindings)
    save(H/'semantic-term-chips.json',dict(schemaVersion=1,part=1,fontSize=44,kindLabelSize=40,
        source='Approved lesson glossary; first-definition passage; exact source word clocks',
        inputs=dict(timelineSha256=sha(H/'timeline.json'),scriptSha256=sha(P/'script/revision-v7-two-part/part-01.ko.json'),implementationSha256=sha(Path(__file__))),
        sceneASS=scenes,canonicalTermCount=len({t['ko']for t in terms}),spokenNameCueCount=len(terms),modelRegionUncovered=True,sourceCreatorFraming=False,
        viewReview='pending actual1080/375 encoded pixels',allApprovedSpokenWordsUnchanged=True))
    print('Canonical term chips linked to actual spoken words:',len(terms),flush=True)
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--plan-only',action='store_true');args=a.parse_args();build(args.plan_only)
