"""Full decode and paired-output checks. Reports evidence, never human review."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,importlib.util,json,re,subprocess
R=Path(__file__).resolve().parents[3]
BOOT=argparse.ArgumentParser(add_help=False);BOOT.add_argument('--queue',required=True);BA,_=BOOT.parse_known_args();QB=json.loads(Path(BA.queue).read_text(encoding='utf-8-sig'));P=R/'projects'/QB['project']
spec=importlib.util.spec_from_file_location('compose',R/'production/batches/game-math-remaining-20261104/compose-module.py');M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
def run(args,log):
    with log.open('w',encoding='utf-8') as f:r=subprocess.run(list(map(str,args)),stdout=f,stderr=subprocess.STDOUT,creationflags=M.CREATE)
    return r.returncode
def parse_time(s):
    h,m,tail=s.split(':');sec,ms=tail.split(',');return int(h)*3600+int(m)*60+int(sec)+int(ms)/1000
def subtitles(p,duration):
    blocks=p.read_text(encoding='utf-8-sig').strip().split('\n\n');issues=[];last=0
    for i,b in enumerate(blocks):
        lines=b.splitlines();assert int(lines[0])==i+1
        a,z=map(parse_time,lines[1].split(' --> '));text=' '.join(lines[2:])
        if a<last-.002 or z<=a or z>duration-10+.05:issues.append({'id':i+1,'type':'timing','start':a,'end':z,'last':last})
        if '{\\' in text or '<font' in text or '\\N' in text:issues.append({'id':i+1,'type':'not-plain-srt'})
        if z-a<.45:issues.append({'id':i+1,'type':'brief-cue','seconds':z-a,'text':text})
        last=z
    return {'cues':len(blocks),'issues':issues}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--queue',required=True);ap.add_argument('--output',required=True);a=ap.parse_args()
    M.G.authorized();q=Path(a.queue).resolve();dest=Path(a.output).resolve();assert q.is_relative_to(P/'production/local') and dest.is_relative_to(R/'output')
    queue=M.read(q);progress=M.read(q.parent/'composite/progress.json');assert progress['status']=='encoded-internal-QA-pending'
    W=q.parent/'final-qa';W.mkdir(exist_ok=True);frames=queue['bodyFrames']+720;duration=frames/60
    report={'createdAt':datetime.now(timezone.utc).isoformat(),'queueSha256':M.sha(q),'expectedFrames':frames,'files':{},'humanListening':False,'humanViewing':False,'internalVisualReview':False,'readyForUserReview':False}
    audio=[]
    for kind in ['clean','captioned']:
        p=dest/(P.name+'.'+kind+'.mp4');M.video_check(p,frames)
        code=run([M.FF,'-hide_banner','-nostdin','-threads','2','-err_detect','explode','-i',p,'-map','0:v:0','-map','0:a:0','-f','null','-'],W/(kind+'-full-decode.log'))
        digest=subprocess.check_output([str(M.FF),'-v','error','-i',str(p),'-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','-'],text=True,creationflags=M.CREATE).strip();audio.append(digest)
        report['files'][kind]={'path':str(p),'sha256':M.sha(p),'bytes':p.stat().st_size,'fullDecodeExitCode':code,'audioPacketHash':digest,'probe':M.probe(p)}
    assert audio[0]==audio[1],'Clean/captioned audio differs'
    assert all(x['fullDecodeExitCode']==0 for x in report['files'].values()),'Full media decode failed'
    for lang in ['ko','en']:
        p=dest/(P.name+'.'+lang+'.srt');report[lang+'Subtitles']={**subtitles(p,duration),'sha256':M.sha(p),'path':str(p)}
    cap=dest/(P.name+'.captioned.mp4')
    rc=run([M.FF,'-hide_banner','-nostdin','-threads','2','-i',cap,'-vn','-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-'],W/'final-loudness.log');assert rc==0
    data=re.findall(r'\{\s*"input_i"[\s\S]+?\}',(W/'final-loudness.log').read_text(encoding='utf-8'));assert data;report['actualMixLoudness']=json.loads(data[-1]);report['truePeakWithinLimit']=float(report['actualMixLoudness']['input_tp'])<=-1.3
    assert report['truePeakWithinLimit'],'Encoded true peak exceeds planned ceiling'
    alignment=M.read(queue['wordAlignment']);report['originalPcmUnchanged']=M.sha(Path(queue['audioDirectory'])/'narration.wav')==alignment['narrationSha256'];assert report['originalPcmUnchanged']
    samples=[]
    # Inspect realised transition, middle and final phase of every lecture beat.
    for s in alignment['scenes']:
        for phase,u in [('opening',.08),('middle',.5),('closing',.9)]:
            frame=120+s['startFrame']+round((s['endFrame']-s['startFrame']-1)*u);png=W/(s['id']+'-'+phase+'.png')
            if not png.exists():
                code=run([M.FF,'-loglevel','error','-nostdin','-n','-threads','2','-ss',frame/60,'-i',cap,'-frames:v','1','-threads','1',png],W/(s['id']+'-'+phase+'-extract.log'));assert code==0
            samples.append({'scene':s['id'],'frame':frame,'phase':phase,'path':str(png),'viewed':False})
    report['samples']=samples;report['status']='technical-checks-complete-direct-visual-and-content-review-pending'
    from PIL import Image,ImageDraw
    for page,start in enumerate(range(0,len(samples),12)):
        sheet=Image.new('RGB',(1500,3*236),'#080808');draw=ImageDraw.Draw(sheet)
        for j,entry in enumerate(samples[start:start+12]):
            im=Image.open(entry['path']).convert('RGB');im.thumbnail((375,211),Image.Resampling.LANCZOS);x=j%4*375;y=j//4*236;sheet.paste(im,(x,y));draw.text((x+8,y+214),entry['scene']+' '+entry['phase'],fill='white')
        sheet.save(W/('contact-'+str(page).zfill(2)+'.png'))
    M.save(W/'report.json',report)
    print(json.dumps({'technicalChecks':'complete','visualSamples':len(samples),'report':str(W/'report.json'),'readyForUserReview':False}))
if __name__=='__main__':main()
