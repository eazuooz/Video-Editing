"""New targeted source-native frames around four visually observed missed edits.
Do not rerun prior action/contact-sheet extraction or classify detector scores as cuts.
"""
import hashlib,json,os,re,subprocess,time
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
STATE=HERE/'omd3-missed-edges.json'
OUT=HERE.parent/'research-local/omd3-missed-edges'
if STATE.exists(): raise RuntimeError('Reuse existing targeted result instead of rerunning')
acq=json.loads((HERE/'acquisition-combined.json').read_text(encoding='utf-8'))
source=next(s for s in acq['results'] if s['videoId']=='wl7MCdFifH8')
media=ROOT/source['localMediaPath']
OUT.mkdir(parents=True,exist_ok=True)
ranges=[(2460,2565),(3060,3105),(5280,5325)]
nums=[n for a,b in ranges for n in range(a,b)]
stamp=lambda:time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
rel=lambda p:str(p.relative_to(ROOT)).replace('\\','/')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
state={'schemaVersion':1,'pid':os.getpid(),'startedAt':stamp(),'status':'extracting','sourceId':'wl7MCdFifH8','sourceSha256':source['fileSha256'],'nativeFps':'60/1','nativeFrameRangesInclusiveExclusive':ranges,'purpose':'Every native frame only around41–42.75 /51–51.75 /88–88.75 missed edit contexts','cpuThreads':2,'sourceAudioUsed':False,'actualCutApproval':False,'newGitImages':0}
def save():
    state['updatedAt']=stamp();STATE.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    qpath=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
    q=json.loads(qpath.read_text(encoding='utf-8'));i=next(i for i in q['items'] if i['slug']=='making-game-sequels')
    i['stage']='targeted-native-continuity-review';i['execution'].update({'pid':state['pid'],'sessionId':state.get('sessionId'),'phase':'CPU-targeted-source-native-edges','runner':rel(Path(__file__)),'state':rel(STATE),'activeTasks':[{'pid':state.get('childPid'),'log':state.get('log')}] if state['status']=='extracting' else [],'cpuProductionJobs':1 if state['status']=='extracting' else 0,'sourceDownloadJobs':0,'gpuSynthesisJobs':0,'renderJobs':0,'uploads':0,'status':state['status'],'updatedAt':stamp()});q['updatedAt']=stamp();qpath.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
log=OUT/'targeted-native.log';state['log']=rel(log);save()
expr='+'.join('between(n\\,%d\\,%d)'%(a,b-1) for a,b in ranges)
with log.open('ab') as f:
    child=subprocess.Popen(['C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe','-hide_banner','-threads','2','-filter_threads','1','-t','89','-i',str(media),'-an','-vf',f'select={expr},showinfo,scale=960:540','-vsync','0','-q:v','3',str(OUT/'frame-%04d.jpg')],stdout=f,stderr=f,creationflags=subprocess.CREATE_NO_WINDOW)
    state['childPid']=child.pid;save();code=child.wait()
if code:state['status']='failed';state['exitCode']=code;save();raise RuntimeError('Targeted extraction failed')
files=sorted(OUT.glob('frame-*.jpg'));pts=[float(v) for v in re.findall(r'Parsed_showinfo[^\n]*?\bn:\s*\d+[^\n]*?pts_time:([\d.]+)',log.read_text(encoding='utf-8',errors='replace'))]
if len(files)!=len(nums) or len(pts)!=len(nums) or any(abs(t-n/60)>0.00006 for n,t in zip(nums,pts)):raise RuntimeError('Native frame/PTS count differs')
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22);boards=[]
for offset in range(0,len(files),16):
    board=Image.new('RGB',(2560,1552),(238,238,238));draw=ImageDraw.Draw(board)
    for j,p in enumerate(files[offset:offset+16]):
        x=j%4*640;y=j//4*388
        with Image.open(p) as im:board.paste(im.resize((640,360)),(x,y+28))
        draw.text((x+4,y+2),f'n{nums[offset+j]} {nums[offset+j]/60:.6f}s',font=font,fill=(0,0,0))
    p=OUT/f'sheet-{offset//16+1:02d}.jpg';board.save(p,quality=94);boards.append({'path':rel(p),'sha256':sha(p),'tiles':min(16,len(files)-offset)})
state.update({'status':'extracted-awaiting-direct-native-edge-review','childPid':None,'exitCode':0,'endedAt':stamp(),'frames':[{'path':rel(p),'frame':n,'pts':t,'sha256':sha(p)} for p,n,t in zip(files,nums,pts)],'sheets':boards});save()
print(json.dumps({'pid':state['pid'],'frames':len(files),'sheets':len(boards),'exitCode':0}))
