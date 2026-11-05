"""Check both A01 masters and package the new review beside the preserved first version."""
from edit import H,P,R,L,B,read,save,rel,sha,ff
from datetime import datetime,timezone
from pathlib import Path
import subprocess,shutil,sys,re,difflib,os
REV='unreal-kit-v2'
GRANT='animation-assigning-unreal-kit-v2'
OLD=P/'production/grid-v1'
def scripts():
    for lang in ('ko','en','spoken-ko'):
        base=read(P/'script/grid-v1'/f'narration.{lang}.json')
        additions=read(H/f"added.{'en' if lang=='en' else 'ko'}.json")['scenes']
        rows={s['id']:s['lines'] for s in base['scenes']}
        rows['01'].append(additions[0]['lines'][0])
        rows['03'][1]=additions[1]['lines'][0]
        rows['06'].insert(1,additions[2]['lines'][0])
        rows['07'].insert(1,additions[3]['lines'][0])
        base.update(revision=REV,timingLocked=True,status='final-review-script')
        if lang=='en':base['sourceKoSha256']=sha(H/'final.ko.json')
        save(H/f'final.{lang}.json',base)
def readback():
    # Use the existing full-audio recognizer with its output guard relocated
    # to this revision. Reference timestamps and words are never fed to ASR.
    sys.path.insert(0,str(OLD))
    import storage_paths as storage
    storage.LOCAL=L;storage.HERE=H
    import audio_pipeline as analysis
    analysis.LOCAL=L
    os.environ['VIDEO_BATCH_ASR_DEVICE']='cpu'
    ff(['-i',L/'audio.m4a','-ac','1','-ar','16000','-c:a','pcm_s16le',L/'check-aac.wav'],'decode-aac')
    asr=analysis.full_asr(L/'check-aac.wav',L/'encoded-asr.json',final=True)
    assert asr['completeAudioSubmitted'] and asr['noExpectedPrompt']
    def normalize(text):
        word=re.sub(r'\s+','',text.lower())
        for src,dst in [('버추어','버추얼'),('예순','60'),('열두','12'),('열둘','12'),('영점이','02')]:word=word.replace(src,dst)
        return re.sub('[^가-힣a-z0-9]','',word)
    expected=normalize(' '.join(p for s in read(H/'final.spoken-ko.json')['scenes'] for p in s['lines']))
    heard=normalize(asr['text']);m=difflib.SequenceMatcher(None,expected,heard,autojunk=False)
    save(L/'readback-review.json',{'coverage':sum(b.size for b in m.get_matching_blocks())/len(expected),
         'differences':[(expected[i:j],heard[k:l]) for z,i,j,k,l in m.get_opcodes() if z!='equal'],
         'audioSha256':sha(L/'audio.m4a'),'completeAudioSubmitted':True,'humanListening':False})
def verify():
    import importlib.util
    helper=R/'projects/unreal-engine-6-verse-gameplay/production'
    sys.path.insert(0,str(helper))
    spec=importlib.util.spec_from_file_location('master_checks',helper/'finish.py')
    checks=importlib.util.module_from_spec(spec);spec.loader.exec_module(checks);checks.L=L
    save(L/'cue-review.json',read(L/'captions.json')['cues'])
    checks.verify(read(L/'timeline.json'))
    def packet(file):
        return subprocess.check_output(['ffmpeg','-v','error','-i',file,'-map','0:a','-c','copy','-f','hash','-hash','sha256','-']).decode().strip()
    v=read(L/'encoded-verification.json')
    assert packet(L/'audio.m4a')==v['masters']['captioned']['audio']
def collect():
    v=read(L/'encoded-verification.json');readback_report=read(L/'readback-review.json')
    assert v['masters']['captioned']['sha256']==sha(L/'captioned.mp4') and readback_report['completeAudioSubmitted']
    plan=read(L/'timeline.json');old=read(OLD/'edit-plan.json')
    gameIds={cut['id'] for cut in old['cuts'] if cut['kind']=='independent-gameplay'}
    actual=sum(s['frames'] for s in plan['segments'] if s.get('cut') in gameIds)
    assert actual==sum(c['frames'] for c in old['cuts'] if c['kind']=='independent-gameplay')
    oldLedger=read(OLD/'checkpoint.json')
    original=B/'delivery/output'/P.name/(P.name+'.captioned.mp4')
    assert sha(original)==oldLedger['captionedMasterSha256']
    official='https://dev.epicgames.com/documentation/en-us/unreal-engine/game-animation-sample-project-in-unreal-engine'
    oldCredits=(P/'publishing/studio-grid-v1/description.ko.txt').read_text('utf-8-sig').split('영상·음악 출처')[-1].strip().splitlines()
    credit='영상·음악 출처\n'+'\n'.join(line for line in oldCredits if 'RG Poly' not in line)+'\nEpic Games · Game Animation Sample · 언리얼 엔진에서 직접 촬영 — '+official+'\n'
    (H/'sources.txt').write_text(credit,encoding='utf-8')
    native={}
    for key in read(H/'stage-plan.json')['stages']:
        build=read(L/'unreal'/f'{key}-build.json')
        plate=L/'unreal'/(key+('-final.mp4' if key in ('stop','turn') else '-inplace.mp4'))
        native[key]={'level':build['level'],'sequence':build['sequence'],'movieRenderQueue':build['captureConfig'],'samples':build['sourceAnimation'],'engine':'5.8','frames':build['frames'],'resolution':build['resolution'],'fps':60,'captureSha256':sha(plate)}
        if key=='turn':native[key]['motionWindow']='0.45–2.45s of each original clip; root yaw sampled from the original at 60 Hz and applied to a centered mannequin.'
        if key=='stop':native[key]['motionWindow']='Last two seconds of each original foot-specific stop, ending on its settled pose.'
    extra=[dict(s) for s in plan['segments'] if s['kind']=='added']
    project=read(P/'project.json');project.update(revision=REV,status='local-delivery-user-review-pending',publishReady=False)
    project['paths'].update(script=rel(H/'final.spoken-ko.json'),scriptKo=rel(H/'final.ko.json'),scriptEn=rel(H/'final.en.json'),narrationKo=rel(H/'final.ko.json'),videoClean=rel(L/'clean.mp4'),videoBurnedCaptions=rel(L/'captioned.mp4'),captionsKo=rel(L/'captions.ko.srt'),captionsEn=rel(L/'captions.en.srt'),audioMix=rel(L/'final-mix.wav'),timeline=rel(H/'edit-plan-final.json'),checkpoint=rel(H/'checkpoint.json'))
    project['editing'].update(measuredBodyGameplayShare=actual/plan['bodyFrames'],measuredBodyExplanationShare=1-actual/plan['bodyFrames'],ratioChoiceRecord=rel(H/'edit-plan-final.json'),visualStyle='Game Animation Sample comparison stage and retained independent game footage')
    project['voice']['revisionAdditions']={'provider':'local Qwen3-TTS 1.7B Base','ownVoice':True,'manifest':rel(H/'tts-manifest.json'),'passages':4,'preservedOriginalMix':True}
    project['delivery'].update(localStorageRoot=rel(L/'delivery'),directory=rel(L/'delivery/output'/P.name),manifest=rel(L/'delivery/output'/P.name/'delivery-manifest.json'),captionedMasterSha256=sha(L/'captioned.mp4'))
    project['youtube']={'authorized':False,'state':'new-version-local-review-pending','previousUploadPreparation':rel(P/'publishing/studio-grid-v1/upload.json')}
    project['review']={'actualUserViewed':False,'humanWholeListening':'pending','baseline':rel(OLD/'checkpoint.json')}
    project['titles']={'ko':project['title'],'en':read(H/'final.en.json')['title']}
    strike=R/'projects/animation-exaggeration/production/local/fighters-v4-kula-lili/unreal/renders/A02-E004'
    strike_reference={'source':rel(strike),'classification':'our previously rendered Unreal explanation','firstFrameSha256':sha(strike/'000000.png'),'lastFrameSha256':sha(sorted(strike.glob('*.png'))[-1]),'teachingRole':'Arms and torso during the example attack; the labeled 12-frame interval is an authored example.'}
    save(H/'edit-plan-final.json',dict(plan,independentGameFrames=actual,gameplayShare=actual/plan['bodyFrames'],baseline=rel(OLD/'edit-plan.json'),baselinePolicy=rel(OLD/'editorial-ratio-choice.json'),ratioReason='The user selected a deeper authored Unreal demonstration. All existing independent game shots remain at native speed. The measured difference is the added explanation.',nativeStages=native,reusedAttackStudy=strike_reference,originalGameSourceRecords=rel(OLD/'edit-plan.json')))
    save(P/'project.json',project);subprocess.run(['node','scripts/collect-video-output.cjs',P.name],cwd=R,check=True)
    dest=L/'delivery/output'/P.name;report=read(P/'production/delivery-output.json')
    assert all(sha(dest/f['name'])==f['sha256'] for f in report['files'])
    save(dest/'delivery-manifest.json',report);shutil.copyfile(H/'sources.txt',dest/'sources.txt')
    labels=['서서 걷기와 웅크려 걷기','같은 첫발을 두 방향에서','멈추기 직전의 발','90도 방향 전환']
    anchors=' · '.join(f'<a href="{P.name}.captioned.mp4#t={s["start"]/60:.2f}">{label}</a>' for label,s in zip(labels,extra))
    index=dest/'index.html';index.write_text(index.read_text('utf-8').replace('</h1>','</h1><p>'+anchors+'</p><p><a href="sources.txt">영상·음악 출처</a></p>',1),encoding='utf-8')
    ledger={'episode':'A01','revision':REV,'status':project['status'],'checkedAt':datetime.now(timezone.utc).isoformat(),'title':project['title'],'captionedMasterSha256':sha(dest/(P.name+'.captioned.mp4')),'durationSeconds':plan['totalFrames']/60,'directory':rel(dest),'files':report['files'],'bilingualCues':report['cueCounts'],'baselineHash':oldLedger['captionedMasterSha256'],'retainedSourceMix':rel(B/'edit/final-mix.wav'),'gameplayShare':actual/plan['bodyFrames'],'nativeStages':native,'additions':extra,'technicalQA':v,'wholeAACReadback':readback_report,'humanReviewedThisHash':False,'youtubeMutation':False}
    save(H/'checkpoint.json',ledger)
if __name__=='__main__':
    assert read(R/'shared/publishing/video-production-control.json')['scopedProductionAuthorizations'][GRANT]['renderAuthorized']
    {'scripts':scripts,'listen':readback,'verify':verify,'collect':collect}[sys.argv[1]]()
