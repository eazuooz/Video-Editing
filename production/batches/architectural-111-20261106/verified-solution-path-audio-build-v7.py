"""Read-only existing11.05 mix verifier; no FFmpeg, worker, resource or model.

The pinned verifier core reconstructs actual accepted scalar files, ONE whole
2x voice resample, uniform voice gain, music-only loop/duck/headroom and sum.
It checks saved actual tool receipts; it does not remeasure LUFS or claim hearing.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
PRODUCER=HERE/'prepare-solution-path-audio-mix-v7.py'
PRODUCER_SHA='ce2fa55a6a4d161be2485020ac669327273a287fcb45fe9e310b97c810067238'
SELF_SHA=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
class Pending(RuntimeError):pass
def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def verified_audio_build(path):
    if PRODUCER_SHA is None:raise Pending('Waiting for reviewed frozen V5 producer pin')
    if sha(__file__)!=SELF_SHA or sha(PRODUCER)!=PRODUCER_SHA:raise Pending('Reviewed immutable mix verifier/producer changed')
    spec=importlib.util.spec_from_file_location('solution_audio_actual_rebuild_v7',PRODUCER)
    source=importlib.util.module_from_spec(spec);sys.modules[spec.name]=source;spec.loader.exec_module(source)
    try:result=source.verify_existing_core(path)
    except source.Pending as error:raise Pending(str(error)) from error
    if sha(PRODUCER)!=PRODUCER_SHA or sha(__file__)!=SELF_SHA:raise Pending('Mix verification source changed during existing-artifact validation')
    return result
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--audio-build');args=parser.parse_args()
    if not args.audio_build:
        print(json.dumps(dict(ready=False,reason='Exact actual11.05 audio-build path required',writesPerformed=False,ffmpegStarted=False,modelLoaded=False)));return
    try:
        report=verified_audio_build(args.audio_build)
        print(json.dumps(dict(ready=True,fingerprint=report['fingerprint'],audioBuild=dict(path=str(Path(args.audio_build).resolve()),sha256=sha(args.audio_build)),
            mixWav=report['mixWav'],exactFloat32RebuildVerified=True,actualLoudnessRemeasured=False,writesPerformed=False,
            ffmpegStarted=False,actualListening=False,humanApproval=False),ensure_ascii=False))
    except (Pending,FileNotFoundError) as error:
        print(json.dumps(dict(ready=False,reason=str(error),writesPerformed=False,ffmpegStarted=False,actualListening=False,humanApproval=False)))
if __name__=='__main__':main()
