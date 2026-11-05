"""Compositing preflight against the actual ASR-derived global caption clock."""
from pipeline import *
from PIL import Image, ImageDraw, ImageFont
import subprocess,io
p=read(H/'edit-plan.json');by={c['id']:c for c in p['cuts']};out=L/'qa/gameplay';out.mkdir(parents=True,exist_ok=True)
samples=[('A02-F11',.78),('A02-F12',.32),('A02-F12',.70),('A02-F21',.83),('A02-F22',.18),('A02-F22',.75),('A02-F31',.76),('A02-F32',.21),('A02-F32',.81)]
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15)
sheet=Image.new('RGB',(375*3,(211+22)*3),'#181818');draw=ImageDraw.Draw(sheet);rows=[]
for n,(id,portion) in enumerate(samples):
 c=by[id];fr=round(c['frames']*portion);g=(c['startFrame']+fr)/60;src=L/'edit'/(id+'.mp4')
 ass=(L/'edit/captions.ko.ass').as_posix().replace(':','\\:');vf=f"setpts=PTS-STARTPTS+{g}/TB,ass='{ass}',scale=375:211"
 raw=subprocess.check_output(['ffmpeg','-v','error','-threads','2','-ss',str(fr/60),'-i',str(src),'-frames:v','1','-vf',vf,'-f','image2pipe','-vcodec','png','-threads','1','-'])
 im=Image.open(io.BytesIO(raw)).convert('RGB');x=n%3*375;y=n//3*233;sheet.paste(im,(x,y));draw.text((x+4,y+211),f'{id} global {g:.2f}',font=font,fill='white')
 rows.append({'id':id,'sourceFrame':fr,'globalSeconds':g,'cutHash':sha(src)})
sheet.save(out/'gameplay-with-captions-mobile.jpg',quality=94)
save(out/'preflight.json',{'samples':rows,'actualCaptions':artifact(L/'edit/captions.ko.ass'),'sheet':artifact(out/'gameplay-with-captions-mobile.jpg')})
checks=[]
for c in p['cuts']:
 if c.get('playbackSpeed')!=.25:continue
 n=by[c['normalSpeedReference']]
 assert n['endFrame']==c['startFrame'] and n['playbackSpeed']==1 and n['sourceSha256']==c['sourceSha256']
 assert n['sourceStart']<=c['sourceStart']<c['sourceEndExclusive']<=n['sourceEndExclusive']
 checks.append({'native':n['id'],'replay':c['id'],'identicalSource':c['sourceSha256'],'beforeAfterSameMotion':True,'globalCutFrame':c['startFrame'],'slowInterval':[c['sourceStart'],c['sourceEndExclusive']],'nativeSourceContainsFullSlowInterval':True})
save(H/'native-then-replay.json',{'proof':checks,'preflight':artifact(out/'preflight.json'),'timingChoices':['Begin the Kula spin passage with a right-side establishing pose. Cut to the complete movement, then replay it during the specific direction/landing phrases.','At Lili’s source-camera jump, suppress the previous full-body box; track only the visible torso when the foot leaves the source frame.'],'fullMasterStillRequiresVerification':True})
