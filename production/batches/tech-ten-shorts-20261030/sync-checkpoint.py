"""Aggregate only the selected ten from current evidence. No production/platform actions."""
from pathlib import Path
import argparse
import json
import os
import uuid
from batch_job_lock import inspect_lock
from scoped_context import BATCH, ROOT, MEDIA, REVISION, inventory, read, sha, now, process_snapshot

STAGES = ('voice','voice-asr','captions','visual-preparation','native-capture','header',
          'visual-render','audio-mix','audio-report','mix-asr','video-pair','integrity','qa','review')
FOUR = ('clean.mp4','captioned.mp4','captions.ko.srt','captions.en.srt')


def save(path, value):
    path = Path(path); temporary = path.with_name(path.name + '.' + uuid.uuid4().hex + '.partial')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
    os.replace(temporary, path)


def optional(path):
    return read(path) if Path(path).is_file() else {}


class Evidence:
    """Hash files once per snapshot; reject changes during hashing."""
    def __init__(self): self.cache = {}
    def artifact(self, path):
        path = Path(path).resolve(); before = path.stat()
        key = (str(path), before.st_size, before.st_mtime_ns, before.st_ctime_ns)
        if key not in self.cache:
            digest = sha(path); after = path.stat()
            if (before.st_size,before.st_mtime_ns,before.st_ctime_ns) != (after.st_size,after.st_mtime_ns,after.st_ctime_ns):
                raise RuntimeError('File changed during snapshot: '+str(path))
            self.cache[key] = digest
        return dict(path=str(path), bytes=before.st_size, sha256=self.cache[key])
    def verify(self, rows):
        for row in rows:
            actual = self.artifact(row['path'])
            if actual['bytes'] != row['bytes'] or actual['sha256'] != row['sha256']:
                raise RuntimeError('Artifact/dependency no longer matches: '+row['path'])


def verified_stages(state, evidence):
    passed, issues = [], []
    for name in STAGES:
        record = state.get('stages',{}).get(name,{})
        if record.get('status') != 'pass': continue
        try:
            artifacts = record.get('artifacts',[])
            if not artifacts and not (name == 'native-capture' and record.get('result',{}).get('unityClaimed') is False):
                raise RuntimeError('Passed stage has no artifact evidence.')
            evidence.verify(artifacts)
            for key in ('files','code','inputs'): evidence.verify(record.get('dependencies',{}).get(key,[]))
            passed.append(name)
        except (OSError,KeyError,RuntimeError) as error:
            issues.append(dict(stage=name,error=str(error)))
    return passed, issues


def caption_snapshot(project, passed, evidence):
    """Recognize separately derived CPU artifacts without passing runner stages."""
    result = dict(available='captions' in passed, status='pipeline-verified' if 'captions' in passed else 'not-derived',
                  pipelineAdoptionPending=False, issues=[])
    if 'captions' in passed:
        return result
    local = project/'production/local'; audio = local/'audio-v1'
    receipts = sorted(local.glob('caption-derivation-cpu-*/receipt.json'))
    if not receipts:
        return result
    path = receipts[-1]; receipt = read(path)
    try:
        if (receipt.get('slug') != project.name or receipt.get('revision') != REVISION or receipt.get('exitCode') != 0
                or receipt.get('GPUUsed') is not False or receipt.get('modelInferenceUsed') is not False
                or receipt.get('newSourceEncodingPerformed') is not False or receipt.get('runnerStageStatusChanged') is not False):
            raise RuntimeError('Standalone CPU caption receipt is incomplete or out of scope.')
        expected = {str(p.resolve()) for p in [project/'script/captions.json', audio/'caption-alignment.json',
            audio/'caption-layout.json', audio/'captions.ko.ass', audio/'captions.ko.srt', audio/'captions.en.srt']}
        if {str(Path(row['path']).resolve()) for row in receipt.get('artifacts',[])} != expected:
            raise RuntimeError('Standalone caption receipt does not identify the exact six outputs.')
        evidence.verify(receipt['artifacts'])
        voice_sha = evidence.artifact(audio/'voice/narration.wav')['sha256']
        alignment = read(audio/'caption-alignment.json'); fingerprints = alignment['fingerprints']
        if receipt.get('voiceSha256') != voice_sha:
            raise RuntimeError('Standalone captions belong to another assembled voice.')
        expected_hashes = {'voiceSha256':voice_sha,
            'asrSha256':evidence.artifact(audio/('asr-voice-'+voice_sha[:12]+'.json'))['sha256'],
            'narrationSha256':evidence.artifact(project/'script/narration.spoken.ko.json')['sha256'],
            'clausesSha256':evidence.artifact(project/'script/caption-clauses.json')['sha256'],
            'reconciliationSha256':evidence.artifact(audio/'asr-reconciliation.json')['sha256'] if (audio/'asr-reconciliation.json').exists() else None}
        if any(fingerprints.get(key) != value for key,value in expected_hashes.items()):
            raise RuntimeError('Standalone caption alignment input hashes are stale.')
        captions = read(project/'script/captions.json')
        if captions.get('fps') != 60 or captions.get('timingInputs',{}).get('voiceSha256') != voice_sha:
            raise RuntimeError('Standalone caption timing belongs to another voice or frame rate.')
        result.update(available=True,status='artifact-verified-pending-stage-adoption',pipelineAdoptionPending=True,
            receipt=evidence.artifact(path),artifacts=receipt['artifacts'],voiceSha256=voice_sha,
            frames=captions['frames'],alignmentReviewFlags=alignment.get('reviewFlags',[]),
            actualListening='pending',fullRealtimePlayback='pending',runnerStagePassed=False)
    except (OSError,KeyError,RuntimeError) as error:
        result['issues'].append(str(error));result['status']='standalone-caption-evidence-needs-inspection'
    return result


def final_snapshot(project, manifest, passed, evidence):
    directory = (project/manifest['currentFinalDirectory']).resolve()
    if not directory.is_relative_to((MEDIA/manifest['slug']/'local').resolve()):
        raise RuntimeError('Final directory escaped selected project media.')
    result = dict(directory=str(directory), fourOutputsVerified=False, reviewFilesGenerated=False,
                  presentOutputNames=[name for name in FOUR if (directory/name).exists()], issues=[])
    # Files being written, or a deliberate pause before integrity, are not failures.
    if len(result['presentOutputNames']) != 4 or not {'video-pair','integrity'}.issubset(passed): return result
    try:
        files = {name:evidence.artifact(directory/name) for name in FOUR}
        if any(row['bytes'] <= 0 for row in files.values()): raise RuntimeError('Empty final output.')
        pair, integrity = read(directory/'pair-build.json'), read(directory/'integrity.json')
        if integrity.get('status') != 'pass': raise RuntimeError('Integrity did not pass.')
        for key,name in dict(clean='clean.mp4',captioned='captioned.mp4',captionsKo='captions.ko.srt',captionsEn='captions.en.srt').items():
            if pair.get(key) != files[name]['sha256']: raise RuntimeError('Pair hash differs: '+name)
        reports = {row['name']:row for row in integrity['outputs']}; captions = read(project/'script/captions.json')
        for name in ('clean','captioned'):
            row = reports[name]; video = row['video']
            if (row['sha256'] != files[name+'.mp4']['sha256'] or row.get('decoded') is not True or row.get('ptsRegular60') is not True
                or (video['width'],video['height'],video['r_frame_rate']) != (1080,1920,'60/1') or row['frames'] != captions['frames']):
                raise RuntimeError('Current FHD60 integrity proof differs: '+name)
        if not integrity.get('identicalAac') or not integrity.get('allCaptionTimesInsideVideo'):
            raise RuntimeError('Audio/caption integrity proof missing.')
        result.update(fourOutputsVerified=True,files=files,masterSHA256=files['captioned.mp4']['sha256'])
        if 'review' not in passed: return result
        delivery = read(directory/'delivery.json'); records = {row['name']:row for row in delivery['files']}
        if delivery.get('revision') != REVISION or (delivery['width'],delivery['height'],delivery['fps']) != (1080,1920,60):
            raise RuntimeError('Delivery version/dimensions differ.')
        for name,row in files.items():
            if records[name]['sha256'] != row['sha256'] or records[name]['bytes'] != row['bytes']: raise RuntimeError('Delivery hash differs: '+name)
        result.update(reviewFilesGenerated=True,reviewPage=str(directory/'index.html'),delivery=str(directory/'delivery.json'))
    except (OSError,KeyError,ValueError,RuntimeError) as error: result['issues'].append(str(error))
    return result


def classify(source_ready, code_ready, state, passed, final, issues, active, games, occupied):
    if active: return 'running-'+active.get('stage','owned-job')
    if issues or final['issues']: return 'evidence-needs-inspection'
    if final['reviewFilesGenerated']: return 'review-files-generated-internal-review-pending'
    if not source_ready: return 'source-review-and-scene-preparation'
    if state.get('status') == 'failed': return 'production-failed-needs-inspection'
    if state.get('status') == 'running': return 'interrupted-job-needs-inspection'
    if games: return 'waiting-for-game-exit'
    if not code_ready: return 'native-or-code-preflight-pending'
    if occupied: return 'waiting-for-current-owned-job'
    if state.get('status') == 'deferred': return 'ready-to-resume-after-defer'
    return 'ready-after-'+passed[-1] if passed else 'ready-for-local-production'


def collect():
    batch, selected = inventory(); evidence = Evidence(); readiness = optional(BATCH/'readiness.json')
    processes = process_snapshot(); games = [p for p in processes if p['name'].lower() != 'unity.exe']
    lock = inspect_lock(); selected_slugs = {row['slug'] for row in selected}
    live = lock if lock and lock.get('ownerLive') and lock.get('slug') in selected_slugs else None
    rows, previews, attempts = [], [], set()
    for item in selected:
        slug=item['slug']; project=ROOT/'projects'/slug; manifest=read(project/'project.json')
        plan=read(project/'planning/production-plan.json'); metadata=read(project/'publishing/metadata.json')
        state=optional(project/'production/local/finite-pipeline-v1/state.json')
        if state and (state.get('slug') != slug or state.get('revision') != REVISION): raise RuntimeError('Wrong pipeline version: '+slug)
        passed,issues=verified_stages(state,evidence); final=final_snapshot(project,manifest,passed,evidence)
        captions=caption_snapshot(project,passed,evidence)
        issues += [dict(stage='standalone-cpu-captions',error=message) for message in captions['issues']]
        source_ready=all(plan.get(k) is True for k in ('scriptFinalized','independentFootageViewed','rightsAndFhdReady'))
        ready=readiness.get('projects',{}).get(slug,{}); code_ready=ready.get('codeReadyForActualProduction') is True
        if code_ready:
            try:
                evidence.verify(ready['fingerprints']['code']); evidence.verify(ready['fingerprints']['inputs'])
            except (OSError,KeyError,RuntimeError) as error:
                code_ready=False; issues.append(dict(stage='readiness',error=str(error)))
        active=live if live and live['slug']==slug else None; ledger=optional(project/'production/review-ledger.json')
        rows.append({**item,'title':metadata['title'],'status':classify(source_ready,code_ready,state,passed,final,issues,active,games,bool(lock)),
            'scriptFinalized':plan.get('scriptFinalized') is True,'sourceAndFhdReady':source_ready,
            'codeReadyRecorded':ready.get('codeReadyForActualProduction') is True,'codeReadinessEvidenceCurrent':code_ready,
            'verifiedStages':passed,'stageEvidenceIssues':issues,'pipelineStatus':state.get('status','not-started'),
            'currentStage':active.get('stage') if active else state.get('currentStage'),'actualVoiceGenerated':'voice' in passed,
            'captionArtifactsAvailable':captions['available'],'captionEvidence':captions,
            'fourOutputsVerified':final['fourOutputsVerified'],'generatedReviewVideo':final['reviewFilesGenerated'],'finalOutputs':final,
            'humanFinalReview':ledger.get('humanFinalReview','pending'),'actualFullListeningRecorded':ledger.get('actualCompleteHumanListening') is True,
            'visualPlaybackReviewRecorded':ledger.get('visualPlaybackReview','pending'),
            'reviewEvidenceSource':'existing-review-ledger-only; never inferred from generation'})
        for path in sorted((MEDIA/slug/'local').glob('unity-preflight-*/native-receipt.json')):
            receipt=read(path); version=path.parent.name.removeprefix('unity-preflight-')
            job=optional(MEDIA/'capture-jobs'/(item['candidateId']+'-preview-'+version+'.json'))
            previews.append(dict(slug=slug,receipt=str(path),sha256=evidence.artifact(path)['sha256'],
                success=receipt.get('success') is True,frameCount=sum(str(a.get('path','')).endswith('.jpg') for a in receipt.get('artifacts',[])),
                sceneVersion=job.get('sceneVersion'),visualReviewInferred=False))
        records=list(state.get('stages',{}).items())+[(r.get('stage'),r.get('record',{})) for r in state.get('history',[])]
        for stage,record in records:
            if record.get('startedAt'): attempts.add((slug,stage,record['startedAt']))
    complete=sum(row['generatedReviewVideo'] for row in rows)
    if live: status='running-'+live.get('stage','owned-job')
    elif complete==len(rows): status='local-review-files-generated'
    elif any('needs-inspection' in row['status'] for row in rows): status='production-evidence-needs-inspection'
    elif games: status='waiting-for-game-exit'
    else: status='ready-to-continue-with-source-and-runtime-holds'
    return dict(recordedAt=now(),status=status,projects=rows,generatedReviewVideos=complete,
        verifiedFourOutputSets=sum(r['fourOutputsVerified'] for r in rows),actualVoiceGeneratedCount=sum(r['actualVoiceGenerated'] for r in rows),
        verifiedCaptionArtifactSets=sum(r['captionArtifactsAvailable'] for r in rows),
        captionSetsPendingStageAdoption=sum(r['captionEvidence']['pipelineAdoptionPending'] for r in rows),
        sourceReadyCount=sum(r['sourceAndFhdReady'] for r in rows),productionJobsStarted=len(attempts),
        productionJobCountScope='Unique (slug,stage,startedAt) attempts, including deferred/failed. Native previews listed separately.',
        nativePreflightReceipts=previews,activeOwnedJob=live,finiteQueueRunning=bool(live and live.get('stage')!='native-preflight'),
        activeGameProcesses=games,observedApps=processes,serialLock=lock,platformActionsPerformedBySnapshot=False,humanReviewInferred=False)


def persist(snapshot):
    # Validate shared targets before writing; only exact selected rows/authorization are changed.
    _, authorized = inventory()
    if [row['slug'] for row in snapshot['projects']] != [row['slug'] for row in authorized]:
        raise RuntimeError('Snapshot scope differs from the exact authorized ten.')
    control_path=ROOT/'shared/publishing/video-production-control.json'; control=read(control_path)
    if control['explicitTechTenBatch20261030'].get('id') != 'explicit-tech-ten-shorts-20261030': raise RuntimeError('Unexpected authorization.')
    worklist_path=ROOT/'shared/publishing/shorts-worklist.json'; worklist=read(worklist_path)
    if any(sum(r.get('slug')==item['slug'] for r in worklist['rows'])>1 for item in snapshot['projects']): raise RuntimeError('Duplicate selected worklist row.')
    for item in snapshot['projects']:
        path=ROOT/'projects'/item['slug']/'production/checkpoint.json'; cp=optional(path); completed=list(cp.get('completed',[]))
        if item['sourceAndFhdReady']:
            for key in ('independent-fhd-footage-acquisition-and-viewing','final-script','heading-free-ko-en-script-readthrough'):
                if key not in completed: completed.append(key)
        for stage in item['verifiedStages']:
            key='verified-pipeline-'+stage
            if key not in completed: completed.append(key)
        if item['captionEvidence']['pipelineAdoptionPending']:
            key='cpu-caption-artifacts-verified-stage-adoption-pending'
            if key not in completed: completed.append(key)
        pending=[] if item['sourceAndFhdReady'] else ['resolve-source-fit-and-rights-evidence','finalize-source-matched-script']
        if not item['codeReadinessEvidenceCurrent']: pending.append('latest-native-runtime-or-code-preflight')
        pending+=['pipeline-'+s for s in STAGES if s not in item['verifiedStages']]
        if not item['actualFullListeningRecorded']: pending.append('actual-full-listening')
        if item['visualPlaybackReviewRecorded'] not in ('pass','complete','completed'): pending.append('real-time-visual-and-mobile-review')
        if item['humanFinalReview'] in (False,None,'pending','not-reviewed'): pending.append('human-final-review')
        cp.update(recordedAt=snapshot['recordedAt'],status=item['status'],completed=completed,pending=pending,
            sourceAndFhdReady=item['sourceAndFhdReady'],scriptFinalized=item['scriptFinalized'],
            verifiedPipelineStages=item['verifiedStages'],pipelineEvidenceIssues=item['stageEvidenceIssues'],
            priorNativeDraftPreviews=[r for r in snapshot['nativePreflightReceipts'] if r['slug']==item['slug']],
            nativeOrDiagramReadinessRecorded=item['codeReadyRecorded'],actualVoiceGenerated=item['actualVoiceGenerated'],
            captionArtifactsAvailable=item['captionArtifactsAvailable'],captionEvidence=item['captionEvidence'],
            finalVideoGenerated=item['fourOutputsVerified'],generatedReviewVideo=item['generatedReviewVideo'],finalOutputs=item['finalOutputs'],
            reviewEvidenceSource=item['reviewEvidenceSource'],batchCheckpoint='production/batches/tech-ten-shorts-20261030/checkpoint.json')
        # Existing human/platform records are never reset or inferred from generation.
        cp.setdefault('humanReview','pending'); cp.setdefault('actualFullListening','pending'); cp.setdefault('platformActions',False)
        repair=ROOT/'projects'/item['slug']/'production/local/audio-v1/reused-paragraph-pcm-check.json'
        if repair.exists():
            proof=read(repair)
            cp.setdefault('voiceRepair',{}).update(unchangedParagraphPcmEvidence={
                'path':str(repair.resolve()),'sha256':sha(repair),'paragraphs':proof.get('paragraphs',[]),
                'newFirstParagraphOnly':proof.get('newFirstParagraphOnly') is True,'actualListening':'pending',
                'scope':'Root recorded raw-file and normalized FLOAT32 sample identity; WAV PEAK timestamps may differ. No full-listening claim.'})
        save(path,cp)
    path=BATCH/'checkpoint.json'; cp=read(path); cp.update(snapshot)
    cp['next']='Continue evidence-backed local stages serially; resolve source/runtime holds. Full listening, moving/mobile review and human final review remain separate.'
    cp['remainingProduction']=[dict(slug=r['slug'],status=r['status'],nextPipelineStage=next((s for s in STAGES if s not in r['verifiedStages']),None),
        sourceReady=r['sourceAndFhdReady'],fourOutputsVerified=r['fourOutputsVerified'],actualFullListeningRecorded=r['actualFullListeningRecorded'],humanFinalReview=r['humanFinalReview'])
        for r in snapshot['projects'] if not r['generatedReviewVideo'] or r['humanFinalReview'] in (False,None,'pending','not-reviewed')]
    cp.setdefault('automaticBackgroundContinuationStarted',False); save(path,cp)
    # Do not reactivate a paused/disabled authorization; do not grant platform authority.
    control['explicitTechTenBatch20261030'].update(currentStage=snapshot['status'],activeGameProcesses=snapshot['activeGameProcesses'],
        localReviewVideosCompleted=snapshot['generatedReviewVideos'],checkpoint='production/batches/tech-ten-shorts-20261030/checkpoint.json')
    save(control_path,control)
    next_order=max((r.get('order',0) for r in worklist['rows']),default=0)+1
    for item in snapshot['projects']:
        matches=[r for r in worklist['rows'] if r.get('slug')==item['slug']]
        if matches: row=matches[0]
        else: row=dict(order=next_order,slug=item['slug']);next_order+=1;worklist['rows'].append(row)
        row.update(candidateId=item['candidateId'],title=item['title'],status=item['status'],production=item['status'],
            technicalReview=dict(verifiedStages=item['verifiedStages'],fourOutputsVerified=item['fourOutputsVerified'],reviewFilesGenerated=item['generatedReviewVideo'],
                captionArtifactsAvailable=item['captionArtifactsAvailable'],captionStageAdoptionPending=item['captionEvidence']['pipelineAdoptionPending']),
            review='Technical progress only; listening, moving review and human approval remain in the review ledger.',
            authorization='explicit-tech-ten-shorts-20261030',updatedAt=snapshot['recordedAt'],checkpoint='projects/'+item['slug']+'/production/checkpoint.json')
        for key,value in dict(humanReview='pending',platform='not-uploaded',youtube='not-uploaded',drive='outside-default-workflow',scheduled=False,published=False).items():
            row.setdefault(key,value)
    save(worklist_path,worklist)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--dry-run',action='store_true');args=parser.parse_args()
    snapshot=collect()
    if not args.dry_run: persist(snapshot)
    print(json.dumps(dict(batchStatus=snapshot['status'],readySources=snapshot['sourceReadyCount'],
        actualVoiceGenerated=snapshot['actualVoiceGeneratedCount'],verifiedFourOutputSets=snapshot['verifiedFourOutputSets'],
        verifiedCaptionArtifactSets=snapshot['verifiedCaptionArtifactSets'],captionSetsPendingStageAdoption=snapshot['captionSetsPendingStageAdoption'],
        completeReviewVideos=snapshot['generatedReviewVideos'],productionStageAttempts=snapshot['productionJobsStarted'],
        activeOwnedJob=snapshot['activeOwnedJob'],activeGames=[p['name'] for p in snapshot['activeGameProcesses']],
        projectStatuses={r['slug']:r['status'] for r in snapshot['projects']},dryRun=args.dry_run),ensure_ascii=False))


if __name__=='__main__': main()
