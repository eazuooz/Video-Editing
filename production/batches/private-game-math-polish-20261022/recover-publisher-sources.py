"""Recover only selected publisher media; inspect source dimensions, never upscale."""
import urllib.request,urllib.parse,zipfile,shutil
from polish_common import *
O=R/'shared/output/private-game-math-polish-20261022';target=B/'publisher-source-restoration.json';results=read(target) if target.exists() else {}
inventory=read(B/'source-restoration-inventory.json')
def authorized():
 a=read(R/'shared/publishing/video-production-control.json')['scopedBatchAuthorizations']['private-math-overnight-polish-20261022'];assert a['status']=='active' and a['fullProductionAuthorized']
def fetch(url):
 req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'});return urllib.request.urlopen(req,timeout=40)
for appid,prefix in [('620','portal2-steam'),('2198150','tiny-glade'),('2162800','shapez2')]:
 try:
  authorized();url=f'https://store.steampowered.com/api/appdetails?appids={appid}&l=english';data=json.load(fetch(url));save(O/f'steam-{appid}-metadata.json',data);movies=data[appid]['data']['movies']
  for row in inventory:
   path=R/row['path']
   if not path.stem.startswith(prefix+'-'):continue
   authorized();ident=int(path.stem.removeprefix(prefix+'-'));movie=next((m for m in movies if m['id']==ident),None)
   if not movie:results[row['path']]={'status':'selected-movie-no-longer-listed','appId':appid,'movieId':ident};save(target,results);continue
   if path.exists():
    v=video(path)
    if v['height']>=1080 and v['width']>=1920:continue
   media=movie.get('dash_h264') or movie.get('hls_h264') or movie.get('mp4',{}).get('max');assert media
   info=probe(media);vs=[s for s in info['streams'] if s['codec_type']=='video'];v=max(vs,key=lambda s:s['width']*s['height'])
   record={'sourcePage':f'https://store.steampowered.com/app/{appid}/','sourceUrl':media,'movieId':ident,'metadata':rel(O/f'steam-{appid}-metadata.json'),'width':v['width'],'height':v['height'],'originalSelectionRetained':True,'currentCutReview':'pending'}
   if v['width']<1920 or v['height']<1080:record['status']='original-source-below-FHD-await-user-resolution-choice'
   else:
    path.parent.mkdir(parents=True,exist_ok=True);log=O/(path.stem+'-download.log')
    with log.open('w',encoding='utf8') as f:subprocess.run(['ffmpeg','-hide_banner','-loglevel','warning','-y','-i',media,'-map',f'0:{v["index"]}','-an','-c:v','copy','-movflags','+faststart',str(path)],check=True,stdout=f,stderr=subprocess.STDOUT)
    decoded=video(path);assert decoded['width']>=1920 and decoded['height']>=1080;record.update(status='restored-FHD-current-cut-review-pending',sha256=sha(path),fps=decoded['r_frame_rate'],duration=probe(path)['format']['duration'])
   results[row['path']]=record;save(target,results);print(path.stem,record['status'],flush=True)
 except Exception as ex:
  results['steam-app-'+appid]={'status':'recovery-needs-followup','error':str(ex)[-1600:]};save(target,results);print(appid,str(ex)[-300:],flush=True)
try:
 authorized();url='https://cdn.toukana.com/dorfromantik/presskit/Dorfromantik_Videos.zip';zip_path=O/'Dorfromantik_Videos.zip'
 if not zip_path.exists():
  with fetch(url) as src,zip_path.open('wb') as dst:shutil.copyfileobj(src,dst)
 path=next(R/r['path'] for r in inventory if Path(r['path']).name=='Dorfromantik_Explanation_Trailer.webm');path.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(zip_path) as z:
  names=[n for n in z.namelist() if Path(n).name==path.name];assert len(names)==1,names
  with z.open(names[0]) as src,path.open('wb') as dst:shutil.copyfileobj(src,dst)
 v=video(path);results[rel(path)]={'status':'restored-FHD-current-cut-review-pending' if v['width']>=1920 and v['height']>=1080 else 'original-source-below-FHD-await-user-resolution-choice','sourcePage':'https://www.toukana.com/dorfromantik/presskit','sourceArchive':url,'archiveEntry':names[0],'width':v['width'],'height':v['height'],'fps':v['r_frame_rate'],'sha256':sha(path),'duration':probe(path)['format']['duration'],'currentCutReview':'pending'};save(target,results);print('Dorfromantik restored',v['width'],v['height'],flush=True)
except Exception as ex:
 results['dorfromantik-presskit']={'status':'recovery-needs-followup','error':str(ex)[-1600:]};save(target,results);print('Dorfromantik',str(ex)[-300:],flush=True)
