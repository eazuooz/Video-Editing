"""Native-speed selected preflight with unchanged narration and current captions."""
import html,sys
from polish_common import *
e=Episode(sys.argv[1]);e.authorized();plan=read(e.H/'observed-guides.json');composition=read(e.H/'composition-polish.json')
out=e.O/'moving-observed-preflight';out.mkdir(exist_ok=True);records=[]
windows_by_episode={
 'M07':{'IG01':(2.5,12),'IG10':(0,8.5),'IG02':(0,5.5),'IG07':(0,13),'08':(24,41),'14':(4.5,10)},
 'M08':{'IG03':(0,6.5),'IG04':(0,5.5),'IG11':(0,4.5),'IG05':(10.8,16.5),'IG08':(9.8,14.5),'IG09':(6.8,11.5),'IG06':(0,8.5),'17':(2.5,7.5),'20':(18.8,31.5),'23':(48.8,56)}
}
windows=windows_by_episode[e.id]
for sid,(start,end) in windows.items():
 e.authorized();s=next(s for s in e.T['scenes'] if s['id']==sid);src=R/composition['inputs'][sid]['path'];target=out/f'{sid}.mp4'
 frames=round((end-start)*60)
 vf=f"settb=1/60,setpts=PTS+{s['start']+start}/TB,ass=composition-polish.ass,ass=captions.ko.ass,setpts=PTS-STARTPTS"
 e.ff(['-ss',start,'-i',src,'-ss',s['start']+start,'-i',e.O/'baseline-audio.m4a','-vf',vf,'-frames:v',frames,'-t',end-start,'-map','0:v','-map','1:a','-c:a','aac','-b:a','160k',*ENC,target],'moving-observed-'+sid+'.log',e.O)
 e.verify(target,frames);records.append({'scene':sid,'path':rel(target),'sha256':sha(target),'start':start,'end':end,'currentPixels':'pending'})
 print(e.id,sid,'native-speed preflight encoded',flush=True)
buttons=''.join(f'<button data-src="{x["scene"]}.mp4">{x["scene"]}: {x["start"]}-{x["end"]}s</button>' for x in records)
(out/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>Observed guide preflight</title><style>body{background:#151515;color:white;font:18px system-ui}video{display:block;width:min(96vw,1280px)}button{margin:6px;padding:10px}</style><video controls id="v"></video>'''+buttons+'''<script>for(const b of document.querySelectorAll('button'))b.onclick=()=>{const v=document.querySelector('video');v.src=b.dataset.src;v.play()}</script>''',encoding='utf8')
save(e.H/'moving-observed-guide-preflight.json',{'status':'await-native-playback-inspection','clips':records,'compositionSha256':sha(e.H/'composition-polish.json'),'fullMasterApproval':False})
