"""Reproducible local sample: plan -> Manim render -> assemble -> burn -> QA.

Use the repository's approved Qwen voice and word-aligned KO/EN subtitle tools
before `plan`. This script does not publish, upload, or change other projects.
"""
from pathlib import Path
import argparse,csv,hashlib,io,json,math,re,shutil,subprocess,sys
import numpy as np
import soundfile as sf
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'projects/game-math-polar-sample'
WORK=ROOT/'shared/output/game-math-polar-sample';WORK.mkdir(parents=True,exist_ok=True)
MC=ROOT/'motion-canvas/src/projects/game-math-polar-sample'
MF=BASE/'project.json';FPS=60
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def write(p,v):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def rel(p):return Path(p).relative_to(ROOT).as_posix()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(args,log=None):
    r=subprocess.run([str(a) for a in args],cwd=ROOT,capture_output=True,encoding='utf8',errors='replace',creationflags=subprocess.CREATE_NO_WINDOW)
    if log:write(WORK/log,r.stdout+r.stderr)
    if r.returncode:raise RuntimeError(' '.join(str(a) for a in args[:6])+'\n'+r.stderr[-4500:])
    return r.stdout+r.stderr
def ff(args,log=None):return run(['ffmpeg','-hide_banner','-y','-threads','4',*args],log)
def probe(p):return json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',p]))
def srt_stamp(t):
    n=round(t*1000);h,n=divmod(n,3600000);mi,n=divmod(n,60000);s,n=divmod(n,1000)
    return f'{h:02}:{mi:02}:{s:02},{n:03}'
def parse_stamp(t):
    h,mi,s=re.split('[:,]',t)[:3];ms=t.split(',')[-1]
    return int(h)*3600+int(mi)*60+int(s)+int(ms)/1000
def parse_srt(p):
    out=[]
    for block in Path(p).read_text(encoding='utf-8-sig').strip().split('\n\n'):
        lines=block.splitlines();a,b=lines[1].split(' --> ')
        out.append({'start':parse_stamp(a),'end':parse_stamp(b),'text':'\n'.join(lines[2:])})
    return out
def srt(cues):return '\n\n'.join(f'{i}\n{srt_stamp(c["start"])} --> {srt_stamp(c["end"])}\n{c["text"]}' for i,c in enumerate(cues,1))+'\n'

def plan():
    m=read(MF);ko=read(ROOT/m['paths']['script'])
    out=ROOT/m['tts']['outputDir'];stem=m['tts']['filenameStem']
    timing=read(out/(stem+'.timing.json'))
    assert timing.get('alignment'), 'Run word-timestamp subtitle alignment first'
    classes={'01':'Overview','03':'Locate','05':'Convert','07':'Cylinder'}
    default=dict(zip(['01','02','03','04','05','06','07'],[1320,1320,1560,1392,1680,1320,1488]))
    raw={};minimum={}
    for scene in ko['scenes']:
        f=out/'chunks'/f'{scene["id"]}-scene.wav';audio,sr=sf.read(f,dtype='float32')
        raw[scene['id']]=(audio,sr,f);minimum[scene['id']]=math.ceil((len(audio)/sr+.55)*FPS)
    body=10080
    for classification,ids in [('explanation',list(classes)),('actual',['02','04','06'])]:
        share=.6 if classification=='explanation' else .4
        body=max(body,math.ceil(sum(minimum[i] for i in ids)/share/5)*5)
    frames=default.copy()
    for ids,total in [(list(classes),int(body*.6)),(['02','04','06'],int(body*.4))]:
        for i in ids:frames[i]=max(frames[i],minimum[i])
        while sum(frames[i] for i in ids)>total:
            key=max(ids,key=lambda i:frames[i]-minimum[i]);assert frames[key]>minimum[key]
            frames[key]-=1
        while sum(frames[i] for i in ids)<total:
            key=min(ids,key=lambda i:frames[i]/default[i]);frames[key]+=1
    scenes=[];start=2
    voice=np.zeros(round((body/FPS+12)*24000),dtype='float32')
    for s in ko['scenes']:
        i=s['id'];audio,sr,f=raw[i];assert sr==24000 and audio.ndim==1
        entries=[x for x in timing['entries'] if x['scene_id']==i];origin=entries[0]['start']
        cues=[{'start':x['start']-origin,'end':x['end']-origin,'text':x['text']} for x in entries]
        slot={'id':i,'title':s['title'],'start':start,'frames':frames[i],'seconds':frames[i]/FPS,'voice':rel(f),'voiceSeconds':len(audio)/sr,'voiceSha256':sha(f),'rawOrigin':origin,'cues':cues,'classification':'explanation' if i in classes else 'actual','manimClass':classes.get(i)}
        scenes.append(slot);at=round(start*sr);voice[at:at+len(audio)]=audio;start+=frames[i]/FPS
    timeline={'fps':FPS,'frames':body+720,'seconds':body/FPS+12,'bodyFrames':body,'bodySeconds':body/FPS,'actualFrames':int(body*.4),'explanationFrames':int(body*.6),'actualShare':.4,'explanationShare':.6,'introSeconds':2,'outroSeconds':10,'scenes':scenes}
    assert abs(start+10-timeline['seconds'])<1e-8
    sf.write(ROOT/m['paths']['narration'],voice,24000)
    for lang in ['ko','en']:
        source=parse_srt(BASE/f'script/voice-aligned.{lang}.srt');final=[]
        for c in source:
            s=next(s for s in reversed(scenes) if c['start']>=s['rawOrigin']-.004)
            final.append({**c,'start':s['start']+c['start']-s['rawOrigin'],'end':s['start']+c['end']-s['rawOrigin'],'scene':s['id']})
        write(ROOT/m['paths']['captions'+lang.title()],srt(final));timeline[lang+'Captions']=final
    assert [(c['start'],c['end']) for c in timeline['koCaptions']]==[(c['start'],c['end']) for c in timeline['enCaptions']]
    cuts=read(BASE/'sources/gameplay-cuts.json')
    for c in cuts['cuts']:c['duration']=next(s['seconds'] for s in scenes if s['id']==c['scene'])
    write(BASE/'sources/gameplay-cuts.json',cuts)
    for s in scenes:
        if s['classification']=='actual':s['cut']=next(c for c in cuts['cuts'] if c['scene']==s['id'])
    write(BASE/'production/timeline.json',timeline)
    m['video']['durationSeconds']=timeline['seconds']
    m['editing'].update(actualGameplaySeconds=timeline['actualFrames']/FPS,actualExplanationSeconds=timeline['explanationFrames']/FPS,actualGameplayShare=.4,actualCommercialGameplaySeconds=timeline['actualFrames']/FPS,actualDevelopmentFootageSeconds=0,actualPrototypeExplanationSeconds=0,timingStatus='measured-waveforms-and-word-aligned-bilingual-cues')
    m['editing']['openingOverview']['narrationSeconds']=scenes[0]['voiceSeconds']
    write(MF,m);records();print(json.dumps({'seconds':timeline['seconds'],'body':timeline['bodySeconds'],'actual':timeline['actualFrames']/FPS,'explanation':timeline['explanationFrames']/FPS,'captions':len(timeline['koCaptions']),'slots':[(s['id'],s['seconds'],s['voiceSeconds']) for s in scenes]}))

def records():
    """Export editor timing and cut records from the measured final timeline."""
    p=read(BASE/'production/timeline.json');scenes=p['scenes']
    for s in scenes:
        if s.get('cut'):
            c=s['cut'];s['cuts']=[{'source':'shared/output/game-math-polar-sample/sources/SlqDHvpYgZo.mp4','sourceIn':c['in'],'sourceOut':c['in']+c['duration'],'outputStart':s['start'],'durationSeconds':s['seconds'],'frames':s['frames'],'classification':'actual-existing-game','sourceAudioUsed':False,'viewport':c.get('viewport')}]
    write(BASE/'production/timeline.json',p)
    write(MC/'timing.ts','// Measured editorial slots; generated from production/timeline.json.\n'
        f'export const NARRATION_FPS = {p["fps"]};\nexport const TOTAL_DURATION = {p["seconds"]};\nexport const TOTAL_FRAMES = {p["frames"]};\n'
        f'export const SCENE_STARTS = {json.dumps([s["start"] for s in scenes])} as const;\n'
        f'export const SCENE_DURATIONS = {json.dumps([s["seconds"] for s in scenes])} as const;\n'
        f'export const SCENE_TITLES = {json.dumps([s["title"] for s in scenes],ensure_ascii=False)} as const;\n')
    buf=io.StringIO(newline='');writer=csv.writer(buf)
    writer.writerow(['scene','start','end','segment_type','visual','source','source_in','source_out','source_audio','bgm','status'])
    writer.writerow(['intro',0,2,'excluded-branding','original cat logo','shared/assets/branding/yamyamcoding-cats-original.png','','','off','continuous-Nimbus','rendered'])
    for s in scenes:
        c=s.get('cut',{});writer.writerow([s['id'],s['start'],s['start']+s['seconds'],s['classification'],s['title'],'SlqDHvpYgZo' if c else s['manimClass'],c.get('in',''),c['in']+c['duration'] if c else '','off','continuous-Nimbus','rendered-measured'])
    writer.writerow(['outro',p['seconds']-10,p['seconds'],'excluded-membership','original member profiles, names, badges','shared/assets/membership/member-list-20260929.png','','','off','continuous-Nimbus','rendered'])
    write(BASE/'planning/edit-cues.csv',buf.getvalue())

ENC=['-an','-c:v','libx264','-threads','4','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-r','60','-video_track_timescale','90000','-movflags','+faststart']
def render():
    run([sys.executable,'-m','manim','-qh','--disable_caching','--media_dir',rel(WORK/'manim'),'manim/projects/game-math-polar-sample/scene.py','BrandIntro','Overview','Locate','Convert','Cylinder','MemberOutro'],'manim-render.log')
    print('Manim renders completed.')
def loudness(file,target=-16,tp=-2):
    txt=ff(['-i',file,'-af',f'loudnorm=I={target}:TP={tp}:LRA=11:print_format=json','-f','null','-'])
    return json.loads(re.search(r'\{\s*"input_i"[\s\S]*?\}',txt).group())
def assemble(reuse_clips=False):
    m=read(MF);p=read(BASE/'production/timeline.json');cuts=read(BASE/'sources/gameplay-cuts.json');vdir=WORK/'manim/videos/scene/1080p60';clipdir=WORK/'clips';clipdir.mkdir(exist_ok=True)
    assets=MC/'assets';assets.mkdir(exist_ok=True)
    clips=[]
    for sid,cls,count in [('intro','BrandIntro',120),*[(s['id'],s.get('manimClass'),s['frames']) for s in p['scenes']],('outro','MemberOutro',600)]:
        target=clipdir/(sid+'.mp4')
        if reuse_clips:
            vi=next(x for x in probe(target)['streams'] if x['codec_type']=='video')
            assert int(vi['nb_frames'])==count and vi['width']==1920 and vi['height']==1080 and vi['r_frame_rate']=='60/1'
            clips.append(target);shutil.copy2(target,assets/f'{sid}.mp4')
            print('Existing clip',sid,'verified',count,'frames',flush=True)
            continue
        if cls:
            source=vdir/(cls+'.mp4');info=probe(source);video=next(x for x in info['streams'] if x['codec_type']=='video')
            assert float(video['duration'])>=count/FPS-1/FPS, (cls,video['duration'],count/FPS)
            # Cairo may round a fractional-second final wait down one frame.
            # Only original explanation/branding frames may use this static
            # end compensation; actual gameplay is never extended or looped.
            ff(['-i',source,'-vf','fps=60,setsar=1,tpad=stop_mode=clone:stop_duration=0.05','-frames:v',str(count),*ENC,target],f'clip-{sid}.log')
            write(clipdir/(sid+'.json'),{'source':rel(source),'sourceFrames':int(video['nb_frames']),'targetFrames':count,'endFrameCompensation':max(0,count-int(video['nb_frames'])),'classification':'explanation-or-excluded-branding'})
        else:
            c=next(c for c in cuts['cuts'] if c['scene']==sid)
            viewport='crop='+':'.join(str(v) for v in c['viewport'])+',' if c.get('viewport') else ''
            ff(['-ss',str(c['in']),'-i',ROOT/cuts['source']['file'],'-vf',viewport+'scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=60','-frames:v',str(count),*ENC,target],f'clip-{sid}.log')
        vi=next(x for x in probe(target)['streams'] if x['codec_type']=='video');assert int(vi['nb_frames'])==count
        clips.append(target);shutil.copy2(target,assets/f'{sid}.mp4')
        print('Clip',sid,'verified',count,'frames',flush=True)
    normalized=WORK/'voice-normalized.wav';lv=loudness(ROOT/m['paths']['narration'])
    f=f'loudnorm=I=-16:TP=-2:LRA=11:measured_I={lv["input_i"]}:measured_TP={lv["input_tp"]}:measured_LRA={lv["input_lra"]}:measured_thresh={lv["input_thresh"]}:offset={lv["target_offset"]}:linear=true,aresample=48000,aformat=channel_layouts=stereo'
    ff(['-i',ROOT/m['paths']['narration'],'-af',f,'-c:a','pcm_s16le',normalized],'voice-normalization.log')
    assert abs(float(probe(normalized)['format']['duration'])-p['seconds'])<.001
    filter=f'[0:a]asplit[n][d];[1:a]atrim=duration={p["seconds"]},asetpts=PTS-STARTPTS,loudnorm=I=-28:TP=-3:LRA=11,aresample=48000,aformat=channel_layouts=stereo,afade=t=in:d=0.4,afade=t=out:st={p["seconds"]-.6}:d=0.6[b];[b][d]sidechaincompress=threshold=.08:ratio=2.2:attack=15:release=280[bg];[n][bg]amix=inputs=2:normalize=0,alimiter=limit=.82:level=false:latency=true[mix]'
    write(WORK/'mix-filter.txt',filter)
    raw_mix=WORK/'mix-unmastered.wav'
    ff(['-i',normalized,'-i',ROOT/m['audio']['backgroundMusic']['file'],'-filter_complex_script',WORK/'mix-filter.txt','-map','[mix]','-t',str(p['seconds']),'-ar','48000','-ac','2','-c:a','pcm_s16le',raw_mix],'audio-mix.log')
    raw_measure=loudness(raw_mix,-16,-1.6)
    master=f'loudnorm=I=-16:TP=-1.6:LRA=11:measured_I={raw_measure["input_i"]}:measured_TP={raw_measure["input_tp"]}:measured_LRA={raw_measure["input_lra"]}:measured_thresh={raw_measure["input_thresh"]}:offset={raw_measure["target_offset"]}:linear=true,aresample=48000'
    ff(['-i',raw_mix,'-af',master,'-c:a','pcm_s16le',ROOT/m['paths']['editorAudioMix']],'mix-mastering.log')
    ff(['-i',ROOT/m['paths']['editorAudioMix'],'-c:a','aac','-b:a','192k',ROOT/m['paths']['audioMix']],'audio-aac.log')
    measure=loudness(ROOT/m['paths']['audioMix'],-16,-1.5)
    assert abs(float(measure['input_i'])+16)<=.65 and float(measure['input_tp'])<=-1.45,measure
    write(BASE/'audio/mix-measurements.json',{'voiceInput':lv,'rawMix':raw_measure,'final':measure,'continuousNimbus':True,'sourceAudioUsed':False,'humanListening':'pending','seconds':p['seconds']})
    write(WORK/'concat.txt','\n'.join("file '"+f.as_posix()+"'" for f in clips)+'\n')
    ff(['-f','concat','-safe','0','-i',WORK/'concat.txt','-i',ROOT/m['paths']['audioMix'],'-map','0:v','-map','1:a','-c','copy','-t',str(p['seconds']),'-movflags','+faststart',ROOT/m['paths']['videoClean']],'final-clean.log')
    print('Clean narrated sample assembled; captions and pixel QA next.')

def mix():
    """Resume audio assembly after all current-plan clips were rendered."""
    assemble(reuse_clips=True)

def ass_time(t):
    n=round(t*100);h,n=divmod(n,360000);mi,n=divmod(n,6000);s,n=divmod(n,100)
    return f'{h}:{mi:02}:{s:02}.{n:02}'
def burn():
    m=read(MF);p=read(BASE/'production/timeline.json');font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',48)
    header='''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Text,Malgun Gothic,48,&H00090B08,&H00090B08,&H00090B08,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1
Style: Shape,Malgun Gothic,48,&H00FFFFFF,&H00FFFFFF,&H00FFFFFF,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
'''
    events=[];layouts=[]
    for i,c in enumerate(p['koCaptions'],1):
        lines=c['text'].splitlines();assert len(lines)<=2
        width=max(font.getlength(line) for line in lines)+44;height=len(lines)*62+22
        assert width<=1614
        x,y=round(960-width/2),round(970-height/2);w=round(width);h=height
        assert x>=0 and y>=0 and x+w+14<=1920 and y+h+14<=1080
        a,b=ass_time(c['start']),ass_time(c['end'])
        def rect(layer,color,xx,yy,ww,hh):
            path=f'm {xx} {yy} l {xx+ww} {yy} {xx+ww} {yy+hh} {xx} {yy+hh}'
            events.append(f'Dialogue: {layer},{a},{b},Shape,,0,0,0,,{{\\an7\\pos(0,0)\\c&H{color}&\\p1}}{path}{{\\p0}}')
        rect(0,'323C07',x+14,y+14,w,h);rect(1,'181B16',x,y,w,h);rect(2,'FFFFFF',x+3,y+3,w-6,h-6)
        payload=c['text'].replace('\n',r'\N')
        events.append(f'Dialogue: 3,{a},{b},Text,,0,0,0,,{{\\an5\\pos(960,970)\\q2}}{payload}')
        layouts.append({'cue':i,'start':c['start'],'end':c['end'],'lines':len(lines),'box':[x,y,w,h],'center':[960,970],'shadow':[14,14],'scene':c['scene']})
    ass=BASE/'script/final.ko.ass';write(ass,header+'\n'.join(events)+'\n')
    ff(['-i',ROOT/m['paths']['videoClean'],'-vf',f'ass={rel(ass)}','-c:v','libx264','-threads','6','-preset','fast','-crf','19','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',ROOT/m['paths']['videoBurnedCaptions']],'burn-captions.log')
    write(BASE/'production/caption-layout.json',{'style':'boxed-white-forest-v1','editableText':'script/final.ko.ass','allCenters':[960,970],'layouts':layouts,'pixelReview':'pending'})
    print('Fixed bottom-center editable Korean captions burned.')

def qa():
    m=read(MF);p=read(BASE/'production/timeline.json');folder=WORK/'qa';folder.mkdir(exist_ok=True)
    videos={}
    for key in ['videoClean','videoBurnedCaptions']:
        file=ROOT/m['paths'][key];ff(['-v','error','-i',file,'-f','null','-'],f'decode-{key}.log')
        info=probe(file);v=next(x for x in info['streams'] if x['codec_type']=='video');a=next(x for x in info['streams'] if x['codec_type']=='audio')
        assert v['width']==1920 and v['height']==1080 and v['r_frame_rate']=='60/1' and int(v['nb_frames'])==p['frames'],v
        assert abs(float(info['format']['duration'])-p['seconds'])<=.03
        audio=run(['ffmpeg','-v','error','-i',file,'-map','0:a','-c','copy','-f','md5','-']).strip()
        videos[key]={'path':m['paths'][key],'sha256':sha(file),'frames':int(v['nb_frames']),'duration':float(info['format']['duration']),'fullDecode':True,'audioPacketMd5':audio}
    assert videos['videoClean']['audioPacketMd5']==videos['videoBurnedCaptions']['audioPacketMd5']
    font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18);strips=[];samples=[]
    for i,c in enumerate(p['koCaptions']):
        t=(c['start']+c['end'])/2;dest=folder/f'cue-{i+1:03}.jpg'
        ff(['-ss',str(t),'-i',ROOT/m['paths']['videoBurnedCaptions'],'-frames:v','1','-q:v','2',dest])
        page=i//24
        if page==len(strips):strips.append(Image.new('RGB',(1920,24//2*130),'#e9ecee'))
        im=Image.open(dest).crop((0,880,1920,1080)).resize((960,100));xx=(i%2)*960;yy=(i%24//2)*130
        strips[page].paste(im,(xx,yy+25));ImageDraw.Draw(strips[page]).text((xx+8,yy),f'Cue {i+1:03} · {t:.2f}s · scene {c["scene"]}',font=font,fill='#202020')
    for i,page in enumerate(strips):page.save(folder/f'caption-strips-{i+1:02}.jpg',quality=95)
    times=[.8,2.5,*[s['start']+s['seconds']*.55 for s in p['scenes']],p['seconds']-5]
    times.extend([next(s['start'] for s in p['scenes'] if s['id']=='07')+v for v in [2,10,16]])
    for i,t in enumerate(times):
        dest=folder/f'composition-{i+1:02}.jpg';ff(['-ss',str(t),'-i',ROOT/m['paths']['videoBurnedCaptions'],'-frames:v','1','-q:v','2',dest]);samples.append({'time':t,'path':rel(dest)})
    for start in range(0,len(samples),4):
        page=Image.new('RGB',(1920,1120),'#e9ecee')
        for j,s in enumerate(samples[start:start+4]):
            x=(j%2)*960;y=(j//2)*560;im=Image.open(ROOT/s['path']).resize((960,540));page.paste(im,(x,y+20));ImageDraw.Draw(page).text((x+8,y),f'{s["time"]:.2f}s',font=font,fill='#202020')
        page.save(folder/f'composition-sheet-{start//4+1:02}.jpg',quality=95)
    result={'fullDecodePassed':True,'videos':videos,'frames':p['frames'],'seconds':p['seconds'],'bodyFrames':p['bodyFrames'],'actualFrames':p['actualFrames'],'explanationFrames':p['explanationFrames'],'actualShare':.4,'explanationShare':.6,'ratioErrorFrames':0,'koEnMatchingTimes':True,'captionCount':len(p['koCaptions']),'captionStripPages':len(strips),'compositionSamples':samples,'directVisualReview':'pending','humanListening':'pending','rightsReview':'Uploader reuse permission checked; game IP and original Nimbus library file review pending','upload':'not requested; local sample only'}
    write(BASE/'production/qa.json',result);print(json.dumps({k:result[k] for k in ['seconds','frames','actualFrames','explanationFrames','ratioErrorFrames','captionCount','captionStripPages','directVisualReview']}))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['plan','records','render','assemble','mix','burn','qa']);args=parser.parse_args()
    globals()[args.stage]()
