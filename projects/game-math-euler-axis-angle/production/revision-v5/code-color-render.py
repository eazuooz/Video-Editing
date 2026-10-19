"""M04 selected visual-only code/working examples; original renderers remain untouched.

CPU/Pillow authored static explanation states, encoded at the measured FHD60
scene frame budget. No speech, captions, gameplay, geometry or timing is edited.
"""
from pathlib import Path
import argparse, hashlib, json, os, re, subprocess, sys
from datetime import datetime, timezone
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[4]
PROJECT = ROOT / 'projects/game-math-euler-axis-angle'
HERE = Path(__file__).resolve().parent
OUT = PROJECT / 'production/local/revision-v5/code-color'
TIMELINE = PROJECT / 'production/revision-v3/timeline.json'
LESSON = PROJECT / 'production/revision-v3/lesson.json'
CAPTIONS = PROJECT / 'production/local/revision-v3/captions.ko.ass'
CONTROL = ROOT / 'shared/publishing/video-production-control.json'
WIDTH, HEIGHT, FPS = 1920, 1080, 60
PALETTE = dict(background='#080A0D', body='#F6F7F9', heading='#FFDE59',
               keyword='#C4B5FD', function='#67E8F9', variable='#9FE6C3',
               literal='#FFC98B', comment='#A7B2BE', rule='#39414C',
               activeFill='#143C32', activeEdge='#72DDA6')
FONTS = {'body': Path('C:/Windows/Fonts/malgun.ttf'),
         'bold': Path('C:/Windows/Fonts/malgunbd.ttf'),
         'code': Path('C:/Windows/Fonts/consola.ttf'),
         'symbol': Path('C:/Windows/Fonts/seguisym.ttf')}
CMAPS = {k:TTFont(str(p)).getBestCmap() for k,p in FONTS.items()}
TOKEN = re.compile(r'//[^\n]*|/\*.*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|\d+(?:\.\d+)?(?:[eE][+-]?\d+)?|[A-Za-z_]\w*|[θΔπω]|\s+|.', re.S)
KEYWORDS = {'double', 'constexpr', 'if', 'return', 'float', 'const', 'bool', 'int'}
VARIABLES = {'angle', 'pi', 'tau', 'w', 'delta', 'value', 'start', 'end', 't', 'e', 'n', 'θ', 'Δ', 'ω'}
FLAGS = (subprocess.CREATE_NO_WINDOW | subprocess.BELOW_NORMAL_PRIORITY_CLASS) if os.name == 'nt' else 0

def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def rel(p): return Path(p).resolve().relative_to(ROOT).as_posix()
def save(p,v): Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def selected():
    if read(CONTROL)['selectedVideo'] != PROJECT.name:raise RuntimeError('Selected video changed; no media stage started.')
    if (ROOT/'shared/output/GPU_HANDOFF.json').exists():raise RuntimeError('Exclusive voice/GPU lease active; defer media jobs.')
@lru_cache(maxsize=100)
def font(size,kind='body'):return ImageFont.truetype(str(FONTS[kind]),size)
def font_runs(s,size,kind):
    runs=[]
    for ch in s:
        role=kind if ord(ch) in CMAPS[kind] else 'symbol'
        assert ord(ch) in CMAPS[role],('Unsupported display glyph',ch,hex(ord(ch)))
        if runs and runs[-1][1]==role:runs[-1]=(runs[-1][0]+ch,role)
        else:runs.append((ch,role))
    return [(part,font(size,role),role) for part,role in runs]
def measure(s,size,kind):return sum(f.getlength(v) for v,f,_ in font_runs(s,size,kind))
def token_spans(s):
    parts=TOKEN.findall(s);assert ''.join(parts)==s
    result=[]
    for i,p in enumerate(parts):
        after=''.join(parts[i+1:]).lstrip()
        kind=('comment' if p.startswith(('//','/*')) else
              'literal' if p[:1] in ('"',"'") or p[:1].isdigit() or p=='π' else
              'keyword' if p in KEYWORDS else
              'function' if re.fullmatch(r'[A-Za-z_]\w*',p) and after.startswith('(') else
              'variable' if p in VARIABLES else 'body')
        result.append((p,kind))
    return result
def contrast(a,b):
    def lum(s):
        rgb=[int(s[k:k+2],16)/255 for k in (1,3,5)]
        rgb=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb]
        return sum(v*w for v,w in zip(rgb,(.2126,.7152,.0722)))
    a,b=sorted((lum(a),lum(b)));return (b+.05)/(a+.05)

class Canvas:
    def __init__(self):
        self.image=Image.new('RGB',(WIDTH,HEIGHT),PALETTE['background'])
        self.draw=ImageDraw.Draw(self.image);self.texts=[]
    def line(self,s,x,y,size=54,kind='body',semantic=False,color=None,center=False,max_width=1720,tag='body'):
        f=font(size,kind)
        while measure(s,size,kind)>max_width:
            size-=1;f=font(size,kind)
        if size<34:raise ValueError(('Readable font size guard',s,size))
        if center:x-=measure(s,size,kind)/2
        baseline=y+f.getmetrics()[0]
        spans=token_spans(s) if semantic else [(s,color or 'body')]
        cursor=x;boxes=[];fallback=[]
        for token,category in spans:
            for part,face,role in font_runs(token,size,kind):
                self.draw.text((cursor,baseline),part,font=face,fill=PALETTE.get(category,category),anchor='ls')
                b=self.draw.textbbox((cursor,baseline),part,font=face,anchor='ls')
                if b[3]>b[1]:boxes.append(b)
                if role!=kind:fallback.append(dict(text=part,font=role))
                cursor+=face.getlength(part)
        box=[min(b[0] for b in boxes),min(b[1] for b in boxes),max(b[2] for b in boxes),max(b[3] for b in boxes)]
        assert 80<=box[0] and box[2]<=1840 and 28<=box[1] and box[3]<=870,(tag,s,box)
        self.texts.append(dict(text=s,font=kind,size=size,box=box,tag=tag,spans=[dict(text=a,role=b) for a,b in spans],glyphFallbacks=fallback))
        return box
    def header(self,title):
        self.line(title,100,42,62,'bold',color='heading',tag='title')
        self.line('게임수학 · 오일러 각과 축–각',100,125,36,color='comment',tag='series')
        self.draw.line((100,188,1820,188),fill=PALETTE['rule'],width=2)
    def beat(self,s):self.line(s,960,807,42,semantic=True,center=True,max_width=1700,tag='beat')
    def formula(self,s,y,size=66):self.line(s,960,y,size,semantic=True,center=True,max_width=1680,tag='formula')

def code_rows(c,code,rows,active,y,size,gap):
    f=font(size,'code')
    while max(f.getlength(code[r]) for r in rows)>1580:
        size-=1;f=font(size,'code')
    # A persistent band names the currently explained source line. It is
    # editorial focus, not a fabricated debugger or execution measurement.
    yy=y+active*gap
    c.draw.rectangle((130,yy-5,1790,yy+size+12),fill=PALETTE['activeFill'],outline=PALETTE['activeEdge'],width=3)
    c.draw.polygon([(100,yy+10),(119,yy+25),(100,yy+40)],fill=PALETTE['heading'])
    for j,row in enumerate(rows):c.line(code[row],150,y+j*gap,size,'code',semantic=True,max_width=1580,tag=f'code-source-line-{row+1}')

def make_state(scene,i):
    c=Canvas();c.header(scene['title']);c.beat(scene['beats'][i])
    if scene['id']=='15':
        for x,label,role in [(110,'형·키워드','keyword'),(420,'함수','function'),(660,'변수','variable'),(900,'값·문자열','literal'),(1260,'주석','comment')]:
            c.line(label,x,211,36,color=role,tag='syntax-legend')
        c.line('▶ 현재 설명 줄',1510,211,36,color='activeEdge',max_width=330,tag='focus-legend')
        rows=[[0,1,2,3,4,5,6],[1,2,3],[4,5,6],[4],[7,8],[]][i]
        if rows:code_rows(c,scene['code'],rows,[0,2,0,0,0,0][i],275 if i==0 else 300,58 if i==0 else 68,70 if i==0 else 90)
        if i==1:
            c.formula('w = remainder(angle, 2π)',610,58);c.formula('입력과 결과의 단위: rad',696,52)
        elif i==2:
            c.formula('−π rad → +π rad',610,62);c.formula('−π < result ≤ π',696,56)
        elif i==3:
            for x,a,b in [(540,'angle = −π rad','참 → w = +π rad'),(1380,'angle = π/2 rad','거짓 → w = π/2 rad')]:
                c.line(a,x,488,54,semantic=True,center=True,max_width=770,tag='trace-input')
                c.line(b,x,590,54,semantic=True,center=True,max_width=770,tag='trace-result')
        elif i==4:
            c.formula('Δ = wrapPi(end − start)',610,58);c.formula('angle(t) = start + t × Δ',700,58)
        elif i==5:
            for s,y in [('입력 · 출력: 라디안(rad)',330),('도와 라디안을 혼용하지 않기',460),('한 축의 wrap ≠ 최단 삼차원 경로',590)]:c.formula(s,y,64)
    else:
        c.line('문제 1' if i<3 else '문제 2',100,235,56,'bold',color='heading',tag='problem')
        if i<3:c.formula('+170°  →  −170°',355,84)
        elif i<5:c.formula('회전벡터 → 축·각',355,72)
        examples=[['start = +170°','end = −170°'],['Δdeg = −340° + 360° = +20°'],['170° + 0.5 × 20° = 180°','wrapPi(−17π/9) = +π/9 rad'],['e = (0, π/2, 0) rad'],['θ = ||e|| = π/2 rad = 90°','n = e/||e|| = (0,1,0)'],['다른 축의 회전 합성: 행렬 곱','벡터의 성분합과 구분']]
        for j,s in enumerate(examples[i]):c.formula(s,(530 if i<5 else 420)+j*105,66)
    # Text rows may share semantic spans, but separate authored rows cannot
    # collide. Background focus bands are intentionally excluded.
    for a_index,a in enumerate(c.texts):
        for b in c.texts[a_index+1:]:
            aa,bb=a['box'],b['box']
            if min(aa[2],bb[2])>max(aa[0],bb[0]) and min(aa[3],bb[3])>max(aa[1],bb[1]):raise ValueError(('Text overlap',a,b))
    return c

def run(cmd,log):
    selected()
    with Path(log).open('w',encoding='utf-8') as f:r=subprocess.run([str(v) for v in cmd],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,creationflags=FLAGS)
    if r.returncode:raise RuntimeError(f'{log}: '+Path(log).read_text(encoding='utf-8',errors='replace')[-2000:])
def probe(p):return read_json_command(['ffprobe','-v','error','-show_streams','-of','json',p])
def read_json_command(cmd):return json.loads(subprocess.check_output([str(v) for v in cmd],creationflags=FLAGS))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--render',action='store_true');args=ap.parse_args()
    selected();OUT.mkdir(parents=True,exist_ok=True)
    timing=read(TIMELINE);lesson=read(LESSON);old=read(PROJECT/'production/revision-v2/lesson.json')
    protected=[TIMELINE,LESSON,CAPTIONS,PROJECT/'production/revision-v3/render-flat.py',PROJECT/'production/revision-v3/math_visuals.py']
    hashes={rel(p):sha(p) for p in protected}
    config=dict(schemaVersion=1,scope='M04 visual-only selected scenes15/25',palette=PALETTE,
                syntaxRoles=dict(keyword='C++ types/control/declarations',function='Callable identifier immediately before (',variable='Named example variables/constants',literal='Numeric and string literals; pi symbol',comment='Source comments only; this approved code has none'),
                activeLine='Persistent current-explanation source-line band, not a measured debugger state',
                contrast={k:{bg:round(contrast(v,PALETTE[bg]),3) for bg in ['background','activeFill']} for k,v in PALETTE.items() if k in ['body','heading','keyword','function','variable','literal','comment']},
                textHierarchy='Black background; yellow headings; white body/operators; restrained semantic terms/values and muted secondary text',
                captions='Clean outputs do not contain captions. Existing canonical global ASS remains untouched; fixed48px at960,970 is used only for QA sample PNGs.',
                fonts={k:dict(path=str(p),sha256=sha(p)) for k,p in FONTS.items()},protectedInputHashes=hashes,
                sourceCodeUnchanged=True,narrationPcmUnchanged=True,timingUnchanged=True,geometryUnchanged=True)
    assert min(v['activeFill'] for v in config['contrast'].values())>=4.5
    save(HERE/'code-color-design.json',config)
    reports=[]
    for sid in ['15','25']:
        s=next(s for s in timing['scenes'] if s['id']==sid);l=next(s for s in lesson['scenes'] if s['id']==sid);prior=next(s for s in old['scenes'] if s['id']==sid)
        assert all(l[k]==prior[k] for k in ['title','ko','en','beats'])
        if sid=='15':assert l['code']==prior['code']
        assert sha(ROOT/s['retainedRender']['file'])==s['retainedRender']['sha256']
        assert sha(ROOT/s['voice'])==s['voiceSha256']
        boundaries=[round(t*FPS) for t in s['lineStarts']]+[s['frames']]
        assert boundaries[0]==0 and all(b>a for a,b in zip(boundaries,boundaries[1:]))
        state_reports=[];inputs=[]
        for i,(a,b) in enumerate(zip(boundaries,boundaries[1:])):
            c=make_state(l,i);p=OUT/f'{sid}-state-{i}.png';c.image.save(p)
            state_reports.append(dict(index=i,startFrame=a,frames=b-a,seconds=(b-a)/FPS,png=rel(p),sha256=sha(p),text=c.texts))
            inputs += ['-loop','1','-framerate','60','-i',str(p)]
        target=OUT/f'{sid}.mp4'
        filters=[f'[{i}:v]trim=end_frame={r["frames"]},setpts=PTS-STARTPTS[v{i}]' for i,r in enumerate(state_reports)]
        filters.append(''.join(f'[v{i}]' for i in range(len(state_reports)))+f'concat=n={len(state_reports)}:v=1:a=0,scale=in_range=auto:out_range=tv:out_color_matrix=bt709,format=yuv420p,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709,setsar=1,settb=expr=1/60,setpts=N[out]')
        cmd=['ffmpeg','-hide_banner','-loglevel','warning','-y','-filter_complex_threads','2',*inputs,'-filter_complex',';'.join(filters),'-map','[out]','-an','-sn','-dn','-frames:v',str(s['frames']),'-c:v','libx264','-threads','4','-preset','fast','-crf','17','-pix_fmt','yuv420p','-r','60','-fps_mode','cfr','-enc_time_base','1:60','-color_range','tv','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-video_track_timescale','60000','-movflags','+faststart',str(target)]
        report=dict(scene=sid,globalStartFrame=s['startFrame'],globalEndFrame=s['endFrame'],frames=s['frames'],seconds=s['seconds'],lineStarts=s['lineStarts'],stateBoundaries=boundaries,states=state_reports,command=cmd,output=rel(target),captionBurned=False,renderer='Pillow11.0 CPU authored semantic text, FFmpeg/libx264',protectedInputHashes=hashes,sourceCodeExact=(l.get('code')==prior.get('code')),sourceNarrationPcmSha256=s['voiceSha256'],retainedPrevious=s['retainedRender'],newMediaJobStarted=args.render)
        if args.render:
            run(cmd,OUT/f'{sid}-render.log');p=probe(target);v=p['streams']
            assert len(v)==1 and v[0]['codec_type']=='video'
            v=v[0];assert (v['width'],v['height'],v['r_frame_rate'],v['avg_frame_rate'],int(v['nb_frames']))==(WIDTH,HEIGHT,'60/1','60/1',s['frames'])
            assert (v['pix_fmt'],v['color_range'],v['color_space'],v['time_base'])==('yuv420p','tv','bt709','1/60000')
            report.update(outputSha256=sha(target),stream=v,frameAdjustment=0)
        save(OUT/f'{sid}.json',report);reports.append(report)
    assert all(sha(ROOT/p)==d for p,d in hashes.items()),'Protected original changed during rendering'
    save(OUT/'render-report.json',dict(createdAt=datetime.now(timezone.utc).isoformat(),scenes=reports,sourceSha256=sha(__file__),designSha256=sha(HERE/'code-color-design.json'),mediaJobsStarted=args.render,wholeFinalMasterReview='pending parent composition and changed-range QA'))
    print(json.dumps([dict(scene=r['scene'],startFrame=r['globalStartFrame'],frames=r['frames'],output=r['output'],sha256=r.get('outputSha256'),captionBurned=False) for r in reports],ensure_ascii=False),flush=True)

if __name__=='__main__':main()
