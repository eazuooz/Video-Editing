"""Bind seven sections to real PCM/caption words; prepare only the reviewed4s source.

--check is read-only and permitted for this authorized finite batch member.
No extraction, FFmpeg, server, model or rendering occurs on import/--check.
"""
from pathlib import Path
import argparse, hashlib, json, math, re, subprocess
from audio_revision import P, R, LOCAL, VOICE, REVISION, CAPTION_CLAUSES, read, sha
from visual_revision import (IDS, SOURCE_START, SOURCE_END, SOURCE_SHA256,
                             static_guard, execution_guard, selected_source)


def write(path, value):
    path=Path(path); data=json.dumps(value,ensure_ascii=False,indent=2)+'\n'
    if path.exists() and path.read_text(encoding='utf8')!=data:
        archive=LOCAL/'actual-visuals/previous';archive.mkdir(parents=True,exist_ok=True)
        target=archive/(path.stem+'-'+sha(path)[:16]+path.suffix)
        if not target.exists():target.write_bytes(path.read_bytes())
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(data,encoding='utf8')


def run(args):
    execution_guard()
    result=subprocess.run(args,cwd=R,capture_output=True)
    if result.returncode:raise RuntimeError(result.stderr.decode(errors='replace')[-4000:])
    return result.stdout


def build_sections_and_events(captions, pcm, config, canonical, derived):
    """Pure time-binding function; receives existing evidence, never invents final PCM."""
    cues=captions['cues'];entries=sorted(pcm['entries'],key=lambda e:e['lineIndex'])
    if (len(entries)!=len(IDS) or [e['lineIndex'] for e in entries]!=list(range(len(IDS)))
            or [c['id'] for c in cues]!=[c['id'] for c in derived]
            or captions['fps']!=60
            or captions['frames']!=math.ceil((pcm['duration_seconds']+.6)*60-1e-8)):
        raise RuntimeError('Real paragraph/caption ownership, frame count or derived-cue coverage differs.')
    bounds=[0]
    for index,entry in enumerate(entries[1:],1):
        previous_end=max(c['endFrame'] for c in cues if c['lineIndex']==index-1)
        first=min(c['startFrame'] for c in cues if c['lineIndex']==index)
        if previous_end>first:raise RuntimeError('Adjacent actual caption paragraphs overlap.')
        candidate=math.floor((entry['start']+.2)*60+.5)
        bounds.append(max(previous_end,min(first,candidate)))
    bounds.append(captions['frames'])
    if bounds[1]<240:raise RuntimeError('Natural opening is shorter than inspected4s action; review picture continuity, do not pad/slow voice.')
    sections=[]
    for index,section_id in enumerate(IDS):
        a,b=bounds[index:index+2]
        if not a<b:raise RuntimeError('Empty teaching section.')
        sections.append(dict(id=section_id,kind='mixed' if section_id=='game' else 'diagram',
            startFrame=a,endFrame=b,start=a/60,end=b/60,forceDiagram=section_id!='game'))
    anchors={c['id']:{k:c[k] for k in ['startFrame','endFrame','start','end']} for c in cues}
    events={key:dict(value) for key,value in anchors.items()}
    canonical_map={c['id']:c for c in canonical}
    def members(original_id):
        original=canonical_map[original_id]
        found=[c for c in cues if (c['id']==original_id or re.fullmatch(re.escape(original_id)+r'[a-z]+',c['id']))
               and c['lineIndex']==original['lineIndex']]
        normalize=lambda s:re.sub(r'\s+','',s)
        if normalize(''.join(c['spoken'] for c in found))!=normalize(original['spoken']):
            raise RuntimeError('Derived semantic-cue expansion changed spoken text: '+original_id)
        return found
    def span(found):
        a=min(c['startFrame'] for c in found);b=max(c['endFrame'] for c in found)
        return dict(startFrame=a,endFrame=b,start=a/60,end=b/60,
                    cueIds=[c['id'] for c in found],timingBasis='actual-ASR-word-edges-and-PCM')
    for original_id in canonical_map:
        events[original_id]=span(members(original_id))
    for name,original_ids in config['eventCues'].items():
        found=[]
        for original_id in original_ids:found.extend(members(original_id))
        events[name]=span(found)
    if 'p7-2b' not in events['conclusion']['cueIds']:
        raise RuntimeError('Conclusion must include the preserved split sentence ending.')
    return sections,anchors,events


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args(argv)
    static_guard(require_current_selection=not args.check)
    source,source_record=selected_source()
    if args.check:
        print(json.dumps({'revision':REVISION,'inputGuard':'passed','sourceSHA256':SOURCE_SHA256,
                          'selectedNativeSeconds':4,'sourceAudioAdopted':False,
                          'actualPcmPresent':VOICE.is_file(),'extractionStarted':False}));return
    execution_guard()
    captions=read(P/'script/captions.json');pcm=read(VOICE.with_suffix('.timing.json'));config=read(P/'production/visual-config.json')
    derived=read(CAPTION_CLAUSES)['clauses'];canonical=read(P/'script/clauses.json')['clauses']
    if (captions['timingInputs']['voiceSha256']!=sha(VOICE)
            or captions['timingInputs']['clausesSha256']!=sha(CAPTION_CLAUSES)
            or pcm.get('voiceSha256')!=sha(VOICE)):
        raise RuntimeError('Current PCM, paragraph timing and strict captions are not the same version.')
    sections,anchors,events=build_sections_and_events(captions,pcm,config,canonical,derived)
    probe=json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(source)]))
    stream=next(s for s in probe['streams'] if s['codec_type']=='video')
    if (stream['width'],stream['height'],stream['avg_frame_rate'])!=(1920,1080,'60/1') or float(probe['format']['duration'])<SOURCE_END:
        raise RuntimeError('Inspected original1920x1080/60 source required.')
    count=240;out=LOCAL/'frames/game';receipt=out/'capture.json'
    recipe=dict(sourceSHA256=SOURCE_SHA256,sourceStart=SOURCE_START,sourceEnd=SOURCE_END,frames=count,fps=60,
                nativeDimensions=[1920,1080],rate=1,sourceAudioAdopted=False,
                quantization='Requested source timestamps;FFmpeg60fps decode uses available source-frame boundaries, without slowing/holding/looping.')
    if receipt.exists():
        prior=read(receipt);files=sorted(out.glob('*.jpg'))
        if prior.get('recipe')!=recipe or len(files)!=count or len(prior.get('artifacts',[]))!=count:
            raise RuntimeError('Preserve differing extraction receipt.')
        for file,artifact in zip(files,prior['artifacts']):
            if file.name!=artifact['name'] or sha(file)!=artifact['sha256']:
                raise RuntimeError('Previously extracted source frame changed.')
    else:
        if list(out.glob('*.jpg')):raise RuntimeError('Preserve unreceipted prior frames.')
        execution_guard();out.mkdir(parents=True,exist_ok=True)
        run(['ffmpeg','-v','error','-n','-threads','2','-ss',str(SOURCE_START),'-i',str(source),'-an',
             '-vf','fps=60','-frames:v',str(count),'-q:v','3','-threads','1','-start_number','0',str(out/'%06d.jpg')])
        files=sorted(out.glob('*.jpg'))
        if len(files)!=count:raise RuntimeError('Source extraction incomplete; preserve for inspection.')
        write(receipt,dict(recipe=recipe,artifacts=[{'name':f.name,'sha256':sha(f)} for f in files]))
    native=[dict(id='game',kind='game',source='game-master',start=0,end=4,startFrame=0,endFrame=240,
                 sourceStart=SOURCE_START,sourceEnd=SOURCE_END,rate=1,nativeAudioAdopted=False)]
    timing=dict(revision=REVISION,previewOnly=False,fps=60,frames=captions['frames'],durationSeconds=captions['durationSeconds'],
        voiceOffsetSeconds=.2,sections=sections,nativeSegments=native,cueAnchors=anchors,events=events,
        timingInputs=dict(voiceSha256=sha(VOICE),canonicalClausesSha256=sha(P/'script/clauses.json'),
                          productionClausesSha256=sha(CAPTION_CLAUSES),captionTimingSha256=sha(P/'script/captions.json')),
        sources={'game-master':dict(path=str(source),sourceSHA256=SOURCE_SHA256,originalOffsetSeconds=0,
            nativeAudioAdopted=False,sourceAudioAdopted=False,nativeDimensions=[1920,1080],
            sourceKind='official-independent-gameplay-development-demo')},
        preparedFrames=[dict(id='game',receipt=str(receipt.resolve()),frames=count)],actualGameSeconds=4,
        note='Seven continuous actual-PCM teaching sections.Only first4s is native officialspray; remaining firstparagraph becomes indexdiagram.No sourcefreeze/loop/slowdown.')
    config.update(sourceGameMaster=str(source),sourceSHA256=SOURCE_SHA256,
        cuts={'game':dict(inSeconds=SOURCE_START,maxDuration=4,frameDirectory='game',firstFrame=0,digits=6)},
        framesPrepared=True,footageReady=True,productionRenderReady=True,
        frameRoot='/@fs/D:/Github/VideoEditing/projects/shorts-teardown-spray-palette/production/local/frames/',
        status='actual-PCM-bound; sourceframesprepared; encodedvisualQA-pending')
    execution_guard();write(P/'production/visual-config.json',config)
    write(P/'production/visual-timing.json',timing);write(LOCAL/'visual-timing.json',timing)
    from visual_revision import actual_inputs
    actual_inputs()
    print(json.dumps({'frames':captions['frames'],'seconds':captions['durationSeconds'],
                      'nativeSeconds':4,'teachingSections':len(sections),'cueAnchors':len(anchors),
                      'conclusionEndFrame':events['conclusion']['endFrame']}))


if __name__=='__main__':main()
