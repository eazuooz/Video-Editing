"""Prepare a guarded six-scene worker from the preserved pilot renderer."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
folder=Path(__file__).parent
dest=folder/'render-polar-six-gameplay-pilots-v4.py';assert not dest.exists()
s=(folder/'render-polar-five-gameplay-pilots-v1.py').read_text(encoding='utf-8')
s=s.replace('five narrated gameplay overlays; scene08 remains held.','six repaired narrated gameplay overlays; previous pilots are preserved.')
s=s.replace('import os, json, subprocess, importlib.util','import os, json, subprocess, importlib.util, argparse')
s=s.replace('five-moving-pilots-v1','six-moving-pilots-v4').replace('five-moving-pilots-execution-v1','six-moving-pilots-execution-v4')
s=s.replace('prepare-polar-remaining-annotations-v3.py','prepare-polar-remaining-annotations-v4.py')
s=s.replace('remaining-editorial-annotation-preparation-v3.json','remaining-editorial-annotation-preparation-v4.json')
s=s.replace('remaining-annotation-sampled-review-v1.json','remaining-editorial-annotation-direct-review-v4.json')
s=s.replace("assert proof['fiveUnchangedSourceSceneLayoutsApproved'] and not proof['scene08ReframeApproved']", "assert proof['sixBoundedPreparedLayoutsApproved'] and proof['all150PreparedSamplesAnd27BoardsDirectlyRead']")
s=s.replace("            if sid=='08':continue\n",'')
s=s.replace("      'scene08HeldReason':'One jump-end helmet partly lost to the180px crop; adjust source interval before rendering scene08.',", "      'scene08RepairEvidence':'scene08-selected-source-direct-review-v2.json',")
s=s.replace("'scenes':5", "'scenes':6")
needle='def main():\n'
guard="""def main():
    ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);ap.add_argument('--asr-outer-exit-code',required=True,type=int);args=ap.parse_args()
    assert args.asr_outer_exit_code==0
    asr=json.loads((OUT/'current-whole-audio-asr-execution-v1.json').read_text(encoding='utf-8'))
    assert asr['exitCode']==0 and asr['completed']==38
    assert not psutil.pid_exists(asr['pid']) or psutil.Process(asr['pid']).create_time()!=asr['createTime']
    resource=json.loads((ROOT/args.resource).read_text(encoding='utf-8'))
    assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8000000
    assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'])).total_seconds()<240
"""
assert needle in s;s=s.replace(needle,guard,1)
s=s.replace("'startedAt':datetime.now(timezone.utc).isoformat(),", "'resourceEvidence':args.resource,'priorAsrOuterExitCode':args.asr_outer_exit_code,'startedAt':datetime.now(timezone.utc).isoformat(),",1)
dest.write_text(s,encoding='utf-8')
compile(s,str(dest),'exec')
print('Prepared only: six moving pilots v4; no rendering started.')
