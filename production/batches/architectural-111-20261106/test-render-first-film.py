"""Synthetic CPU-only renderer contracts; never starts a decoder/encoder/model."""
from __future__ import annotations
import copy
import hashlib
import importlib.util
import io
import json
import math
import tempfile
from pathlib import Path
from types import SimpleNamespace
from PIL import Image

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('firstfilm_renderer_fixture',HERE/'render-first-film.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)


def fixture():
    game=lambda sid,start,end,pts:dict(id=sid,kind='gameplay',startFrame=start,endFrameExclusive=end,
        sourceId=sid,sourcePath=sid+'.mp4',sourceSHA256='0'*64,sourceLocalInPts=pts,rate=1,
        catPose=None,termChips=[],annotationCues=[])
    native=lambda sid,mode,start,end,hold=None:dict(id=sid,kind='native',startFrame=start,endFrameExclusive=end,
        native=dict(mode=mode,layout='dual' if hold is None else 'single-top',startNativeFrame=0 if hold is None else 70,
            frameCount=270 if hold is None else 1,playbackRate=1,holdPolicy=hold),
        catPose=None,termChips=[],annotationCues=[])
    rows=[game('A',0,30,25),game('B',30,60,40),native('N','narrow',60,330),native('W','wide',330,600),
        native('H','narrow',600,620,dict(frame=70,reason='Explain the actual footprint at the blocked position'))]
    rows[0]['annotationCues']=[dict(kind='opening-tracks',startFrame=0,endFrameExclusive=30)]
    return dict(schemaVersion='03-02-final-timeline-v1',status='synthetic-fixture-no-production-proof',
        format=dict(width=1080,height=1920,fps=60),totalFrames=620,sections=rows,
        captions=[dict(id='c',startFrame=0,endFrameExclusive=620,ko='시험 문장',en='Test clause',koLines=['시험 문장'],enLines=['Test clause'])])


checks=[]
def reject(name,call):
    try:call()
    except (ValueError,RuntimeError):checks.append(dict(check=name,result='rejected'))
    else:raise AssertionError('Accepted invalid fixture: '+name)


def change_and_check(name,change):
    value=fixture();change(value);reject(name,lambda:r.validate_structure(value))


def main():
    # Any accidental production tool launch fails this entire CPU test.
    r.subprocess.Popen=lambda *a,**k:(_ for _ in ()).throw(AssertionError('No subprocess in synthetic QA'))
    good=fixture();audit=r.validate_structure(good)
    assert audit['nativeMovingFrames']==dict(narrow=270,wide=270)
    checks.append(dict(check='normal exact60fps source/native/hold timeline',result='passed'))
    change_and_check('30fps master rejected',lambda t:t['format'].update(fps=30))
    change_and_check('picture-cut gap rejected',lambda t:t['sections'][1].update(startFrame=31))
    change_and_check('picture-cut overlap rejected',lambda t:t['sections'][1].update(startFrame=29))
    change_and_check('native retiming rejected',lambda t:t['sections'][2]['native'].update(playbackRate=.5))
    change_and_check('native missing final frame rejected',lambda t:t['sections'][2]['native'].update(frameCount=269))
    change_and_check('native frame270 rejected',lambda t:t['sections'][4]['native'].update(startNativeFrame=270))
    change_and_check('native repeat clock rejected',lambda t:t['sections'][3]['native'].update(mode='narrow'))
    change_and_check('unexplained native freeze rejected',lambda t:t['sections'][4]['native']['holdPolicy'].update(reason=''))
    change_and_check('gameplay hold rejected',lambda t:t['sections'][0].update(holdPolicy={'frame':0}))
    change_and_check('gameplay slowdown rejected',lambda t:t['sections'][0].update(rate=.5))
    change_and_check('gameplay repeated source interval rejected',lambda t:t['sections'][1].update(sourceId='A',sourceLocalInPts=25.2))
    change_and_check('source-crossing annotation rejected',lambda t:t['sections'][0]['annotationCues'][0].update(endFrameExclusive=31))
    change_and_check('unknown native guide component rejected',lambda t:t['sections'][2].update(annotationCues=[dict(kind='native-guides',startFrame=60,endFrameExclusive=330,guideParts=['invented-ray'])]))
    change_and_check('caption word omission rejected',lambda t:t['captions'][0].update(koLines=['시험']))
    change_and_check('cat on dual view rejected',lambda t:t['sections'][2].update(catPose='realize'))
    change_and_check('global cat on dual view rejected',lambda t:t.update(catCues=[dict(pose='realize',startFrame=90,endFrameExclusive=120,easeInFrames=7,easeOutFrames=9)]))
    reject('output outside scoped C-media attempt rejected',lambda:r.selected_output_root('D:/Github/VideoEditing/output'))
    with tempfile.TemporaryDirectory(prefix='yamyam-firstfilm-cpu-') as directory:
        file=Path(directory)/'input.bin';file.write_bytes(b'actual fixture bytes')
        record=dict(path=str(file),sha256=r.sha(file));assert r.bound_file(record,'fixture')==file
        file.write_bytes(b'changed')
        reject('changed bound input rejected',lambda:r.bound_file(record,'fixture'))

    # Test the real source cadence scheduler with two raw RGB frames. At60fps
    # presentation, the original30fps frame is repeated normally, never renamed.
    frame_bytes=1920*1080*3
    decoder=object.__new__(r.CutDecoder)
    decoder.selected=[25.,25+1/30];decoder.index=-1;decoder.image=None;decoder.last_desired=-1
    decoder.process=SimpleNamespace(stdout=io.BytesIO(bytes(frame_bytes)+bytes([1])*frame_bytes))
    _,a=decoder.at(25.);_,b=decoder.at(25+1/60);_,c=decoder.at(25+2/60)
    assert a==b==25. and abs(c-(25+1/30))<1e-8
    reject('source time reversal rejected',lambda:decoder.at(25))
    checks.append(dict(check='30fps source cadence retained within60fps output',result='passed'))
    rounded=object.__new__(r.CutDecoder)
    rounded.selected=[25.,25.033333,25.066667];rounded.index=-1;rounded.image=None;rounded.last_desired=-1
    rounded.process=SimpleNamespace(stdout=io.BytesIO(bytes(frame_bytes*3)))
    actual=[rounded.at(25+i/60)[1] for i in range(6)]
    assert actual==[25.,25.,25.033333,25.033333,25.066667,25.066667]
    checks.append(dict(check='six-decimal decoded PTS retains two output frames per actual source frame',result='passed'))
    truncated=object.__new__(r.CutDecoder)
    truncated.selected=[0.];truncated.index=-1;truncated.image=None;truncated.last_desired=-1
    truncated.process=SimpleNamespace(stdout=io.BytesIO(b'truncated'))
    reject('missing decoded frame is not silently held',lambda:truncated.at(0.))

    class FakeNative:
        def compose(self,mode,frame,**kwargs):
            return SimpleNamespace(image=Image.new('RGB',(1080,1920)),evidence=dict(mode=mode,frame=frame))
    class FakeGame:
        def compose(self,picture,source_id,local_pts,annotations):
            return SimpleNamespace(image=Image.new('RGB',(1080,1920)),evidence=dict(sourceId=source_id,pts=local_pts,annotations=annotations))
    class FakeDecoder:
        def __init__(self,*args):self.closed=False
        def at(self,t):return Image.new('RGB',(1920,1080)),math.floor(t*30+.000001)/30
        def close(self,*args):self.closed=True
    class FakeStyle:
        tokens=dict(muted='white')
        def _captions(self,*args):return None
        def text(self,*args):return None
    r.CutDecoder=FakeDecoder;r.probe_pts=lambda *args:[0.]
    router=object.__new__(r.FrameRouter);router.timeline=good;router.work=Path('.')
    router.ffmpeg='never-launched';router.ffprobe='never-launched';router.native=FakeNative();router.game=FakeGame();router.style=FakeStyle()
    router.starts=[s['startFrame'] for s in good['sections']];router.caption_starts=[0]
    router.current_section=None;router.decoder=None;router.pts_cache={};router.cut_counter=0;router.hold_cache={}
    router.game_last_key=None;router.game_last_result=None
    assert router.compose(0)[2]['source']['annotations'] is True
    assert router.compose(29)[2]['source']['sourceId']=='A'
    switched=router.compose(30)[2]['source']
    assert switched['sourceId']=='B' and switched['annotations'] is False
    for output,mode,nf in [(60,'narrow',0),(329,'narrow',269),(330,'wide',0),(599,'wide',269),(600,'narrow',70),(619,'narrow',70)]:
        actual=router.compose(output)[2]['source'];assert actual['mode']==mode and actual['frame']==nf
    reject('output final frame end-exclusive',lambda:router.compose(620))
    checks.append(dict(check='cut boundaries clear old source annotations and preserve native0..269 clock',result='passed'))
    wrapped=dict(ko='시험 문장',koLines=['시험','문장'],emphasis={'ko':[dict(start=3,end=5,role='term')]})
    assert r.caption_emphasis(wrapped)==(1,0,2,'term')
    wrapped['emphasis']['ko'][0].update(start=0)
    reject('cross-line caption emphasis rejected',lambda:r.caption_emphasis(wrapped))
    checks.append(dict(check='authored clause span follows exact wrapped line',result='passed'))
    router.close()
    reveals=dict(annotationCues=[
        dict(kind='native-guides',startFrame=10,endFrameExclusive=20,guideParts=['clearance']),
        dict(kind='native-guides',startFrame=20,endFrameExclusive=30,guideParts=['clearance','footprint']),
        dict(kind='native-guides',startFrame=30,endFrameExclusive=40,guideParts=['clearance','footprint','input'])])
    assert not r.guide_request(reveals,9)['enabled']
    assert r.guide_request(reveals,10)['parts']==('clearance',)
    assert r.guide_request(reveals,20)['parts']==('clearance','footprint')
    assert r.guide_request(reveals,30)['parts']==r.GUIDE_PARTS
    assert not r.guide_request(reveals,40)['enabled']
    legacy=dict(annotationCues=[dict(kind='native-guides',startFrame=0,endFrameExclusive=10)])
    assert r.guide_request(legacy,0)['reviewedBundle'] is True
    checks.append(dict(check='gap then footprint then input reveal at exact cue boundaries; legacy bundle retained',result='passed'))
    # Pixel-level component checks on an otherwise black synthetic canvas use
    # the existing real trace/projection/tokens. No timeline/movie or sample
    # file is created, and this is not final visual/motion QA.
    native_module=r.load_module('firstfilm_actual_guide_contract',r.PROJECT/'production/composite-native-frame.py')
    native=native_module.NativeFrameComposer()
    painter=object.__new__(r.FrameRouter);painter.native=native;painter.style=native
    row=native.trace['narrow'][70];blank=Image.new('RGB',(1080,1920))
    clearance,cm=painter._guide_parts(blank,row,'dual',('clearance',))
    footprint,fm=painter._guide_parts(blank,row,'dual',('footprint',))
    radius=float(row['playerDiameter'])/2
    p=native._top_point(float(row['playerX'])+radius,float(row['playerZ']),False)
    pixel=(round(p[0]),round(p[1]))
    assert clearance.getpixel(pixel)==(0,0,0) and footprint.getpixel(pixel)!=(0,0,0)
    assert cm['shownParts']==['clearance'] and fm['shownParts']==['footprint']
    _,im=painter._guide_parts(blank,native.trace['wide'][269],'dual',('input',))
    assert im['shownParts']==['input'] and im['inputTarget'] is not None
    dx,dy,dw,dh=native.spec['nativeCropMaps']['top']['destinationInLower']
    assert dx<im['inputTarget'][0]<dx+dw and dy<im['inputTarget'][1]<dy+dh
    checks.append(dict(check='actual same-native geometry draws only requested components and keeps final input target inside captured panel',result='passed'))
    report=dict(scope='Synthetic CPU fixtures only; no production timeline, media encode, decoder subprocess, model or GPU',
        rendererPath=str(HERE/'render-first-film.py'),rendererSHA256=r.sha(HERE/'render-first-film.py'),
        testSHA256=r.sha(__file__),checks=checks,count=len(checks),allPassed=True,
        productionRenderExecuted=False,productionProofCreated=False,metadataChanged=False)
    target=HERE/'first-renderer-cpu-validation.json'
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(checks=len(checks),allPassed=True,report=str(target))))


if __name__=='__main__':main()
