"""One raw-PCM clock for speech, bilingual captions and simultaneous panes.

No observation slots, time stretching, voice regeneration or media rendering.
Every native24k sample is retained. A scene only receives its sub-frame tail
pad so all video boundaries are exact60fps; words keep their raw sample clock.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json, math

H=Path(__file__).resolve().parent
R=H.parents[3]
P=R/'projects/game-math-euler-axis-angle'
O=P/'production/local/revision-v7-part1'
A=O/'audio'
S=P/'script/revision-v7-two-part'
FPS=60

def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p): return Path(p).resolve().relative_to(R).as_posix()
def save(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def module(name,path):
    sp=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod);return mod

def authorized():
    auth=read(H/'authorization.json');ctl=read(R/'shared/publishing/video-production-control.json')
    claim=ctl.get('scopedProductionAuthorizations',{}).get(P.name,{})
    assert auth['selectedPart']==1 and auth['fullProductionAuthorized']
    assert sha(S/'part-01.ko.json')==auth['approvedScriptSha256']
    assert ctl['selectedVideo']==P.name or (claim.get('fullProductionAuthorized') and claim.get('authorizationSha256')==sha(H/'authorization.json'))
    return auth

def normalizer():
    return module('v7_timing_source_normalization',H/'voice-analysis.py').alignment_helpers()[1]

def make_timeline():
    auth=authorized();alignment=read(A/'source-alignment.json')
    assert alignment['status']=='complete-current-word-alignment' and not alignment['pending']
    assert alignment['sceneCount']==21 and alignment['paragraphCount']==135
    ko=read(S/'part-01.ko.json');voice=read(H/'voice-input.json');norm=normalizer()
    assert len(ko['scenes'])==len(voice['scenes'])==len(alignment['scenes'])==21
    frame=120;scenes=[]
    for src,spoken,al in zip(ko['scenes'],voice['scenes'],alignment['scenes']):
        sid=src['id'];assert sid==spoken['id']==al['id']
        assert al['sampleRate']==24000 and sha(R/al['sourceFile'])==al['sourceSha256']
        frames=math.ceil(al['samples']/400);lines=[];assert len(src['lines'])==len(spoken['lines'])==len(al['lines'])
        for i,(text,speech,line) in enumerate(zip(src['lines'],spoken['lines'],al['lines']),1):
            assert norm(text)==norm(speech),(sid,i,'Display/source timing normalization must agree')
            assert len(norm(text))==len(line['characterStarts'])==len(line['characterEnds'])
            lines.append(dict(line=i,paragraphId=f'{sid}.L{i:02}',rawStart=line['rawStart'],rawEnd=line['rawEnd'],
                globalStart=frame/FPS+line['rawStart'],globalEnd=frame/FPS+line['rawEnd'],
                startFrame=round(frame+line['rawStart']*FPS),endFrame=round(frame+line['rawEnd']*FPS),
                sourceTextSha256=hashlib.sha256(text.encode('utf8')).hexdigest(),normalizedCharacterCount=len(norm(text))))
        scenes.append(dict(id=sid,title=src['title'],startFrame=frame,endFrame=frame+frames,frames=frames,
            start=frame/FPS,end=(frame+frames)/FPS,rawVoiceFile=al['sourceFile'],rawVoiceSha256=al['sourceSha256'],
            rawVoiceSamples=al['samples'],sampleRate=24000,rawVoiceSeconds=al['seconds'],sourceSpeed=1,
            tailPadSamples=frames*400-al['samples'],insertedObservationFrames=0,lines=lines))
        frame+=frames
    result=dict(schemaVersion=1,revision='v7-part1-raw-voice-clock',part=1,fps=FPS,width=1920,height=1080,
        introFrames=120,outroFrames=600,bodyStartFrame=120,bodyEndFrame=frame,totalFrames=frame+600,
        duration=(frame+600)/FPS,sourceRawSeconds=sum(s['rawVoiceSeconds'] for s in scenes),
        insertedObservationFrames=0,sceneGapFrames=0,voiceRate=1,tailPaddingOnly=True,
        paneLayout=dict(game=[40,250,896,504],explanation=[980,180,900,660],simultaneous=True),
        inputs=dict(koSha256=sha(S/'part-01.ko.json'),enSha256=sha(S/'part-01.en.json'),
            authorizationSha256=sha(H/'authorization.json'),alignmentSha256=sha(A/'source-alignment.json'),
            normalizationImplementationSha256=sha(H/'voice-analysis.py'),implementationSha256=sha(Path(__file__))),
        scenes=scenes,humanFinalVideoReview='pending')
    save(H/'timeline.json',result)
    print(json.dumps(dict(sceneCount=21,paragraphCount=135,frames=result['totalFrames'],seconds=result['duration'],insertedObservationFrames=0)))
    return result

class Clock:
    def __init__(self):
        self.timeline=read(H/'timeline.json');self.alignment=read(A/'source-alignment.json')
        assert self.timeline['inputs']['alignmentSha256']==sha(A/'source-alignment.json')
        self.scenes={s['id']:s for s in self.timeline['scenes']}
        self.raw={s['id']:s for s in self.alignment['scenes']}
        self.script={s['id']:s for s in read(S/'part-01.ko.json')['scenes']}
        self.normalize=normalizer()
    def word(self,sid,line,offset,end=False):
        """Global seconds at an exact approved paragraph Unicode boundary."""
        text=self.script[sid]['lines'][line-1];assert 0<=offset<=len(text)
        data=self.raw[sid]['lines'][line-1];count=len(self.normalize(text[:offset]))
        if end:
            assert count>0;local=data['characterEnds'][count-1]
        else:
            assert count<len(data['characterStarts']);local=data['characterStarts'][count]
        return self.scenes[sid]['startFrame']/FPS+local
    def frame(self,sid,line,offset,end=False): return round(self.word(sid,line,offset,end)*FPS)
    def literal(self,sid,line,literal,after=0,end=False):
        text=self.script[sid]['lines'][line-1];at=text.index(literal,after)
        return self.word(sid,line,at+len(literal) if end else at,end)

def make_captions():
    authorized();clock=Clock();design=read(H/'caption-plan.json')
    assert design['inputs']['koSha256']==sha(S/'part-01.ko.json')
    assert design['inputs']['enSha256']==sha(S/'part-01.en.json')
    geom=module('v7_approved_caption_geometry',P/'production/revision-v6/captions.py');geom.O=O
    caps=[];previous=0.;counts={};coverage=[]
    for row in design['cues']:
        sid,line=row['scene'],row['line'];key=(sid,line)
        text=clock.script[sid]['lines'][line-1];data=clock.raw[sid]['lines'][line-1]
        a,b=row['sourceKoOffset'],row['sourceKoEnd']
        assert text[a:b]==row['sourceKo']
        lo=len(clock.normalize(text[:a]));hi=len(clock.normalize(text[:b]))
        # Tokens cannot be split between clauses. Both direct substring and
        # whole-prefix normalization must describe the same source characters.
        assert hi-lo==len(clock.normalize(row['sourceKo'])),row['id']
        assert lo==counts.get(key,0) and 0<=lo<hi<=len(data['characterStarts'])
        begin=clock.word(sid,line,a);end=clock.word(sid,line,b,True)
        assert begin>=previous-0.02,(row['id'],begin,previous)
        begin=max(begin,previous);assert end-begin>=.04,(row['id'],'Needs actual word/context timing review')
        begin=round(begin,6);end=round(end,6)
        caps.append(dict(row,start=begin,end=end,startFrame=round(begin*FPS),endFrame=round(end*FPS),
            rawStart=begin-clock.scenes[sid]['startFrame']/FPS,rawEnd=end-clock.scenes[sid]['startFrame']/FPS,
            nativePixelReview='pending actual paired moving output',mobileMovingReview='pending'))
        counts[key]=hi;previous=end
    for sid,scene in clock.script.items():
        for i,text in enumerate(scene['lines'],1):
            assert counts[(sid,i)]==len(clock.normalize(text));coverage.append(dict(scene=sid,line=i,complete=True))
    assert len(caps)==386 and len(coverage)==135
    folder=O/'captions';folder.mkdir(parents=True,exist_ok=True)
    for language in ['ko','en']:
        srt='\n\n'.join(f'{i}\n{geom.timestamp(x["start"])} --> {geom.timestamp(x["end"])}\n'+ '\n'.join(x[language+'Lines']) for i,x in enumerate(caps,1))+'\n'
        (O/f'captions.{language}.srt').write_text(srt,encoding='utf8')
        geometry=geom.ass(caps,language);save(folder/f'geometry.{language}.json',geometry)
    result=dict(schemaVersion=1,revision='v7-part1',fps=FPS,sceneCount=21,paragraphCount=135,cueCount=len(caps),
        inputs=dict(captionPlanSha256=sha(H/'caption-plan.json'),timelineSha256=sha(H/'timeline.json'),
            alignmentSha256=sha(A/'source-alignment.json'),implementationSha256=sha(Path(__file__))),
        cues=caps,paragraphCoverage=coverage,identicalBilingualSemanticTimes=True,noSourceTextDeletion=True,
        pixelReview='pending actual encoded output',humanPaceListening='pending')
    save(folder/'captions.json',result)
    review=dict(schemaVersion=1,part=1,completeParagraphMapping=True,paragraphCount=135,cueCountKo=len(caps),cueCountEn=len(caps),
        captionsSha256=sha(folder/'captions.json'),timelineSha256=sha(H/'timeline.json'),
        koSrtSha256=sha(O/'captions.ko.srt'),enSrtSha256=sha(O/'captions.en.srt'),
        mapping=[dict(scene=x['scene'],line=x['line'],cueIds=[c['id'] for c in caps if c['scene']==x['scene'] and c['line']==x['line']],complete=True)for x in coverage],
        status='exact full bilingual paragraph coverage and measured raw-word clocks; final encoded pixel/motion review pending')
    save(folder/'caption-alignment-review.json',review)
    print(json.dumps(dict(cues=len(caps),paragraphs=len(coverage),lastCueEnd=previous,plainSrt=True)))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--timeline',action='store_true');ap.add_argument('--captions',action='store_true');args=ap.parse_args()
    if args.timeline:make_timeline()
    if args.captions:make_captions()
    if not(args.timeline or args.captions):ap.print_help()
if __name__=='__main__':main()
