from pathlib import Path
import json,hashlib,subprocess,datetime,concurrent.futures
import yt_dlp
R=Path(__file__).resolve().parents[3];P=R/'projects/vampire-survivors-d2-copyright';O=P/'production/local/sources';O.mkdir(parents=True,exist_ok=True)
assert json.loads((R/'shared/publishing/video-production-control.json').read_text('utf-8-sig'))['selectedVideo']==P.name
jobs=[('d2','https://www.youtube.com/watch?v=KlxyIREH63M',[(100,220),(740,860),(1500,1620),(2400,2520)]),('vs','https://www.youtube.com/watch?v=bzYEU3rBD-Y',[(60,200),(780,920),(1580,1720)]),('ms','https://www.youtube.com/watch?v=oqTFK2ErLhg',[(80,140),(330,390)])]
prepared=[]
for name,url,ranges in jobs:
 with yt_dlp.YoutubeDL({'quiet':True,'no_warnings':True,'socket_timeout':20,'retries':1,'js_runtimes':{'node':{'path':'C:/Program Files/nodejs/node.exe'}}}) as y:d=y.extract_info(url,download=False)
 v=next(f for f in d['formats'] if f['format_id']=='299');assert(v['width'],v['height'])==(1920,1080)
 a=next((f for f in d['formats'] if f['format_id']=='140'),None)
 prepared.extend((name,url,i,lo,hi,v,a,d.get('uploader'),d['title'],d.get('license')) for i,(lo,hi) in enumerate(ranges,1))
def acquire(job):
 name,url,i,lo,hi,v,a,creator,title,license=job;stem=name+'-'+str(i).zfill(2);f=O/(stem+'.mp4');sig=O/(stem+'.receipt.json')
 if f.exists() and sig.exists():return json.loads(sig.read_text('utf-8'))
 vf=O/(stem+'.video.mp4');af=O/(stem+'.audio.m4a');print('Acquiring',stem,lo,hi,flush=True)
 for kind,fmt,out in [('video',v,vf),('audio',a,af)]:
  if fmt is None:continue
  cmd=['ffmpeg','-v','error','-y','-rw_timeout','15000000','-ss',str(lo),'-i',fmt['url'],'-t',str(hi-lo),'-c','copy']+(['-an'] if kind=='video' else ['-vn'])+[str(out)]
  z=subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,timeout=150 if kind=='video' else 75);(O/(stem+'.'+kind+'.log')).write_bytes(z.stderr);assert z.returncode==0,(stem,kind,z.returncode)
 cmd=['ffmpeg','-v','error','-y','-i',str(vf)]
 if a:cmd+=['-i',str(af),'-map','0:v:0','-map','1:a:0']
 cmd+=['-c','copy','-avoid_negative_ts','make_zero','-movflags','+faststart',str(f)];subprocess.run(cmd,check=True,timeout=30)
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(f)]));vv=next(x for x in probe['streams'] if x['codec_type']=='video');assert(vv['width'],vv['height'])==(1920,1080)
 rec={'file':f.relative_to(R).as_posix(),'sourceUrl':url,'sourceStart':lo,'sourceEnd':hi,'duration':float(probe['format']['duration']),'width':vv['width'],'height':vv['height'],'fps':vv['r_frame_rate'],'hasOriginalAudio':any(x['codec_type']=='audio' for x in probe['streams']),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'creator':creator,'title':title,'licenseMetadata':license};sig.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n','utf-8');print('Acquired',stem,flush=True);return rec
results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
 for rec in pool.map(acquire,prepared):results.append(rec)
for name,url,ranges in jobs:
 record={'sourceUrl':url,'acquiredAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sections':[x for x in results if Path(x['file']).name.startswith(name+'-')],'sourceKind':'independent-gameplay','rightsStatus':'No explicit recording reuse license inferred; local critical comparison excerpts require final quotation/rights record.','sourceAudio':'D2 includes presenter voice, not isolated game sound; original game-only sources inspected before use.'}
 (O/(name+'-acquisition.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf-8')
print('COMPLETE',len(results),'FHD sources',flush=True)
