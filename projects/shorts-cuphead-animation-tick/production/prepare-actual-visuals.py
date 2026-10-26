"""Bind six teaching sections to actual PCM; extract only reviewed native cuts."""
from pathlib import Path
import hashlib, json, math, subprocess
from audio_revision import P, R, LOCAL, VOICE, REVISION, guard, assert_no_game_apps

IDS = ['game', 'frames', 'source-rates', 'pose24', 'position24', 'close']
def read(p): return json.loads(Path(p).read_text(encoding='utf8'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p, value):
    p=Path(p); data=json.dumps(value, ensure_ascii=False, indent=2)+'\n'
    if p.exists() and p.read_text(encoding='utf8')!=data:
        archive=LOCAL/'actual-visuals/previous'; archive.mkdir(parents=True,exist_ok=True)
        backup=archive/(p.stem+'-'+sha(p)[:16]+p.suffix)
        if not backup.exists(): backup.write_bytes(p.read_bytes())
    p.parent.mkdir(parents=True,exist_ok=True); p.write_text(data,encoding='utf8')
def run(args):
    r=subprocess.run(args,cwd=R,capture_output=True)
    if r.returncode: raise RuntimeError(r.stderr.decode(errors='replace')[-3000:])
    return r.stdout

def main():
    guard(); assert_no_game_apps()
    c=read(P/'script/captions.json'); pcm=read(VOICE.with_suffix('.timing.json'))
    config=read(P/'production/visual-config.json')
    assert c['timingInputs']['voiceSha256']==sha(VOICE)
    assert c['fps']==60 and c['frames']==math.ceil((pcm['duration_seconds']+.6)*60-1e-8)
    entries=sorted(pcm['entries'],key=lambda e:e['lineIndex'])
    assert len(entries)==6 and [e['lineIndex'] for e in entries]==list(range(6))
    # Caption edges and PCM boundaries can quantize one frame differently.
    # Move only the picture join, so every observed speech cue stays in its paragraph.
    bounds=[0]
    for i,e in enumerate(entries[1:],1):
        previous_end=max(q['endFrame'] for q in c['cues'] if q['lineIndex']==i-1)
        first=min(q['startFrame'] for q in c['cues'] if q['lineIndex']==i)
        assert previous_end<=first
        bounds.append(max(previous_end,min(first,math.floor((e['start']+.2)*60+.5))))
    bounds.append(c['frames'])
    events={q['id']:{k:q[k] for k in ['startFrame','endFrame']} for q in c['cues']}
    sections=[]; native=[]; outputs=[]
    source=Path(config['source']); assert sha(source)==config['sourceSHA256']
    probe=json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(source)]))
    v=next(x for x in probe['streams'] if x['codec_type']=='video')
    assert v['width']>=1920 and v['height']>=1080
    for i, id in enumerate(IDS):
        a,b=bounds[i:i+2]
        sections.append(dict(id=id,kind='mixed' if id in config['cuts'] else 'diagram',startFrame=a,endFrame=b,start=a/60,end=b/60))
        if id not in config['cuts']: continue
        cut=config['cuts'][id]; count=min(b-a,math.floor(cut['maxDuration']*60+1e-8)); at=cut['in']
        assert 0<=at<at+count/60<=float(probe['format']['duration'])
        cut['maxDuration']=count/60
        item=dict(id=id,kind='game',source='game-master',start=a/60,end=(a+count)/60,
                  startFrame=a,endFrame=a+count,sourceStart=at,sourceEnd=at+count/60,rate=1,nativeAudioAdopted=False)
        native.append(item)
        out=LOCAL/'frames'/id; receipt=out/'capture.json'
        recipe=dict(sourceSHA256=sha(source),sourceStart=at,sourceEnd=at+count/60,frames=count,fps=60,nativeDimensions=[1920,1080])
        if receipt.exists():
            prior=read(receipt); assert prior['recipe']==recipe
            files=sorted(out.glob('*.jpg')); assert len(files)==count
            assert sha(files[0])==prior['firstSHA256'] and sha(files[-1])==prior['lastSHA256']
        else:
            assert not list(out.glob('*.jpg')), 'Preserve unreceipted prior extraction'
            guard(); assert_no_game_apps(); out.mkdir(parents=True,exist_ok=True)
            run(['ffmpeg','-v','error','-n','-threads','2','-ss',str(at),'-i',str(source),'-an',
                 '-vf','fps=60','-frames:v',str(count),'-q:v','3','-threads','1','-start_number','0',str(out/'%06d.jpg')])
            files=sorted(out.glob('*.jpg')); assert len(files)==count
            write(receipt,dict(recipe=recipe,firstSHA256=sha(files[0]),lastSHA256=sha(files[-1])))
        outputs.append(dict(id=id,receipt=str(receipt.resolve()),frames=count))
    timing=dict(revision=REVISION,previewOnly=False,fps=60,frames=c['frames'],durationSeconds=c['durationSeconds'],
        voiceOffsetSeconds=.2,sections=sections,nativeSegments=native,events=events,
        timingInputs=dict(voiceSha256=sha(VOICE),clausesSha256=sha(P/'script/clauses.json')),
        sources={'game-master':dict(path=str(source),sourceSHA256=sha(source),originalOffsetSeconds=0,
            nativeAudioAdopted=False,sourceAudioAdopted=False,nativeDimensions=[1920,1080])},
        preparedFrames=outputs,actualGameSeconds=sum(s['end']-s['start'] for s in native),
        note='Six contiguous teaching sections; nativeSegments are the exact unslowed game intervals. Remaining time is the authored diagram, never held/looped gameplay.')
    config['framesPrepared']=True;config['status']='exact-native-cuts-prepared; actual-PCM-timing-bound'
    write(P/'production/visual-config.json',config)
    write(P/'production/visual-timing.json',timing);write(LOCAL/'visual-timing.json',timing)
    print(json.dumps(dict(frames=c['frames'],seconds=c['durationSeconds'],nativeSeconds=timing['actualGameSeconds'])))

if __name__=='__main__': main()
