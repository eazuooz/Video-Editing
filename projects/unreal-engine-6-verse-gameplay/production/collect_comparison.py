"""Collect the verified two-part edit without replacing the twelve-scene baseline."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import html
import json
import shutil
import subprocess
import soundfile as sf

P=Path(__file__).resolve().parents[1]
R=P.parents[1]
V1=P/'production/local/v1'
V2=P/'production/local/engine-comparison-v2'
S2=P/'script/engine-comparison-v2'
TITLE='블루프린트가 사라지면 언리얼을 왜 쓸까? | 언리얼 6·고도·유니티 비교'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def rel(path):
    return path.relative_to(R).as_posix()


def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f,'sha256').hexdigest()


def main():
    verification=read(V2/'encoded-verification.json')
    voice_review=read(V2/'encoded-audio-readback.json')
    plan=read(V2/'timeline.json')
    notes=read(V2/'direct-review-notes.json')
    base_plan=read(V1/'timeline.json')
    base_cues=read(V1/'cue-review.json')
    all_cues=read(V2/'cue-review.json')
    assert plan['scenes'][:12]==base_plan['scenes'] and all_cues[:len(base_cues)]==base_cues
    import os
    os.environ["UE6_EDITION"]="engine-comparison-v2"
    from edition import sealed_voice_batch
    initial=sealed_voice_batch(V1/'voice','narration',[f'{i:02}' for i in range(1,13)])
    final=sealed_voice_batch(V2/'voice','comparison',[str(i) for i in range(13,18)])
    assert initial and final and final==plan['sealedPrimaryTakes']
    assert len(plan['scenes'])==17 and len(voice_review['scenes'])==17 and voice_review['complete']
    assert voice_review['aacContainerSha256']==sha(V2/'audio.m4a')
    assert verification['allCuePixelSamples']==len(all_cues)
    selected_timeline=P/'production/engine-comparison-v2-timeline.json'
    shutil.copyfile(V2/'timeline.json',selected_timeline)
    assert sha(selected_timeline)==sha(V2/'timeline.json')
    assert notes['captionedSha256']==verification['masters']['captioned']['sha256']
    assert notes['allCuesInspected']==len(all_cues)
    for label in ['clean','captioned']:
        assert verification['masters'][label]['sha256']==sha(V2/f'{label}.mp4')
    capture_start=2+plan['scenes'][12]['startFrame']/60
    first_cue=next(c for c in all_cues if c['scene']=='13')
    chapters=[dict(id=s['id'],title=s['title'],startSeconds=2+s['startFrame']/60,
                   voicePlacementSeconds=2+s['voiceStart']) for s in plan['scenes']]
    # Populate the default complete-project cache with ordinary copies so an
    # explicit future retake can never mutate the preserved source revision.
    full_voice=V2/'voice-complete'
    (full_voice/'chunks').mkdir(parents=True,exist_ok=True)
    (full_voice/'asr').mkdir(exist_ok=True)
    import numpy as np
    cursor=0
    with sf.SoundFile(full_voice/'narration.wav','w',samplerate=24000,channels=1,subtype='PCM_16') as joined:
        for s in plan['scenes']:
            raw=(V1 if int(s['id'])<=12 else V2)/'voice'
            for name in [f"chunks/{s['id']}-scene.wav",f"asr/{s['id']}.json"]:
                target=full_voice/name
                if not target.exists():shutil.copyfile(raw/name,target)
                assert sha(target)==sha(raw/name)
            samples,rate=sf.read(raw/f"chunks/{s['id']}-scene.wav",dtype='int16')
            start=round(s['voiceStart']*24000)
            assert start>=cursor and rate==24000
            joined.write(np.zeros(start-cursor,dtype=np.int16))
            joined.write(samples);cursor=start+len(samples)
    for lang in ['ko','en','spoken-ko']:
        rows=read(P/f'script/narration.{lang}.json')['scenes']+read(S2/f'narration.{lang}.json')['scenes']
        assert [r['id'] for r in rows]==[f'{n:02}' for n in range(1,18)]
        save(S2/f'complete.{lang}.json',{'scenes':rows})
    # Keep the generation manifests valid for their respective scene ranges.
    # The complete script, edit timeline and two original stores remain explicit.
    project=read(P/'project.json')
    project.update(revision='engine-comparison-v2',title=TITLE,status='local-delivery-user-review-pending',
                   humanFinalReview=False,publishReady=False,platformStatus='local-only')
    project.setdefault('titles',{})['ko']=TITLE
    project['paths'].update(script=rel(S2/'complete.spoken-ko.json'),scriptEn=rel(S2/'complete.en.json'),
        scriptKo=rel(S2/'complete.ko.json'),narrationScriptReview=rel(S2/'전체대본.md'),
        timeline=rel(selected_timeline),audioMix=rel(V2/'final-mix.wav'),narration=rel(full_voice/'narration.wav'),
        videoClean=rel(V2/'clean.mp4'),videoBurnedCaptions=rel(V2/'captioned.mp4'),
        captionsKo=rel(V2/'captions.ko.srt'),captionsEn=rel(V2/'captions.en.srt'))
    project['delivery']={'localStorageRoot':rel(V2/'delivery')}
    project['narrationSources']=[{'scenes':'01–12','folder':rel(V1/'voice/chunks'),'reuse':'original PCM'},
        {'scenes':'13–17','folder':rel(V2/'voice/chunks'),'ttsManifest':rel(P/'production/engine-comparison-v2-voice.json')}]
    # Default whole-version rebuild is isolated from both stores above.
    project['tts'].update(outputDir=rel(V2/'voice-complete'),filenameStem='narration')
    project['finalRender']={'status':'local-final-review','openItems':notes['userListeningNotes']}
    save(P/'project.json',project)
    subprocess.run(['node',str(R/'scripts/collect-video-output.cjs'),P.name],cwd=R,check=True)
    directory=V2/'delivery/output'/P.name
    index=directory/'index.html'
    shutil.copyfile(P/'publishing/sources.txt',directory/'sources.txt')
    assert sha(P/'publishing/sources.txt')==sha(directory/'sources.txt')
    page=index.read_text(encoding='utf-8')
    cue_link=f'<p><a href="{P.name}.captioned.mp4#t={capture_start:.3f}">4분 57초부터 언리얼·고도·유니티 비교 보기</a></p>'
    page=page.replace('</h1>','</h1>'+cue_link,1)
    sources=[]
    for line in (P/'publishing/sources.txt').read_text(encoding='utf-8').splitlines()[1:]:
        escaped=html.escape(line)
        sources.append(f'<a href="{escaped}">{escaped}</a>' if line.startswith('https://') else escaped)
    page+='\n<details><summary>자료·음악 출처</summary><p><a href="sources.txt">출처 원문 열기</a></p><p>'+'<br>'.join(sources)+'</p></details>\n'
    index.write_text(page,encoding='utf-8')
    report=read(P/'production/delivery-output.json')
    for row in report['files']:
        assert sha(directory/row['name'])==row['sha256']
    ledger={'episode':P.name,'revision':'engine-comparison-v2','title':TITLE,
        'status':'local-delivery-user-review-pending','createdAt':datetime.now(timezone.utc).isoformat(),
        'directory':rel(directory),'reviewIndex':rel(directory/'index.html'),
        'captioned':rel(directory/f'{P.name}.captioned.mp4'),
        'masterSha256':verification['masters']['captioned']['sha256'],'files':report['files'],
        'totalFrames':plan['totalFrames'],'durationSeconds':plan['totalFrames']/60,
        'format':'1920x1080 60 fps','bilingualCueCount':len(all_cues),
        'comparisonPictureStart':capture_start,'comparisonVoiceStart':2+plan['scenes'][12]['voiceStart'],
        'comparisonFirstCaptionStart':first_cue['start'],'chapters':chapters,
        'currentPricingAsOf':'2026-11-05','pricingEvidence':rel(P/'planning/engine-comparison-v2.json'),
        'editDecisionList':rel(selected_timeline),'editDecisionListSha256':sha(selected_timeline),
        'researchAndSourceMapping':rel(P/'planning/sources.json'),
        'descriptionSources':rel(P/'publishing/sources.txt'),
        'audioChecks':{'integratedLufs':verification['audioMeasurement']['input_i'],
            'truePeakDbtp':verification['audioMeasurement']['input_tp'],
            'sourcePcmAndBgmPrefix':read(V2/'retained-prefix.json'),
            'sourcePcmAsr':'12 original scenes + 5 new scenes each hash-bound',
            'encodedReadback':rel(V2/'encoded-audio-readback.json'),
            'exactDecodedAsrReuses':sum(bool(s.get('reusedExactDecodedBaseline')) for s in voice_review['scenes']),
            'continuity':rel(V2/'encoded-level-continuity.json'),'technicalVerification':rel(V2/'encoded-verification.json')},
        'scope':'Local final review only','userReviewedThisHash':False,'wholeHumanListening':False,
        'manualReview':notes,'platformMutation':False}
    save(P/'production/checkpoint.json',ledger)
    print(json.dumps({k:ledger[k] for k in ['directory','captioned','masterSha256','durationSeconds','bilingualCueCount','comparisonPictureStart','comparisonFirstCaptionStart']},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
