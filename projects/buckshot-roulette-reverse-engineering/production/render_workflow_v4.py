"""Editable v4 workflow diagrams; ordinary preparation never starts an encode.

Examples (paths are project-relative unless absolute)::
  python production/render_workflow_v4.py --template production/local/workflow-v4/timings.template.json
  python production/render_workflow_v4.py --self-check --preview
  python production/render_workflow_v4.py --timings production/local/workflow-v4/timings.json --preview
  python production/render_workflow_v4.py --timings production/local/workflow-v4/timings.json --render

The three layouts distinguish general options, REA's tool role, and our actual
route. They are explanatory diagrams, never a terminal/UI reenactment. Captions
are added by the master compositor; y >= 892 remains completely clear here.
Full rendering requires measured durations AND every measured local cue offset.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from fractions import Fraction
from functools import lru_cache
import json
import math
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw, ImageFont, ImageOps

from assemble_documentary import PROJECT, ROLE_COLORS, digest, load, now, probe, save, tool, video_stream

W, H, FPS = 1920, 1080, 60
OUT = PROJECT / 'production/local/workflow-v4'
FONT = Path('C:/Windows/Fonts/malgun.ttf')
BOLD = Path('C:/Windows/Fonts/malgunbd.ttf')
COLORS = {k: '#'+v for k,v in ROLE_COLORS.items()}
BG = '#000000'
CAPTION_TOP = 892

SPECS = {
    'workflow-overview': {
        'title':'원작을 이해하고, 새 기본 게임으로',
        'kind':'일반 경로 · 도구 선택지',
        'cues':['source','logic','resources','agent','assets','engine','result'],
        'cueDescriptions':{
            'source':'기존 게임의 실행 파일과 패키지',
            'logic':'REA, 필요한 경우 Ghidra 등으로 규칙 조사',
            'resources':'모델·텍스처·애니메이션 구조 확인',
            'agent':'분석한 규칙을 독립 코드로 구현',
            'assets':'새 모델 제작 도구, 선택적으로 Tripo MCP',
            'engine':'Unity / Unreal / Godot 등 구현 환경 선택',
            'result':'규칙과 시각 요소가 연결된 기본 프로토타입'},
    },
    'rea-role': {
        'title':'REA · Reverse Engineer Anything',
        'kind':'도구의 역할 · 분석 원리도',
        'cues':['agent','toolbox','inspect','evidence','verify'],
        'cueDescriptions':{
            'agent':'AI 에이전트가 필요한 조사를 정함',
            'toolbox':'REA는 에이전트가 호출하는 분석 도구 묶음',
            'inspect':'이번에는 REA CLI로 Godot PCK 조사',
            'evidence':'파일 목록·경로·크기·무결성 근거를 받음',
            'verify':'반환된 근거를 확인하고 다음 분석으로 연결'},
    },
    'actual-route': {
        'title':'이번에 실제로 연결한 제작 경로',
        'kind':'실행 기록에 근거한 요약',
        'cues':['source','rea','script','code','models','engine','result'],
        'cueDescriptions':{
            'source':'직접 플레이한 벅샷 룰렛',
            'rea':'REA CLI로 내장 PCK를 읽음',
            'script':'읽을 수 있는 GDScript에서 규칙 분석',
            'code':'AI 에이전트와 독립 규칙 코드·검사 작성',
            'models':'Blender Python으로 새 모델 제작',
            'engine':'Godot에 동작·모델·애니메이션 연결',
            'result':'NEON CHAMBER 프로토타입 실행'},
    },
}


def resolve(path):
    path=Path(path)
    return path.resolve() if path.is_absolute() else (PROJECT/path).resolve()


def relative(path):
    return str(Path(path).resolve().relative_to(PROJECT.resolve())).replace('\\','/')


@lru_cache(maxsize=40)
def font(size, bold=False):
    if size<48: raise ValueError('Core diagram text must be at least 48px')
    return ImageFont.truetype(str(BOLD if bold else FONT),size)


def ease(x):
    x=max(0.0,min(1.0,x))
    return x*x*(3-2*x)


@dataclass
class Text:
    x:int
    y:int
    value:str
    size:int=48
    role:str='text'
    bold:bool=False


@dataclass
class Node:
    key:str
    rect:tuple[int,int,int,int]
    texts:list[Text]
    cue:str
    thumb:str|None=None
    thumb_rect:tuple[int,int,int,int]|None=None


@dataclass
class Edge:
    key:str
    points:list[tuple[int,int]]
    cue:str
    role:str='focus'


@dataclass
class Layout:
    mode:str
    nodes:list[Node]=field(default_factory=list)
    edges:list[Edge]=field(default_factory=list)
    fixed:list[Text]=field(default_factory=list)


def make_layout(mode):
    if mode not in SPECS: raise ValueError('Unknown layout: '+mode)
    b=Layout(mode)
    b.fixed=[Text(70,40,SPECS[mode]['title'],60,'heading',True),
             Text(70,118,SPECS[mode]['kind'],48,'secondary')]
    if mode=='workflow-overview':
        b.nodes=[
          Node('source',(70,315,390,635),[Text(92,335,'기존 게임',60,'heading',True),Text(92,411,'EXE · PCK',48,'secondary')],'source','original',(92,477,368,632)),
          Node('logic',(470,205,900,425),[Text(494,222,'규칙 분석',56,'text',True),Text(494,293,'REA',60,'focus',True),Text(494,365,'Ghidra · 필요 시',48,'secondary')],'logic'),
          Node('resources',(470,493,900,713),[Text(494,511,'리소스 구조',56,'text',True),Text(494,582,'모델·텍스처',48),Text(494,644,'형태·연결 확인',48,'secondary')],'resources'),
          Node('agent',(990,298,1425,680),[Text(1014,315,'AI 에이전트',56,'text',True),Text(1014,392,'독립 코드 구현',48,'focus'),Text(1014,463,'새 모델 제작',48),Text(1014,544,'Tripo MCP',52,'heading',True),Text(1014,611,'선택 도구',48,'secondary')],'agent'),
          Node('engine',(1495,212,1865,433),[Text(1519,227,'게임 엔진',56,'text',True),Text(1519,298,'Unity / Unreal',48),Text(1519,360,'Godot 등',48,'secondary')],'engine'),
          Node('result',(1515,498,1845,765),[Text(1535,511,'기본 게임',56,'result',True)],'result','prototype',(1535,587,1825,750)),
        ]
        b.edges=[Edge('source-logic',[(390,475),(428,475),(428,315),(470,315)],'logic'),
                 Edge('source-resource',[(390,475),(428,475),(428,603),(470,603)],'resources'),
                 Edge('logic-agent',[(900,315),(945,315),(945,450),(990,450)],'agent'),
                 Edge('resource-agent',[(900,603),(945,603),(945,520),(990,520)],'assets'),
                 Edge('agent-engine',[(1425,450),(1470,450),(1470,308),(1495,308)],'engine'),
                 Edge('engine-result',[(1680,433),(1680,498)],'result','result')]
        b.fixed.append(Text(70,806,'원리와 구조 파악 → 재구현 → 실행 확인',48,'secondary'))
    elif mode=='rea-role':
        b.nodes=[
          Node('agent',(70,246,490,558),[Text(94,270,'AI 에이전트',60,'text',True),Text(94,367,'무엇을 조사할지',48),Text(94,431,'판단하고 요청',48,'focus')],'agent'),
          Node('toolbox',(602,246,1222,558),[Text(628,270,'분석 도구 묶음',60,'text',True),Text(628,362,'REA CLI',64,'focus',True),Text(628,452,'파일·코드·구조 조사',48)],'toolbox'),
          Node('evidence',(1334,246,1844,558),[Text(1358,270,'확인 가능한 근거',56,'text',True),Text(1358,365,'파일 목록·경로',48),Text(1358,429,'크기·무결성',48,'result')],'evidence'),
          Node('actual',(602,644,1844,792),[Text(628,655,'이번 실행: REA CLI → Godot PCK 파일 목록',48,'heading'),Text(628,721,'반환된 결과를 확인하고 GDScript 규칙 분석으로 연결',48)],'inspect'),
        ]
        b.edges=[Edge('request',[(490,402),(602,402)],'toolbox'),
                 Edge('result',[(1222,402),(1334,402)],'evidence','result'),
                 Edge('verify',[(1590,558),(1590,615),(280,615),(280,558)],'verify','result')]
        b.fixed.append(Text(70,815,'REA가 AI 모델인 것은 아닙니다 · 에이전트가 호출하는 도구',48,'secondary'))
    else:
        b.nodes=[
          Node('source',(70,316,400,653),[Text(92,334,'벅샷 룰렛',56,'heading',True),Text(92,410,'직접 플레이',48,'secondary')],'source','original',(92,486,378,647)),
          Node('rea',(490,212,1020,456),[Text(514,230,'REA CLI',60,'focus',True),Text(514,307,'내장 PCK 확인',48),Text(514,378,'GDScript 규칙 분석',48)],'rea'),
          Node('models',(490,552,1020,755),[Text(514,572,'Blender Python',56,'heading',True),Text(514,651,'새 모델 직접 제작',48)],'models'),
          Node('code',(1140,212,1840,456),[Text(1164,230,'AI 에이전트와 독립 구현',56,'text',True),Text(1164,312,'규칙 코드 · 검증 코드',48,'focus'),Text(1164,381,'374 규칙 검사 + 32 통합 검사',48,'result')],'code'),
          Node('engine',(1140,552,1420,755),[Text(1164,572,'Godot',64,'focus',True),Text(1164,655,'동작 연결',48)],'engine'),
          Node('result',(1510,524,1840,787),[Text(1532,538,'프로토타입',52,'result',True)],'result','prototype',(1532,610,1818,771)),
        ]
        b.edges=[Edge('source-rea',[(400,475),(444,475),(444,334),(490,334)],'rea'),
                 Edge('script-code',[(1020,334),(1140,334)],'code'),
                 Edge('code-engine',[(1280,456),(1280,552)],'engine'),
                 Edge('models-engine',[(1020,653),(1140,653)],'engine'),
                 Edge('engine-result',[(1420,653),(1510,653)],'result','result')]
        b.fixed.append(Text(70,815,'핵심 규칙을 확인하고 새 그래픽으로 연결한 기본 프로토타입',48,'secondary'))
    return b


def text_bounds(t):
    f=font(t.size,t.bold)
    return [t.x,t.y,t.x+f.getlength(t.value),t.y+math.ceil(t.size*1.25)]


def validate(layout):
    rows=[]
    for node in layout.nodes:
        x0,y0,x1,y1=node.rect
        if not(40<=x0<x1<=1880 and 180<=y0<y1<=876):raise ValueError('Unsafe node '+node.key)
        for t in node.texts:
            bound=text_bounds(t)
            if bound[0]<x0 or bound[1]<y0 or bound[2]>x1 or bound[3]>y1:
                raise ValueError(f'Text does not fit {layout.mode}/{node.key}: {t.value}: {bound} vs {node.rect}')
            rows.append({'text':t.value,'fontPx':t.size,'bounds':bound,'node':node.key})
        if node.thumb_rect:
            a,b,c,d=node.thumb_rect
            if not(x0<=a<c<=x1 and y0<=b<d<=y1):raise ValueError('Unsafe thumbnail')
    for t in layout.fixed:
        bound=text_bounds(t)
        if bound[0]<40 or bound[1]<26 or bound[2]>1880 or bound[3]>876:raise ValueError('Unsafe fixed text '+t.value)
        rows.append({'text':t.value,'fontPx':t.size,'bounds':bound,'node':'fixed'})
    for edge in layout.edges:
        if any(not(40<=x<=1880 and 180<=y<=876) for x,y in edge.points):raise ValueError('Unsafe arrow')
    return rows


def trim_path(points,fraction):
    lengths=[math.dist(a,b) for a,b in zip(points,points[1:])]
    target=sum(lengths)*max(0,min(1,fraction));done=0.0;out=[points[0]]
    for a,b,n in zip(points,points[1:],lengths):
        if target>=done+n:out.append(b);done+=n;continue
        f=(target-done)/n if n else 0
        out.append((a[0]+(b[0]-a[0])*f,a[1]+(b[1]-a[1])*f));break
    return out


def draw_arrow(draw,points,fill,width,progress=1):
    p=trim_path(points,progress)
    if len(p)<2 or math.dist(p[-1],p[-2])<2:return
    draw.line(p,fill=fill,width=width,joint='curve')
    a,b=p[-2:];ang=math.atan2(b[1]-a[1],b[0]-a[0]);back=(b[0]-17*math.cos(ang),b[1]-17*math.sin(ang))
    side=(11*math.sin(ang),-11*math.cos(ang))
    draw.line([(back[0]+side[0],back[1]+side[1]),b,(back[0]-side[0],back[1]-side[1])],fill=fill,width=width,joint='curve')


class Renderer:
    def __init__(self,layout,entry):
        self.layout,self.entry=layout,entry
        self.cues=entry['cueTimes']; self.duration=entry['durationSeconds']
        self.layers={};self.thumb_evidence=[]
        thumbnails=entry.get('thumbnails',{})
        for node in layout.nodes:
            x0,y0,x1,y1=node.rect
            layer=Image.new('RGBA',(W,H));d=ImageDraw.Draw(layer)
            for text in node.texts:d.text((text.x,text.y),text.value,font=font(text.size,text.bold),fill=COLORS[text.role],anchor='lt')
            if node.thumb and node.thumb in thumbnails:
                record=thumbnails[node.thumb];path=resolve(record['path'])
                if not record.get('reviewEvidence'):raise ValueError('Thumbnail requires an actual review evidence path')
                if digest(path)!=record['sha256']:raise ValueError('Thumbnail hash differs')
                if not resolve(record['reviewEvidence']).is_file():raise ValueError('Thumbnail review evidence missing')
                picture=Image.open(path).convert('RGB')
                if record.get('crop'):picture=picture.crop(tuple(record['crop']))
                a,b,c,destination_bottom=node.thumb_rect
                fitted=ImageOps.contain(picture,(c-a,destination_bottom-b),Image.Resampling.LANCZOS)
                layer.paste(fitted,(a+(c-a-fitted.width)//2,b+(destination_bottom-b-fitted.height)//2))
                self.thumb_evidence.append({'slot':node.thumb,**record,'sourceKind':'previously reviewed still thumbnail; diagram illustration'})
            elif node.thumb:
                a,b,c,destination_bottom=node.thumb_rect
                d.rectangle((a,b,c,destination_bottom),outline=COLORS['secondary'],width=3)
                # A diagram symbol is used instead of an invented game screenshot.
                cx=(a+c)//2;cy=(b+destination_bottom)//2
                d.rectangle((cx-60,cy-40,cx+60,cy+40),outline=COLORS['secondary'],width=5)
                d.line((cx,cy+40,cx,cy+65),fill=COLORS['secondary'],width=5)
            # Cache only each node's occupied area, keeping the CPU pipe small.
            self.layers[node.key]=layer.crop(node.rect)

    def cue_progress(self,key,t):
        return ease((t-self.cues[key])/.42)

    def frame(self,t):
        canvas=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(canvas)
        for text in self.layout.fixed:d.text((text.x,text.y),text.value,font=font(text.size,text.bold),fill=COLORS[text.role],anchor='lt')
        ordered=sorted(self.cues.items(),key=lambda p:p[1])
        current=next((key for key,value in reversed(ordered) if value<=t),ordered[0][0])
        # Edges reveal with speech while retaining their paths for continuity.
        for edge in self.layout.edges:
            draw_arrow(d,edge.points,'#505858',3)
            p=self.cue_progress(edge.cue,t)
            if p:draw_arrow(d,edge.points,COLORS[edge.role],6,p)
        for node in self.layout.nodes:
            p=self.cue_progress(node.cue,t)
            active=current==node.cue or (self.layout.mode=='actual-route' and current=='script' and node.key=='rea') or (self.layout.mode=='workflow-overview' and current=='assets' and node.key=='agent') or (self.layout.mode=='rea-role' and current=='inspect' and node.key=='toolbox')
            # Even unreached gray labels retain >4.5:1 contrast on black.
            opacity=.72+.28*p
            layer=self.layers[node.key]
            canvas.paste(layer,node.rect[:2],layer.getchannel('A').point(lambda v:round(v*opacity)))
            d=ImageDraw.Draw(canvas)
            d.rectangle(node.rect,outline=COLORS['heading' if active else 'focus'] if p else '#505858',width=7 if active else 3)
        if self.layout.mode=='workflow-overview' and current=='assets':
            d.rectangle((60,795,1860,876),fill=BG)
            d.text((70,806),'MCP: AI 에이전트와 도구를 잇는 연결 규약',font=font(48),fill=COLORS['secondary'],anchor='lt')
        return canvas


def check_evidence(mode):
    files=[PROJECT/'planning/tool-audit.md',PROJECT/'planning/package-inventory.json']
    if mode=='actual-route':
        files += [PROJECT/'planning/mechanics-findings.json',PROJECT/'prototype/scripts/rules.gd',
                  PROJECT/'production/create_original_assets.py',PROJECT/'prototype/scripts/stage.gd',
                  PROJECT/'production/local/test-evidence/prototype-demo-fhd-capture.json',
                  PROJECT/'production/local/test-evidence/rules-test-report.json',PROJECT/'production/local/test-evidence/integration-test-report.json']
        a,b=load(files[-2]),load(files[-1])
        if not a['passed'] or a['checks']!=374 or a['failures'] or not b['passed'] or b['check_count']!=32 or b['failures']:
            raise ValueError('Displayed test evidence changed')
    return [{'path':relative(p),'sha256':digest(p)} for p in files]


def prepare(entry,out,synthetic=False):
    entry=dict(entry);mode=entry['mode'];spec=SPECS[mode]
    # Use directly reviewed source frames, never placeholder game imagery. These
    # remain still thumbnails inside an analytical diagram, not gameplay footage.
    thumb_review=OUT/'thumbnail-review.json'
    if thumb_review.is_file():
        known={Path(r['file']).name:r for r in load(thumb_review).get('rows',[])}
        thumbnails=dict(entry.get('thumbnails',{}))
        for slot in ['original','prototype']:
            name=slot+'-still.png';path=OUT/name;row=known.get(name)
            if slot not in thumbnails and row and path.is_file():
                if digest(path)!=row['sha256'] or not row.get('review'):
                    raise ValueError('Reviewed thumbnail changed: '+slot)
                thumbnails[slot]={'path':relative(path),'sha256':row['sha256'],
                                  'reviewEvidence':relative(thumb_review)}
        entry['thumbnails']=thumbnails
    duration=float(entry['durationSeconds'])
    if duration<=0:raise ValueError('A positive duration is required')
    frames=round(duration*FPS)
    if frames<1:raise ValueError('No complete frame')
    entry['durationSeconds']=frames/FPS
    values=dict(entry.get('cueTimes',{}));estimated=[]
    if any(k not in spec['cues'] for k in values):raise ValueError('Unexpected cue key')
    for i,key in enumerate(spec['cues']):
        if key not in values:
            values[key]=duration*i/len(spec['cues']);estimated.append(key)
        values[key]=round(float(values[key])*FPS)/FPS
        if not 0<=values[key]<entry['durationSeconds']:raise ValueError('Cue outside clip '+key)
    # A tool-definition paragraph can discuss REA before its AI caller. Highlight
    # the actual spoken order; graph topology does not dictate narration order.
    entry['cueTimes']=values
    layout=make_layout(mode);text_layout=validate(layout)
    receipt={'schemaVersion':1,'preparedAtUtc':now(),'id':entry['id'],'mode':mode,
      'assetKind':'analysis-visualization','actualFootage':False,'realToolUiCapture':False,
      'title':spec['title'],'sourceKindLabel':spec['kind'],'width':W,'height':H,'fps':FPS,'frames':frames,
      'durationSeconds':entry['durationSeconds'],'speechEndSeconds':entry.get('speechEndSeconds'),
      'timingVerified':bool(entry.get('timingVerified')) and not synthetic,
      'cueTimes':values,'cueEvidence':entry.get('cueEvidence',{}),'estimatedCues':estimated,
      'syntheticLayoutTest':synthetic,'captionAreaReserved':[0,892,1920,1060],
      'minimumTextPx':48,'textLayout':text_layout,'evidence':check_evidence(mode),
      'rendererSha256':digest(Path(__file__)),'rendered':False,'motionReviewed':False,
      'executionScope':'General optional tool pipeline' if mode=='workflow-overview' else 'REA tool role, not an AI model' if mode=='rea-role' else 'Only recorded actual REA CLI, readable script analysis, independently authored code, Blender Python and Godot route',
      'limitations':['A semantic illustration, not a replay of actual tool UI.','Static preview is not encoded motion or final caption QA.','Optional Ghidra/Tripo/engine choices are never marked as performed in this project.']}
    folder=out/entry['id'];folder.mkdir(parents=True,exist_ok=True)
    renderer=Renderer(layout,entry);receipt['thumbnails']=renderer.thumb_evidence
    save(folder/'entry.resolved.json',entry);save(folder/'receipt.json',receipt)
    return renderer,receipt,folder


def previews(renderer,receipt,folder):
    records=[]
    for key,t in receipt['cueTimes'].items():
        t=min(receipt['durationSeconds']-1/FPS,t+.6)
        p=folder/(key+'.png');mobile=folder/(key+'.mobile.png')
        frame=renderer.frame(t);frame.save(p);frame.resize((375,211),Image.Resampling.LANCZOS).save(mobile)
        records.append({'cue':key,'seconds':t,'path':relative(p),'sha256':digest(p),'mobilePath':relative(mobile),'mobileSha256':digest(mobile),'directVisualReview':False})
    receipt['previews']=records;save(folder/'receipt.json',receipt)


def render(renderer,receipt,folder,plan):
    if not receipt['timingVerified'] or receipt['syntheticLayoutTest'] or receipt['estimatedCues']:
        raise ValueError('Full encode requires measured duration and all measured cue times')
    if not all(receipt['cueEvidence'].get(key,{}).get('method') for key in receipt['cueTimes']):
        raise ValueError('Each supplied word cue needs evidence/method; no implied listening')
    mp4=folder/(receipt['id']+'.mp4')
    if mp4.exists() and not plan.get('overwrite'):raise FileExistsError(mp4)
    args=[tool('ffmpeg',plan),'-hide_banner','-v','warning','-nostdin','-y','-f','rawvideo',
          '-pix_fmt','rgb24','-s:v',f'{W}x{H}','-r',str(FPS),'-i','pipe:0','-an',
          '-c:v','libx264','-threads','2','-preset','veryfast','-crf','18',
          '-pix_fmt','yuv420p','-movflags','+faststart','-frames:v',str(receipt['frames']),str(mp4)]
    with (folder/'render.log').open('w',encoding='utf-8') as log:
        process=subprocess.Popen(args,stdin=subprocess.PIPE,stdout=log,stderr=log)
        try:
            for frame in range(receipt['frames']):process.stdin.write(renderer.frame(frame/FPS).tobytes())
            process.stdin.close();returncode=process.wait()
        except BaseException:
            if process.stdin:process.stdin.close()
            process.wait();raise
    if returncode:raise RuntimeError('FFmpeg failed; see render.log')
    metadata=probe(mp4,plan);stream=video_stream(metadata)
    if stream['width']!=W or stream['height']!=H or Fraction(stream['avg_frame_rate'])!=FPS or int(stream['nb_frames'])!=receipt['frames']:
        raise ValueError('Encoded output differs from frame-exact FHD60 contract')
    save(folder/'ffprobe.json',metadata)
    receipt.update({'rendered':True,'renderedAtUtc':now(),'path':relative(mp4),'sha256':digest(mp4),'command':args})
    save(folder/'receipt.json',receipt)


def template():
    return {'schemaVersion':1,'kind':'measured-workflow-v4-timings','instructions':[
      'id is free, mode is workflow-overview / rea-role / actual-route; reuse a mode with different timings.',
      'durationSeconds includes only existing breathing up to the next paragraph boundary. speechEndSeconds remains actual voice end.',
      'cueTimes are clip-local seconds obtained from actual word/phrase alignment. cueEvidence records method and source.',
      'thumbnails are optional reviewed stills: {original|prototype:{path,sha256,reviewEvidence,crop?}}.',
      'Default operation prepares only. --preview writes a few stills. --render is an explicit costly operation after authorization.'
    ],'entries':[{'id':mode,'mode':mode,'durationSeconds':None,'speechEndSeconds':None,'timingVerified':False,
                 'cueTimes':{},'cueEvidence':{},'cueDescriptions':spec['cueDescriptions'],'thumbnails':{}}
                for mode,spec in SPECS.items()]}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--template',type=Path);ap.add_argument('--timings',type=Path)
    ap.add_argument('--out',type=Path,default=OUT);ap.add_argument('--only',action='append')
    ap.add_argument('--prepare',action='store_true',help='Explicit alias of the safe default')
    ap.add_argument('--preview',action='store_true');ap.add_argument('--render',action='store_true')
    ap.add_argument('--self-check',action='store_true');ap.add_argument('--overwrite',action='store_true')
    args=ap.parse_args()
    if args.template:save(resolve(args.template),template());return
    if args.self_check and args.render:ap.error('Synthetic preview can never render')
    out=resolve(args.out)
    if not out.is_relative_to((PROJECT/'production/local').resolve()):raise ValueError('Generated files must remain in this project production/local')
    if args.self_check:
        entries=template()['entries']
        for entry in entries:entry['durationSeconds']=24.0
        out=out/'layout-self-check'
    elif args.timings:entries=load(resolve(args.timings))['entries']
    else:ap.error('--timings, --template or --self-check is required')
    receipts=[]
    for entry in entries:
        if args.only and entry['id'] not in args.only:continue
        renderer,receipt,folder=prepare(entry,out,args.self_check)
        if args.preview:previews(renderer,receipt,folder)
        if args.render:render(renderer,receipt,folder,vars(args))
        receipts.append(receipt)
        print(f'{receipt["id"]}: {receipt["mode"]}, {receipt["frames"]} frames, rendered={receipt["rendered"]}')
    save(out/'index.json',{'createdAtUtc':now(),'rendered':args.render,'entries':receipts})


if __name__=='__main__':main()
