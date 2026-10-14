"""Prepare a final244-cue pixel observer bound to the reviewed detailed pairV3."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
source=(B/'extract-orientation-current34-pixels-v1.py').read_text('utf-8-sig')
source=source.replace('current34-{a.mode}-pixel-v1','current34-{a.mode}-pixel-v2').replace('current34-{a.mode}-pixel-execution-v1','current34-{a.mode}-pixel-execution-v2').replace('current34-final-pair-execution-v1.json','current34-final-pair-execution-v3.json')
anchor="        tasks=[dict(id='captioned',video=pair['path'],videoSha256=pair['sha256'],frames=worker['frames'],points=points)]"
assert source.count(anchor)==1
insert="""        inputs=read(O/'current34-assembly-inputs-v3.json')
        assert inputs['detailedExplanationPieceCount']==17 and inputs['detailedMixedPieceCount']==3
        offsets={};offset=0
        for piece in worker['pieces']:
            offsets[piece['id']]=offset;offset+=piece['frames']
        assert offset==worker['frames']
        detail=read(O/'current34-detailed-explanations-sampled-direct-review-v1.json')
        mixed=read(O/'current34-mixed-detailed-direct-review-v1.json')
        guides=read(O/'current34-guides-pixel-execution-v1.json')
        overview=read(O/'current34-overview-direct-review-v5.json')
        assert detail['all605SamplesDirectlyRead'] and mixed['all172SamplesDirectlyRead']
        assert read(O/'current34-baseline-guides-direct-review-v1.json')['all562SamplesDirectlyRead']
        # Bind the final captioned frames to every prior selected moving subject/guide sample.
        for record,key in [(detail,'rows'),(mixed,'rows'),(guides,'results')]:
            for row in record[key]:
                sid=row.get('scene',row.get('id'))
                assert sid in offsets
                for sample in row['samples']:put(offsets[sid]+sample['frame'],'reviewed-subject-or-guide-'+sid)
        # The overview record may bind its samples through rows or scenes.
        ovexec=read(O/'current34-overview-render-execution-v5.json')
        for row in ovexec['scenes']:
            for sample in row['samples']:put(offsets[row['id']]+sample['frame'],'reviewed-detailed-overview-'+row['id'])
        for piece in worker['pieces']:
            if piece['id'] not in ['intro','19','outro']:
                for f in range(offsets[piece['id']],offsets[piece['id']]+piece['frames'],60):put(f,'current-detailed-motion-'+piece['id'])
"""
source=source.replace(anchor,insert+anchor)
source=source.replace("ap.add_argument('--mode',choices=['guides','pair'],required=True)","ap.add_argument('--mode',choices=['pair'],required=True)")
resourceguard="    assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8_000_000"
source=source.replace(resourceguard,resourceguard+"\n    node='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'\n    subprocess.run([node,'scripts/review-video-duplicates.cjs','game-math-orientation-matrices','--candidate-file',str(O/'duplicate-candidate-v1.json'),'--check'],cwd=ROOT,check=True)")
detailguard="        assert inputs['detailedExplanationPieceCount']==17 and inputs['detailedMixedPieceCount']==3"
source=source.replace(detailguard,detailguard+"\n        for pk,hk in [('detailedSampleReview','detailedSampleReviewSha256'),('detailedNormalReview','detailedNormalReviewSha256'),('overviewReview','overviewReviewSha256'),('guideReview','guideReviewSha256'),('mixedDetailReview','mixedDetailReviewSha256')]:\n            assert sha(ROOT/inputs[pk])==inputs[hk]")
cmdline="            cmd=[FF,'-hide_banner','-nostdin','-v','info','-threads','2','-filter_threads','1','-i',str(video),'-vf',f\"select='{selector}',showinfo\",'-fps_mode','passthrough','-frames:v',str(len(indices)),'-threads','2',str(folder/'sample-%04d.png')]"
assert source.count(cmdline)==1
source=source.replace(cmdline,"            filterp=folder/'absolute-PTS-selection.fffilter'\n            filterp.write_text(f\"select='{selector}',showinfo\",'utf-8')\n            # Keep the complete selection in a file, below Windows argv limits.\n            cmd=[FF,'-hide_banner','-nostdin','-v','info','-threads','2','-filter_threads','1','-i',str(video),'-filter_script:v',str(filterp),'-fps_mode','passthrough','-frames:v',str(len(indices)),'-threads','2',str(folder/'sample-%04d.png')]")
p=B/'extract-orientation-current34-pixels-v2.py';assert not p.exists();p.write_text(source,'utf-8')
rec=(B/'record-orientation-current34-pixels-worker-v1.py').read_text('utf-8-sig').replace('current34-{a.mode}-pixel-execution-v1','current34-{a.mode}-pixel-execution-v2')
p=B/'record-orientation-current34-pixels-worker-v2.py';assert not p.exists();p.write_text(rec,'utf-8')
compile(source,str(B/'extract-orientation-current34-pixels-v2.py'),'exec');compile(rec,str(p),'exec')
print('Prepared pairV3-bound pixelV2 and actual-session recorder; no extraction executed.')
