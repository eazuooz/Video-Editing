"""Explicit mobile-review request: FHD60 derivative, unchanged captions and AAC audio."""
from pathlib import Path
import argparse,datetime,hashlib,json,subprocess

H=Path(__file__).resolve().parent
SOURCE=H/'local/full-video-v2/final/ai-3d-lofi-gaming-room.captioned.mp4'
FOLDER=H/'local/full-video-v2/mobile-review'
TARGET=FOLDER/'ai-3d-lofi-gaming-room.v2.mobile-fhd60.mp4'
FOLDER.mkdir(parents=True,exist_ok=True)

def run(args):return subprocess.run(list(map(str,args)),check=True,capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW)
def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def audio_hash(path):return run(['ffmpeg','-hide_banner','-v','error','-i',path,'-map','0:a:0','-c','copy','-f','hash','-hash','sha256','-']).stdout.decode().strip()

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--verify-only',action='store_true');args=parser.parse_args()
    expected='ad2e7437f7f87e63a63d135c29b32fe6077b9b218da27ff8e0ebb28ddcc70f3f'
    assert sha(SOURCE)==expected,'The explicitly labeled completed v2 baseline changed'
    if not args.verify_only:
        assert not TARGET.exists(),'Preserve the existing derivative; use --verify-only'
        base=['ffmpeg','-hide_banner','-loglevel','error','-y','-i',SOURCE,'-map','0:v:0','-c:v','libx264','-preset','fast','-b:v','1000k','-threads','4','-pix_fmt','yuv420p','-r','60','-passlogfile',FOLDER/'h264-1000k-pass']
        run(base+['-an','-pass','1','-f','null','NUL'])
        run(base+['-map','0:a:0','-c:a','copy','-pass','2','-movflags','+faststart',TARGET])
    assert TARGET.exists() and TARGET.stat().st_size<104857600
    probe=json.loads(run(['ffprobe','-v','error','-count_frames','-show_entries','stream=codec_name,codec_type,width,height,r_frame_rate,nb_read_frames,pix_fmt:format=duration','-of','json',TARGET]).stdout)
    v=next(s for s in probe['streams'] if s['codec_type']=='video')
    assert (v['codec_name'],v['width'],v['height'],v['r_frame_rate'],int(v['nb_read_frames']),v['pix_fmt'])==('h264',1920,1080,'60/1',38208,'yuv420p')
    assert abs(float(probe['format']['duration'])-636.8)<.05
    run(['ffmpeg','-hide_banner','-v','error','-threads','2','-i',TARGET,'-f','null','-'])
    pts=run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','frame=best_effort_timestamp_time','-of','csv=p=0',TARGET]).stdout.decode()
    values=[float(x.split(',')[0]) for x in pts.splitlines() if x.split(',')[0].strip()]
    error=max(abs(b-a-1/60) for a,b in zip(values,values[1:]))
    assert len(values)==38208 and error<.000003
    a,b=audio_hash(SOURCE),audio_hash(TARGET);assert a==b,'Review audio changed'
    record={
        'request':'2026-11-18 user asked to watch the complete video on mobile',
        'revision':'completed full-video-v2; before latest rattan furniture and v5 tutorial changes',
        'sourceMaster':{'path':str(SOURCE),'sha256':expected,'bytes':SOURCE.stat().st_size},
        'mobileReview':{'path':str(TARGET),'sha256':sha(TARGET),'bytes':TARGET.stat().st_size,'width':1920,'height':1080,'fps':60,'frames':38208,'durationSeconds':636.8},
        'conversion':'H.264 two-pass 1000 kbit/s, yuv420p, faststart; original burnt-in captions retained in source pixels; original AAC packets copied without re-encoding',
        'integrity':{'fullDecodePassed':True,'uniformPtsPassed':True,'maximumFrameDeltaError':error,'sameOriginalEncodedAudio':True,'aacPacketHash':a},
        'latestRattanRevisionFinalVideoAvailable':False,
        'productionMasterUnchanged':True,'replacesProductionMaster':False,
        'cloudReviewAuthorizedByThisExplicitMobileRequest':True,
        'physicalPhonePlayback':'pending user device check','humanFinalReview':False,
        'checkedAtKst':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),
        'drive':{'status':'upload-pending','sharing':'retain new file default owner-only; no public permission grant'}
    }
    (H/'mobile-review-delivery.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps({'fullDecodePassed':True,'sameAudio':True,'frames':38208,'bytes':TARGET.stat().st_size,'sha256':record['mobileReview']['sha256']}))
