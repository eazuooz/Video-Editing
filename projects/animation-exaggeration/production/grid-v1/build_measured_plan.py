"""Bind A02's unchanged narration to explicit, editable visual teaching cues.

Creates a measured proposal and native profile book in this revision only.
Does not import Unity profiles, render, change audio, or authorize publication.
"""
from pathlib import Path
import copy, math
import audio_pipeline as ap
import video_pipeline as vp
H=Path(__file__).resolve().parent
R=H.parents[3]
L=H.parent/'local/grid-v1'

def main():
    ap.require_authorized('caption-input')
    plan=ap.read(H/'caption-timing-plan.json')
    source_plan=ap.read(H.parents[1]/'planning/production-plan.json')
    source_rows={r['key']:r for r in source_plan['primaryGameExamples']}
    windows={r['id']:r for r in source_plan['reviewedNativeWindows']}
    proposal=ap.read(H/'source-callout-proposal.json')
    stills={r['sourceFrame']:r for r in proposal['stillChoices']}
    captions=ap.read(L/'edit/captions.json')['cues']
    C={r['cue']:r for r in captions}
    def F(t):return round(t*60)
    def cue(n):return C[n]['start']
    scene_map={s['id']:s for s in plan['scenes']}
    cuts=[];profiles=[];specs=[]
    cursor=120
    def base(scene,end,purpose,key=None):
        nonlocal cursor
        end=F(end);key=key or f'A02-E{sum(not c["id"].endswith("B") for c in cuts)+1:03d}'
        assert end>cursor,(key,cursor,end)
        c={'id':key,'scene':scene,'startFrame':cursor,'endFrame':end,'frames':end-cursor,
           'teachingPurpose':purpose,'playbackSpeed':1,'loop':False,'marks':[],
           'captionProtectedRect':vp.CAPTION_RECT,
           'speechCues':[r['cue'] for r in captions if r['start']<end/60 and r['end']>cursor/60]}
        cuts.append(c);cursor=end;return c
    def actual(scene,window,purpose):
        w=windows[window];s=source_rows[w['sourceKey']];t=s['technical']
        c=base(scene,cursor/60+w['nativeFrames']/60,purpose)
        c.update(kind='independent-gameplay',source=w['sourceKey'],sourceFile=t['fullMediaPath'],
                 sourceSha256=t['fullMediaSha256'],sourceUrl=s['url'],sourceStart=w['sourceInSeconds'],
                 sourceEndExclusive=w['sourceOutSecondsExclusive'],sourceNativeFps=60,
                 sourceVideoDimensions=[1920,1080],sourceAttribution={'publisher':s['publisher'],'url':s['url'],'game':s['game']},
                 viewport=[160,0,1600,900],gameLabel=s['game'],pictureLabel='실제 게임 영상',
                 sourceNativeCutsInside=[],sourceAudioEnabled=True,rights=s['rights'],rightsFinalized=False,
                 sourceAudioDecision='Retain original action track in this short analytical local review; no extracted music or claimed recorder licence. Final contextual listening pending.',
                 observedBefore=w['before'],observedAction=w['action'],observedResult=w['result'],
                 annotationReason='Native motion remains clear; pose/shape callouts follow on the inspected explanatory still. No invented rig measurement.',
                 sourceWindow=window)
        return c
    def still(scene,end,frame,purpose,output_revision='stills-v1'):
        s=stills[frame];c=base(scene,end,purpose);out=L/output_revision/c['id']
        spec={'id':c['id'],'frames':c['frames'],'sourceFile':s['sourceFile'],'sourceSha256':s['sourceSha256'],
              'frameTimeSeconds':s['frameTimeSeconds'],'crop':s['crop'],'viewport':s['viewport'],
              'title':s['title'],'contextLabel':s['contextLabel'],'outputDir':ap.relative(out),
              'resampling':'nearest' if frame in [179,181] else 'lanczos',
              'sourceFrameEvidence':s['decodedFrame'],'cropReview':s['purpose']}
        specs.append(spec)
        c.update(kind='explanation',renderer='inspected source-frame composition',explanationMode='source-frame-analysis',
                 sourceKind='labelled actual-game frame analysis',sourceFile=s['sourceFile'],sourceSha256=s['sourceSha256'],
                 sourceStart=s['frameTimeSeconds'],sourceStillTimestamp=s['frameTimeSeconds'],
                 renderedSource=ap.relative(out/'explanation.mp4'),renderedSourceSha256=None,renderedStartFrame=0,
                 explanationRender={'kind':'annotated-still','status':'pending'},sourceFrameEvidence=s['decodedFrame'])
        for i,mark in enumerate(s['marks']):
            m={k:copy.deepcopy(mark[k]) for k in ['shape','x','y','w','h','points','label','labelPosition','color','thickness'] if k in mark}
            m.update(id=f'{c["id"]}-mark{i+1}',t0=.1,t1=max(.2,c['frames']/60-.1),revealSeconds=.2)
            c['marks'].append(m)
        return c
    def native(scene,end,mode,purpose,phases,key=None):
        c=base(scene,end,purpose,key);start=c['startFrame'];last=0;rows=[];prior=-1
        for i,p in enumerate(phases):
            phase,absolute,motion_at,motion_duration,*reason=p
            begin=0 if i==0 else F(absolute)-start
            finish=c['frames'] if i==len(phases)-1 else F(phases[i+1][1])-start
            assert begin==last and finish>begin,(c['id'],begin,finish,last)
            motion=max(0,F(motion_at)-start-begin) if motion_at is not None else 0
            duration=F(motion_duration)/60
            assert motion/60+duration<=(finish-begin)/60+.0001,(c['id'],phase,motion,duration,finish-begin)
            row={'phase':phase,'start':begin/60,'end':finish/60,'motionStart':motion/60,'motionDuration':duration}
            if phase==prior:
                assert reason and reason[0];row['replayReason']=reason[0]
            if mode in ['normal-and-pause','size-amplitude','paused-pose-context']:
                row['holdNativeAt']='peak'
                row['holdReason']='After the complete native one-shot, display the explicitly labelled analysed pose while its narrated distinction is explained.'
            rows.append(row);last=finish;prior=phase
        profile={'id':c['id'],'episode':'A02','revision':'grid-v1','mode':mode,'duration':c['frames']/60,
                 'freezeSeconds':8/60,'phases':rows,'timingStatus':'speech-locked-from-current-PCM-and-captions',
                 'captionCueIds':c['speechCues'],'sourcePcmSha256':ap.read(L/'voice/source-assembly.json')['sha256'],
                 'captionSchedule':ap.artifact(L/'edit/captions.json'),'humanReview':False,
                 'timingBasis':'Native60fps frame boundaries rounded from measured speech cue starts; no audio stretch or inserted narration silence.',
                 'nativeMotionPolicy':'Each explicit playback cue is one native-speed imported clip. Any repeat has a new narrated comparison and reason; no editorial loop or game footage retiming.'}
        if c['id']=='A02-E002B':
            profile['actorYawDegrees']=160
            profile['viewReason']='Use the already verified three-quarter rig view so the narrated extended arm is visible rather than foreshortened; no clip, timing or bone change.'
        profiles.append(profile)
        directory=L/'render'/(c['id']+'-v1')/mode
        c.update(kind='explanation',renderer='Unity',sourceKind='our implemented animation comparison',
                 explanationMode=mode,nativeProfile=c['id'],renderedSource=ap.relative(directory/'unity.mp4'),
                 renderedSourceSha256=None,renderedStartFrame=0,nativeCapture={'status':'pending'},captureState='pending')
        return c
    s1=scene_map['01']['endFrame']/60;s2=scene_map['02']['endFrame']/60
    s3=scene_map['03']['endFrame']/60;s4=scene_map['04']['endFrame']/60;end=plan['totalFrames']/60-10
    actual('01','A02-TK01','Opening full native attack: guard, visible body turn/kick and return, followed by the same inspected pose.')
    still('01',cue(3),10086,'Inspect the visible torso direction after the full attack; end before the arm-extension clause, which this kick frame cannot demonstrate.','stills-v2')
    native('01',cue(4),'normal-and-pause','Show the actual extended-arm pose in our native punch when the narration explicitly mentions the arm; do not imply that the preceding kick frame shows this.',
           [(1,cursor/60,None,0)],key='A02-E002B')
    native('01',cue(8),'normal-and-pause','Connect normal motion, one frozen pose and torso contribution.',
           [(0,cursor/60,cue(4),0),(1,cue(5),None,0),(2,cue(6),cue(6)+.2,0)])
    native('01',cue(9),'size-amplitude','Preview actual-screen-size comparison in the spoken abstract.',[(2,cursor/60,cursor/60+.2,0)])
    native('01',cue(10),'shoulder-control','Preview the shared hand target and different shoulder control.',[(3,cursor/60,cursor/60+.1,1)])
    native('01',cue(11),'linear-overshoot','Preview overshoot and settling as the third step of the overview.',[(2,cursor/60,cursor/60+.2,2.8)])
    native('01',cue(14),'normal-and-pause','Hold the force-carrying pose while explaining appearance-only corrections.',[(1,cursor/60,None,0)])
    native('01',cue(16),'normal-and-pause','Play full native punch, then point to the torso in its peak pose.',[(0,cursor/60,cue(14)+.1,0),(1,cue(15),None,0)])
    native('01',s1,'normal-and-pause','Compare the same clip/time with torso contribution limited.',[(2,cursor/60,cue(16)+.1,0)])
    native('02',cue(27),'size-amplitude','Compare equal motion in a close and small view; replay only at the next spoken observation.',
           [(0,cursor/60,cue(20),0),(0,cue(22),cue(22)+.15,0,'Narration changes from close-view shoulder reading to the small-view comparison.'),
            (0,cue(24),cue(25),0,'Return attention to actual play size while comparing the same movement.')])
    native('02',cue(34),'size-amplitude','First vary view size, then lock camera/time and increase selected joint amplitude.',
           [(0,cursor/60,cue(28)-.4,0),(1,cue(29),cue(29)+.2,0),(2,cue(30),cue(30)+.1,0)])
    native('02',s2,'size-amplitude','Work the recommendation in the same small view with a cue-specific second comparison.',
           [(1,cursor/60,cue(35)+.1,0),(2,cue(37),cue(38)+.1,0),
            (2,cue(39),cue(40),0,'Repeat the same controlled comparison when narration explicitly asks to judge it at actual play size.')])
    native('03',cue(47),'shoulder-control','Reveal the linked bones before moving the arm surface.',
           [(0,cursor/60,None,0),(1,cue(45),cue(45)+.1,2.2)])
    native('03',cue(55),'shoulder-control','Raise the arm, then distinguish rotation about an anchor from translating the anchor.',
           [(1,cursor/60,cue(47)+.1,2),(1,cue(50),cue(50)+.1,2,'Narration defines rotation at the same joint anchor.'),
            (2,130.0,130.08,1.8)])
    native('03',s3,'shoulder-control','Same endpoint target, fixed versus translatable shoulder: real two-bone IK.',
           [(3,cursor/60,cue(56),2.3),(3,cue(59),cue(59)+.2,2.8,'Revisit the controlled reach as the narration explains the extra range of expression.')])
    actual('04','A02-VF01','A second independent game shows the whole kick before any pose judgement.')
    actual('04','A02-VF02','Keep the next distinct native camera shot intact; source cut clears all marks.')
    still('04',cue(65),1848,'A visible high-kick pose is a bridge from actual action to our isolated direction explanation.')
    native('04',cue(70),'paused-pose-context','Observe body chain, pause at overlapping directions, then resume from that exact pose.',
           [(0,cursor/60,cue(65)+.1,0),(1,cue(67),None,0),(2,cue(69),cue(69)+.1,0)])
    native('04',s4,'paused-pose-context','Follow the recommended review order: normal whole motion, selected pose, its role in continued motion.',
           [(0,cursor/60,cue(70)+.2,0),(1,cue(72),None,0),(2,cue(74),cue(74)+.1,0)])
    native('05',cue(82),'linear-overshoot','Compare stopping at a target with moving beyond it and settling before naming Overshoot.',
           [(0,cursor/60,None,0),(1,cue(78),cue(78)+.2,2.7),(2,cue(79),cue(79)+.1,2.2)])
    native('05',cue(90),'linear-overshoot','Worked0→100 versus0→110→100cm example, then measured authored10cm overshoot.',
           [(0,cursor/60,None,0),(1,cue(84),cue(84)+.1,2),(2,cue(85),cue(85)+.1,1.8),
            (3,cue(87),None,0),(4,cue(88),None,0)])
    actual('05','A02-KB01','Kirby copies Needle and activates it at native speed before the two drawing comparison.')
    native('05',cue(94),'shape-overshoot','Transfer the linear endpoint idea to our authored spike shape.',
           [(0,cursor/60,None,0),(1,cue(92),cue(92),3.2)])
    still('05',cue(95),179,'Same crop and scale: the larger native spike drawing.')
    still('05',cue(96),181,'Same crop and scale: the immediately following smaller native drawing; retain its actual colour change.')
    native('05',cue(97),'shape-overshoot','Confirm the visible settling impression using our controllable shape.',[(3,cursor/60,cursor/60+.1,1.4)])
    native('05',cue(99),'size-amplitude','Return to the same play-size comparison for the overall thesis.',[(2,cursor/60,cue(98),0)])
    native('05',cue(100),'linear-overshoot','Tie the selected overshoot moment to the final conclusion.',[(2,cursor/60,cursor/60+.1,2.2)])
    native('05',end,'size-amplitude','Close on the same visibly readable small character action.',[(2,cursor/60,cursor/60+.1,0)])
    assert cursor==plan['totalFrames']-600
    actual_frames=sum(c['frames'] for c in cuts if c['kind']=='independent-gameplay')
    choice={'id':'a02-controlled-animation-explanation-v1','episode':'A02','slug':'animation-exaggeration','revision':'grid-v1',
            'scope':'Only this A02 grid-v1 local review; no global quota or platform change.',
            'basis':'recommended-production-choice-v1','actualHumanApproval':False,
            'defaultContractAcknowledged':'actual60:explanation40',
            'decision':'Use native game actions at their meaningful length and the controlled Unity comparisons needed by this animation lesson; report measured share.',
            'reasons':['The source-ordered lesson depends on same-clip/same-camera amplitude, shoulder controls and hypothetical position/shape comparisons; commercial footage cannot establish those internals.',
                       'The independently inspected game actions total10.3s; extending their source windows introduces other moves or transitions.',
                       'The requested animation-tool grid presentation is implemented with labelled native game frames and original editable demonstrations, preserving all narration depth.'],
            'actualFrames':actual_frames,'bodyFrames':plan['bodyFrames'],'actualShare':actual_frames/plan['bodyFrames'],
            'prohibited':['Unrelated footage padding','Game loops/slowdown','Relabelled Unity as actual gameplay','Reference lesson clips'],
            'retained':'IndependentFHD native speed/aspect, precise source records, fixed captions, full original learning order, user review pending.'}
    ap.save(H/'editorial-ratio-choice.json',choice)
    previous=ap.read(R/'projects/animation-assigning/production/grid-v1/edit-plan.json')
    plan.update(episode='A02',status='measured-proposal-native-capture-and-QA-pending',cuts=cuts,
                expectedGameplayShare=actual_frames/plan['bodyFrames'],ratioToleranceFrames=1,
                ratioChoice={'path':ap.relative(H/'editorial-ratio-choice.json'),'sha256':ap.sha(H/'editorial-ratio-choice.json')},
                audio=copy.deepcopy(previous['audio']),outputDir=ap.relative(L/'edit'),outputStem='animation-exaggeration',
                captionsAss=ap.relative(L/'edit/captions.ko.ass'),sourcePlan=ap.artifact(H.parents[1]/'planning/production-plan.json'),
                sourceCalloutProposal=ap.artifact(H/'source-callout-proposal.json'),userReviewed=False,
                bodyContract='Measured episode-specific delegated clarity choice; commercial actions remain native and unique.')
    vp.validate_plan(plan)
    ap.save(H/'measured-edit-plan.proposal.json',plan)
    ap.save(H/'measured-native-profiles.json',{'schemaVersion':1,'episode':'A02','revision':'grid-v1',
        'timingStatus':'speech-locked-native-preflight-required','humanReview':False,'presentations':profiles})
    for spec in specs:ap.save(H/'still-specs'/f'{spec["id"]}.json',spec)
    ap.save(H/'measured-plan-binding.json',{'episode':'A02','createdAt':ap.now(),'plan':ap.artifact(H/'measured-edit-plan.proposal.json'),
       'profiles':ap.artifact(H/'measured-native-profiles.json'),'captionSchedule':ap.artifact(L/'edit/captions.json'),
       'sourceAudio':ap.artifact(L/'voice/narration-source.wav'),'sceneSplit':ap.artifact(L/'voice/scene-split-review.json'),
       'cuts':len(cuts),'nativeCuts':len(profiles),'stillCuts':len(specs),'actualFrames':actual_frames,
       'speechUnmodified':True,'fullRenderComplete':False,'humanReviewed':False,
       'pending':'Current native profile validation, source marks, current output pixel/motion/audio QA.'})
    print(f'Prepared {len(cuts)} measured cuts, {len(profiles)} native profiles, {len(specs)} stills; actual {actual_frames}/{plan["bodyFrames"]}.')
if __name__=='__main__':main()
