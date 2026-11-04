"""Bounded ending fade from exact raw; preserve v1, PCM, captions and native scenes.

CPU preflight is separate from guarded costly execution. No project selection,
common source or platform state is changed by this helper.
"""
from pathlib import Path
import argparse, hashlib, inspect, json, os, sys, types, uuid

ROOT = Path('D:/Github/VideoEditing')
B = ROOT / 'production/batches/tech-ten-shorts-20261030'
sys.path.insert(0, str(B))
import scoped_pipeline as sp
from batch_job_lock import SerialJobLock
import importlib.util
s = importlib.util.spec_from_file_location('ending_runner', B / 'run-batch.py')
r = importlib.util.module_from_spec(s); s.loader.exec_module(r)
SLUG = 'shorts-batman-origins-snow-below-camera'
C = r.make_context(SLUG); P = C['P']; LOCAL = C['LOCAL']; A = C['L']
OLD = LOCAL / 'final-reviewed-v1'; OUT = LOCAL / 'final-reviewed-v2'
RAW = LOCAL / 'motion-canvas-output/shorts-batman-origins-snow-below-camera-tech-ten-v1.mp4'
PREP = LOCAL / 'ending-v2-preparation'
PINS = {
    RAW: '97412f4be1e805640061ab26320d5e437078221b3e3fd401dc4e039e1ef942e0',
    LOCAL / 'unity-capture/native-receipt.json': 'dfab7ab9d61cb701055be8abdf7e6acc10946ebf46800c0f3dbb786fbc40ad2f',
    LOCAL / 'unity-capture/input-receipt.json': 'aae92b4ec2a676ca481bbf28cb8455503c486fb07783055bd9be1e9f1295f928',
    P / 'production/visual-timing.json': 'fc1f8ca1ccc04e500ac4aba92248221cc8ca2452693e983d9cfa5d8de3c56bba',
    P / 'script/captions.json': '420973c076d919849c97f3fa8955c493bc413bc802613c10001344945681b4db',
    A / 'final-mix.m4a': 'bd94269c329483de0fde6bf0162df63707238393a0736d9d34a5b254659f8103',
    A / 'captions.ko.ass': '7f8441d7adad90b99f8a253606e37db6b3d1e712384b2ac0dbd220dbb0ea4f24',
    LOCAL / 'static-header-v1.png': 'f8afd148f4b142c21a7f279f57bdef7c2609da6c431b00f95dfbbf561f2f390a',
    ROOT / 'projects/shorts-factorio-belt-gaps/production/finish-video.py': 'c6657c9fdef7dd4c1951784ac86201b7180e51a3e1305281d6114d108af3bd0f',
    ROOT / 'projects/shorts-factorio-belt-gaps/production/build-review.py': 'e4d437066e470bb5941ae4ab207f51b61a9d556cbd5bff1cad61677b7954835c',
    B / 'run-batch.py': 'f03a9eda694867d0c500418412d53770ccf372b931bb5db35ca4f9e8c1f79b76',
    B / 'scoped_pipeline.py': 'af4a709b534c953914419a0f4004037dbfae9a29e6011d8de80876846c2448f4',
}
BASE_FILTER = '[0:v][2:v]overlay=0:0:format=auto[v]'
ENDING_FILTER = '[0:v][2:v]overlay=0:0:format=auto,fade=t=out:start_frame=3028:nb_frames=12[v]'

def check_inputs():
    for path, digest in PINS.items():
        if not path.is_file() or r.sha(path) != digest:
            raise RuntimeError('Ending-v2 input changed: ' + str(path))
    delivery = r.read(OLD / 'delivery.json')
    for item in delivery['files']:
        file = Path(item['path'])
        if r.sha(file) != item['sha256'] or file.stat().st_size != item['bytes']:
            raise RuntimeError('Preserved v1 output changed: ' + str(file))
    assert r.read(P / 'script/captions.json')['frames'] == 3064
    timing = r.read(P / 'production/visual-timing.json')
    assert timing['actualGameSeconds'] == 7 and timing['sections'][-2]['endFrame'] == 3040
    assert timing['sections'][-1]['startFrame'] == 3040 and timing['sections'][-1]['endFrame'] == 3064
    assert max(q['endFrame'] for q in r.read(P / 'script/captions.json')['cues']) == 3037
    return delivery

def prepare():
    delivery = check_inputs(); PREP.mkdir(exist_ok=True)
    module, _, record = sp.load_template(SLUG, 'finish-video'); module.L = OUT
    acceptance = module.verify_pair_inputs(RAW, r.read(P / 'script/captions.json'), LOCAL / 'static-header-v1.png')
    receipt = dict(schemaVersion=1, correction='purposeful-ending-fade-v2', frames=3064,
        original=delivery, pins=[r.artifact(p) for p in PINS], helper=r.artifact(Path(__file__)),
        originalFilter=BASE_FILTER, selectedFilter=ENDING_FILTER,
        fadeFrames=[3028,3040], blackTailFrames=[3040,3064], actualFootageSeconds=7,
        rationale='Fade the final actual-game conclusion to black, keeping the existing0.4-second audio tail. Suppress the unintended new Unity scene. No frozen/looped footage or footage-share padding.',
        inputAcceptance=acceptance, nativeRecapture=False, audioChange=False, captionDataChange=False,
        oldFinalPreserved=True, complete=False, humanListening='pending', humanReview='pending')
    prepared_path = PREP / 'prepared.json'
    if prepared_path.exists() and r.read(prepared_path) != receipt:
        archive = PREP / ('prepared-preserved-' + r.sha(prepared_path) + '.json')
        if not archive.exists():
            archive.write_bytes(prepared_path.read_bytes())
    r.save(prepared_path, receipt)
    print(json.dumps(receipt, ensure_ascii=False, indent=2))

def verify_ending(module):
    import numpy as np
    packet_hashes = {}
    for name, path in [('v1-clean', OLD/'clean.mp4'), ('v1-captioned', OLD/'captioned.mp4'),
                       ('v2-clean', OUT/'clean.mp4'), ('v2-captioned', OUT/'captioned.mp4'), ('source-mix', A/'final-mix.m4a')]:
        data = module.run(['ffmpeg','-v','error','-i',str(path),'-map','0:a:0','-c','copy','-f','adts','pipe:1'])
        packet_hashes[name] = hashlib.sha256(data).hexdigest()
    assert len(set(packet_hashes.values())) == 1, 'Exact AAC packets changed'
    body = [180,800,1500,2100,2700,3000,3027]
    tail = [3028,3033,3039,3040,3051,3063]
    def decode(path, indices):
        expression = '+'.join('eq(n\\,'+str(i)+')' for i in indices)
        data = module.run(['ffmpeg','-v','error','-threads','2','-i',str(path),'-vf','select='+expression,
            '-fps_mode','vfr','-frames:v',str(len(indices)),'-pix_fmt','rgb24','-threads','1','-f','rawvideo','pipe:1'])
        assert len(data) == len(indices)*1080*1920*3
        return np.frombuffer(data,dtype=np.uint8).reshape(len(indices),1920,1080,3)
    previous = decode(OLD/'captioned.mp4',body)
    current = decode(OUT/'captioned.mp4',body+tail)
    comparisons = []
    for i, frame in enumerate(body):
        diff = previous[i].astype(np.float32)-current[i].astype(np.float32)
        row = dict(frame=frame,meanAbsolutePixelDifference=float(np.abs(diff).mean()),
            meanSquaredPixelDifference=float((diff*diff).mean()),maximumPixelDifference=float(np.abs(diff).max()))
        assert row['meanAbsolutePixelDifference'] < 2, 'Unexpected broad body change: '+str(row)
        comparisons.append(row)
    tail_stats = [dict(frame=n,mean=float(current[len(body)+i].mean()),maximum=int(current[len(body)+i].max())) for i,n in enumerate(tail)]
    assert all(row['maximum']<=2 for row in tail_stats if row['frame']>=3040), 'Tail is not black'
    r.save(OUT/'ending-v2-verification.json',dict(aacPacketsAllIdentical=True,aacPacketHashes=packet_hashes,
        bodySamples=comparisons,tailSamples=tail_stats,
        bodyMeaning='Same pinned raw/header/caption inputs and identity filter before3028. Lossy re-encoding can change decoded quantization; sample differences are measured, not claimed bit-identical.',
        fullDurationFrames=3064,captionDataUnchanged=True,actualFullListening='pending',humanReview='pending'))

def execute():
    prepared = r.read(PREP / 'prepared.json'); check_inputs()
    assert prepared['helper']['sha256'] == r.sha(Path(__file__))
    assert not OUT.exists(), 'Preserve any previous v2 attempt; inspect before retry.'
    with SerialJobLock(SLUG, 'ending-v2-pair'):
        r.safe_resources(C, 'ending-v2-pair')
        import psutil
        lease = ROOT / 'shared/output/GPU_HANDOFF.json'; token = uuid.uuid4().hex
        with lease.open('x', encoding='utf8') as f:
            json.dump(dict(project=SLUG, state='ending-v2-pair-qa', token=token,
                coordinator=dict(pid=os.getpid(), createTime=psutil.Process().create_time())), f)
        try:
            module, _, _ = sp.load_template(SLUG, 'finish-video'); module.L = OUT
            original_run = module.run; changes = []
            def scoped_run(args):
                args = list(args)
                if BASE_FILTER in args:
                    assert not changes, 'Exactly one clean ending overlay is expected.'
                    args[args.index(BASE_FILTER)] = ENDING_FILTER; changes.append(ENDING_FILTER)
                return original_run(args)
            module.run = scoped_run
            print('START Batman ending-v2 pair', flush=True); module.pair(RAW); assert changes == [ENDING_FILTER]
            pair = r.read(OUT / 'pair-build.json')
            pair['endingCorrection'] = dict(preparedSha256=r.sha(PREP / 'prepared.json'), helperSha256=r.sha(Path(__file__)), filter=ENDING_FILTER, originalFramesUnchangedUntil=3028, blackTail=[3040,3064], oldMasterSha256='e641cec700642682cb1e9540b611dd7c83fe4240a9eacd981e7562dab7f36a5b')
            r.save(OUT / 'pair-build.json', pair)
            print('START Batman ending-v2 integrity', flush=True); module.integrity()
            print('START Batman ending-v2 packet/pixel verification', flush=True); verify_ending(module)
            print('START Batman ending-v2 qa', flush=True); module.qa()
            # Keep the standard review algorithm; adapt only its selected output path.
            review, _, _ = sp.load_template(SLUG, 'build-review')
            source = inspect.getsource(review.main).replace('팩토리오 쇼츠 검수', '게임 기술 쇼츠 검수')
            old = "out=P/project['currentFinalDirectory']"; assert source.count(old) == 1
            namespace = dict(vars(review)); namespace['ENDING_V2_OUT'] = OUT
            exec(compile(source.replace(old, 'out=ENDING_V2_OUT'), str(__file__) + ':review-output-only', 'exec'), namespace)
            namespace['main']()
            check_inputs()
            r.save(OUT / 'ending-v2-complete.json', dict(status='technical-output-complete-sampled-tail-review-pending',
                preparedSha256=r.sha(PREP / 'prepared.json'), helperSha256=r.sha(Path(__file__)),
                files=r.read(OUT / 'delivery.json')['files'], originalInputsPreserved=True,
                audioIdentical=r.read(OUT / 'integrity.json')['identicalAac'],
                captionFilesIdentical=all(r.sha(OUT / n)==r.sha(OLD / n) for n in ['captions.ko.srt','captions.en.srt']),
                actualListening='pending', humanReview='pending'))
        finally:
            if lease.exists() and r.read(lease).get('token') == token:
                lease.unlink()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--execute', action='store_true'); args = parser.parse_args()
    execute() if args.execute else prepare()
