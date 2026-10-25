"""Prepare only the root-selected eight-cut visual patch; no media jobs/copies."""
from pathlib import Path
import copy
import argparse
import hashlib
import json
import audio_pipeline as audio
import video_pipeline as video

HERE=Path(__file__).resolve().parent
MC=audio.ROOT/'motion-canvas/src/projects/similar-game-design/revision-v2'
BASE=HERE/'edit-plan-final.json'
DEST=HERE/'edit-plan-final-v4.json'
MC_CUTS=['cut006','cut007','cut008','cut027','cut029','cut032']
PIXEL_CUTS=sorted([*MC_CUTS,'cut018','cut022'])


def write_checked(file,content,refresh=False):
    if file.exists() and file.read_text('utf-8-sig')!=content and not refresh:
        raise ValueError('Preserve existing incompatible prepared source: '+str(file))
    file.write_text(content,'utf-8')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh-prepared',action='store_true',help='Refresh only unrendered/unbacked-up v4 authored preparation after a frozen sidecar update')
    args=parser.parse_args()
    base=audio.read(BASE);plan=copy.deepcopy(base)
    local=audio.current_local_output(plan['outputDir'])
    if args.refresh_prepared and ((local/'previous-cuts-v2/preservation.json').exists()
        or audio.repo_path('projects/similar-game-design/production/local/reference-preserving-v2/rendered/similar-game-design-patch-v4.mp4').exists()):
        raise ValueError('v4 production has begun; preserve it and create a new version')
    sidecar=HERE/'visual-fix-marks-v4.json';fix=audio.read(sidecar)
    if fix['basePlanSha256']!=audio.sha(BASE):
        raise ValueError('Annotation sidecar is bound to another base plan')
    if fix['coordinateSpace']!='output1920x1080' or fix['changedCuts']!=['cut018','cut022']:
        raise ValueError('Unexpected visual-fix scope')
    byid={c['id']:c for c in plan['cuts']};old={c['id']:c for c in base['cuts']}
    byid['cut027'].update(endFrame=12489,frames=184)
    byid['cut028'].update(startFrame=12489,endFrame=12681)
    byid['cut029'].update(startFrame=12681,frames=220)
    captions_path=audio.current_local_output(plan['outputDir'])/'captions.json'
    captions=audio.read(captions_path)
    cues={c['cue']:c for c in captions['cues']}
    for cid,numbers,summary in [('cut027',[80,81,82,83],None),('cut029',[80,81,82,83],None),
                                ('cut032',[90,91,92,93],'서로 다른 매력입니다')]:
        c=byid[cid]
        c.update(visual='effortExamples',diagramId='concrete-three-experience-confirmation',
                 title='세 가지 경험에 공들이기',cues=[cues[n]['start']-c['startFrame']/60 for n in numbers],
                 primaryOverlapFrames=c['frames'],paragraphOverlapFrames={c['primaryParagraphId']:c['frames']})
        c['initialVisible']=[i for i,t in enumerate(c['cues']) if t<=0]
        c.pop('visibilityContinuity',None)
        c['exampleCueIds']=numbers
        if summary:
            c['exampleSummary']=summary
    # Keep the complete explanatory-frame ledger unchanged, while patched cuts
    # sample their own finite render. Every other physical MC source/offset stays.
    ledger=0;patch=0
    patch_source='projects/similar-game-design/production/local/reference-preserving-v2/rendered/similar-game-design-patch-v4.mp4'
    for c in plan['cuts']:
        if c['kind']=='explanation':
            c['mcStartFrame']=ledger;ledger+=c['frames'];c['mcEndFrame']=ledger
            if c['id'] in MC_CUTS:
                c.update(renderedSource=patch_source,renderedStartFrame=patch,
                         patchStartFrame=patch,patchEndFrame=patch+c['frames'])
                patch+=c['frames']
    assert ledger==6675 and patch==2498
    for cid in ['cut018','cut022']:
        if byid[cid]['viewport']!=fix['viewport']:
            raise ValueError('Annotation coordinates do not match actual final viewport')
        byid[cid]['marks']=copy.deepcopy(fix['cuts'][cid]['marks'])
        byid[cid]['annotationStatus']='v4 native-frame-reviewed correction; final encoded pixels pending'
    # ASS pixels and relative text timing stay byte-identical. Only their binding
    # to the changed mark geometry/output clock is regenerated in metadata.
    for cid in ['cut018','cut022','cut028']:
        c=byid[cid];guide=c['editorialGuideAss']
        for event in guide['events']:
            event['globalStart']=c['startFrame']/60+event['start']
            event['globalEnd']=c['startFrame']/60+event['end']
        guide['cutBindingSha256']=video.editorial_guide_binding(c,plan)
        video.editorial_guide_ass(c,plan)
        if cid in ['cut018','cut022']:
            video.annotations(c,plan)  # Font/geometry only; no ASS/media write.
    plan.update(outputStem='similar-game-design-v4',status='v4-selected-visual-patch-prepared-no-render-claim')
    plan['visualPatchV4']={'basePlan':audio.artifact(BASE),'annotationSidecar':audio.artifact(sidecar),
        'visualSource':audio.artifact(MC/'visuals.tsx'),'captions':audio.artifact(captions_path),
        'pixelChangedBodyCutIds':PIXEL_CUTS,'mcCutIds':MC_CUTS,'patchRenderFrames':patch,
        'unchangedBodyCutFilesToReuse':len(plan['cuts'])-len(PIXEL_CUTS),
        'timelineOnlyRebindCutIds':['cut028'],
        'worldTimelineDecision':{'fromFrames':[12566,12758],'toFrames':[12489,12681],
            'nativeSourceSeconds':[46,49.2],'nativeFrames':192,
            'basis':'Root-reviewed source ASR word clock: mining clause ends208.14; World begins208.15 and covers208.4–210.76. Inherit the general word 같은211.02–211.38, then switch before 코스를211.38/나란히211.86.',
            'sourceAsr':audio.artifact(audio.NARRATION/'whole-source-asr.json'),
            'captionCues':[cues[n] for n in [80,81,82,83]],'audioUnchanged':True},
        'mediaProduced':False,'masterV2Preserved':True,'finalPixelReview':'pending new selected renders'}
    assert audio.audio_plan_contract(plan)==audio.audio_plan_contract(base)
    assert plan['scenes']==base['scenes'] and plan['audio']==base['audio']
    ratio=video.validate_plan(plan)
    for cid,c in byid.items():
        if c['kind']=='independent-gameplay':
            for key in ['sourceFile','sourceStart','sourceSha256','frames','sourceAudioEnabled','viewport']:
                assert c[key]==old[cid][key],(cid,key)
        if cid not in PIXEL_CUTS and cid!='cut028':
            assert c==old[cid],('Unselected cut metadata changed',cid)
    for c in plan['cuts']:
        if c['kind']=='explanation' and c['id'] not in MC_CUTS:
            assert (c['renderedSource'],c['renderedStartFrame'])==(old[c['id']]['renderedSource'],old[c['id']]['renderedStartFrame'])
    for cid in MC_CUTS:
        c=byid[cid];options={key:c[key] for key in ['cues','title','imagePaths','initialVisible','exampleSummary'] if key in c}
        options['duration']=c['frames']/60
        source="// Selected v4 patch; measured existing narration clock.\nimport {makeScene2D} from '@motion-canvas/2d';\nimport {lesson} from './visuals';\nexport default makeScene2D(function*(view) { yield* lesson(view, "+json.dumps(c['visual'])+", "+json.dumps(options,ensure_ascii=False)+"); });\n"
        write_checked(MC/('patch-v4-'+cid+'.tsx'),source,args.refresh_prepared)
    source="import {makeProject} from '@motion-canvas/core';\n"+'\n'.join(f"import s{i} from './patch-v4-{cid}?scene';" for i,cid in enumerate(MC_CUTS))+"\nexport default makeProject({scenes:["+','.join('s'+str(i) for i in range(len(MC_CUTS)))+"]});\n"
    write_checked(MC/'patch-v4-project.ts',source,args.refresh_prepared)
    write_checked(DEST,json.dumps(plan,ensure_ascii=False,indent=2)+'\n',args.refresh_prepared)
    proof={'status':'prepared-no-media-jobs','basePlan':audio.artifact(BASE),'v4Plan':audio.artifact(DEST),
        'cutIds':len(plan['cuts']),'pixelChangedCutIds':PIXEL_CUTS,'timelineOnlyRebind':['cut028'],
        'unchangedBodyFiles':31,'mcPatchFrames':2498,'mcTotal':ledger,'ratio':ratio,
        'audioPlanContractIdentical':True,'sourceAudioAndInOutIdentical':True,
        'pcmCaptionFilesUnchanged':True,'viewportOfEveryActualSourceUnchanged':True,
        'physicalMcSourceAndOffsetOfUnselectedCutsUnchanged':True,
        'patchRanges':[{k:byid[cid][k] for k in ['id','frames','patchStartFrame','patchEndFrame']} for cid in MC_CUTS],
        'backupAndRenderingByRoot':'Required before replacing the eight selected cut files; helper defaults to dry-run.'}
    write_checked(HERE/'visual-patch-v4-review.json',json.dumps(proof,ensure_ascii=False,indent=2)+'\n',args.refresh_prepared)
    print(json.dumps(proof,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
