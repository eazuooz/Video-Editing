"""Verify all native rattan captures once; keep observed contacts separate from human approval."""
from pathlib import Path
import datetime,hashlib,json,subprocess

H=Path(__file__).resolve().parent;L=H/'local/living-room-v11'
def run(args):return subprocess.run(list(map(str,args)),check=True,capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW)
results=[]
for folder,expected in [('walk-source',720),('sofa-entry',1440),('',5400)]:
    source=L/folder/'unity-native-clean.mp4'
    probe=json.loads(run(['ffprobe','-v','error','-select_streams','v:0','-show_frames','-show_streams','-show_format','-show_entries','frame=best_effort_timestamp_time:stream=width,height,r_frame_rate,codec_name:format=duration','-of','json',source]).stdout)
    stream=probe['streams'][0]
    assert (stream['width'],stream['height'],stream['r_frame_rate'])==(1920,1080,'60/1')
    frames=[float(f['best_effort_timestamp_time']) for f in probe['frames']]
    maximum=max(abs(b-a-1/60) for a,b in zip(frames,frames[1:]))
    assert len(frames)==expected and maximum<.000003
    assert abs(float(probe['format']['duration'])-expected/60)<.025
    run(['ffmpeg','-hide_banner','-v','error','-threads','2','-i',source,'-f','null','-'])
    with source.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
    results.append({'path':source.relative_to(H.parent).as_posix(),'sha256':digest,'bytes':source.stat().st_size,'width':1920,'height':1080,'fps':60,'frames':len(frames),'durationSeconds':expected/60,'maximumFrameDeltaError':maximum,'fullDecodePassed':True})
record={'revision':'living-room-v11 actual Tripo rattan furniture','checkedAtKst':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),'media':results,'observations':{'furnitureTextures':'Actual exported 4096px BaseColor and 2048px Normal, no upscaling; URP Lit material.','nativeEntry':'Observed walk approach, slow sit, lift feet above the tabletop before extending, then raise the book.','settledFeet':'Both actual ankle targets reached sofa-local x=-.48/-.22,y=.515,z=.73 to the reported .0001 m precision; former z=.84 exceeded leg reach.','bookContacts':'Front and reverse native screenshots inspected; reading arm clips and IK support the cover.','cat':'Same real Tripo calico and localized chest/tail deformation; prior face-stability sample retained.'},'nativeMotionSource':'KayKit sit/stand plus EmacEArt PHILIPP reclining body and masked reading arms; Tripo character Walk/Idle','evidence':['production/local/living-room-v11/contact-book.png','production/local/living-room-v11/contact-reverse.png','production/local/living-room-v11/sofa-entry/contact-sheet.jpg'],'webBuildQa':'pending separate browser check','wholeHumanListening':'pending','humanFinalReview':False}
(H/'rattan-v11-native-qa.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps({'captures':len(results),'frames':sum(x['frames'] for x in results),'allFhd60':True,'fullDecodesPassed':True}))
