"""Selected source bank, not final timing or caption-pixel approval."""
import hashlib,json,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[4];PR=Path(__file__).parent
NODE='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,d):
    p=Path(p);t=p.with_name(p.name+'.tmp-'+str(os.getpid()));t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(t,p)
def main():
    p=ROOT/'shared/output/presenting-game-scores/balatro-countup-framing-v4/execution.json';v=read(p)
    assert v['exitCode']==0 and v['sampleCount']==10 and v['boardCount']==2
    for r in v['images']+v['boards']:assert sha(r['path'])==r['sha256']
    save(PR/'balatro-countup-framing-direct-review-v4.json',dict(reviewedAt=now(),execution=str(p),executionSha256=sha(p),
        reviewedBoards=[1,2],sampleCount=10,allListedHashesMatched=True,allListedBoardsDirectlyRead=True,
        framing='Full-width original closeup shifted48px upward at scale1, same-source blurred lower48px fill.',
        preservedVisibleFields=['Five of a Kind lvl5','chip number','multiplier number','enlarging/rotating number glyphs'],
        sourceAlreadyTruncatedRoundScore=True,noClaimAboutRoundTotal=True,
        sourceFramingSamplesApproved=True,captionMaxLines=1,captionCenter=[960,970],
        finalNarrationCaptionPixelsApproved=False,allNativeFramesDirectlyReviewed=False,allFinalPixelsReviewed=False,rasterGitAdditions=0))
    trial=read(ROOT/'shared/output/presenting-game-scores/native-cut-trials-v1/execution-resume-v1.json')
    sources=[];cuts=[]
    contexts={
        'classic-01':('02-score-and-lines','Placement changes SCORE while LINES can remain unchanged; then a line clear changes both.','Separate result measure from quantity/progress; no exact formula claim.'),
        'classic-02':('03-same-count','Both players reach the same line count with different scores during live placement.','Two equal-height line counters versus different score towers.'),
        'classic-03':('07-name-and-unit','SCORE, LINES and signed differences stay labeled during play.','Attach a name and unit to each quantity; no health or ability diagnosis.'),
        'classic-04':('09-feedback-hierarchy','Score and line fields update as pieces drop and rows clear, while both totals remain available.','Persistent total and transient feedback have different roles.'),
        'modern-01':('04-evaluation-weights','T-SPIN DOUBLE and BACK-TO-BACK notices appear with changing scores/lines.','A score can encode a chosen evaluation; footage does not reveal full weights.'),
        'modern-02':('05-events-and-total','TETRIS/BACK-TO-BACK notifications and score changes accompany row clears.','Explain the event without claiming every scoring cause is visible.'),
        'modern-03':('06-relative-gap','Both LINES are27 at f2915, scores14096 and17016 with signed difference2920.','Absolute total and relative comparison are different displays.'),
        'modern-04':('06-relative-gap','At f3455 left29lines/19919 vs right32lines/19778, left+141; subsequent samples change the lead.','A point lead differs from a lead in lines; never infer final winner.'),
        'modern-05':('10-audit-and-close','Placement, line clears and score differences continue before the top-out/results screen.','Audit meaning, comparison reference and legibility during action; exclude results/waits.')}
    for s in trial['sources']:
        if s['name'] not in ['classic','modern','balatro']:continue
        sources.append(dict(name=s['name'],rawPath=s['rawPath'],sha256=s['rawSha256'],nativeFrameCount=s['nativeFrameCount'],ptsPath=s['ptsPath'],ptsSha256=s['ptsSha256'],
            nativeFps={'classic':'25/1','modern':'30000/1001','balatro':'30/1'}[s['name']],timebase='1/25000' if s['name']=='classic' else '1/30000',
            sourceAudioSelected=False,rights='Official owner press/B-roll with read reuse conditions; original commentary and no source music. Final public-rights approval pending.',
            officialUrl='https://playbalatro.com/' if s['name']=='balatro' else 'https://www.tetriseffect.game/connected/media/',
            recordingOwner='LocalThunk/Playstack' if s['name']=='balatro' else 'Enhance Games',
            sourceVersion='Historic official press master, not current patch proof.' if s['name']=='balatro' else 'Official TEC press B-roll; not current patch proof.'))
        if s['name']=='balatro':
            for ident,lo,hi,variant,action in [
                ('balatro-hand',1710,1801,'original-full-frame-one-line-caption','Five selected A cards react with +10/Mult notifications; unselected lower cards are not the observation target.'),
                ('balatro-countup',1810,1887,'shift-y48-same-frame-blur-fill-one-line-caption','Five of a Kind lvl5, chips and multiplier enlarge and count upward; original montage closeup not a full run.')]:
                cuts.append(dict(cutId=ident,source='balatro',startFrame=lo,endFrameExclusive=hi,startPts=lo*1000,lastPts=(hi-1)*1000,endPtsExclusive=hi*1000,timebase='1/30000',startSeconds=lo/30,endSecondsExclusive=hi/30,durationSeconds=(hi-lo)/30,
                    scene='08-scoring-feedback',visibleAction=action,diagramConnection='Separate hand/event name, chips and multiplier, then animate their contribution; no exact optimal strategy or final round total claim.',framing=variant,captionMaxLines=1,sourceSamplesDirectlyReviewed=True,actualNarrationCuePixelsApproved=False))
            continue
        for c in s['cuts']:
            c=dict(c);ident=c['cutId']
            if ident=='classic-01':c.update(startFrame=50,startPts=50000,startSeconds=2.0,sampledNativeFrames=[n for n in c['sampledNativeFrames'] if n>=50])
            if ident=='modern-01':c.update(startFrame=607,startPts=607607,startSeconds=607607/30000,sampledNativeFrames=[n for n in c['sampledNativeFrames'] if n>=607])
            tb=25000 if s['name']=='classic' else 30000
            step=1000 if s['name']=='classic' else 1001
            c.update(source=s['name'],endPtsExclusive=c['endFrameExclusive']*step,timebase=f'1/{tb}',endSecondsExclusive=c['endFrameExclusive']*step/tb,
                durationSeconds=(c['endFrameExclusive']-c['startFrame'])*step/tb,scene=contexts[ident][0],visibleAction=contexts[ident][1],diagramConnection=contexts[ident][2],
                framing='shift-y120-same-frame-blur-fill',captionMaxLines=2,sourceSamplesDirectlyReviewed=True,actualNarrationCuePixelsApproved=False,directReview=True,adopted=True)
            cuts.append(c)
    assert len(cuts)==11
    bank=dict(schemaVersion=4,slug='presenting-game-scores',createdAt=now(),sources=sources,cuts=cuts,
        selectedMaximumUniqueActionSeconds=sum(c['durationSeconds'] for c in cuts),
        sourceSamplesAndFramingApproved=True,allNativeFramesDirectlyReviewed=False,wholeContinuousPlaybackDirectlyWatched=False,
        finalMeasuredTimingApproved=False,bodyRatioApproved=False,allFinalPixelsReviewed=False,sourceAudioSelected=False,
        publicRightsApproved=False,newRasterGitAdditions=0,
        rejected=[dict(game='Ballionaire',reason='Raw Fury requires a functional product link; adoption held rather than silently disregarding the condition under public-credit omission preference.'),
            dict(game='Balatro',interval='11.4-18.9',reason='Ending grey game-over and lower UI caption conflict; not counted as actual action.'),
            dict(game='Balatro',interval='53.4-57',reason='Inventory/tarot transition excluded; only observed scored-hand and count-up shots retained.'),
            dict(game='Tetris Effect: Connected',interval='Classic0-2;139.75-end;Modern0-20.2535667;149.75-end',reason='Black/readiness/top-out/wait/static results/EXP are excluded.')],
        reviewProofs=[str(PR/'native-framing-direct-review-v2.json'),str(PR/'balatro-native-pre-clearance-direct-review-v3.json'),str(PR/'balatro-countup-framing-direct-review-v4.json')],
        caution='Selected maximum is a source bank, not a finished timeline or actual60:40 approval. Subdivision/trimming follows measured approved narration; no loop or slowdown.')
    assert not (PR/'source-action-bank-v4.json').exists();save(PR/'source-action-bank-v4.json',bank)
    r=subprocess.run([NODE,'scripts/review-video-duplicates.cjs','presenting-game-scores','--check'],cwd=ROOT,capture_output=True,text=True)
    assert r.returncode==0,r.stdout+r.stderr
    qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);item=next(i for i in q['items'] if i['slug']=='presenting-game-scores')
    item['stage']='reviewed-source-bank-independent-script-next'
    item['preflight'].update(officialSourcesTechnicallyVerified=4,observationSamplesRead=886,observationBoardsRead=149,
        nativeTrialSamplesRead=295,nativeTrialBoardsRead=50,reframedTetrisSamplesRead=133,reframedTetrisBoardsRead=23,
        balatroAdditionalNativeSamplesRead=25,balatroNativeBoardsRead=5,balatroCountupRepairSamplesRead=10,balatroCountupRepairBoardsRead=2,
        nativeIntervalsApproved=True,footageAdopted=False,sourceActionBank=str((PR/'source-action-bank-v4.json').relative_to(ROOT)).replace('\\','/'),
        sourceActionBankSha256=sha(PR/'source-action-bank-v4.json'),sourceBankMaximumActionSeconds=bank['selectedMaximumUniqueActionSeconds'],
        duplicateCheckExit=0,newProjectCreated=False,recordedAt=now(),needsCurrentDuplicateCheckBeforeProjectCreation=True)
    item['nextAction']='Current duplicate check, create independent KO/EN with reviewed source-bank action connections and overview; research-black-v1 projected explanations. Measured timing and all final-media gates remain pending.'
    jobs=[('tetris-classic-official',53093,45460,0),('tetris-modern-official',14562,59704,0),('native-trial-filter-failure',14745,None,1),('native-trial-preserved-PTS-recovery',48612,29712,0),('cached-tetris-framing',62241,68048,0),('balatro-only-missing-native-targets',17008,50928,0)]
    oldnames={j['name'] for j in item['closedSourceJobs']}
    item['closedSourceJobs'] += [dict(name=n,sessionId=s,pid=p,exitCode=e) for n,s,p,e in jobs if n not in oldnames]
    item['ownedJob'].update(resourceObservation=str((PR/'resources-before-balatro-native-v3.json').relative_to(ROOT)).replace('\\','/'),heavyWorkerRunning=False,researchPauseOrProcessChanges=0)
    save(qp,q)
    rp=ROOT/'production/batches/sakurai-planning-game-design/README.md';text=rp.read_text(encoding='utf-8')
    para=f"2026-10-09 latest source checkpoint: presenting-game-scores has a current distinct check and eleven source-bank intervals, maximum{bank['selectedMaximumUniqueActionSeconds']:.6f}s of unique normal-speed action from official TEC Classic/Score Attack and two Balatro scored-hand/count-up shots. All149 nominal boards/886 samples,50 native trial boards/295 overlays,23 reframed Tetris boards/133 samples,5 Balatro native boards/25 samples and2 corrected count-up boards/10 samples were directly read. The uncropped caption collisions and original filter failure are preserved history. Source-bank review is not final timing, actual-narration caption or final-pixel approval. Four originals and all QA rasters stay local; no new project/TTS/media/upload yet. Black projected explanations are next. Research processes remain untouched. Fifteen completed private deliveries and one content duplicate remain preserved.\n\n"
    first=text.find('\n\n');text=text[:first+2]+para+text[first+2:];rp.write_text(text,encoding='utf-8')
    print(json.dumps(dict(selectedCuts=11,maxSeconds=bank['selectedMaximumUniqueActionSeconds'],duplicateCheckExit=0,projectCreated=False)))
if __name__=='__main__':main()
