"""Record only this explicitly selected batch from actual files; no production."""
from pathlib import Path
import json
from scoped_context import BATCH, ROOT, MEDIA, read, sha, now, process_snapshot


def save(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf8')


def main():
    batch=read(BATCH/'batch.json'); checkpoint=read(BATCH/'checkpoint.json')
    if checkpoint.get('generatedReviewVideos', 0):
        raise RuntimeError('This preparation-only snapshot must not replace completed video records.')
    processes=process_snapshot()
    games=[p for p in processes if p['name'].lower() not in {'unity.exe'}]
    rows=[]
    for item in batch['projects']:
        project=ROOT/'projects'/item['slug']; plan=read(project/'planning/production-plan.json')
        metadata=read(project/'publishing/metadata.json')
        state_path=project/'production/local/finite-pipeline-v1/state.json'
        state=read(state_path) if state_path.exists() else {}
        ready=all(plan.get(k) is True for k in ['scriptFinalized','independentFootageViewed','rightsAndFhdReady'])
        status=state.get('status') or ('waiting-for-game-exit' if ready and games else 'preproduction')
        if not ready:status='source-review-and-scene-preparation'
        rows.append({**item,'title':metadata['title'],'status':status,'scriptFinalized':plan.get('scriptFinalized') is True,
            'sourceAndFhdReady':ready,'humanFinalReview':'pending','generatedReviewVideo':False})
    previews=[]
    for item in batch['projects']:
        for receipt in (MEDIA/item['slug']/'local').glob('unity-preflight-*/native-receipt.json'):
            data=read(receipt)
            previews.append({'slug':item['slug'],'receipt':str(receipt),'sha256':sha(receipt),
                'success':data.get('success') is True,'frameCount':sum(a['path'].endswith('.jpg') for a in data['artifacts']),
                'latestSourceRevalidationRequired':True})
    for item in rows:
        path=ROOT/'projects'/item['slug']/'production/checkpoint.json'; project_checkpoint=read(path)
        completed=project_checkpoint.get('completed',[])
        if item['sourceAndFhdReady']:
            for key in ['independent-fhd-footage-acquisition-and-viewing','final-script','heading-free-ko-en-script-readthrough']:
                if key not in completed:completed.append(key)
        own_previews=[r for r in previews if r['slug']==item['slug']]
        native=item['slug'] not in {'shorts-starcraft-diagonal-bridge-square-path-grid','shorts-starcraft-eud-compatibility-emulator','shorts-starcraft2-replay-input-resimulation'}
        pending=[] if item['sourceAndFhdReady'] else ['resolve-source-fit-and-rights-evidence','finalize-source-matched-script']
        pending+=['latest-native-runtime-and-visual-preflight' if native else 'full-motion-diagram-review',
                  'TTS-ASR-caption-alignment','render-mix-four-outputs','actual-full-listening-and-mobile-review','human-final-review']
        project_checkpoint.update(recordedAt=now(),status=item['status'],completed=completed,pending=pending,
            gpuJobStarted=bool(own_previews) or item['slug']=='shorts-sea-of-thieves-water-masking',
            sourceAndFhdReady=item['sourceAndFhdReady'],scriptFinalized=item['scriptFinalized'],
            priorNativeDraftPreviews=own_previews,latestNativeRuntimeVerified=False if native else None,
            actualVoiceGenerated=False,finalVideoGenerated=False,actualFullListening='pending',humanReview='pending',
            batchCheckpoint='production/batches/tech-ten-shorts-20261030/checkpoint.json',platformActions=False)
        save(path,project_checkpoint)
    checkpoint.update(recordedAt=now(),status='gpu-wait-source-and-scene-preparation',projects=rows,
        productionJobsStarted=1,generatedReviewVideos=0,nativePreflightReceipts=previews,
        productionJobCountScope='One attempted SoT voice-model load; prior native draft previews are listed separately. Zero narration PCM paragraphs generated.',
        finiteQueueRunning=False,automaticBackgroundContinuationStarted=False,
        activeGameProcesses=games,latestUserFootageInstruction='스타크래프트 장면은 유튜브에서 가져다 사용해~ 많자나~',
        next='After game exit: revalidate changed native code/scenes, refresh inspected fingerprints, then run ready projects serially. Resolve held source-fit/publisher evidence without claiming completion.',
        remainingProduction=['Revalidate source-versioned Unity scene generation and cue-driven transitions after GPU becomes available.',
            'Run exact approved Qwen voice, raw ASR and measured captions for source-ready projects; no voice PCM was produced by the first deferred attempt.',
            'Verify native motion, scene labels/marks, full audio and 375px output; deliver four actual outputs only after they exist.',
            'Keep Alyx visible-liquid source, Batman footprint source, and WB/Sony publisher evidence gaps explicit.',
            'Distinguish Batman console relief-mapped illustration from actual PC-style displaced mesh demonstration before final visuals.'],
        computerUse='Battle.net/game control remains stopped. StarCraft sources are independently recorded YouTube gameplay.',
        platformActions=False)
    save(BATCH/'checkpoint.json',checkpoint)
    control_path=ROOT/'shared/publishing/video-production-control.json'; control=read(control_path)
    control['explicitTechTenBatch20261030'].update(status='production-active',currentStage='waiting-for-game-exit',
        activeGameProcesses=games,localReviewVideosCompleted=0,checkpoint=str((BATCH/'checkpoint.json').relative_to(ROOT)).replace('\\','/'))
    save(control_path,control)
    worklist_path=ROOT/'shared/publishing/shorts-worklist.json'; worklist=read(worklist_path)
    next_order=max((r.get('order',0) for r in worklist['rows']),default=0)+1
    for item in rows:
        matches=[r for r in worklist['rows'] if r.get('slug')==item['slug']]
        if len(matches)>1:raise RuntimeError('Duplicate selected worklist row')
        if matches:row=matches[0]
        else:
            row={'order':next_order,'slug':item['slug']}; next_order+=1;worklist['rows'].append(row)
        row.update(candidateId=item['candidateId'],title=item['title'],status=item['status'],
            production='script-finalized' if item['scriptFinalized'] else 'source-review-and-script-draft',
            humanReview='pending-no-complete-video-delivered',review='native-samples-only; full-motion-and-listening-pending',
            platform='not-uploaded',youtube='not-uploaded',drive='outside-default-workflow',
            authorization='explicit-tech-ten-shorts-20261030',productionDateKst='2026-10-30',updatedAt=now(),
            checkpoint='projects/'+item['slug']+'/production/checkpoint.json',scheduled=False,published=False)
    save(worklist_path,worklist)
    print(json.dumps({'batchStatus':checkpoint['status'],'readySources':sum(r['sourceAndFhdReady'] for r in rows),
        'successfulNativePreflightReceipts':len(previews),'completeReviewVideos':0,'activeGames':[p['name'] for p in games]}))


if __name__=='__main__':main()
