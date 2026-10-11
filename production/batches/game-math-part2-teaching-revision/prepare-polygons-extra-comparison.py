"""Secure precise fresh actual-action intervals, still unapproved for narration."""
from pathlib import Path
import hashlib,json,subprocess,shutil
ROOT=Path(__file__).resolve().parents[3]; B=Path(__file__).parent
O=ROOT/'shared/output/game-math-part2-teaching-revision/polygons-extra-comparison';O.mkdir(exist_ok=True)
F=ROOT/'shared/output/game-math-part2-teaching-revision/polygons-fresh-candidates'
source=ROOT/'shared/output/game-math-part2-full-series/sources/igcymdI4XYM.mp4';assert source.exists()
plans=[('noita-outline-a',source,170,202),('noita-outline-b',source,445,478),
 ('noita-outline-c',source,601,632),('noita-outline-d',source,780,813),
 ('tiny-release-wall',F/'tiny-glade/tiny-glade-257046593.mp4',0,8.8),
 ('tiny-release-build',F/'tiny-glade/tiny-glade-257046593.mp4',10,24),
 ('tiny-release-water',F/'tiny-glade/tiny-glade-257046593.mp4',30.5,40.3),
 ('tiny-gameplay-wall',F/'tiny-glade/tiny-glade-256965562.mp4',0,18.7),
 ('tiny-gameplay-terrain',F/'tiny-glade/tiny-glade-256965562.mp4',23,31.7),
 ('tiny-gameplay-build',F/'tiny-glade/tiny-glade-256965562.mp4',33,46.5),
 ('shapez-reveal-cutter',F/'shapez2-257294952.mp4',0,4),
 ('shapez-gameplay-cutter',F/'shapez2-257312662.mp4',38,46.8),
 ('shapez-gameplay-boundary',F/'shapez2-257312662.mp4',30,34)]
rows=[]
for identifier,path,start,end in plans:
 dest=O/(identifier+'.mp4')
 if not dest.exists():
  subprocess.run(['ffmpeg','-v','error','-threads','2','-ss',str(start),'-i',str(path),'-t',str(end-start),
   '-map','0:v:0','-an','-vf','scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,fps=60',
   '-c:v','libx264','-threads','2','-preset','veryfast','-crf','19','-y',str(dest)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
 rows.append(dict(id=identifier,file=dest.name,seconds=end-start,sourceFile=path.relative_to(ROOT).as_posix(),sourceStart=start,sourceEnd=end,
  sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),selectionApproved=False))
 print('Precise candidate',identifier,end-start,flush=True)
(O/'inputs.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
script=(B/'prepare-polygons-fresh-review.py').read_text(encoding='utf8').replace("O=ROOT/'shared/output/game-math-part2-teaching-revision/polygons-fresh-candidates'", "O=ROOT/'shared/output/game-math-part2-teaching-revision/polygons-extra-comparison'")
exec(compile(script,str(B/'prepare-polygons-fresh-review.py'),'exec'))
