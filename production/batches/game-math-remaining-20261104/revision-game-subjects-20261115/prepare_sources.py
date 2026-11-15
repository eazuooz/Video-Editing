"""Genuine frames from already inspected independent FHD recordings; no new art."""
import sys,json,subprocess,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];OLD=HERE.parent/'revision-teaching-sync-20261115'
sys.path.insert(0,str(OLD));from render_revision import FF
SOURCES={
 'mario':('projects/game-math-euler-axis-angle/production/local/revision-v3/sources/_wH_-1saHnw-hls.mp4',714.5,'Super Mario Odyssey','_wH_-1saHnw'),
 'kart':(str(OLD.relative_to(ROOT)/'sources/CrbHin3jDqM.mp4'),9,'Mario Kart 8 Deluxe','CrbHin3jDqM'),
 'kart-sprite':(str(OLD.relative_to(ROOT)/'sources/CrbHin3jDqM.mp4'),14,'Mario Kart 8 Deluxe','CrbHin3jDqM'),
 'forza':('projects/game-math-shading-lights/production/local/footage-review/forza5-xPnKcvo8A1E-000-070.mp4',35.5,'Forza Horizon 5','xPnKcvo8A1E'),
 'doom':('projects/game-math-shading-lights/production/local/footage-review/doom3-Hu94MHBQCis.mp4',118,'Doom 3','Hu94MHBQCis'),
 'windmill':('projects/game-math-rigid-body-inertia/production/local/footage-review/besiege-T3ncWUwKUns.mp4',338.5,'Besiege','T3ncWUwKUns'),
 'beamng':('projects/game-math-springs-damping/production/local/footage-review/beamng-stock-suspension-d5fiou39Htc-744-850.mp4',8,'BeamNG.drive','d5fiou39Htc'),
 'town':('shared/output/game-math-part2-full-series/sources/FRfnXAIbA-M.mp4',110,'Townscaper','FRfnXAIbA-M'),
 'portal':('projects/shorts-portal-teleport-momentum/production/local/gameplay.mp4',452,'Portal','AmJ4orxVpss'),
 'train':('projects/game-math-parametric-hermite/production/local/footage-review/sources/_HVv2GnldbU.mp4',706,'Satisfactory','_HVv2GnldbU'),
 'maker':('projects/game-math-parametric-hermite/production/local/footage-review/sources/E-Sj-E0Ssds-2960-3330.mp4',242,'Super Mario Maker 2','E-Sj-E0Ssds'),
 'galaxy':('projects/game-math-parametric-hermite/production/local/footage-review/sources/HALSoFBzIlw-0480-0800.mp4',140,'Super Mario Galaxy','HALSoFBzIlw'),
 'chomp':('projects/game-math-euler-axis-angle/production/local/revision-v3/sources/_wH_-1saHnw-hls.mp4',1232,'Super Mario Odyssey','_wH_-1saHnw'),
 'collision':('projects/game-math-euler-axis-angle/production/local/revision-v3/sources/_wH_-1saHnw-hls.mp4',1449,'Super Mario Odyssey','_wH_-1saHnw')}
def digest(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 out=HERE/'local/sources';out.mkdir(parents=True,exist_ok=True);records=[]
 for key,(file,t,game,sid) in SOURCES.items():
  target=out/(key+'.png');source=ROOT/file
  if not target.exists():subprocess.run([str(FF),'-v','error','-nostdin','-n','-threads','1','-ss',str(t),'-i',str(source),'-frames:v','1','-threads','1',str(target)],check=True)
  im=Image.open(target);assert im.width>=1920 and im.height>=1080
  records.append(dict(id=key,game=game,sourceFile=str(source),sourceIn=t,sourceId=sid,recordingUrl='https://www.youtube.com/watch?v='+sid,decodedDimensions=list(im.size),frameFile=str(target),frameSha256=digest(target),sourceSha256=digest(source),kind='independent-gameplay-frame',use='explanation illustration; not a measured game model',visualReview='pending-crop-review',rightsEvidence='Inherited existing independent-source evidence in teaching-sync inventory/game-additions and cited project footage review.'))
 board=Image.new('RGB',(1920,1080*len(records)//4+270),'black');d=ImageDraw.Draw(board)
 for i,row in enumerate(records):
  x=i%4*480;y=i//4*300;im=Image.open(row['frameFile']);im.thumbnail((480,270));board.paste(im,(x,y));d.text((x+8,y+276),row['id']+' '+row['game'],fill='white')
 board.crop((0,0,1920,900)).save(out/'contact.jpg',quality=95)
 (HERE/'sources.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
if __name__=='__main__':main()
