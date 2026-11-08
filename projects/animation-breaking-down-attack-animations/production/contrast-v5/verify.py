"""Current encoded visual samples and one technical pass, no new speech recognition."""
from pathlib import Path
import json,subprocess,shutil
from PIL import Image,ImageDraw,ImageFont
from prepare import H,P,R,B,L,read,save,sha
from render import probe,ff
def audiohash(p):return subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:a:0','-c','copy','-f','hash','-hash','sha256','-']).decode().strip()
def main():
 plan=read(H/'edit-plan.json');base=plan['baseline'];V=L/'rendered';Q=L/'qa';Q.mkdir(exist_ok=True)
 baseline=R/next(x['path'] for x in base['files'] if x['kind']=='clean.mp4');expected=audiohash(baseline);results={}
 for kind in ['clean.mp4','captioned.mp4']:
  p=V/(P.name+'.'+kind);info=probe(p);v=next(x for x in info['streams'] if x['codec_type']=='video');assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1920,1080,'60/1',plan['totalFrames'])
  ff(['-threads','4','-i',p,'-f','null','NUL'],Q/(kind+'.decode.log'))
  assert not (Q/(kind+'.decode.log')).read_bytes().strip(),kind+' decode reported errors'
  digest=audiohash(p);assert digest==expected
  packet=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','packet=pts,dts','-of','json',str(p)]))['packets'];assert len(packet)==plan['totalFrames'];assert all(x['pts']==i*1000 and x['dts']==i*1000 for i,x in enumerate(packet))
  results[kind]={'path':str(p),'sha256':sha(p),'width':v['width'],'height':v['height'],'fps':v['r_frame_rate'],'frames':int(v['nb_frames']),'fullDecode':'pass','uniformFrameTimes':True,'aacPacketSha256':digest,'baselineAACPacketsIdentical':True}
 for lang in ['ko','en']:
  p=V/(P.name+'.'+lang+'.srt');old=R/next(x['path'] for x in base['files'] if x['kind']==lang+'.srt');assert p.read_bytes()==old.read_bytes();results[lang+'.srt']={'path':str(p),'sha256':sha(p),'unchangedBytes':True}
 mix=P/'production/local/relations-v4/mix.wav';assert sha(mix)==base['audioProof']['mixSha256']
 # Explicitly verify no replacement intersects the retained narrated map.
 anchor=round(base['insertion']['pictureFrame']);end=anchor+round(base['insertion']['duration']*60);assert not any(r['start']<end and r['end']>anchor for r in plan['rows'])
 samples=[]
 def add(label,key,offset):
  row=next(x for x in plan['rows'] if x['key']==key);frame=min(row['end']-1,row['start']+offset);samples.append({'label':label,'frame':frame,'time':frame/60,'replacement':key})
 for n in [1,2,3]:add('normal-'+str(n),'relocated-'+str(n),23)
 for f in [0,35,48,68]:add('normal-motion-'+str(f),'relocated-1',f)
 add('four-phase','cut-13',136);add('preparation-guide','cut-14',32);add('hit-stop-guide','cut-29',24);add('follow-through-guide','cut-44',52);add('control-difference','cut-55',766);add('summary-phases','cut-75',205)
 add('preparation-start','cut-14',0);add('preparation-end','cut-14',44);add('follow-through-start','cut-44',0);add('follow-through-end','cut-44',128)
 row=next(x for x in plan['rows'] if x['key']=='cut-14');samples.extend([{'label':'before-replacement','frame':row['start']-1,'time':(row['start']-1)/60},{'label':'return-to-game','frame':row['end']+1,'time':(row['end']+1)/60}])
 cap=V/(P.name+'.captioned.mp4')
 for s in samples:
  p=Q/(s['label']+'.png');ff(['-threads','2','-ss',s['time'],'-i',cap,'-frames:v','1',p],Q/(s['label']+'.extract.log'));s['path']=str(p)
  Image.open(p).resize((375,211),Image.Resampling.LANCZOS).save(Q/(s['label']+'-375.png'))
 sheet=Image.new('RGB',(1125,251*((len(samples)+2)//3)),'#141414');d=ImageDraw.Draw(sheet)
 for i,s in enumerate(samples):
  x=i%3*375;y=i//3*251;sheet.paste(Image.open(Q/(s['label']+'-375.png')),(x,y));d.text((x+8,y+217),s['label'],fill='white')
 sheet.save(Q/'mobile-sheet.jpg',quality=94)
 save(L/'qa.json',{'revision':'contrast-v5','technicalChecks':results,'unchangedOriginalMixSha256':sha(mix),'mapFramesRetained':[anchor,end],'newTts':False,'newASR':False,'visualSamples':samples,'visualReview':'pending actual encoded sample inspection','fullWatch':False,'humanReview':False,'platformChanged':False})
 print('technical QA and current encoded samples ready')
if __name__=='__main__':main()
