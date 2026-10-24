"""Keep the prior lesson and captions; replace only planned gameplay intervals."""
from pathlib import Path
import importlib.util,sys,json,subprocess,shutil,datetime
spec=importlib.util.spec_from_file_location('patchlib',Path(__file__).with_name('render-patches.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
from numpy import zeros_like,linspace
import numpy as np
import soundfile as sf
R=m.R;B=m.B
def loudness(path,target=-16):
    p=subprocess.run(['ffmpeg','-hide_banner','-i',str(path),'-af',f'loudnorm=I={target}:TP=-1.5:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,encoding='utf8',check=True)
    return json.loads(p.stderr[p.stderr.rfind('{'):p.stderr.rfind('}')+1])
def main():
    plan=m.read(Path(sys.argv[1]));slug=plan['slug'];m.auth(plan['episode'])
    P=R/'projects'/slug;old=P/'production/concept-fit-v2';oldlocal=P/'production/local/concept-fit-v2';O=P/'production/local'/plan['revision'];H=P/'production'/plan['revision'];T=m.read(old/'timeline.json');slots={s['id']:s for s in T['scenes']}
    patches=m.read(H/'patches.json')['patches'];assert len(patches)==len(plan['patches'])
    D=R/'output'/f'{slug}-{plan["revision"]}';D.mkdir(parents=True,exist_ok=True)
    if (H/'outputs.json').exists() and (H/'technical-qa.json').exists():
        previous=m.read(H/'outputs.json')
        if previous.get('planSha256')==m.sha(Path(sys.argv[1])) and previous.get('patchIdentities')==[x['identity'] for x in patches] and all((R/x['path']).exists() and m.sha(R/x['path'])==x['sha256'] for x in previous['outputs']):
            print('Exact current delivery already encoded and technically checked; keeping existing files',flush=True)
            return
    narr=oldlocal/'audio/narration-matched.wav';voice,sr=sf.read(narr,dtype='float32',always_2d=True);assert sr==48000
    oldmix=m.read(old/'audio-mix.json');games=np.zeros_like(voice);tracks=[]
    for patch in plan['patches']:
        at=slots[patch['scene']]['start']+patch['offset'];source_info=plan['sources'][patch['source']];source=R/(source_info.get('audioPath') or source_info['path']);has_audio=any(s['codec_type']=='audio' for s in m.probe(source)['streams'])
        for i,s in enumerate(patch['segments']):
            if s['kind']=='motion' and has_audio:
                raw=O/f'game-{patch["scene"]}-{i}.wav'
                m.ff(['-i',source,'-vn','-af',f'atrim=start={s["in"]}:duration={s["seconds"]},asetpts=PTS-STARTPTS','-ar','48000','-ac','2','-c:a','pcm_f32le',raw],O/f'game-{patch["scene"]}-{i}.log',O)
                g,rr=sf.read(raw,dtype='float32',always_2d=True);assert rr==48000;count=round(s['seconds']*48000);assert len(g)>=count
                measurement=loudness(raw,-23);gain=-23-float(measurement['input_i']);g=g[:count]*10**(gain/20)
                ramp=min(480,len(g)//2);g[:ramp]*=np.linspace(0,1,ramp)[:,None];g[-ramp:]*=np.linspace(1,0,ramp)[:,None]
                off=round(at*48000);games[off:off+count]+=g
                tracks.append(dict(scene=patch['scene'],source=m.rel(source),sourceStart=s['in'],seconds=s['seconds'],timelineStart=at,gainDb=gain,initialLufs=-23))
            at+=s['seconds']
    gamefile=O/'game-synchronized.wav';sf.write(gamefile,games,48000,subtype='FLOAT')
    gain=oldmix['narrationGainDb'];graph=f'[0:a]volume={gain:.8f}dB,asplit=2[n][key];[1:a][key]sidechaincompress=threshold=0.08:ratio=2.2:attack=15:release=280:makeup=1[g];[n][g]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.80:attack=5:release=80:level=false:latency=true[out]'
    mix=O/'mix.m4a';m.ff(['-i',narr,'-i',gamefile,'-filter_complex',graph,'-map','[out]','-ar',48000,'-c:a','aac','-b:a','192k',mix],O/'mix.log',O)
    levels=loudness(mix)
    limiter=.80
    if float(levels['input_tp'])>-1.5:
        limiter=.74
        graph=graph.replace('limit=0.80','limit=0.74')
        m.ff(['-i',narr,'-i',gamefile,'-filter_complex',graph,'-map','[out]','-ar',48000,'-c:a','aac','-b:a','192k',mix],O/'mix-headroom.log',O)
        levels=loudness(mix)
    assert float(levels['input_tp'])<=-1.5
    m.save(H/'audio-mix.json',dict(path=m.rel(mix),sha256=m.sha(mix),narrationSource=m.rel(narr),narrationSourceSha256=m.sha(narr),narrationPcmChanged=False,narrationGainDb=gain,gameTracks=tracks,analyticalStillsHaveNoGameAudio=True,addedBgm=False,levels=levels,actualListening=False))
    prior_outputs=m.read(old/'outputs.json')['outputs'];base=R/next(x['path'] for x in prior_outputs if x['path'].endswith('.clean.mp4'))
    for ext in ['ko.ass','ko.srt','en.srt']:
        shutil.copy2(oldlocal/f'captions.{ext}',O/f'captions.{ext}')
    args=['-i',base];filters=['[0:v]setpts=PTS-STARTPTS,setsar=1[v0]']
    for i,patch in enumerate(patches,1):
        p=R/patch['path'];assert m.sha(p)==patch['sha256'];args+=['-i',p]
        begin=patch['start'];end=begin+patch['duration'];fadeout=max(0,patch['duration']-.18)
        filters.append(f'[{i}:v]format=yuva420p,fade=t=in:st=0:d=0.15:alpha=1,fade=t=out:st={fadeout}:d=0.18:alpha=1,setpts=PTS+{begin}/TB[p{i}]')
        filters.append(f'[v{i-1}][p{i}]overlay=0:0:eof_action=pass:enable=\'gte(t,{begin})*lt(t,{end})\'[v{i}]')
    filters.append(f'[v{len(patches)}]split=2[clean][capin]');filters.append('[capin]ass=captions.ko.ass[captioned]')
    args+=['-filter_complex_threads','2','-filter_complex',';'.join(filters)]
    for kind in ['clean','captioned']:
        args+=['-map',f'[{kind}]','-frames:v',T['frames'],'-an',*m.ENC,O/f'{kind}-video.mp4']
    m.auth(plan['episode']);print('Encoding full pair with preserved lesson',flush=True);m.ff(args,O/'final-pair.log',O)
    for kind in ['clean','captioned']:
        m.ff(['-i',O/f'{kind}-video.mp4','-i',mix,'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',D/f'{slug}.{kind}.mp4'],O/f'mux-{kind}.log',O)
    for lang in ['ko','en']:shutil.copy2(O/f'captions.{lang}.srt',D/f'{slug}.{lang}.srt')
    outputs=[dict(path=m.rel(p),bytes=p.stat().st_size,sha256=m.sha(p)) for p in [D/f'{slug}.{x}' for x in ['clean.mp4','captioned.mp4','ko.srt','en.srt']]]
    native=sum(p['nativeGameSeconds'] for p in patches);stills=sum(p['analyticalStillSeconds'] for p in patches)
    m.save(H/'outputs.json',dict(status='encoded-qa-pending',outputs=outputs,planSha256=m.sha(Path(sys.argv[1])),patchIdentities=[x['identity'] for x in patches],frames=T['frames'],seconds=T['seconds'],nativeGameSeconds=native,analyticalStillSeconds=stills,oldOutputsPreserved=True,oldBase=m.rel(base),oldBaseSha256=m.sha(base),newTts=False,humanReview='pending',actualWholeListening=False))
    title=next(x['title'] for x in m.read(B/'edit-list-audit.json')['entries'] if x['id']==plan['episode'])
    (D/'index.html').write_text(f'<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>{title} · 게임 장면 수정</title><style>body{{background:#101412;color:#f5f5ef;font:18px/1.7 system-ui;max-width:1200px;margin:30px auto;padding:20px}}h1{{color:#ffd773}}video{{width:100%}}a{{color:#80d3a2}}</style><h1>{title} · 게임 장면 수정</h1><p>기존 설명·수식·음성·길이 보존. 게임 장면과 표식, 연결 수정. <b>내부 검수 중</b></p><video controls src="{slug}.captioned.mp4"></video><p><a href="{slug}.captioned.mp4">자막 영상</a> · <a href="{slug}.clean.mp4">무자막 영상</a> · <a href="{slug}.ko.srt">한국어 자막</a> · <a href="{slug}.en.srt">영어 자막</a></p><p>정상 재생 {native:.1f}초 / 해설 중 관찰 정지 {stills:.1f}초. 정지 시간은 게임 재생 시간으로 세지 않습니다.</p><p><a href="../private-math-gameplay-20261024/index.html">18편 진행표</a></p></html>',encoding='utf8')
    print('Four files encoded, internal QA pending',flush=True)
if __name__=='__main__':main()
