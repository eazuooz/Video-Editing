"""Intervals read against the unscaled matches and training-mode recording."""
from pipeline import *
def records():
 rec={}
 for key,name,game,label in [('kula','kof-xiii','THE KING OF FIGHTERS XIII','KOF XIII · 쿨라'),('lili','t8-lili-practice','TEKKEN 8 Closed Network Test','철권 8 CNT · 리리'),('rank','t8-lili','TEKKEN 8','철권 8 · 리리')]:
  d=L/'sources';j=read(d/(name+'.info.json'));assert 'Creative Commons Attribution' in j['license']
  rec[key]={'game':game,'label':label,'file':rel(d/(name+'.mp4')),'title':j['title'],'url':'https://www.youtube.com/watch?v='+j['id'],'recorder':j['uploader'],'license':j['license']+' (recording attribution; original game rights remain with the publisher).'}
 return rec
def normal_map():
 # Global cut lengths come from the preserved original lesson. No source is looped.
 rows={
 'E001':('rank',224.15,'Opening: Lili lifts a leg above her head in a live round.'),
 'E002':('rank',254.2,'A low starting pose becomes an inverted launch.'),
 'E002B':('kula',318.66,'Kula reverses direction in the air and extends her leg in the arcade match.'),
 'E003':('rank',275.58,'Actual play size: contrasting lunges, airborne extension and recovery in an uninterrupted round.'),
 'E007':('kula',177.4,'Upper-body wind-up and recovery against a close opponent in a small sprite.'),
 'E008':('lili',28.22,'Lili moves her upper body with her long-reaching strike.'),
 'E009':('rank',242.62,'The fighters repeatedly contract, extend and recover within the play space.'),
 'E010':('kula',166.48,'The camera shows the whole arena; through jumps, crouches and sweeps the small silhouette must still read.'),
 'E012':[['kula',242.2,1032,'Actual play size: compact guard and full extension in a round against Leona.'],['kula',270.8,None,'A subsequent takeoff isolates the same expanding outline.']],
 'E016':('lili',30.34,'A single instant in a larger attack.'),
 'E017':('rank',255.73,'Forward momentum is readable from the change of the torso relative to the leading foot.'),
 'E018':('kula',172.19,'A low sweep pushes the foot out along the floor.'),
 'E019':('rank',292.32,'Read full-speed actions together in a continuous match before isolating poses.'),
 'E020':[['kula',311.75,1080,'Track an uninterrupted exchange: takeoff, extension, guard and recovery at native speed.'],['kula',336.4,None,'Return to the lowered pose in the same match with the camera unchanged.']],
 'E028':('rank',320.10,'Return to the full playable image to read the travel of Lili’s body.'),
 'E029':('kula',258.23,'Compare the compact guard and open movement at normal scale.'),
 'E030':('rank',307.95,'Lili’s extended finish confirms the direction of the attack.')}
 return {'A02-'+k:v for k,v in rows.items()}
def bind():
 data=read(H/'sources/reviewed-footage.json');out=[]
 for i,m in enumerate(data['motions']):
  move={'source':['kula','lili','kula'][i],'range':m['slowSourceRange'],'keyframes':[[k['sourceTime'],*k['box']] for k in m['keyframes']],'hiddenSourceIntervals':m['hiddenSourceIntervals'],'slowCue':2,'nativeTail':[.12,.20,.18][i],'chapter':['쿨라 · 몸을 낮췄다 솟기','리리 · 발차기 방향','쿨라 · 회전에서 착지까지'][i],'label':['도약','발차기','회전'][i],'observation':m['observation'],'returnId':['kula','rank','kula'][i],'returnSource':[171.50,254.15,321.01][i],'returnPurpose':['Confirm how the compact recovery belongs to the full-speed movement.','Confirm how Lili’s changing outline reads in actual ranked play, from a camera framing the whole fight.','Follow how Kula regains stance and changes height and direction in live play.'][i]}
  if i==0:move.update(slowDelay=.58,returnSource=171.12)
  if i==2:move.update(slowDelay=1.23,returnSource=320.88,introContext={'duration':1.95,'sourceStart':336.4,'actionStart':319.08})
  out.append(move)
 save(H/'analysis-beats.json',{'sources':records(),'moves':out,'nativeCutMap':normal_map(),'evidence':artifact(H/'sources/reviewed-footage.json'),'renderingNote':'No detector or hitbox claim. A source frame subset is played full speed first; the same half-open source interval is replayed once at quarter speed. Guides clear on occlusion and source changes.','speechPolicy':'New Qwen for these three independently observed passages only; keep all other original paragraphs/PCM.'})
if __name__=='__main__':bind()
