"""Finite addendum: actual moving game observations AFTER completed explanations."""
import json, pathlib, subprocess, hashlib
from PIL import Image, ImageDraw, ImageFont
HERE=pathlib.Path(__file__).resolve().parent; ROOT=HERE.parents[3]
OLD=HERE.parent/'revision-direction-overview-20261115'
FF=pathlib.Path(r'C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin/ffmpeg.exe')
FP=FF.with_name('ffprobe.exe')
def read(p): return json.loads(pathlib.Path(p).read_text(encoding='utf-8-sig'))
def save(p,v): pathlib.Path(p).parent.mkdir(parents=True,exist_ok=True);pathlib.Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
SOURCES={
 'mario':('projects/game-math-euler-axis-angle/production/local/revision-v3/sources/_wH_-1saHnw-hls.mp4','Super Mario Odyssey','_wH_-1saHnw'),
 'kart':(str((HERE.parent/'revision-teaching-sync-20261115/sources/CrbHin3jDqM.mp4').relative_to(ROOT)),'Mario Kart 8 Deluxe','CrbHin3jDqM'),
 'forza':('projects/game-math-shading-lights/production/local/footage-review/forza5-xPnKcvo8A1E-000-070.mp4','Forza Horizon 5','xPnKcvo8A1E'),
 'showroom':('projects/game-math-shading-lights/production/local/footage-review/forzavista-ferrari-020-120.mp4','Forza Motorsport 6','X9UdRR_4Rog'),
 'doom':('projects/game-math-shading-lights/production/local/footage-review/doom3-Hu94MHBQCis.mp4','Doom 3','Hu94MHBQCis'),
 'besiege':('projects/game-math-rigid-body-inertia/production/local/footage-review/besiege-T3ncWUwKUns.mp4','Besiege','T3ncWUwKUns'),
 'beam':('projects/game-math-springs-damping/production/local/footage-review/beamng-stock-suspension-d5fiou39Htc-744-850.mp4','BeamNG.drive','d5fiou39Htc'),
 'suspension':('projects/game-math-springs-damping/production/local/footage-review/beamng-suspension-cKarsLzGuFE.mp4','BeamNG.drive','cKarsLzGuFE'),
 'crash':('projects/game-math-springs-damping/production/local/footage-review/beamng-Eoh7qwVDsbk.mp4','BeamNG.drive','Eoh7qwVDsbk'),
 'town':('shared/output/game-math-part2-full-series/sources/FRfnXAIbA-M.mp4','Townscaper','FRfnXAIbA-M'),
 'portal':('projects/shorts-portal-teleport-momentum/production/local/gameplay.mp4','Portal','AmJ4orxVpss'),
 'train':('projects/game-math-parametric-hermite/production/local/footage-review/sources/_HVv2GnldbU.mp4','Satisfactory','_HVv2GnldbU'),
 'maker':('projects/game-math-parametric-hermite/production/local/footage-review/sources/E-Sj-E0Ssds-2960-3330.mp4','Super Mario Maker 2','E-Sj-E0Ssds'),
 'galaxy':('projects/game-math-parametric-hermite/production/local/footage-review/sources/HALSoFBzIlw-0480-0800.mp4','Super Mario Galaxy','HALSoFBzIlw'),
 'rider':('shared/output/game-math-part2-full-series/sources/4Odvp_TIeQU.mp4','Riders Republic','4Odvp_TIeQU'),
 'zelda':('projects/game-math-euler-axis-angle/production/local/revision-v3/sources/YNQ20CKbY8U-hls.mp4','The Legend of Zelda: Tears of the Kingdom','YNQ20CKbY8U'),
}
# Broad native-motion candidates. Adopt only after directly inspecting each temporal strip.
CANDIDATES={
 'car-reflection':('showroom',46,68), 'town-orbit':('town',350,374), 'doom-light':('doom',108,127),
 'mario-joints':('mario',680,702), 'rider-joints':('rider',198,222), 'town-build':('town',135,157),
 'portal-occlude':('portal',423,444), 'mario-water':('mario',748,765),
 'mario-run':('mario',2498,2512), 'car-speed':('forza',22,35), 'mario-jump':('mario',1460,1483),
 'kart-start':('kart',7,28), 'car-land':('forza',47,65), 'rider-air':('rider',224,244),
 'kart-turn':('kart',40,62), 'rotor':('besiege',330,349), 'zelda-turn':('zelda',990,1014),
 'beam-climb':('beam',30,54), 'cannon':('besiege',175,191), 'zelda-contact':('zelda',933,955),
 'chomp':('mario',1222,1245), 'suspension':('beam',5,27), 'rider-follow':('rider',783,805),
 'crash-impact':('crash',20,42), 'besiege-impact':('besiege',296,314), 'mario-contact':('mario',1440,1457),
 'beam-joints':('beam',73,98), 'train-curve':('train',718,742), 'maker-path':('maker',213,235),
 'galaxy-flight':('galaxy',129,148), 'rail-edit':('train',236,260), 'maker-corner':('maker',213,235),
 'rail-train':('train',816.25,840.25), 'rail-local':('train',258,282),
}
def main():
 (HERE/'local/candidates').mkdir(parents=True,exist_ok=True)
 records={}
 for k,(rel,game,sid) in SOURCES.items():
  p=ROOT/rel
  if not p.exists():raise FileNotFoundError(p)
  meta=json.loads(subprocess.check_output([FP,'-v','error','-show_streams','-show_format','-of','json',str(p)],creationflags=subprocess.CREATE_NO_WINDOW))
  v=next(s for s in meta['streams'] if s['codec_type']=='video');assert v['width']>=1920 and v['height']>=1080,(k,v['width'],v['height'])
  records[k]=dict(file=str(p),game=game,sourceId=sid,width=v['width'],height=v['height'],fps=v['r_frame_rate'],duration=float(meta['format']['duration']),sha256=sha(p),hasAudio=any(s['codec_type']=='audio' for s in meta['streams']))
  recovered={'rider':'projects/game-math-skinning-normal-map/production/local/footage-review/riders-original-audio.m4a','portal':'projects/game-math-pipeline-shaders/production/local/footage-review/portal-original-audio.m4a'}
  if k in recovered:
   ap=ROOT/recovered[k];assert ap.exists();records[k].update(audioFile=str(ap),audioSha256=sha(ap),audioRecoveredFromSameRecording=True)
 save(HERE/'sources.json',records)
 font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',17)
 for k,(src,a,z) in CANDIDATES.items():
  row=records[src]; assert z<row['duration'],(k,row['duration'])
  out=HERE/'local/candidates'/f'{k}.jpg'
  if out.exists():continue
  board=Image.new('RGB',(1280,770),'#10151b');d=ImageDraw.Draw(board)
  for i in range(12):
   t=a+(z-a)*i/12; path=out.with_name(f'{k}-{i:02}.png')
   subprocess.run([FF,'-v','error','-nostdin','-y','-threads','1','-ss',str(t),'-i',row['file'],'-vf','scale=320:180','-frames:v','1','-threads','1',str(path)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
   im=Image.open(path); x=(i%4)*320;y=(i//4)*250;board.paste(im,(x,y));d.text((x+5,y+185),f'{k}  {t:.2f}s',font=font,fill='white');path.unlink()
  board.save(out,quality=90)
 save(HERE/'candidate-review.json',dict(status='awaiting-actual-temporal-review',candidates={k:dict(source=s,start=a,end=z,strip=str(HERE/'local/candidates'/f'{k}.jpg')) for k,(s,a,z) in CANDIDATES.items()}))
 print('prepared',len(records),'FHD sources and',len(CANDIDATES),'native temporal strips',flush=True)
if __name__=='__main__':main()
