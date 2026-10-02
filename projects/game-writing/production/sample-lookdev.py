from pathlib import Path
import subprocess,json
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent/'lookdev-proof';OUT.mkdir(exist_ok=True)
source=ROOT/'shared/output/motion-canvas/game-writing-explanation-lookdev-v3.mp4'
records=[]
for i in range(6):
    for phase,delta in [('early',1.5),('result',6.7)]:
        seconds=i*8+delta;target=OUT/f'concept-{i+1:02d}-{phase}.png'
        subprocess.run(['ffmpeg','-v','error','-threads','2','-ss',str(seconds),'-i',str(source),'-frames:v','1','-threads','2','-y',str(target)],check=True)
        records.append({'concept':i+1,'seconds':seconds,'phase':phase,'path':target.relative_to(ROOT).as_posix()})
(OUT/'samples.json').write_text(json.dumps({'source':source.relative_to(ROOT).as_posix(),'classification':'explanation-only visual draft','samples':records},indent=2),encoding='utf-8')
print('12 native explanation draft samples saved. Direct review still required.')
