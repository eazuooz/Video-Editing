"""CPU2/GPU0 local-only sampled source review. No motion/allocation approval."""
import json, pathlib, hashlib, subprocess, math, datetime, os
from PIL import Image, ImageDraw, ImageFont
import psutil
ROOT=pathlib.Path(__file__).resolve().parents[3]
BASE=ROOT/'production/research/game-lighting-history/local/part1-native-review-v166'
FF=r'C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''): h.update(b)
    return h.hexdigest()
plan=read(BASE/'candidates.json'); statepath=BASE/'sample-execution.json'
if statepath.exists(): raise RuntimeError('Preserve existing extraction checkpoint')
for s in plan['sources'].values():
    if sha(ROOT/s['path']) != s['sha256']: raise RuntimeError('Changed source')
p=psutil.Process(); state={'startedAt':datetime.datetime.now().astimezone().isoformat(),'status':'running','pid':p.pid,'createTime':p.create_time(),'commandLine':p.cmdline(),'cwd':str(ROOT),'cpuThreads':2,'gpuJobs':0,'completed':0,'rows':[],'newGitImages':0,'allMotionReviewed':False,'finalUseApproved':False}
save(statepath,state)
try:
    font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',17)
    for r in plan['rows']:
        a,b=r['ranges'][0]; folder=BASE/'samples'/r['id']; folder.mkdir(parents=True,exist_ok=True)
        cmd=[FF,'-hide_banner','-loglevel','error','-nostdin','-threads','2','-ss',str(a),'-i',str(ROOT/r['path']),'-t',str(b-a),'-vf','fps=1/5,scale=960:-2','-an','-filter_threads','2','-threads','2',str(folder/'sample-%03d.png')]
        result=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        (folder/'extract.log').write_bytes(result.stderr)
        if result.returncode: raise RuntimeError('Failed source '+r['id'])
        endcmd=[FF,'-hide_banner','-loglevel','error','-nostdin','-threads','2','-ss',str(b-.05),'-i',str(ROOT/r['path']),'-frames:v','1','-vf','scale=960:-2','-an','-filter_threads','2','-threads','2',str(folder/'end.png')]
        endresult=subprocess.run(endcmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        if endresult.returncode: raise RuntimeError('Failed end '+r['id'])
        files=list(sorted(folder.glob('sample-*.png')))+[folder/'end.png']; samples=[]
        for i,f in enumerate(files): samples.append({'path':f.relative_to(ROOT).as_posix(),'sha256':sha(f),'nominalLocalSeconds':b-.05 if f.name=='end.png' else min(b,a+2.5+5*i)})
        boards=[]
        for offset in range(0,len(files),8):
            pack=files[offset:offset+8]; board=Image.new('RGB',(1920,800),(18,18,18)); draw=ImageDraw.Draw(board)
            for j,f in enumerate(pack):
                im=Image.open(f).convert('RGB'); im.thumbnail((480,360))
                x=j%4*480;y=j//4*400
                board.paste(im,(x,y+30)); sample=samples[offset+j]
                draw.text((x+5,y+4),f"{r['id'][:24]} {sample['nominalLocalSeconds']:.2f}s",fill='white',font=font)
            dest=folder/f'board-{offset//8+1:02d}.png';board.save(dest)
            boards.append({'path':dest.relative_to(ROOT).as_posix(),'sha256':sha(dest),'directlyRead':False})
        state['rows'].append({'id':r['id'],'range':[a,b],'sourceSha256':r['sha256'],'samples':samples,'boards':boards,'extractionExitCode':0,'allMotionReviewed':False});state['completed']+=1;save(statepath,state)
        print(json.dumps({'completed':state['completed'],'id':r['id'],'boards':len(boards)}),flush=True)
    state.update(status='completed-samples-only',endedAt=datetime.datetime.now().astimezone().isoformat(),sampleImages=sum(len(x['samples']) for x in state['rows']),boards=sum(len(x['boards']) for x in state['rows']))
    save(statepath,state)
except Exception as e:
    state.update(status='failed-preserve-partial',error=str(e),endedAt=datetime.datetime.now().astimezone().isoformat());save(statepath,state);raise
