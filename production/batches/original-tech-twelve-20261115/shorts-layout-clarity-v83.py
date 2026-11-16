"""Exact12 frame composition; source pixels and pure diagrams only.

This module assigns no narration timings. Actual accepted speech and reviewed
whole-word cues must drive a final film. Samples are not completed videos.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json
import av
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
layout=module('ot12_fixed_caption_layout',HERE/'lockon-layout-v1.py')
diagrams=module('ot12_original_technical_diagrams',HERE/'tech-diagrams-v2.py')
TITLES={
 'shorts-oot-ninja-show-z-targeting':['닌자쇼에서 찾은','젤다 락온의 비밀'],
 'shorts-mario64-lakitu-camera':['3D 게임 카메라를 바꾼','마리오64'],
 'shorts-journey-sand-sparkle':['저니의 모래는','어떻게 반짝일까?'],
 'shorts-horizon-gpu-placement':['호라이즌의 숲은','어떻게 채울까?'],
 'shorts-inside-temporal-antialiasing':['인사이드의 가장자리는','왜 덜 흔들릴까?'],
 'shorts-spiderman-swing-anchor':['거미줄은 어디에','붙어야 잘 날까?'],
 'shorts-control-destruction-pipeline':['컨트롤의 책상은','어떻게 부서질까?'],
 'shorts-returnal-particle-tentacles':['리터널의 촉수는','무엇을 따라 움직일까?'],
 'shorts-ratchet-dimension-streaming':['차원을 넘는 순간','다음 세계는 언제 올까?'],
 'shorts-doom-push-forward-healing':['체력을 채우려면','적에게 다가가라?'],
 'shorts-botw-chemistry-rules':['불과 비의 관계를','장면마다 따로 만들까?'],
 'shorts-mariokart8-spin-boost':['부딪혔는데','왜 더 빨라질까?'],
}
def pin(p):
    p=Path(p)
    with p.open('rb') as f:return dict(path=str(p.resolve()),sha256=hashlib.file_digest(f,'sha256').hexdigest())
class Composer(layout.Composer):
    def __init__(self,slug):
        assert slug in TITLES;self.slug=slug;self.title=layout.font(76,True);self.label=layout.font(34,True);self.body=layout.font(42);self.caption=layout.font(48);self.cats={};self.stream_readers={}
        for t in TITLES[slug]:assert self.title.getlength(t)<=940,t
        provenance=layout.read(ROOT/'shared/assets/branding/cat-reactions-v1/provenance.json')
        for row in provenance['assets']:
            p=ROOT/row['path'];assert pin(p)['sha256']==row['sha256'];self.cats[row['pose']]=Image.open(p).convert('RGBA')
    def base(self,label):
        im=Image.new('RGB',(1080,1920),'black');d=ImageDraw.Draw(im)
        for text,y,color in zip(TITLES[self.slug],[145,240],[layout.TOKENS['ink'],layout.TOKENS['title']]):d.text((492,y),text,font=self.title,anchor='mm',fill=color)
        assert self.label.getlength(label)<=940;d.text((492,348),label,font=self.label,anchor='mm',fill=layout.TOKENS['relation']);return im
    def captioned(self,im,text):
        if not text:return im
        f=self.caption;words=text.split()
        if f.getlength(text)<=800:parts=[text]
        else:
            candidates=[]
            for i in range(1,len(words)):
                a,b=' '.join(words[:i]),' '.join(words[i:]);wa,wb=f.getlength(a),f.getlength(b)
                if max(wa,wb)<=800:
                    orphan=words[i-1].lower() in {'a','an','the','to','of','from','and','or','with','by'}
                    candidates.append((abs(wa-wb)+(200 if orphan else 0),[a,b]))
            assert candidates,'Split the semantic clause at reviewed word boundaries: '+text
            parts=min(candidates,key=lambda x:x[0])[1]
        d=ImageDraw.Draw(im);width=max(f.getlength(x)for x in parts)+44;height=len(parts)*62+22;x=492-width/2;y=1600-height/2
        d.rectangle((round(x+14),round(y+14),round(x+width+14),round(y+height+14)),fill='#073c32');d.rectangle((round(x),round(y),round(x+width),round(y+height)),fill='white',outline='#161b18',width=3)
        for i,line in enumerate(parts):d.text((492,y+42+i*62),line,font=f,fill='#080b09',anchor='mm')
        return im
    def reaction(self,im,pose):
        if pose:
            assert pose in self.cats;cat=self.cats[pose].resize((150,150),Image.Resampling.LANCZOS);im.paste(cat,(35,1194),cat)
        return im
    def game(self,source,seconds,label,caption='',reaction=None):
        # Decode an actual source frame; never loop, invent a replacement or
        # silently choose another media source when a requested frame is absent.
        source=Path(source)
        with av.open(str(source)) as c:
            stream=c.streams.video[0];stream.thread_type='AUTO';c.seek(int(seconds/stream.time_base),stream=stream,backward=True)
            frame=next(f for f in c.decode(stream) if f.time is not None and f.time>=seconds)
            assert frame.width>=1920 and frame.height>=1080;pixels=frame.to_image();pts=frame.time
        im=self.base(label);w=984;h=round(w*pixels.height/pixels.width);assert h<=984;y=396+(984-h)//2;im.paste(pixels.resize((w,h),Image.Resampling.LANCZOS),(0,y))
        # Full source aspect and all original in-picture marks remain visible.
        self.reaction(im,reaction);self.captioned(im,caption)
        return im,dict(source=str(source),sourceFramePts=pts,sourceSize=[frame.width,frame.height],bodyRect=[0,y,w,h],fullSourceAspectPreserved=True,originalInPictureMarksPreserved=True,caption=caption,reaction=reaction,finalFilm=False)
    def diagram(self,key,seconds,caption=''):
        pixels,evidence=diagrams.render(key,seconds);im=self.base('해설용 도식');im.paste(pixels,(0,396));self.captioned(im,caption);return im,dict(diagramEvidence=evidence,bodyRect=[0,396,984,984],caption=caption,finalFilm=False)
    def native_frame(self,mode,view,frame,caption='',capture_kind='full'):
        if self.slug=='shorts-oot-ninja-show-z-targeting':return super().native(mode,view,frame,caption,capture_kind)
        media=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115');remaining={'shorts-spiderman-swing-anchor':'spiderman','shorts-control-destruction-pipeline':'control','shorts-returnal-particle-tentacles':'returnal','shorts-ratchet-dimension-streaming':'ratchet','shorts-doom-push-forward-healing':'doom','shorts-botw-chemistry-rules':'botw','shorts-mariokart8-spin-boost':'mariokart8'}
        base=media/'remaining-seven-native-v1' if self.slug in remaining else media/self.slug/'native-v1';proof=layout.read(base/('accepted-'+capture_kind+'.json'));assert proof['actualUnityCapture'] and proof['mode']==capture_kind
        folder=Path(proof['capture'])
        if self.slug in remaining:folder/=remaining[self.slug]
        source=folder/mode/view/f'{frame:05}.png';assert source.is_file(),'Exact captured frame missing';trace=layout.read(source.parent/'trace.json');assert trace['fingerprint']==proof['fingerprint'];row=next(x for x in trace['frames']if x['frame']==frame)
        label='해설용 모형 · '+('시간 AA 비교'if self.slug=='shorts-inside-temporal-antialiasing'else'직접 만든 비교 장면');im=self.base(label)
        with Image.open(source) as pixels:assert pixels.size==(1080,1080);im.paste(pixels.convert('RGB').resize((984,984),Image.Resampling.LANCZOS),(0,396))
        self.captioned(im,caption);return im,dict(sourceFrame=str(source),framePin=pin(source),traceFrame=row,bodyRect=[0,396,984,984],caption=caption,finalFilm=False)
    def native_stream_frame(self,mode,view,frame,caption='',capture_purpose='full'):
        assert capture_purpose in ['smoke','full']
        media=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115');remaining={'shorts-spiderman-swing-anchor':'spiderman','shorts-control-destruction-pipeline':'control','shorts-returnal-particle-tentacles':'returnal','shorts-ratchet-dimension-streaming':'ratchet','shorts-doom-push-forward-healing':'doom','shorts-botw-chemistry-rules':'botw','shorts-mariokart8-spin-boost':'mariokart8'}
        base=media/('remaining-seven'if self.slug in remaining else self.slug)/'native-stream-v2';proof=layout.read(base/('accepted-'+capture_purpose+'.json'));assert proof['purpose']==capture_purpose and proof['allPixelsRoundTripVerified'];assert proof['framesPerCamera']==(720 if capture_purpose=='full'else 32)
        clip=next(x for x in proof['clips']if x['topic']==remaining.get(self.slug)and x['mode']==mode and x['camera']==view);path=clip['video']['path'];key=(path,clip['video']['sha256'])
        if key not in self.stream_readers:self.stream_readers[key]=NativeStreamReader(clip)
        pixels,rgb=self.stream_readers[key].frame(frame);label='해설용 모형 · '+('540px 테스트의 2배 확대'if self.slug=='shorts-inside-temporal-antialiasing'else'직접 만든 비교 장면');im=self.base(label);im.paste(pixels.resize((984,984),Image.Resampling.LANCZOS),(0,396));self.captioned(im,caption)
        row=self.stream_readers[key].trace[frame];assert row['frame']==frame
        return im,dict(sourceVideo=clip['video'],frame=frame,verifiedRgbSHA256=rgb,traceFrame=row,bodyRect=[0,396,984,984],capturePurpose=capture_purpose,caption=caption,finalFilm=False)
    def close(self):
        for reader in self.stream_readers.values():reader.close()
        self.stream_readers.clear()
class NativeStreamReader:
    def __init__(self,clip):
        self.path=Path(clip['video']['path']);assert pin(self.path)['sha256']==clip['video']['sha256'];self.signature=(self.path.stat().st_size,self.path.stat().st_mtime_ns)
        manifest=Path(clip['frameRgbManifest']['path']);assert pin(manifest)['sha256']==clip['frameRgbManifest']['sha256'];self.frames=layout.read(manifest)['frames'];assert clip['allDecodedPixelsExact']
        trace=Path(clip['trace']['path']);assert pin(trace)['sha256']==clip['trace']['sha256'];self.trace=layout.read(trace)['frames'];assert len(self.trace)==len(self.frames)
        self.container=av.open(str(self.path));self.stream=self.container.streams.video[0];assert self.stream.average_rate==60 and(self.stream.width,self.stream.height)==(1080,1080);self.last=-1;self.decoder=None
    def frame(self,index):
        assert 0<=index<len(self.frames)and(self.path.stat().st_size,self.path.stat().st_mtime_ns)==self.signature
        if self.decoder is None or index!=self.last+1:
            self.container.seek(int(index/(60*self.stream.time_base)),stream=self.stream,backward=True);self.decoder=self.container.decode(self.stream)
        frame=next(f for f in self.decoder if f.time is not None and round(f.time*60)>=index);assert round(frame.time*60)==index
        array=frame.to_ndarray(format='rgb24');digest=hashlib.sha256(array.tobytes()).hexdigest();assert digest==self.frames[index]['rgbSHA256'],'Actual source pixels changed';self.last=index
        return Image.fromarray(array),digest
    def close(self):self.container.close()
def main():
    p=argparse.ArgumentParser();p.add_argument('--samples',type=Path,required=True);a=p.parse_args();a.samples.mkdir(parents=True,exist_ok=False)
    m=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115');rows=[]
    cases=[('botw-fire','shorts-botw-chemistry-rules',m/'shorts-botw-chemistry-rules/sources/botw-part2-rain-candidate-3060-3130-v3.mp4',51.5,'게임 장면 · 에뮬레이터 녹화','불이 나무에 닿으면 불붙은 상태가 되는 식입니다.'),('ratchet-dimension','shorts-ratchet-dimension-streaming',m/'shorts-ratchet-dimension-streaming/sources/ratchet-chase-world-transitions-640-703-v4.mp4',35,'게임 장면 · PS5 녹화','다음 장면의 자료를 읽고 풀어 쓰는 과정을 보겠습니다.')]
    for name,slug,source,seconds,label,caption in cases:
        im,e=Composer(slug).game(source,seconds,label,caption,'puzzled');target=a.samples/(name+'.png');im.save(target);im.resize((375,667),Image.Resampling.LANCZOS).save(a.samples/(name+'-375.png'));rows.append(dict(image=str(target),sourcePin=pin(source),evidence=e))
    im,e=Composer('shorts-returnal-particle-tentacles').diagram('returnal-delay',3.5,'여기서 자식이 읽는 것은 부모의 한 프레임 전 정보입니다.');target=a.samples/'returnal-information.png';im.save(target);im.resize((375,667),Image.Resampling.LANCZOS).save(a.samples/'returnal-information-375.png');rows.append(dict(image=str(target),evidence=e))
    (a.samples/'samples.json').write_text(json.dumps(dict(designSamplesOnly=True,source=pin(__file__),diagramSource=pin(HERE/'tech-diagrams-v2.py'),frames=rows,actualNarrationTimingsAssigned=False,finalFilm=False),ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(a.samples)
if __name__=='__main__':main()
