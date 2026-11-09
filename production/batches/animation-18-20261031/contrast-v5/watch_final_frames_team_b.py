"""Finite seven-episode CPU1 QA extractor; never edits production media.

An extracted image is not an inspected image. Parent/agent must read each
current-master sample before changing the separate visual QA status.
"""
import json,time
import qa_final_episode_frames as qa

IDS=['A06','A08','A10','A12','A14','A16','A18']


def main():
    announced=set();prior={};deadline=time.monotonic()+6*3600
    print(json.dumps({'watching':IDS,'scope':'Finite current animation contrast-v5 review; CPU1 extraction only'}),flush=True)
    while time.monotonic()<deadline:
        passed=[]
        for ep in IDS:
            try:
                proof,*_=qa.identity(ep)
                digest=proof['masterSha256'];key=(ep,digest)
                report=qa.H/'visual-qa'/(ep+'.json')
                old=qa.read(report)if report.exists()else{}
                if old.get('proof',{}).get('masterSha256')==digest and old.get('status')=='sampled-encoded-visual-qa-passed':
                    passed.append(ep);continue
                if key in announced:continue
                if old.get('proof',{}).get('masterSha256')!=digest:
                    result=qa.extract(ep)
                else:
                    result={'episode':ep,'masterSha256':digest,'report':str(report),'contactSheets':old.get('contactSheets',[])}
                announced.add(key)
                print(json.dumps({'inspectionReady':result},ensure_ascii=False),flush=True)
                prior.pop(ep,None)
            except (AssertionError,OSError,KeyError,StopIteration,ValueError)as e:
                reason=str(e)[:220]
                if prior.get(ep)!=reason:
                    print(json.dumps({'waiting':ep,'reason':reason},ensure_ascii=False),flush=True);prior[ep]=reason
        if len(passed)==len(IDS):
            print(json.dumps({'status':'all-seven-current-masters-model-sampled-inspection-recorded','episodes':passed}),flush=True);return
        time.sleep(25)
    print(json.dumps({'status':'finite-watch-expired-incomplete','scope':IDS}),flush=True)


if __name__=='__main__':main()
