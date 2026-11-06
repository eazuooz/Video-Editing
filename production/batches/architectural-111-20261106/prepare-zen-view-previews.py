"""Actual07.04 native-JPEG portrait/mobile still prototypes. CPU only.

No Unity/model/video decoder/encoder/browser, source-image mutation or production
approval. Default validates inputs; --write-samples writes a hash-bound new
preview folder. Native frame/ray/anchor clocks remain unchanged.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
PROJECT=ROOT/'projects/shorts-leveldesign-07-04'
MEDIA=Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106/shorts-leveldesign-07-04')
OUT=MEDIA/'native-previews-v1'
FRAMES=(0,224,239,255,479)
PANELS=((48,410,880,495),(48,992,880,495))
CAPTION_LINES=('벽 두께 안에서 막히면','등대의 그 지점은 보이지 않습니다.')
FONT=Path('C:/Windows/Fonts/NotoSansKR-VF.ttf');HEAD_FONT=Path('C:/Windows/Fonts/malgunbd.ttf')

def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def pin(path):return dict(path=str(Path(path).resolve()),sha256=sha(path))
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def save_once(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():assert path.read_bytes()==data,'Preserve a differing previous preview'
    else:path.write_bytes(data)

class ZenPreviewComposer:
    def __init__(self):
        self.evidence_path=PROJECT/'native-evidence-v1.json';self.evidence=read(self.evidence_path)
        assert self.evidence['captureComplete'] is True and self.evidence['topicId']=='07.04'
        self.base=Path(self.evidence['output']);self.contract=self.evidence['contract']
        assert self.contract['frames']==480 and self.contract['cameras']==['player','observer']
        self.pins=[pin(self.evidence_path),pin(Path(__file__)),pin(FONT),pin(HEAD_FONT)]
        for row in self.evidence['captureProofs']:
            assert sha(row['path'])==row['sha256'];self.pins.append(row)
        hashes=read(self.evidence['frameHashManifest']['path']);assert hashes['fingerprint']==self.evidence['fingerprint']
        self.frame_hashes={r['path']:r for r in hashes['frames']};assert len(self.frame_hashes)==1920
        self.draft=read(PROJECT/'narration-draft.json');self.pins.append(pin(PROJECT/'narration-draft.json'))
        assert ' '.join(CAPTION_LINES) in self.draft['narrationKo'][3],'Representative caption is no longer current authored P4 text'
        style=ROOT/'projects/shorts-leveldesign-03-02/visual-layout-v1.json';self.pins.append(pin(style))
        self.style=read(style);self.tokens=self.style['tokens']['scene'];self.caption_tokens=self.style['tokens']['caption']
        self.fonts={};self.used_frames={};self.metadata={}
        for mode in ('narrow','wide'):
            folder=self.base/mode
            self.metadata[mode]=dict(anchors=[json.loads(r) for r in (folder/'projected-anchors.jsonl').read_text().splitlines()],
                rays=[json.loads(r) for r in (folder/'rays.jsonl').read_text().splitlines()],
                trace=list(csv.DictReader((folder/'trace.csv').open(encoding='utf-8-sig'))))
            assert all(len(rows)==480 for rows in self.metadata[mode].values())
        self.identity=dict(nativeFingerprint=self.evidence['fingerprint'],inputs=self.pins,frames=FRAMES,panels=PANELS,
            captionLines=CAPTION_LINES,format=[1080,1920],mobile=[375,667],method='07-04-native-paired-still-prototype-v1')
        self.fingerprint=digest(self.identity)
    def font(self,size,weight=700,caption=False):
        key=(size,weight,caption)
        if key not in self.fonts:
            value=ImageFont.truetype(str(FONT if caption else HEAD_FONT),size)
            if caption:value.set_variation_by_axes([weight])
            self.fonts[key]=value
        return self.fonts[key]
    def text(self,draw,text,xy,size=38,color=None,anchor='mm'):
        font=self.font(size);draw.text(xy,text,font=font,fill=color or self.tokens['ink'],anchor=anchor,
            stroke_width=2,stroke_fill='#000000')
        return list(draw.textbbox(xy,text,font=font,anchor=anchor,stroke_width=2))
    def picture(self,canvas,mode,camera,frame,panel):
        relative=f'{mode}/{camera}/{frame:04}.jpg';record=self.frame_hashes[relative];path=self.base/relative
        assert sha(path)==record['sha256'] and path.stat().st_size==record['bytes']
        with Image.open(path) as image:
            image.load();assert image.size==(1920,1080)
            canvas.paste(image.convert('RGB').resize(panel[2:],Image.Resampling.LANCZOS),panel[:2])
        source=dict(path=str(path),sha256=record['sha256'],frame=frame,mode=mode,camera=camera,sourceDimensions=[1920,1080],panel=list(panel),crop=None,rotation=None)
        self.used_frames[relative]=source;return source
    def point(self,anchor,camera,panel):
        p=anchor[camera+'Viewport'];assert all(math.isfinite(p[k]) for k in ('x','y','z'))
        assert p['z']>0 and 0<=p['x']<=1 and 0<=p['y']<=1,'Do not clamp or fabricate off-screen anchor'
        return (panel[0]+p['x']*panel[2],panel[1]+(1-p['y'])*panel[3])
    def frame_data(self,mode,frame):
        rows=self.metadata[mode];a,r,t=(rows[k][frame] for k in ('anchors','rays','trace'))
        assert a['frame']==r['frame']==int(t['frame'])==frame
        anchors={q['name']:q for q in a['anchors']};ray=r['rays'][0]
        assert ray['target']=='fixed-landmark-center' and ray['visible']==(t['centerVisible']=='1')
        assert ray['origin']==anchors['eye']['world'] and ray['actualEndpoint']==anchors['fixed-landmark-center-actual-end']['world']
        return anchors,ray
    def caption(self,canvas):
        font=self.font(48,500,True);widths=[font.getlength(t) for t in CAPTION_LINES];assert max(widths)<=800
        width=math.ceil(max(widths))+44;height=146;cx,cy=488,1600;x,y=cx-width/2,cy-height/2;draw=ImageDraw.Draw(canvas)
        draw.rectangle((x+14,y+14,x+width+14,y+height+14),fill=self.caption_tokens['shadow'])
        draw.rectangle((x,y,x+width,y+height),fill=self.caption_tokens['background'],outline=self.caption_tokens['border'],width=3)
        for i,text in enumerate(CAPTION_LINES):draw.text((cx,cy+(i-.5)*62-1),text,font=font,fill=self.caption_tokens['text'],anchor='mm')
        return dict(lines=list(CAPTION_LINES),box=[x,y,x+width,y+height],shadow=[x+14,y+14,x+width+14,y+height+14],
            center=[488,1600],fontPx=48,mobileFontPx=48*375/1080,actualSpeechTimingVerified=False,scriptParagraph=4)
    def canvas(self,subtitle):
        canvas=Image.new('RGB',(1080,1920),self.tokens['background']);draw=ImageDraw.Draw(canvas)
        self.text(draw,'게임은 왜 멋진 풍경을',(488,166),72)
        self.text(draw,'가려 놓을까?',(488,254),82,self.tokens['title'])
        self.text(draw,subtitle,(488,326),34,self.tokens['muted'])
        self.text(draw,'구도 검수용 · 자막 타이밍 미확인',(488,1732),26,self.tokens['muted'])
        return canvas
    def player_mark(self,canvas,anchors,ray,panel):
        draw=ImageDraw.Draw(canvas);role='result' if ray['visible'] else 'problem';color=self.tokens[role]
        self.text(draw,'등대 중심 시야선: '+('통과' if ray['visible'] else '막힘'),(488,panel[1]+panel[3]-33),34,color)
        marks=[]
        if ray['visible']:
            p=self.point(anchors['landmark-center'],'player',panel)
            draw.ellipse((p[0]-21,p[1]-21,p[0]+21,p[1]+21),outline=color,width=7)
            self.text(draw,'등대 중심',(panel[0]+155,panel[1]+170),34,color)
            draw.line([(panel[0]+235,panel[1]+180),(p[0]-26,p[1])],fill=color,width=6)
            marks.append(dict(target='visible-landmark-center',point=list(p),role='verified center-point ray; not a lighthouse pixel bounding box'))
        return marks
    def observer_marks(self,canvas,anchors,ray,panel):
        draw=ImageDraw.Draw(canvas);color=self.tokens['result' if ray['visible'] else 'problem']
        eye=self.point(anchors['eye'],'observer',panel);end=self.point(anchors['fixed-landmark-center-actual-end'],'observer',panel)
        draw.line([eye,end],fill=color,width=10);draw.ellipse((eye[0]-10,eye[1]-10,eye[0]+10,eye[1]+10),fill='#000000',outline=self.tokens['ink'],width=4)
        draw.ellipse((end[0]-12,end[1]-12,end[0]+12,end[1]+12),outline=color,width=7)
        labels=[]
        for kind,center,label_pos,role in [('front',False,(panel[0]+188,panel[1]+353),'relationship'),('back',True,(panel[0]+650,panel[1]+260),'title')]:
            left=self.point(anchors[kind+'-left'],'observer',panel);right=self.point(anchors[kind+'-right'],'observer',panel)
            tint=self.tokens[role];draw.line([left,right],fill=tint,width=8)
            for p in (left,right):draw.line([(p[0],p[1]-9),(p[0],p[1]+9)],fill=tint,width=5)
            midpoint=((left[0]+right[0])/2,(left[1]+right[1])/2)
            text='입구' if kind=='front' else '출구';labels.append(self.text(draw,text,label_pos,34,tint))
            draw.line([(label_pos[0]+(45 if kind=='front' else -45),label_pos[1]),midpoint],fill=tint,width=5)
        labels.append(self.text(draw,'카메라 눈',(panel[0]+185,panel[1]+452),32,self.tokens['ink']))
        draw.line([(panel[0]+270,panel[1]+449),eye],fill=self.tokens['ink'],width=5)
        if ray['visible']:
            label='중심 시야선 통과';pos=(panel[0]+660,panel[1]+175)
        else:
            label='벽에 막힌 지점';pos=(panel[0]+668,panel[1]+399)
        labels.append(self.text(draw,label,pos,34,color));draw.line([(pos[0]-75,pos[1]+15),end],fill=color,width=6)
        return dict(eye=list(eye),actualEndpoint=list(end),actualRay=ray,labels=labels,
            sourceKind='Editorial thick guides using actual same-frame native viewport/world/raycast endpoints; blocked ray is never extended to desired hidden target')
    def compose(self,mode,frame):
        canvas=self.canvas(('좁은 틈' if mode=='narrow' else '넓은 창')+' · 같은 길과 카메라');draw=ImageDraw.Draw(canvas)
        self.text(draw,'직접 만든 Unity 시연 · 눈높이',(488,376),36)
        self.text(draw,'위에서 본 같은 순간 · 관찰용 단면',(488,958),34,self.tokens['relationship'])
        sources=[self.picture(canvas,mode,camera,frame,panel) for camera,panel in zip(('player','observer'),PANELS)]
        anchors,ray=self.frame_data(mode,frame);player=self.player_mark(canvas,anchors,ray,PANELS[0]);observer=self.observer_marks(canvas,anchors,ray,PANELS[1])
        cap=self.caption(canvas)
        return canvas,dict(kind='synchronized-player-observer',mode=mode,frame=frame,sourceFrames=sources,playerMarks=player,observerMarks=observer,
            caption=cap,observerCutaway='Only lintel is not rendered in observer; player and raycasts retain full physical occluder',
            clearance=self.clearance(cap),actualMotionOrSpeechTimingReviewed=False)
    def compare(self):
        canvas=self.canvas('같은 순간 · 바꾸는 건 틈 폭 하나');draw=ImageDraw.Draw(canvas);sources=[];marks=[]
        for mode,panel,letter,label_y in [('narrow',PANELS[0],'A',376),('wide',PANELS[1],'B',958)]:
            self.text(draw,letter+' · '+('좁은 틈' if mode=='narrow' else '넓은 창')+' · 눈높이',(488,label_y),38)
            sources.append(self.picture(canvas,mode,'player',0,panel));anchors,ray=self.frame_data(mode,0);marks.append(self.player_mark(canvas,anchors,ray,panel))
        cap=self.caption(canvas)
        return canvas,dict(kind='same-frame-width-only-A-B',frame=0,sourceFrames=sources,playerMarks=marks,caption=cap,
            fixedConditions='Same path sample, eye, camera orientation/FOV, target, wall depth/slant; only opening width differs',clearance=self.clearance(cap))
    def clearance(self,caption):
        right=max(p[0]+p[2] for p in PANELS);bottom=PANELS[1][1]+PANELS[1][3]
        assert caption['box'][1]>bottom and caption['shadow'][2]<936 and right<936
        return dict(secondPanelBottom=bottom,captionBoxTop=caption['box'][1],panelToCaptionPx=caption['box'][1]-bottom,
            rightPlatformRailStarts=936,panelRight=right,panelToRailPx=936-right,captionShadowToRailPx=936-caption['shadow'][2],
            captionShadowBottom=caption['shadow'][3],bottomMetadataStarts=1760,captionToBottomMetadataPx=1760-caption['shadow'][3],
            nativePanelAspect='880/495 =16/9; full source retained without crop or stretch',platformUiActuallyTested=False)

def png(image):
    import io
    stream=io.BytesIO();image.save(stream,format='PNG');return stream.getvalue()
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--write-samples',action='store_true');args=parser.parse_args();composer=ZenPreviewComposer()
    if not args.write_samples:print(json.dumps(dict(ready=True,fingerprint=composer.fingerprint,nativeFingerprint=composer.evidence['fingerprint'],sourceOnly=True)));return
    folder=OUT/composer.fingerprint[:20];rows=[]
    for mode in ('narrow','wide'):
        for frame in FRAMES:
            image,meta=composer.compose(mode,frame);rows.append((f'{mode}-{frame:04}',image,meta))
    image,meta=composer.compare();rows.append(('compare-frame-0000',image,meta))
    output=[];contact=Image.new('RGB',(375*3,717*4),'#000000');contact_draw=ImageDraw.Draw(contact)
    for index,(name,image,meta) in enumerate(rows):
        native_path=folder/(name+'-1080.png');mobile_path=folder/(name+'-375.png');mobile=image.resize((375,667),Image.Resampling.LANCZOS)
        save_once(native_path,png(image));save_once(mobile_path,png(mobile));meta.update(name=name,native=pin(native_path),mobile=pin(mobile_path),actualAgentVisualInspection='pending')
        output.append(meta);x=(index%3)*375;y=(index//3)*717;contact.paste(mobile,(x,y+40));contact_draw.text((x+12,y+8),name,font=composer.font(24),fill='white')
    contact_path=folder/'mobile-contact.png';save_once(contact_path,png(contact))
    report=dict(schemaVersion='07-04-native-preview-prototypes-v1',fingerprint=composer.fingerprint,nativeFingerprint=composer.evidence['fingerprint'],
        status='CPU still layout prototypes; not actual caption/voice timing or finished video QA',inputs=composer.pins,
        samples=output,contact=pin(contact_path),usedSourceFrames=list(composer.used_frames.values()),captionSource=dict(paragraph=4,text=' '.join(CAPTION_LINES),draft=pin(PROJECT/'narration-draft.json')),
        wholeLighthouseVisibilityClaim=False,visibilityMeaning='Only actual center-target ray clear/blocked. Partial lighthouse/ocean slivers around224/255 remain untouched and are not relabelled invisible.',
        catPolicy=dict(dualCameraExplanationCatCues=False,appliesTo=['S03','S04'],
            reason='Reference-approved large cat would cover the lower observer eye/ray origin. Preserve paired geometry and caption clarity.',
            approvedLargeCatMustNotBeShrunkOrRelocated=True,
            finalCatAllowedOnly='Opening player-only reveal,2D reward diagrams or closing where target is clear and the fixed large-cat area is reserved; final encoded cat QA remains separate'),
        actualSpeechTimingVerified=False,actualMotionPlayback=False,voicePreparationAllowed=False,humanApproval=False,gpuUsed=False,
        processScope='Pillow JPEG reads and still composites only; no Unity/model/video encode/decode/browser/ASR')
    report_path=folder/'manifest.json';save_once(report_path,(json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
    print(json.dumps(dict(output=str(folder),manifest=pin(report_path),samples=len(output),nativeFingerprint=composer.evidence['fingerprint']),ensure_ascii=False))
if __name__=='__main__':main()
