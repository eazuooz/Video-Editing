"""Capture measured A02 scenes sequentially with exact profile/hash checks."""
from pathlib import Path
import subprocess,sys
import capture_grid as cg
H=Path(__file__).resolve().parent
R=H.parents[3]
L=H.parent/'local/grid-v1'
def main():
    plan=cg.read(H/'edit-plan.json');book=cg.read(H/'measured-native-profiles.json')
    assert plan['episode']=='A02' and plan['revision']=='grid-v1'
    unity_book=cg.read(cg.PROFILE)
    assert unity_book==book,'Freeze/import the exact measured profile book first.'
    queue=plan['nativeCaptureQueue']
    for index,item in enumerate(queue,1):
        cg.authorize()
        out=L/'render'/item['revision']/item['mode']
        receipt=out/'render-success.json'
        if receipt.exists():
            r=cg.read(receipt);q=cg.read(out/'request.json')
            assert r['status']=='complete' and r['completed']==item['frames'] and q['frames']==item['frames']
            assert q.get('presentationId')==item['presentation'] and (out/'unity.mp4').is_file()
            print('REUSE',index,len(queue),item['id'],flush=True);continue
        assert not out.exists(),'Preserve incomplete output and inspect before retry: '+str(out)
        args=[sys.executable,'-X','utf8',str(H/'capture_grid.py'),'--action','render','--cut',item['mode'],
              '--revision',item['revision'],'--frames',str(item['frames']),'--presentation',item['presentation']]
        print('CAPTURE',index,len(queue),item['id'],item['frames'],flush=True)
        subprocess.run(args,cwd=R,check=True)
    print('A02 native capture queue complete; final compositing/QA remain.',flush=True)
if __name__=='__main__':main()
