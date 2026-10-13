"""One CPU-only source inspection pass; does not approve footage or final output."""
from pathlib import Path
import datetime, hashlib, json, os, subprocess
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'projects/game-lighting-history-01/production'
OUT = BASE / 'local/native-extra-v1'
SOURCE = ROOT / 'production/research/game-lighting-history/local/epic-lighting-techniques.mp4'
FFMPEG = 'C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
EXPECTED = '9758467122551d523f8a9691b4db59a573e36afa6783d3df6db022a045566d48'
TIMES = list(range(100, 238, 10)) + list(range(2380, 2491, 10)) + list(range(3180, 3401, 10))
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(p, value): p.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def main():
    control = json.loads((ROOT/'shared/publishing/video-production-control.json').read_text(encoding='utf-8-sig'))
    assert control['mode'] == 'manual-one-video-at-a-time'
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == EXPECTED
    OUT.mkdir(parents=True, exist_ok=True)
    state_path=OUT/'execution.json'
    if state_path.exists(): raise SystemExit('Inspection already started; inspect its state instead of repeating.')
    state={'startedAt':now(),'pid':os.getpid(),'command':'python -X utf8 projects/game-lighting-history-01/production/inspect-native-extra-v1.py','source':str(SOURCE.relative_to(ROOT)),'sourceSha256':EXPECTED,'cpuThreads':2,'gpuJobs':0,'status':'running','files':[],'boards':[],'footageApproved':False}
    save(state_path,state)
    try:
        for t in TIMES:
            name=OUT/f'{t:05d}.jpg'
            subprocess.run([FFMPEG,'-nostdin','-hide_banner','-loglevel','error','-threads','2','-ss',str(t),'-i',str(SOURCE),'-frames:v','1','-vf','scale=640:360','-threads','2','-q:v','2',str(name)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
            state['files'].append({'seconds':t,'path':str(name.relative_to(ROOT)),'sha256':hashlib.sha256(name.read_bytes()).hexdigest()})
            save(state_path,state)
        for i in range(0,len(state['files']),6):
            board=Image.new('RGB',(1280,1140),'#17191d');draw=ImageDraw.Draw(board)
            for k,item in enumerate(state['files'][i:i+6]):
                x=(k%2)*640;y=(k//2)*380
                draw.text((x+8,y+3),f"Unreal official source | {item['seconds']}s",fill='white')
                with Image.open(ROOT/item['path']) as frame:board.paste(frame,(x,y+20))
            path=OUT/f'board-{i//6+1:02d}.jpg';board.save(path,quality=94)
            state['boards'].append({'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        state.update(status='complete',completedAt=now(),exitCode=0)
    except Exception as exc:
        state.update(status='failed',failedAt=now(),error=str(exc));raise
    finally:save(state_path,state)
    print(json.dumps({'frames':len(state['files']),'boards':len(state['boards']),'exitCode':0,'footageApproved':False}))
if __name__=='__main__':main()
