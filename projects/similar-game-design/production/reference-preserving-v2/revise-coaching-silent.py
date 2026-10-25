"""Root-run CTA removal: prepare / render / verify. No TTS or Motion Canvas.

The original290.133s v4 files remain untouched. Prepare removes only cue105,
copies revised scripts, fades processed narration in the measured silent gap,
then runs the SAME original mix graph and one new AAC encode. Render copies
the old clean compressed video and encodes only the newly captioned video.
"""
from pathlib import Path
import argparse
import ast
import copy
import inspect
import json
import re
import numpy as np
import soundfile as sf
import audio_pipeline as audio
import video_pipeline as video

HERE=Path(__file__).resolve().parent
PROJECT=HERE.parents[1]
BASE_PLAN=HERE/'edit-plan-final-v4.json'
NEW_PLAN=HERE/'edit-plan-coaching-silent-v3.json'
NEW_SCRIPT=PROJECT/'script/coaching-silent-v3'
VARIANT='coaching-silent-v3'
STEM='similar-game-design-coaching-silent-v3'
RATE=48000
FADE_START=round(274.87*RATE)
MUTE_START=13194240
PREFIX_END=round(274.80*RATE)
CTA_KO='직접 구현하며 점검하고 싶다면, 설명란의 프로그래밍 코칭 안내를 확인해 주세요.'
CTA_EN='For help building and testing that experience, see the programming coaching information in the description.'


def text_write(file,text):
    file.parent.mkdir(parents=True,exist_ok=True)
    if file.exists() and file.read_text('utf-8-sig')!=text:
        raise ValueError('Preserve incompatible existing revision output: '+str(file))
    if not file.exists():file.write_text(text,'utf-8')


def json_write(file,value):
    text_write(file,json.dumps(value,ensure_ascii=False,indent=2)+'\n')


def locations():
    base=audio.read(BASE_PLAN)
    old=audio.current_local_output(base['outputDir'])
    new=audio.current_local_output(old/VARIANT)
    return base,old,new


def mix_graph():
    tree=ast.parse(inspect.getsource(audio.mix))
    items=[n for n in ast.walk(tree) if isinstance(n,ast.Assign)
        and any(isinstance(t,ast.Name) and t.id=='graph' for t in n.targets)]
    if len(items)!=1:raise ValueError('Re-review the current original mix graph')
    graph=ast.literal_eval(items[0].value)
    if 'normalize=0' not in graph or 'alimiter=limit=0.794' not in graph:
        raise ValueError('Original mix profile changed')
    return graph


def expected_stem(old):
    data,rate=sf.read(old/'narration-stem.wav',dtype='int32',always_2d=True)
    if rate!=RATE or data.shape!=(17408*800,2):raise ValueError('Expected exact current stereo48k narration stem')
    revised=data.copy()
    fade=np.linspace(1,0,MUTE_START-FADE_START,endpoint=True,dtype=np.float64)
    # PCM24 is left-aligned in int32. Quantize the480 fade samples once, while
    # keeping every pre-fade sample bit-identical and every later sample zero.
    revised[FADE_START:MUTE_START]=(np.rint((data[FADE_START:MUTE_START].astype(np.float64)/256)*fade[:,None]).astype(np.int32)<<8)
    revised[MUTE_START:]=0
    return data,revised


def prepare():
    base,old,new=locations();new.mkdir(parents=True,exist_ok=True)
    receipt_file=new/'prepare-receipt.json'
    inputs={'basePlan':audio.artifact(BASE_PLAN),'originalAudioBuild':audio.artifact(old/'audio-build.json'),
        'originalStem':audio.artifact(old/'narration-stem.wav'),'originalMix':audio.artifact(old/'final-mix.wav'),
        'musicStem':audio.artifact(old/'music-stem.wav'),'gameStem':audio.artifact(old/'game-stem.wav'),
        'oldClean':audio.artifact(old/(base['outputStem']+'-clean.mp4')),
        'originalCaptions':audio.artifact(old/'captions.json'),
        'fadeSamples':[FADE_START,MUTE_START],'mixGraph':mix_graph()}
    if receipt_file.exists():
        previous=audio.read(receipt_file)
        if previous['inputs']!=inputs:raise ValueError('Existing preparation uses different inputs')
        for record in previous['outputs']:
            if audio.sha(audio.repo_path(record['path']))!=record['sha256']:raise ValueError('Prepared output changed')
        print('Identical prepared revision reused');return
    scripts=[]
    for language in ['ko','en','spoken-ko']:
        src=PROJECT/'script/reference-preserving-v2'/('narration.'+language+'.json')
        doc=audio.read(src);last=doc['scenes'][-1]['lines'][-1]
        suffix=CTA_EN if language=='en' else CTA_KO
        if not last.endswith(suffix):raise ValueError('Exact final CTA suffix changed')
        doc['scenes'][-1]['lines'][-1]=last[:-len(suffix)].rstrip()
        dest=NEW_SCRIPT/src.name;json_write(dest,doc)
        scripts.append({'source':audio.artifact(src),'revised':audio.artifact(dest),'removed':suffix})
    aliases=PROJECT/'script/reference-preserving-v2/caption-aliases.json'
    text_write(NEW_SCRIPT/'caption-aliases.json',aliases.read_text('utf-8-sig'))
    spoken=audio.read(NEW_SCRIPT/'narration.spoken-ko.json')
    text_write(NEW_SCRIPT/'tts-input.ko.txt','\n\n'.join(' '.join(s['lines']) for s in spoken['scenes'])+'\n')
    captions=audio.read(old/'captions.json')
    if len(captions['cues'])!=105 or captions['cues'][-1]['cue']!=105 or captions['cues'][-1]['start']!=275.04:
        raise ValueError('Expected exactly the current final cue105')
    removed=copy.deepcopy(captions['cues'][-1]);captions['cues']=captions['cues'][:104]
    json_write(new/'captions.json',captions)
    layout=audio.read(old/'caption-layout.json');layout['rows']=layout['rows'][:104]
    json_write(new/'caption-layout.json',layout)
    alignment=audio.read(old/'caption-alignment.json')
    alignment.update(status='retained-cue-word-clock-preserved-explicit-cta-deletion',bilingualCueCount=104,
        explicitDeletion={'cue':105,'range':[275.04,280.10],'newAsrRun':False},
        alignmentMetricsScope='Original source alignment; only cue105 intentionally removed; retained cue clocks are unchanged.')
    for paragraph in alignment['paragraphs']:
        if 105 in paragraph['cues']:
            paragraph['cues']=[n for n in paragraph['cues'] if n!=105]
            paragraph.update(koFullContentRetained=False,enFullContentRetained=False,
                retainedCurrentScriptAllCaptionsPresent=True,intentionallyRemovedCueIds=[105])
    json_write(new/'caption-alignment.json',alignment)
    def ass_time(value):
        h,m,s=value.split(':');return int(h)*3600+int(m)*60+float(s)
    for language in ['ko','en']:
        blocks=re.split(r'\r?\n\s*\r?\n',(old/f'captions.{language}.srt').read_text('utf-8-sig').strip())
        if len(blocks)!=105:raise ValueError('Expected105 paired SRT cues')
        text_write(new/f'captions.{language}.srt','\n\n'.join(blocks[:104])+'\n')
        kept=[];count=0
        for line in (old/f'captions.{language}.ass').read_text('utf-8-sig').splitlines(keepends=True):
            fields=line.split(',',3)
            if line.startswith('Dialogue:') and abs(ass_time(fields[1])-275.04)<1e-6 and abs(ass_time(fields[2])-280.10)<1e-6:
                count+=1
            else:kept.append(line)
        if count<3:raise ValueError('Final cue ASS events were not found')
        text_write(new/f'captions.{language}.ass',''.join(kept))
    original,revised=expected_stem(old)
    stem=new/'narration-stem.wav'
    if stem.exists():raise ValueError('Preserve incomplete existing stem; use a distinct revision if retrying')
    sf.write(stem,revised,RATE,subtype='PCM_24')
    back,rate=sf.read(stem,dtype='int32',always_2d=True)
    if rate!=RATE or not np.array_equal(back,revised):raise ValueError('PCM24 edit failed exact sample proof')
    graph=mix_graph();duration=base['totalFrames']/60
    audio.run_ff(['-i',stem,'-i',old/'music-stem.wav','-i',old/'game-stem.wav',
        '-filter_complex',graph,'-map','[out]','-t',duration,'-ar',RATE,'-c:a','pcm_s24le',new/'final-mix.wav'],new/'mix.log')
    # Exactly the original AAC command, once from the new lossless WAV.
    audio.run_ff(['-i',new/'final-mix.wav','-c:a','aac','-b:a','192k',new/'final-mix.m4a'],new/'aac.log')
    plan=copy.deepcopy(base)
    plan.update(outputDir=audio.relative(new),outputStem=STEM,mixFile=audio.relative(new/'final-mix.wav'),
        captionsAss=audio.relative(new/'captions.ko.ass'),variant=VARIANT,
        status='explicit-cta-voice-and-cue105-removal-current-user-revision')
    plan['audioModification']={'basePlan':audio.artifact(BASE_PLAN),'originalSourcePcmPreserved':True,
        'sourceMp3AndSceneChunksModified':False,'sourceStem':inputs['originalStem'],
        'fadeSeconds':[274.87,274.88],'fadeSamples':[FADE_START,MUTE_START],
        'muteFromSample':MUTE_START,'muteFromSeconds':274.88,'prefixPcmCompareUntilSeconds':274.80,
        'actualAsrGapSeconds':[274.72,275.04],'removedCaption':removed,'newTts':False,
        'newScripts':[s['revised'] for s in scripts],'sameMixGraph':graph,
        'musicAndGameInputStemsUnchanged':True,'sidechainsRerunWithRevisedNarration':'Natural existing release; no new normalization/gain',
        'durationAndEndpageFramesUnchanged':True,'coachingLinkPagePreserved':True}
    json_write(NEW_PLAN,plan)
    outputs=[audio.artifact(new/name) for name in ['narration-stem.wav','final-mix.wav','final-mix.m4a',
        'captions.json','caption-layout.json','caption-alignment.json','captions.ko.ass','captions.en.ass','captions.ko.srt','captions.en.srt']]
    json_write(receipt_file,{'status':'prepared-new-audio-and104-cues','inputs':inputs,'outputs':outputs,
        'newPlan':audio.artifact(NEW_PLAN),'scriptTransforms':scripts,'newTts':False,'oldMediaModified':False,
        'wholeListening':'pending','fullLoudnessAndTruePeak':'root measurement pending'})
    print('Prepared104cues and explicit10ms-gap fade/mute; original media retained')


def render():
    base,old,new=locations();plan=audio.read(NEW_PLAN)
    receipt=audio.read(new/'prepare-receipt.json')
    for row in receipt['outputs']:
        if audio.sha(audio.repo_path(row['path']))!=row['sha256']:raise ValueError('Prepared input changed')
    clean=old/(base['outputStem']+'-clean.mp4');aac=new/'final-mix.m4a';ass=new/'captions.ko.ass'
    files=video.output_files(plan,new)
    if any(f.exists() for f in files.values()):raise ValueError('Preserve existing render outputs; do not overwrite')
    temporary={k:p.with_suffix('.partial.mp4') for k,p in files.items()}
    common=['-map','0:v:0','-map','1:a:0','-c:a','copy','-video_track_timescale','60000','-movflags','+faststart']
    audio.run_ff(['-i',clean,'-i',aac,*common,'-c:v','copy',temporary['clean']],new/'clean-remux.log')
    vf='setpts=N/(60*TB),settb=1/60000,setsar=1,format=yuv420p,ass='+video.filter_path(ass)
    audio.run_ff(['-reinit_filter','0','-i',clean,'-i',aac,'-map','0:v:0','-map','1:a:0',
        '-vf',vf,'-frames:v',plan['totalFrames'],*video.ENCODER,'-fps_mode','passthrough',
        '-c:a','copy','-movflags','+faststart',temporary['captioned']],new/'captioned-encode.log')
    for key,file in temporary.items():
        video.assert_video(file,plan['totalFrames']);file.replace(files[key])
    json_write(new/'render-receipt.json',{'sourceClean':audio.artifact(clean),'newAac':audio.artifact(aac),
        'newAss':audio.artifact(ass),'plan':audio.artifact(NEW_PLAN),
        'outputs':{k:audio.artifact(f) for k,f in files.items()},'cleanVideoStreamCopied':True,
        'captionedVideoEncodedOnce':True,'encoder':video.ENCODER,'motionCanvasOrTtsRun':False})
    print('Clean video copied; only captioned video encoded; both share the new AAC')


def verify():
    base,old,new=locations();plan=audio.read(NEW_PLAN)
    original,expected=expected_stem(old)
    stem,rate=sf.read(new/'narration-stem.wav',dtype='int32',always_2d=True)
    oldmix,_=sf.read(old/'final-mix.wav',dtype='int32',always_2d=True)
    newmix,mixrate=sf.read(new/'final-mix.wav',dtype='int32',always_2d=True)
    prefix=np.array_equal(oldmix[:PREFIX_END],newmix[:PREFIX_END])
    proof={'newStemExactlyExpected':rate==RATE and np.array_equal(stem,expected),
        'stemBefore274_87Exact':np.array_equal(original[:FADE_START],stem[:FADE_START]),
        'stemFrom274_88AllZero':bool(np.all(stem[MUTE_START:]==0)),
        'mixBefore274_80Exact':prefix,'mixSampleRate':mixrate,
        'mixSamples':len(newmix),'expectedMixSamples':17408*800,
        'memberAudioPcmExact':np.array_equal(oldmix[16808*800:],newmix[16808*800:]),
        'memberVisualsAndLinksPreserved':True,'humanListening':'pending'}
    if not prefix:
        changed=np.flatnonzero(np.any(oldmix[:PREFIX_END]!=newmix[:PREFIX_END],axis=1))
        proof['prefixDifferences']={'frames':len(changed),'firstSeconds':int(changed[0])/RATE,
            'maxPcm24Lsb':int(np.max(np.abs(oldmix[:PREFIX_END].astype(np.int64)-newmix[:PREFIX_END].astype(np.int64))))/256}
    audio.save(new/'pcm-revision-verification.json',proof)
    if not all(proof[k] for k in ['newStemExactlyExpected','stemBefore274_87Exact','stemFrom274_88AllZero','mixBefore274_80Exact']):
        raise ValueError('PCM preservation check failed; inspect recorded differences, no automatic repair')
    video.verify(plan,new)
    files=video.output_files(plan,new)
    old_video=video.stream_hash(old/(base['outputStem']+'-clean.mp4'),'0:v:0')
    new_video=video.stream_hash(files['clean'],'0:v:0')
    if old_video!=new_video:raise ValueError('Clean compressed video changed')
    aac_hash=video.stream_hash(new/'final-mix.m4a','0:a:0')
    if any(video.stream_hash(f,'0:a:0')!=aac_hash for f in files.values()):raise ValueError('Continuous AAC differs between outputs')
    proof.update(cleanCompressedVideoSha256=old_video,cleanCompressedVideoIdentical=True,
        sameContinuousAacInBothMasters=True,newAacPacketSha256=aac_hash,
        originalSourceMp3AndChunksModified=False,fullHumanListening='pending')
    audio.save(new/'revision-verification.json',proof)
    print('PCM prefix/mute, clean compressed video, full frame/PTS and shared AAC verification passed')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage',choices=['prepare','render','verify'])
    args=parser.parse_args();audio.require_authorized('explicit coaching CTA removal '+args.stage)
    {'prepare':prepare,'render':render,'verify':verify}[args.stage]()


if __name__=='__main__':main()
