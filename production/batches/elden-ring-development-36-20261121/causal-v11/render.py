"""Versioned causal edit using the pinned Shorts layout, voice and native footage."""
import argparse
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import sys
import uuid

from PIL import Image,ImageDraw
import psutil

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
import build_pc_review as edit
import render_established_format_v6 as film
import render_approved_review_v2 as voice
import render_clarity_music_v5 as music
from make_approved_voice_v2 import read,save,sha,resource_guard

WORK=Path('D:/YamyamProduction/elden-ring-development-36-causal-v11')


@contextmanager
def reservation(output):
    guard=resource_guard();guard.OWNER='elden-ring-causal-v11';guard.PROTOCOL='elden-ring-causal-v11-render'
    if reason:=guard.busy_reason():raise RuntimeError(reason)
    worker=guard.SingleWorker(path=WORK/'render-worker.json');worker.acquire()
    token=uuid.uuid4().hex;owned=False
    try:
        if reason:=guard.busy_reason():raise RuntimeError(reason)
        guard.LEASE.parent.mkdir(parents=True,exist_ok=True)
        with guard.LEASE.open('x',encoding='utf8') as target:
            json.dump(dict(protocol=guard.PROTOCOL,owner=guard.OWNER,token=token,
                           **guard.identity(),phase='rendering',output=str(output)),target)
        owned=True
        if reason:=guard.busy_reason(own_token=token):raise RuntimeError(reason)
        yield
    finally:
        if owned and guard.LEASE.exists():
            current=read(guard.LEASE)
            if guard.ours(current) and current.get('token')==token:guard.LEASE.unlink()
        worker.close()


def compose_cut(painter,index,frames,source,offset,phase,dest,native=False):
    target=dest/f'{index}-clean.mp4';receipt=dest/f'{index}-cut.json'
    if receipt.exists():
        previous=read(receipt);assert sha(target)==previous['sha256'];return previous
    info=edit.probe(source)['streams'][0];size=(info['width'],info['height'])
    assert size==(950,650) if native else min(size)>=1080
    x,y,width,height=film.rectangles(size)
    labels=phase['labels'];starts=phase['seconds']
    inputs=[]
    for n,label in enumerate(labels):
        plate=dest/f'{index}-plate-{n}.png'
        picture=painter.base(label)
        if native:
            draw=ImageDraw.Draw(picture)
            draw.text((492,1410),phase.get('description','독립 원리 모형 · 저장된 위치 → 표면 재생' if index==3 else '독립 원리 모형 · 설정할 대상 비교'),
                      font=painter.label.font_variant(size=30),anchor='mm',fill='#f5f5f5')
        picture.save(plate);inputs.extend(['-loop',1,'-framerate',60,'-i',plate])
    raw_index=len(labels)
    inputs.extend(['-ss',offset,'-threads',2,'-i',source])
    cat=dest/f'{index}-reaction.png';picture=Image.new('RGBA',(1080,1920))
    painter.reaction(picture,'realize' if native else 'puzzled');picture.save(cat)
    inputs.extend(['-loop',1,'-framerate',60,'-i',cat])
    chain='';last='0:v'
    for n in range(1,len(labels)):
        chain+=f"[{last}][{n}:v]overlay=enable='gte(t,{starts[n]:.6f})'[plate{n}];";last=f'plate{n}'
    reaction_start=starts[-1] if native else .2
    chain+=(f'[{raw_index}:v]fps=60,scale={width}:{height}:flags=lanczos,setsar=1[body];'
            f'[{last}][body]overlay={x}:{y}:shortest=1[picture];'
            f"[picture][{raw_index+1}:v]overlay=enable='between(t,{reaction_start},{reaction_start+2})'[out]")
    edit.ffmpeg(*inputs,'-filter_complex_threads',2,'-filter_complex',chain,'-map','[out]','-an',
                '-frames:v',frames,'-c:v','libx264','-threads',4,'-preset','ultrafast','-crf',19,
                '-pix_fmt','yuv420p','-movflags','+faststart',target)
    stream=edit.probe(target)['streams'][0]
    assert int(stream['nb_frames'])==frames and stream['avg_frame_rate']=='60/1'
    result=dict(path=str(target),sha256=sha(target),frames=frames,source=str(source),sourceSha256=sha(source),
                sourceStart=offset,sourceSpeed=1,bodyRect=[x,y,width,height],sourceSize=list(size),
                originalAspectPreserved=True,nativeUnity=native,phases=phase)
    save(receipt,result);return result


def run(plan_path,capture_path,execute):
    plan=read(plan_path);lock=read(Path(plan['lock']));number=plan['episode']
    assert plan['version']=='causal-v11' and number==lock['id']
    for pin in plan['inputs']:assert sha(Path(pin['path']))==pin['sha256']
    capture=read(capture_path);assert capture['finalTimedCapture']
    native={r['id']:r for r in capture['captures']}
    for row in native.values():assert sha(Path(row['video']))==row['videoSha256']
    contract=read(film.FORMAT);music_plan=read(music.PLAN_FILE)
    sources=[Path(__file__),plan_path,capture_path,film.FORMAT,music.PLAN_FILE,
             Path(film.__file__),Path(voice.__file__),Path(music.__file__)]
    identity={str(p):sha(p) for p in sources}
    fp=hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest()
    output=WORK/'render'/number/fp[:12]
    print(json.dumps(dict(episode=number,output=str(output),fingerprint=fp),ensure_ascii=False),flush=True)
    if not execute:return
    proof=output/'render-proof.json'
    if proof.exists():
        old=read(proof)
        for flavor in ('clean','captioned'):assert sha(output/old[flavor]['path'])==old[flavor]['sha256']
        print('Exact render preserved; QA status is separate.');return
    output.mkdir(parents=True,exist_ok=True)
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    with reservation(output):
        painter=film.compositor(contract,number)
        lengths=plan['sceneFrames'];frames=sum(lengths)+plan['appendixFrames']
        takes=voice.collect_takes(lock,Path(plan['voiceOutput']));assert takes and len(takes)==4
        # Validate every full-size clause before any long encode, retaining the exact 48px font.
        for paragraph in plan['paragraphs']:
            for cue in paragraph['cues']:painter.captioned(Image.new('RGBA',(1080,1920)),cue['text'])
        rows=[];game={r['index']:r for r in plan['gameplay']}
        cut_lengths=lengths+([plan['appendixFrames']] if plan['appendixFrames'] else [])
        for i,count in enumerate(cut_lengths):
            if i%2:
                source=Path(native[f'{number}-{i}']['video']);offset=0;phase=plan['phases'][str(i)]
            else:
                source=Path(game[i]['path']);offset=game[i]['start']
                phase=dict(seconds=[0],labels=[game[i].get('label','실제 리카드 전투 · 검과 몸의 움직임' if i==4 else '엘든 링 실제 영상 · 검에 붙은 팔')])
            rows.append(compose_cut(painter,i,count,source,offset,phase,output,i%2==1))
            print(f'{number} visual cut {i} complete',flush=True)
        narration=voice.narration_audio(takes,lengths,output)
        padded=output/'narration-with-appendix.wav'
        edit.ffmpeg('-i',narration,'-af','apad','-t',frames/60,'-ar',48000,'-ac',1,padded)
        track=music_plan['music'][1]
        sound,mix=music.mixed_sound(number,track,cut_lengths,output,voice=padded)
        listing=output/'visual.ffconcat'
        listing.write_text(''.join(f"file '{Path(r['path']).as_posix()}'\n" for r in rows),encoding='utf8')
        clean=output/'clean.mp4'
        edit.ffmpeg('-f','concat','-safe',0,'-i',listing,'-i',sound,'-map','0:v:0','-map','1:a:0',
                    '-c','copy','-movflags','+faststart',clean)
        clean_info=edit.validate(clean,frames)
        caption_list,cues=film.caption_track(number,painter,plan['paragraphs'],frames,output)
        captioned=output/'captioned.mp4'
        edit.ffmpeg('-threads',2,'-i',clean,'-f','concat','-safe',0,'-i',caption_list,'-filter_complex_threads',2,
                    '-filter_complex','[0:v][1:v]overlay=0:1470:eof_action=pass:shortest=1[out]',
                    '-map','[out]','-map','0:a:0','-c:v','libx264','-threads',4,'-preset','ultrafast',
                    '-crf',19,'-c:a','copy','-frames:v',frames,'-pix_fmt','yuv420p','-movflags','+faststart',captioned)
        caption_info=edit.validate(captioned,frames)
        pixels=film.caption_pixels(captioned,cues,output)
        en=[]
        for i,paragraph in enumerate(plan['paragraphs']):
            lo=paragraph['cues'][0]['startFrame'];hi=paragraph['cues'][-1]['endFrame']
            en.append(f"{i+1}\n{edit.code_time(lo)} --> {edit.code_time(hi)}\n{lock['narrationEn'][i]}\n")
        (output/'en.srt').write_text('\n'.join(en),encoding='utf8')
        result=dict(version='causal-v11',episode=number,fingerprint=fp,sourceInputs=identity,
                    clean=clean_info,captioned=caption_info,cuts=rows,mix=mix,music=track,
                    captionPixelReview=pixels,subtitles={l:sha(output/f'{l}.srt') for l in ('ko','en')},
                    approvedVoice=True,voiceLockSha256=sha(Path(plan['lock'])),
                    actualGameplayBodyFrames=lengths[0]+lengths[2],nativeUnityFrames=lengths[1]+lengths[3],
                    requestedCombatAppendixFrames=plan['appendixFrames'],
                    finalMixAsr='pending',localLevelContextReview='pending',movingVisualReview='pending',
                    actualHumanListening=False,actualRealtimePlayback=False,finalEpisodeComplete=False)
        save(proof,result);print(f'Rendered for internal QA: {output}',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--edit',type=Path,required=True)
    parser.add_argument('--capture',type=Path,required=True);parser.add_argument('--execute',action='store_true')
    a=parser.parse_args();run(a.edit,a.capture,a.execute)
