"""Reference-style picture beats independent of the approved voice paragraph count."""
import argparse, hashlib, json, math, sys
from pathlib import Path
from PIL import Image,ImageDraw
import psutil
import render as legacy
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from make_approved_voice_v2 import read,save,sha,pcm
from review_approved_voice_v2 import compare_source
edit,film,voice,music=legacy.edit,legacy.film,legacy.voice,legacy.music

class BeatPainter:
    def __init__(self,painter,compact):self.painter=painter;self.compact=compact
    def __getattr__(self,name):return getattr(self.painter,name)
    def base(self,label):
        picture=self.painter.base(label)
        if self.compact:
            draw=ImageDraw.Draw(picture);draw.rectangle((0,70,984,295),fill='black')
            font=self.painter.title.font_variant(size=48)
            assert font.getlength(self.compact)<940
            draw.text((492,202),self.compact,font=font,anchor='mm',fill='#ffdd35')
        return picture

def validate(plan):
    assert plan['version']=='reference-causal-demonstration-v1'
    for p in plan['inputs']:assert sha(Path(p['path']))==p['sha256'],p['path']
    lock=read(Path(plan['lock']));assert lock['id']==plan['episode']
    assert len(plan['voiceFrames'])==len(plan['paragraphs'])==len(lock['narrationKo'])==len(lock['narrationEn'])
    assert sum(plan['voiceFrames'])==plan['bodyFrames']
    cursor=0;actual=native=0
    for c in plan['cuts']:
        assert c['startFrame']==cursor and c['endFrame']-cursor==c['frames']>0
        cursor=c['endFrame'];assert c['kind'] in ('gameplay','unity')
        if c['kind']=='gameplay':
            assert sha(Path(c['path']))==c['sha256'] and c['sourceEnd']>c['sourceStart']
            assert math.isclose(c['sourceEnd']-c['sourceStart'],c['frames']/60,abs_tol=1e-6)
            if not c.get('appendix'):actual+=c['frames']
        else:native+=c['frames']
    assert cursor==plan['bodyFrames']+plan['appendixFrames']
    assert actual==native and plan['cuts'][0]['kind']==plan['cuts'][-1]['kind']=='gameplay'
    return lock

def run(plan_path,capture_path,execute):
    plan=read(plan_path);lock=validate(plan);number=plan['episode'];root=Path(plan['voiceOutput'])
    capture=read(capture_path);assert capture['finalTimedCapture']
    native={r['id']:r for r in capture['captures']}
    for r in native.values():assert sha(Path(r['video']))==r['videoSha256']
    takes=[]
    for i,text in enumerate(lock['narrationKo']):
        path=root/'approved-voice'/f'{number}-{i}.wav';qp=root/'voice-qa-source'/f'{number}-{i}.json'
        q=read(qp);receipt=pcm(path)
        assert q['sha256']==receipt['sha256'] and q['expected']==text
        assert compare_source(text,q)[0]>=.88 and q['timestamped']
        assert plan['voiceFrames'][i]/60>=receipt['samples']/receipt['sampleRate']+.13
        takes.append(dict(path=path,proof=qp,review=q,**receipt))
    inputs=[Path(__file__),Path(legacy.__file__),plan_path,capture_path,film.FORMAT,music.PLAN_FILE,
      Path(film.__file__),Path(voice.__file__),Path(music.__file__)]
    identity={str(p):sha(p) for p in inputs};fp=hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest()
    output=legacy.WORK/'render-reference'/number/fp[:12];proof=output/'render-proof.json'
    print(json.dumps(dict(episode=number,fingerprint=fp,output=str(output),pictureCuts=len(plan['cuts'])),ensure_ascii=False),flush=True)
    if proof.exists():
        q=read(proof)
        for flavor in ('clean','captioned'):assert sha(output/q[flavor]['path'])==q[flavor]['sha256']
        print('Exact reference render preserved.');return
    if not execute:return
    output.mkdir(parents=True,exist_ok=True);psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    with legacy.reservation(output):
        painter=film.compositor(read(film.FORMAT),number);frames=plan['bodyFrames']+plan['appendixFrames']
        for p in plan['paragraphs']:
            for c in p['cues']:painter.captioned(Image.new('RGBA',(1080,1920)),c['text'])
        rows=[]
        for i,c in enumerate(plan['cuts']):
            is_native=c['kind']=='unity'
            if is_native:
                source=Path(native[c['nativeId']]['video']);offset=0;phase=plan['phases'][c['nativeId']]
                assert native[c['nativeId']]['decodedFrames']==c['frames']
            else:source=Path(c['path']);offset=c['sourceStart'];phase=dict(seconds=[0],labels=[c['label']])
            row=legacy.compose_cut(BeatPainter(painter,None if i==0 else plan['compactBodyTitle']),i,c['frames'],source,offset,phase,output,is_native)
            row['storyBeat']=c;rows.append(row);print(f'{number} reference beat {i+1}/{len(plan["cuts"])} complete',flush=True)
        narration=voice.narration_audio(takes,plan['voiceFrames'],output)
        if plan['appendixFrames']:
            extended=output/'narration-appendix.wav'
            edit.ffmpeg('-i',narration,'-af','apad','-t',frames/60,'-ar',48000,'-ac',1,extended);narration=extended
        track=read(music.PLAN_FILE)['music'][1]
        sound,mix=music.mixed_sound(number,track,[r['frames'] for r in rows],output,voice=narration)
        listing=output/'visual.ffconcat';listing.write_text(''.join(f"file '{Path(r['path']).as_posix()}'\n" for r in rows),'utf8')
        clean=output/'clean.mp4'
        edit.ffmpeg('-f','concat','-safe',0,'-i',listing,'-i',sound,'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',clean)
        clean_info=edit.validate(clean,frames)
        captions,cues=film.caption_track(number,painter,plan['paragraphs'],frames,output)
        captioned=output/'captioned.mp4'
        edit.ffmpeg('-threads',2,'-i',clean,'-f','concat','-safe',0,'-i',captions,'-filter_complex_threads',2,
          '-filter_complex','[0:v][1:v]overlay=0:1470:eof_action=pass:shortest=1[out]',
          '-map','[out]','-map','0:a:0','-c:v','libx264','-threads',4,'-preset','ultrafast','-crf',19,
          '-c:a','copy','-frames:v',frames,'-pix_fmt','yuv420p','-movflags','+faststart',captioned)
        caption_info=edit.validate(captioned,frames);pixels=film.caption_pixels(captioned,cues,output)
        en=[]
        for i,p in enumerate(plan['paragraphs']):
            en.append(f"{i+1}\n{edit.code_time(p['cues'][0]['startFrame'])} --> {edit.code_time(p['cues'][-1]['endFrame'])}\n{lock['narrationEn'][i]}\n")
        (output/'en.srt').write_text('\n'.join(en),'utf8')
        save(proof,dict(version=plan['version'],episode=number,fingerprint=fp,sourceInputs=identity,clean=clean_info,captioned=caption_info,
          cuts=rows,voiceFrames=plan['voiceFrames'],voiceLockSha256=sha(Path(plan['lock'])),mix=mix,music=track,
          captionPixelReview=pixels,subtitles={l:sha(output/f'{l}.srt') for l in ('ko','en')},approvedVoice=True,
          actualGameplayBodyFrames=plan['ratio']['actualGameplay'],nativeUnityFrames=plan['ratio']['unity'],
          requestedCombatAppendixFrames=plan['appendixFrames'],finalMixAsr='pending',localLevelContextReview='pending',
          movingVisualReview='pending',comprehensionReview='pending',actualHumanListening=False,finalEpisodeComplete=False))
        print(f'Reference edit rendered for internal QA: {output}',flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--edit',type=Path,required=True);p.add_argument('--capture',type=Path,required=True)
    p.add_argument('--execute',action='store_true');a=p.parse_args();run(a.edit,a.capture,a.execute)
