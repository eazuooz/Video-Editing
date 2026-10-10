from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
dest=B/'assemble-motion-current-pair-v2.py';assert not dest.exists()
s=(B/'assemble-motion-current-pair-v1.py').read_text('utf-8')
s=s.replace('/motion/final-pair-v1','/motion/final-pair-v2').replace("sp=R/'final-pair-execution-v1.json'","sp=R/'final-pair-execution-v2.json'")
s=s.replace('assembling-measured14-scenes-current-pair','assembling-v2-pair-with-only-two-reviewed-visual-repairs')
s=s.replace('oldPcmOrWhiteScenesRegenerated=False','oldPcmRegenerated=False,other18PiecesRegenerated=False,twoExplanationTargetsReplaced=True')
guard="""    repair=read(R/'two-target-repair-direct-review-v3.json')
    assert repair['allSelectedTargetSamplesDirectlyRead'] and repair['normalSpeedTargetMotionApproved'] and not repair['unresolved']
    previous=read(R/'final-pair-execution-v1.json');assert previous['exitCode']==0
    previousClosure=read(R/'final-pair-execution-v1.session.json');assert previousClosure['actualOuterExitCode']==0 and not previousClosure['workerCurrentlyAlive']
"""
s=s.replace("    approved=read(R/'current-mixed-complete-direct-review-v1.json')",guard+"    approved=read(R/'current-mixed-complete-direct-review-v1.json')")
a=s.index("    enc=['-an'");b=s.index("        concat=LOCAL/'current-concat.ffconcat'",a)
s=s[:a]+"""    checkpoint()
    try:
        files=[]
        replacement={6:next(x for x in repair['targets'] if x['id']=='02'),12:next(x for x in repair['targets'] if x['id']=='06b')}
        for i,v in enumerate(previous['pieces']):
            p=ROOT/v['path'];assert sha(p)==v['sha256']
            if i in replacement:
                r=replacement[i];p=ROOT/r['cleanPath'];assert sha(p)==r['cleanSha256'] and r['frames']==v['frames']
                ptscheck(p,v['frames'])
                state['pieces'].append(dict(path=rel(p),sha256=sha(p),frames=v['frames'],kind='reviewed-target-explanation-repair',reencoded=False,allPts1500Verified=True,replacedBaselinePath=v['path'],replacedBaselineSha256=v['sha256'],targetReview='two-target-repair-direct-review-v3.json'))
            else:
                retainedRow=dict(v);retainedRow.update(reencoded=False,reusedByteIdenticalFromPairV1=True)
                state['pieces'].append(retainedRow)
            files.append(p);checkpoint()
        assert len(files)==20 and sum(v['frames'] for v in state['pieces'])==plan['totalFrames']
        state['preservedByteIdenticalPieceCount']=18
"""+s[b:]
s=s.replace('current-pair-complete-awaiting-direct-final-pixels','current-v2-pair-complete-awaiting-direct-final-pixels')
s=s.replace('currentAudioPacketProof=originalaudio,','currentAudioPacketProof=originalaudio,visualRepairReview=\'two-target-repair-direct-review-v3.json\',')
dest.write_text(s,'utf-8')
print('Prepared pair v2 worker; no execution, no approval.')
