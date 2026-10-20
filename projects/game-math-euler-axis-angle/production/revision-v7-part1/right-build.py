"""Build finite900x660 right-pane assets after native capture handoff.

--preview writes only three CPU layout stills from existing approved media.
--build needs the new actual capture receipt. It reframes each finite motion
once, attaches large semantic UI to verified native anchors and makes compact
progressive2D boards. Full lesson timing/left pane/captions belong to the root.
No source loop, voice generation, GPU model, platform action or forced silence.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,math,shutil,subprocess
import psutil
from PIL import Image,ImageDraw,ImageFont

sp=importlib.util.spec_from_file_location('right_prepare',Path(__file__).with_name('right-prepare.py'))
M=importlib.util.module_from_spec(sp);sp.loader.exec_module(M)
S=M.S;ROOT,P,H,O,V6=M.ROOT,M.P,M.H,M.O,M.V6
BG='#080b0d';WHITE='#f5f5f5';GOLD='#e8cf83';TEAL='#73c7c2';MUTED='#b8b8b8'
COLORS={'X':'#ef5a63','Y':'#6cce8e','Z':'#73acf5'}
FONT='C:/Windows/Fonts/malgun.ttf';BOLD='C:/Windows/Fonts/malgunbd.ttf'
W,HT=900,660
ACTIVE_JOB=None

def read(p):return M.read(p)
def sha(p):return M.sha(p)
def rel(p):return M.rel(p)
def save(p,d):M.save(p,d)
def safe(s):return str(s).replace('−','-').replace('‖','||').replace('ᵤ','_u').replace('ₒ','_o')
def color(c):return '&H'+c[5:7]+c[3:5]+c[1:3]+'&'
def ass_text(s):return safe(s).replace('\\','\\\\').replace('{','').replace('}','').replace('\n',r'\N')
def ts(f):
    v=round(f*100/60);h,v=divmod(v,360000);m,v=divmod(v,6000);s,c=divmod(v,100);return f'{h}:{m:02}:{s:02}.{c:02}'
def ass_header():
    return ('[Script Info]\nScriptType: v4.00+\nPlayResX:900\nPlayResY:660\nScaledBorderAndShadow:yes\n'
        '[V4+ Styles]\nFormat: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding\n'
        'Style: Main,Malgun Gothic,64,&H00F5F5F5,&H00F5F5F5,&H000D0B08,&H000D0B08,0,0,0,0,100,100,0,0,1,3,0,5,0,0,0,1\n'
        '[Events]\nFormat: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text\n')
def event(a,b,text,x,y,size=64,c=WHITE,layer=2):
    return f'Dialogue: {layer},{ts(a)},{ts(b)},Main,,0,0,0,,{{\\an5\\pos({x:.1f},{y:.1f})\\fs{size}\\1c{color(c)}}}{ass_text(text)}\n'
def fmt(x):
    if abs(x)<.005:x=0
    return f'{x:.1f}'.rstrip('0').rstrip('.')
def triple(v):return ' / '.join(fmt(v[k])+'°'for k in ['x','y','z'])

def states(path):return [json.loads(l)for l in Path(path).read_text(encoding='utf8').splitlines()if l.strip()]
def roi(rows,shot):
    points=[]
    for row in rows:
        aa={a['name']:a['pixelTopLeft']for a in row['anchors']}
        geometry=[p for key,p in aa.items()if '.geometryCorner'in key]
        if shot.get('model')in['sail','log','hook']and geometry:
            points.extend((p['x'],p['y'])for p in geometry)
            continue
        for prefix in ['a','b']if shot.get('pair')else['a']:
            origin=aa[prefix+'.origin'];points.append((origin['x'],origin['y']))
            for key,p in aa.items():
                if not key.startswith(prefix+'.'):continue
                points.append((p['x'],p['y']))
                # Opposite X/Z bounds preserve wing/tail silhouettes. Gimbals
                # and vertically extended custom objects need both Y ends too.
                if key.endswith(('X','Z'))or shot.get('gimbals')or shot.get('model')in['sail','log','hook']:
                    points.append((2*origin['x']-p['x'],2*origin['y']-p['y']))
    x0=max(0,math.floor(min(x for x,y in points)-42));x1=min(1920,math.ceil(max(x for x,y in points)+42))
    y0=max(0,math.floor(min(y for x,y in points)-42));y1=min(1080,math.ceil(max(y for x,y in points)+42))
    # Even dimensions make subsequent yuv420 output deterministic.
    x0=x0//2*2;y0=y0//2*2;x1=min(1920,(x1+1)//2*2);y1=min(1080,(y1+1)//2*2)
    return [x0,y0,x1-x0,y1-y0]
def placement(crop,pair):
    x,y,w,h=crop;area=[10,140 if pair else 82,880,340 if pair else 454]
    scale=min(area[2]/w,area[3]/h);dw=int(w*scale)//2*2;dh=int(h*scale)//2*2
    return {'crop':crop,'size':[dw,dh],'position':[int((900-dw)/2),int(area[1]+(area[3]-dh)/2)],'scale':[dw/w,dh/h]}
def point(p,layout):
    x,y,_,_=layout['crop'];sx,sy=layout['scale'];ox,oy=layout['position'];return((p['x']-x)*sx+ox,(p['y']-y)*sy+oy)
def title_for(key):
    if key=='v7-sail-move':return '중심만 옮기기'
    if key=='v7-sail-raise':return '위치는 고정 · 자세만 바꾸기'
    if key=='v7-log-align':return '옮기는 일과 맞추는 일'
    if key=='v7-hook-rotate':return '열린 쪽의 방향 바꾸기'
    names={2:'물체 축과 직립 축',3:'왼손 양의 회전',4:'첫 번째 · 헤딩',5:'두 번째 · 피치',6:'세 번째 · 뱅크',7:'관찰 방향을 바꾸기',8:'앞 방향과 비틀림',10:'움직이는 축과 고정 축',11:'서로 다른 동작 · 같은 끝',12:'물체 Y와 직립 Y',13:'어느 단계의 축인가',15:'현재 숫자와 현재 자세',18:'숫자와 마지막 자세',20:'짐벌 락 · 모형에서 검증'}
    return names.get(int(key[3:5]),'우리의 통제된 회전 모형')

def program_numbers(row,shot,prefix):
    cap=prefix.upper();program=shot[prefix]
    if row['hasEulerParameters'+cap]:return triple(row['eulerDegrees'+cap])
    steps=program.get('steps',[])
    return ' → '.join(('X'if abs(st['axis']['x'])>.5 else'Y'if abs(st['axis']['y'])>.5 else'Z')+fmt(st['degrees'])+'°'for st in steps)if steps else'해설 모형의 통제 조건'

def numbers(row,shot):
    if shot.get('model')=='sail':return ['자세 유지 · 위치 이동']if shot['id'].endswith('move')else['중심 고정 · 돛 세우기']
    if shot.get('model')=='hook':return ['위치가 아닌 열린 쪽의 방향']
    if shot.get('model')=='log':return ['이동 → 긴 방향 맞추기']
    if shot.get('pair'):return ['A  '+program_numbers(row,shot,'a'),'B  '+program_numbers(row,shot,'b')]
    return [('h / p / b   'if row['hasEulerParametersA']else'순서   ')+program_numbers(row,shot,'a')]

def pair_names(shot):
    if shot['id'].startswith(('v6-18','v6-20')):return ['A · 각도 묶음','B · 각도 묶음']
    def text(prefix):
        p=shot[prefix];spaces={s.get('space')for s in p.get('steps',[])}
        return '물체 축'if spaces=={'body'}else'고정 축'if spaces=={'upright'}else'기준 모형'
    # Euler parameters describe this approved intrinsic Y-X-Z model, while
    # a fixed-axis sequence must be identified separately for the learner.
    return [('A · '+('물체 축'if shot['a'].get('kind')=='euler'else text('a'))),('B · '+text('b'))]

def native_ass(path,key,rows,shot,layout):
    n=len(rows);txt=ass_header()+event(0,n,title_for(key),450,34,54,GOLD)
    if shot.get('pair'):
        an,bn=pair_names(shot);txt+=event(0,n,an,225,103,64,TEAL)+event(0,n,bn,675,103,64,GOLD)
    elif shot.get('axes',True):txt+=event(0,n,'실선 물체 축 · 점선 직립 축',450,91,36,MUTED)
    sn=int(key[3:5])if key.startswith('v6-')else 0
    labels=S.ACTIVE_AXES.get(sn,['a.bodyY','a.bodyZ'])[:3 if key in ['v6-02.B02','v6-02.B03']else 2]
    for i,row in enumerate(rows):
        for j,line in enumerate(numbers(row,shot)):
            txt+=event(i,i+1,line,450,522+j*82 if shot.get('pair')else 604,64,TEAL if j==0 else GOLD)
        if not shot.get('axes',True):continue
        aa={a['name']:a for a in row['anchors']}
        for name in labels:
            if name not in aa:continue
            a=aa[name]
            if not a['inFrame']:continue
            x,y=point(a['pixelTopLeft'],layout);axis=name[-1];prefix='A 'if name.startswith('a.')and shot.get('pair')else'B 'if shot.get('pair')else''
            label=prefix+axis
            # Clamped text is linked to its real projected anchor; it is not a
            # fabricated game vector. Labels stay out of title/readout regions.
            yy=max(170 if shot.get('pair')else 135,min(450 if shot.get('pair')else 520,y-32));xx=max(50,min(850,x))
            txt+=event(i,i+1,label,xx,yy,64,COLORS[axis],4)
    path.write_text(txt,encoding='utf8')

def draw_board(title,rows,reveal=1):
    im=Image.new('RGBA',(W,HT),(0,0,0,0));d=ImageDraw.Draw(im)
    # The controlled world is dimmed under the explanation, without a generic
    # rounded web-card border or an unrelated decorative container.
    d.rectangle((0,0,899,659),fill=(8,11,13,220))
    d.text((36,34),safe(title),font=ImageFont.truetype(BOLD,56),fill=GOLD)
    for i,line in enumerate(rows[:reveal]):
        y=150+i*(105 if len(rows)<4 else 100)
        d.text((42,y),safe(line),font=ImageFont.truetype(FONT,64),fill=TEAL if i==0 else WHITE)
    return im

def context_background():
    im=Image.open(V6/'spatial-clips/testbed-still.png').convert('RGB').crop((260,220,1060,760))
    im.thumbnail((860,520),Image.Resampling.LANCZOS)
    out=Image.new('RGB',(900,660),BG);out.paste(im,((900-im.width)//2,80))
    return Image.blend(out,Image.new('RGB',out.size,BG),.40)

def native_state_files(out,key,clip,count,contract):
    indices={0,count-1}
    for w in contract['motionWindows']:
        indices.update(w['nativeMotionFrames']);indices.update([w['stateBeforeFrame'],w['stateAfterFrame']])
    for sid,windows in S.PARAGRAPH_WINDOWS.items():
        sn=int(sid[4:6]);ln=int(sid[-2:])
        if S.SPECS[sn][ln-1][0]==key:
            for w in windows:indices.update(w['sourceFrames'])
    indices=sorted(i for i in indices if 0<=i<count)
    folder=out/(key+'.states');folder.mkdir(exist_ok=True)
    expected=[folder/f'frame-{i:06}.png'for i in indices]
    if not all(p.exists()for p in expected):
        assert not any(folder.glob('selected-*.png')),'Preserve partial selected frames for inspection.'
        selector='+'.join('eq(n'+chr(92)+','+str(i)+')'for i in indices)
        # One sequential decode per finite source; PNGs are real source states,
        # not extra frozen video time or newly invented motion.
        run_logged(['ffmpeg','-hide_banner','-loglevel','error','-nostdin','-threads','2','-filter_threads','1','-i',str(clip),'-vf','select='+selector,'-fps_mode','vfr','-threads','2','-n',str(folder/'selected-%06d.png')],out/(key+'.selected-states.log'))
        selected=sorted(folder.glob('selected-*.png'));assert len(selected)==len(indices)
        for old,dst in zip(selected,expected):old.replace(dst)
    return [{'sourceFrame':i,'file':rel(f),'sha256':sha(f)}for i,f in zip(indices,expected)]

def aligned_confirmation(out,key,last,rows,layout):
    aa={a['name']:a['pixelTopLeft']for a in rows[-1]['anchors']}
    ax,ay=point(aa['a.origin'],layout);bx,by=point(aa['b.origin'],layout)
    source=Image.open(last).convert('RGB');g=Image.new('RGBA',(900,660),(0,0,0,255))
    g.paste(source.crop((0,135,450,485)),(0,135))
    patch=source.crop((450,135,900,485)).convert('RGBA');pix=patch.load()
    for y in range(patch.height):
        for x in range(patch.width):
            r,gg,b,_=pix[x,y];pix[x,y]=(r,gg,b,105 if max(r,gg,b)>45 else 0)
    g.alpha_composite(patch,(round(450+ax-bx),round(135+ay-by)))
    model=g.crop((0,135,450,485)).resize((792,616),Image.Resampling.LANCZOS)
    canvas=Image.new('RGB',(900,660),BG);canvas.paste(model.convert('RGB'),(54,50))
    d=ImageDraw.Draw(canvas);d.rectangle((0,0,900,70),fill=BG);d.rectangle((0,575,900,660),fill=BG)
    d.text((450,15),'A와 B · 같은 중심에 겹치기',font=ImageFont.truetype(BOLD,54),fill=GOLD,anchor='mt')
    d.text((450,588),'서로 다른 경로 · 같은 끝 자세',font=ImageFont.truetype(FONT,54),fill=WHITE,anchor='mt')
    f=out/(key+'.aligned.final.png');canvas.save(f)
    return {'file':rel(f),'sha256':sha(f),'method':'Actual final B projected origin aligned to actual final A origin; alpha105 analytical overlay; same geometry/camera projection, no commercial-game values.',
        'sourceBTranslationPixels':[ax-bx,ay-by],'sourceFrame':len(rows)-1,'noClaimOfIntermediatePathEquivalence':True}

def colored_line(draw,spans,y,font):
    width=sum(draw.textlength(text,font=font)for text,c in spans);assert width<=850
    x=(900-width)/2
    for text,c in spans:
        draw.text((x,y),text,font=font,fill=c,anchor='lm');x+=draw.textlength(text,font=font)

def canonical_comparison_states(out,asset):
    folder=out/'canonical-alias';folder.mkdir(exist_ok=True);states=[];ft=ImageFont.truetype(FONT,64)
    for n in range(3):
        im=Image.open(ROOT/asset['lastFrame']).convert('RGB');d=ImageDraw.Draw(im)
        d.rectangle((0,0,900,135),fill=BG);d.text((450,32),'같은 자세 · 대표 범위 고르기',font=ImageFont.truetype(BOLD,52),fill=GOLD,anchor='mm')
        d.text((225,103),'A · 범위 밖',font=ft,fill=GOLD,anchor='mm');d.text((675,103),'B · 범위 안',font=ft,fill=TEAL,anchor='mm')
        d.rectangle((0,486,900,660),fill=BG)
        ca=TEAL if n==2 else WHITE;cp=GOLD if n<2 else WHITE
        colored_line(d,[('A  (',WHITE),('0°',ca),(', ',WHITE),('135°',cp),(', ',WHITE),('0°',ca),(')',WHITE)],522,ft)
        colored_line(d,[('B  (',WHITE),('180°',ca),(', ',WHITE),('45°',cp),(', ',WHITE),('180°',ca),(')',WHITE)],604,ft)
        if n:
            d.line((864,528,864,584),fill=TEAL if n==2 else GOLD,width=8)
            d.polygon([(849,580),(879,580),(864,599)],fill=TEAL if n==2 else GOLD)
        f=folder/f'comparison-{n:02}.png';im.save(f);states.append({'file':rel(f),'sha256':sha(f),'state':n})
    return {'sourceBeatId':'v6-18.B02','states':states,'meaning':'Exact finalA(0,135,0) andB(180,45,180) remain physically identical. Only representative-angle focus changes; no false intermediate angle interpolation or game-internal claim.',
        'targetParagraph':'v7-a19.L03','cues':['피치를 정한 범위 안으로','헤딩과 뱅크도 함께']}

def previews():
    plan=read(M.PLAN);lookup={r['sourceBeatId']:r for r in plan['nativeSourceAssets']};cat={s['id']:s for s in read(S.ENGINE/'spatial-shots.json')['shots']}
    out=O/'preview';out.mkdir(parents=True,exist_ok=True);reports=[]
    cases=[('heading','v7-a04','v6-04.B01','flight-294'),('pair','v7-a11','v6-11.B02','sail-upright'),('range','v7-a19','board-ranges','sail-upright')]
    left=read(H/'game-inputs.json');leftplan=read(P/'planning/revision-v7-two-part/part-01-left-game-plan.json')
    script=read(S.SCRIPT);scene={s['id']:s for s in script['scenes']}
    for name,sid,key,fallback in cases:
        panel=Image.new('RGB',(900,660),BG);caption=scene[sid]['lines'][0]
        if key.startswith('board-'):
            # Existing neutral aircraft contains no baked axis labels.
            im=Image.open(V6/'spatial-clips/testbed-still.png').convert('RGB');im=im.crop((260,220,1060,760));im.thumbnail((860,520));panel.paste(im,((900-im.width)//2,80));panel=Image.blend(panel,Image.new('RGB',panel.size,BG),.65)
            title,lines=S.BOARDS[key[6:]];panel=Image.alpha_composite(panel.convert('RGBA'),draw_board(title,lines,len(lines))).convert('RGB')
            layout=None;native=None
        else:
            src=lookup[key];rows=states(ROOT/src['anchors']);shot=cat[key];layout=placement(roi(rows,shot),shot.get('pair'))
            native=ROOT/src['lastFrame'];im=Image.open(native).convert('RGB');x,y,w,h=layout['crop'];im=im.crop((x,y,x+w,y+h)).resize(layout['size'],Image.Resampling.LANCZOS);panel.paste(im,layout['position']);d=ImageDraw.Draw(panel)
            d.text((26,10),title_for(key),font=ImageFont.truetype(BOLD,54),fill=GOLD)
            for i,line in enumerate(numbers(rows[-1],shot)):d.text((26,500+i*77 if shot.get('pair')else 584),safe(line),font=ImageFont.truetype(FONT,64),fill=TEAL if i==0 else GOLD)
            # Source preview intentionally retains old labels. The final new
            # source omits them in3D instead of painting across the silhouette.
            if shot.get('pair'):
                an,bn=pair_names(shot)
                for label,xx in [(an,225),(bn,675)]:d.text((xx,80),label,font=ImageFont.truetype(FONT,64),fill=TEAL if xx==225 else GOLD,anchor='mt')
            else:
                d.text((450,76),'활성 축 · Y',font=ImageFont.truetype(FONT,52),fill=COLORS['Y'],anchor='mt')
        chosen=next(x for x in leftplan['scenes']if x['targetScene']==sid)['paragraphs'][0]
        stillId=chosen.get('analysisStillIds',[fallback])[0]
        item=left['stills'].get(stillId)or left['stills'][fallback]
        frame=Image.new('RGB',(1920,1080),'black');g=Image.open(ROOT/item['file']).convert('RGB').resize((896,504),Image.Resampling.LANCZOS);frame.paste(g,(40,250));frame.paste(panel,(980,180))
        d=ImageDraw.Draw(frame);d.text((40,58),scene[sid]['title'],font=ImageFont.truetype(BOLD,58),fill=GOLD);d.text((40,178),'실제 게임 · 분석 프레임',font=ImageFont.truetype(FONT,48),fill=WHITE);d.text((990,122),'우리 모형 · 해설용',font=ImageFont.truetype(FONT,44),fill=WHITE)
        # A real approved-script clause, provisional typography only. This is
        # never recorded as timed/encoded final caption evidence.
        clause=caption.split('.')[0]+'.';clause=clause[:34]
        ft=ImageFont.truetype(FONT,48);tw=d.textlength(clause,font=ft);d.rectangle((960-tw/2-22,930,960+tw/2+22,1010),fill='#14231b');d.text((960-tw/2,942),clause,font=ft,fill='white')
        f=out/(name+'.png');frame.save(f);small=out/(name+'.375.png');frame.resize((375,211),Image.Resampling.LANCZOS).save(small)
        reports.append({'name':name,'scene':sid,'sourceBeatId':key,'nativeSource':rel(native)if native else None,'sourceROI':layout,'leftStill':item['file'],
            'native':{'file':rel(f),'sha256':sha(f)},'mobile375':{'file':rel(small),'sha256':sha(small)},'actualTimedCaption':False,
            'limitation':'Old baked small source labels remain only in this pre-capture layout preview; final label-free source/new larger anchor UI not yet rendered. No final motion approval.'})
    save(out/'review.json',{'samples':reports,'gpuStarted':False,'movieRenderStarted':False,'directReview':'pending actual inspection'})
    print(json.dumps({'previewSamples':len(reports),'folder':rel(out)}))

def run_logged(cmd,path):
    with Path(path).open('wb')as log:
        process=subprocess.Popen(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS)
        own=psutil.Process(process.pid);created=own.create_time()
        if ACTIVE_JOB is not None:ACTIVE_JOB['child']={'pid':process.pid,'createTime':created}
        try:code=process.wait()
        except BaseException:
            try:
                if own.is_running()and own.create_time()==created:own.terminate();process.wait(timeout=30)
            except(psutil.NoSuchProcess,subprocess.TimeoutExpired):pass
            raise
    if code:raise RuntimeError(Path(path).read_text(encoding='utf8',errors='replace')[-3000:])

def build():
    M.authorized();receipt=read(O/'spatial-native/capture-receipt.json');assert not receipt['sampleOnly']
    plan=read(M.PLAN);paras=[p for s in plan['scenes']for p in s['paragraphs']];cat={s['id']:s for s in read(O/'prepared-unity/spatial-shots.json')['shots']}
    # Moving then raising the same sail shares one camera-space crop. The
    # exact move endpoint equals the raise start; independently recentering
    # each clip would falsely make that stationary pivot jump at the cut.
    sail_keys=['v7-sail-move','v7-sail-raise']
    native_by_key={n['sourceBeatId']:n for n in receipt['outputs']}
    sail_rows=[r for key in sail_keys for r in states(ROOT/native_by_key[key]['files']['anchors']['file'])]
    sail_layout=placement(roi(sail_rows,cat[sail_keys[0]]),False)
    out=O/'right-assets';out.mkdir(parents=True,exist_ok=True);outputs=[]
    existing={x['sourceBeatId']:x for x in read(O/'right-assets.json').get('assets',[])}if(O/'right-assets.json').exists()else{}
    def record(row):
        outputs.append(row);save(O/'right-assets.json',{'schemaVersion':1,'part':1,'scriptSha256':sha(S.SCRIPT),'planSha256':sha(M.PLAN),'paneDimensions':[900,660],
            'assets':outputs,'paragraphs':paras,'complete':False,'speechTiming':'root ASR cue binding; no forced silence or source loop'})
    for native in receipt['outputs']:
        key=native['sourceBeatId'];file=ROOT/native['files']['clip']['file'];anchor=ROOT/native['files']['anchors']['file'];rows=states(anchor);shot=cat[key];layout=sail_layout if key in sail_keys else placement(roi(rows,shot),shot.get('pair'))
        ass=out/(key+'.ass');native_ass(ass,key,rows,shot,layout);sig={'sourceSha256':native['files']['clip']['sha256'],'anchorsSha256':native['files']['anchors']['sha256'],'layout':layout,'uiSha256':sha(ass),'compositorContract':'crop-scale-pad-ass-r900x660-v1'}
        if key in existing and existing[key].get('inputs')==sig and Path(ROOT/existing[key]['clip']).exists()and sha(ROOT/existing[key]['clip'])==existing[key]['clipSha256']:
            cached=dict(existing[key],targetParagraphs=[p['targetParagraphId']for p in paras if p['sourceBeatId']==key],targetScenes=sorted({p['targetScene']for p in paras if p['sourceBeatId']==key}))
            record(cached);continue
        assert sha(file)==native['files']['clip']['sha256']and sha(anchor)==native['files']['anchors']['sha256']
        dst=out/(key+'.mp4')
        if dst.exists():
            previous=existing.get(key);assert previous and sha(dst)==previous['clipSha256'],'Preserve untracked existing output: '+key
            oldhash=sha(dst)[:16];archive=out/'superseded';archive.mkdir(exist_ok=True);prior=archive/(key+'.'+oldhash+'.mp4');assert not prior.exists(),'Preserve existing same-hash archive for manual inspection.'
            save(archive/(key+'.'+oldhash+'.json'),previous);dst.replace(prior)
            for suffix in ['.states','.first.png','.last.png','.aligned.final.png']:
                old=out/(key+suffix)
                if old.exists():
                    dest=archive/(key+'.'+oldhash+suffix)
                    old.resolve().relative_to(out.resolve());dest.resolve().relative_to(out.resolve())
                    assert not dest.exists();old.replace(dest)
        x,y,w,h=layout['crop'];dw,dh=layout['size'];px,py=layout['position'];vf=f'crop={w}:{h}:{x}:{y},scale={dw}:{dh}:flags=lanczos,pad=900:660:{px}:{py}:color=0x080b0d,ass={rel(ass)}'
        run_logged(['ffmpeg','-hide_banner','-loglevel','warning','-nostdin','-n','-xerror','-err_detect','explode','-threads','2','-filter_threads','1','-i',str(file),'-vf',vf,'-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-r','60','-fps_mode','passthrough',str(dst)],out/(key+'.encode.log'))
        probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,avg_frame_rate,nb_frames','-of','json',str(dst)],text=True))['streams'][0]
        assert [probe['width'],probe['height']]==[900,660]and probe['avg_frame_rate']=='60/1'and int(probe['nb_frames'])==len(rows),(key,probe)
        contract=M.motion_contract(shot,len(rows),rel(anchor))
        statefiles=native_state_files(out,key,dst,len(rows),contract)
        first=out/(key+'.first.png');last=out/(key+'.last.png')
        shutil.copyfile(ROOT/statefiles[0]['file'],first);shutil.copyfile(ROOT/statefiles[-1]['file'],last)
        ghost=aligned_confirmation(out,key,last,rows,layout)if key in ['v6-11.B02','v6-18.B02']else None
        record({**contract,'sourceBeatId':key,'inputs':sig,'targetParagraphs':[p['targetParagraphId']for p in paras if p['sourceBeatId']==key],'targetScenes':sorted({p['targetScene']for p in paras if p['sourceBeatId']==key}),'clip':rel(dst),'clipSha256':sha(dst),'frames':len(rows),'fps':60,'dimensions':[900,660],
            'firstFrame':rel(first),'firstFrameSha256':sha(first),'lastFrame':rel(last),'lastFrameSha256':sha(last),'sourceROI':layout,'uiASS':rel(ass),'uiASSsha256':sha(ass),
            'sourceKind':'authored controlled model and actual source anchors','noGameInternalValueClaim':True,'nativeSpeed':1,'loop':False,'forcedHoldFrames':0,'finalPairedCaptionMotionReview':'pending',
            'internalPairRegions':{'A':[0,135,450,350],'B':[450,135,450,350],'restriction':'Geometry partition only; recompose each numeric readout separately. Verify silhouette clearance in final frames.'}if shot.get('pair')else None,
            'sourceStateBefore':rows[0],'sourceStateAfter':rows[-1],'nativeStateFiles':statefiles,'alignedConfirmation':ghost,'generatorImplementationSha256':sha(Path(__file__)),
            'probe':probe,'nativeSourceFullyDecoded':{'pass':True,'method':'full finite strict-decode crop/scale/ASS encode with-xerror/-err_detect explode and exact output framecount','log':rel(out/(key+'.encode.log'))}})
    # Boards are separate small transparent overlays, composited over the same
    # neutral detailed model by the root. Each reveal is finite and can start
    # on its matching spoken clause; no post-narration waiting is introduced.
    context=context_background();contextfile=out/'context-background.png';context.save(contextfile)
    for key in sorted({p['sourceBeatId']for p in paras if p['sourceBeatId'].startswith('board-')}):
        title,lines=S.BOARDS[key[6:]];folder=out/key;folder.mkdir(exist_ok=True);pngs=[]
        for n in range(0,len(lines)+1):
            f=folder/f'state-{n:02}.png';board=draw_board(title,lines,n);board.save(f)
            full=folder/f'composited-{n:02}.png';Image.alpha_composite(context.convert('RGBA'),board).convert('RGB').save(full)
            pngs.append({'revealCount':n,'file':rel(full),'sha256':sha(full),'transparentOverlay':rel(f),'overlaySha256':sha(f)})
        record({'sourceBeatId':key,'targetParagraphs':[p['targetParagraphId']for p in paras if p['sourceBeatId']==key],'renderer':'code-native semantic2D overlay','states':pngs,
            'stateMeaning':'reveal one relevant line with the spoken clause; root holds current state under continuing speech and can add meaningful value/flow motion. No narration silence is required.',
            'dimensions':[900,660],'title':title,'rows':lines,'background':{'file':rel(contextfile),'sha256':sha(contextfile),'kind':'retained neutral detailed aircraft dimmed behind semantic explanation'},'firstFrame':pngs[0]['file'],'lastFrame':pngs[-1]['file'],'clip':None,
            'frames':None,'forcedHoldFrames':0,'sourceMathMeaningReuse':'same values/logic as oldManim source and approved V7 script, reflowed for halfwidth; never whole-slide scaled'})
    math=read(O/'math-native/outputs.json');assert math['complete']
    requestedMath={p['sourceBeatId']for p in paras if p['sourceBeatId'].startswith('v7-math-')}
    assert requestedMath=={r['sourceBeatId']for r in math['outputs']}
    for native in math['outputs']:
        key=native['sourceBeatId'];file=ROOT/native['files']['clip']['file'];assert sha(file)==native['files']['clip']['sha256']
        sig={'sourceSha256':sha(file),'backgroundSha256':native['background']['sha256'],'compositorContract':'already-halfpane-native-manim-to-rgb-v1'}
        if key in existing and existing[key].get('inputs')==sig and (ROOT/existing[key]['clip']).exists()and sha(ROOT/existing[key]['clip'])==existing[key]['clipSha256']:
            cached=dict(existing[key],targetParagraphs=[p['targetParagraphId']for p in paras if p['sourceBeatId']==key],targetScenes=sorted({p['targetScene']for p in paras if p['sourceBeatId']==key}))
            record(cached);continue
        dst=out/(key+'.mp4');assert not dst.exists(),'Preserve existing nonmatching math panel: '+key
        run_logged(['ffmpeg','-hide_banner','-loglevel','warning','-nostdin','-n','-xerror','-err_detect','explode','-threads','2','-filter_threads','1','-i',str(file),'-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-r','60','-fps_mode','passthrough',str(dst)],out/(key+'.encode.log'))
        windows=[{'object':'a','step':i,'meaning':a['meaning'],'nativeMotionFrames':a['sourceFrames'],'stateBeforeFrame':a['sourceFrames'][0],'stateAfterFrame':a['sourceFrames'][1],'nativeSpeed':1}for i,a in enumerate(native['actions'],1)]
        contract={'sourceBeatId':key,'motionWindows':windows};statefiles=native_state_files(out,key,dst,native['frames'],contract)
        first=statefiles[0]['file'];last=statefiles[-1]['file']
        record({**contract,'inputs':sig,'targetParagraphs':native['targetParagraphs'],'targetScenes':sorted({p['targetScene']for p in paras if p['sourceBeatId']==key}),
            'clip':rel(dst),'clipSha256':sha(dst),'frames':native['frames'],'fps':60,'dimensions':[900,660],'firstFrame':first,'lastFrame':last,
            'nativeStateFiles':statefiles,'sourceROI':{'kind':'native-half-width reflow','crop':[0,0,900,660],'noFullSlideShrink':True},
            'renderer':'Manim Cairo / CPU / retained dim model','sourceKind':'independently authored mathematical illustration','reuseBeat':native['reuseBeat'],'claimLimit':native['claimLimit'],
            'programA':{'kind':'explicit finite mathematical actions','actions':native['actions']},'programB':None,'pair':False,
            'nativeSpeed':1,'loop':False,'forcedHoldFrames':0,'finalPairedCaptionMotionReview':'pending'})
    canonical=canonical_comparison_states(out,next(r for r in outputs if r['sourceBeatId']=='v6-18.B02'))
    readouts={}
    for p in paras:
        policy=p.get('pretermNumericReadoutPolicy')
        if not policy:continue
        pair=cat[p['sourceBeatId']].get('pair',False);x,y,w,h=policy['pairBand'if pair else'singleBand']
        image=Image.new('RGBA',(900,660),(0,0,0,0));d=ImageDraw.Draw(image);d.rectangle((x,y,x+w,y+h),fill=BG)
        label=policy['replacement'];font=ImageFont.truetype(FONT,64);assert font.getlength(label)<=850,(p['targetParagraphId'],label)
        d.text((450,y+h/2),label,font=font,fill=WHITE,anchor='mm')
        file=out/(p['targetParagraphId']+'.preterm-readout.png');image.save(file)
        readouts[p['targetParagraphId']]={'file':rel(file),'sha256':sha(file),'kind':'still','rect':[0,0,900,660],'dimensions':[900,660],'knownUIBand':[x,y,w,h],
            'reason':'Replace only composited h/p/b readout until canonical names are introduced. Native model/axes/rings never painted over.'}
    data=read(O/'right-assets.json');data['pretermReadoutOverrides']=readouts;data['canonicalAliasComparison']=canonical;data['complete']=True;data['sourceCaptureReceiptSha256']=sha(O/'spatial-native/capture-receipt.json');save(O/'right-assets.json',data)
    print(json.dumps({'complete':True,'assets':len(outputs),'paragraphs':len(paras),'manifest':rel(O/'right-assets.json')}),flush=True)

def main():
    global ACTIVE_JOB
    ap=argparse.ArgumentParser();ap.add_argument('--preview',action='store_true');ap.add_argument('--build',action='store_true');a=ap.parse_args()
    if a.preview:previews()
    elif a.build:
        sp=importlib.util.spec_from_file_location('v7_right_build_finite_lease',H/'job-lease.py');lease=importlib.util.module_from_spec(sp);sp.loader.exec_module(lease)
        with lease.finite('M04-A finite right-pane compositing and source-state extraction',require_gpu=False)as record:
            ACTIVE_JOB=record;build()
    else:ap.print_help()

if __name__=='__main__':main()
