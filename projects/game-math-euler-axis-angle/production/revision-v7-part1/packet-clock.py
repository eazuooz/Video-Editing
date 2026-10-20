"""Put the already encoded comparison on an exact60fps packet clock.

The reused branding has a different B-frame decode delay from the native
scene encodes. Concat preserves all pictures but rounds track durations by
up to8ms. Preserve those masters, then copy packet payloads with uniform
decode timestamps and verified presentation ranks. No video/audio encode.
"""
from pathlib import Path
from fractions import Fraction
import hashlib, importlib.util, json, subprocess
import av

H=Path(__file__).resolve().parent;R=H.parents[3]
O=R/'projects/game-math-euler-axis-angle/production/local/revision-v7-part1'

def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p):return Path(p).resolve().relative_to(R).as_posix()
def save(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

def packets(file):
    result={}
    with av.open(str(file))as container:
        for stream in container.streams:
            digest=hashlib.sha256();rows=[]
            with av.open(str(file))as source:
                s=source.streams[stream.index]
                for packet in source.demux(s):
                    if packet.pts is None:continue
                    payload=bytes(packet)
                    digest.update(len(payload).to_bytes(8,'big'));digest.update(payload)
                    rows.append((packet.pts,packet.dts,packet.duration))
            result[stream.type]=dict(rows=rows,payloadSha256=digest.hexdigest(),
                timeBase=str(stream.time_base),averageRate=str(stream.average_rate)if stream.type=='video'else None)
    return result

def main():
    sp=importlib.util.spec_from_file_location('v7_packet_authority',H/'timing.py')
    module=importlib.util.module_from_spec(sp);sp.loader.exec_module(module);module.authorized()
    timeline=read(H/'timeline.json');total=timeline['totalFrames']
    history=O/'qa-history/before-packet-clock';history.mkdir(parents=True,exist_ok=False)
    build=O/'edit/master-build.json';old_build=history/'master-build.json'
    old_build.write_bytes(build.read_bytes());records=[]
    for kind in ['clean','captioned']:
        target=O/f'part1-{kind}.mp4';before=packets(target)
        video=before['video'];rows=video['rows'];ordered=sorted(x[0]for x in rows)
        assert video['timeBase']=='1/60000'and len(rows)==total and len(set(ordered))==total
        # Each existing displayed picture is already within half a frame of
        # its intended index. Never invent/drop/repeat/reorder a picture.
        assert all(round(pts/1000)==i for i,pts in enumerate(ordered))
        assert max(i-round(row[0]/1000)for i,row in enumerate(rows))<=2
        original=history/target.name;target.replace(original)
        log=O/'edit'/f'{kind}-packet-clock.log'
        command=['ffmpeg','-hide_banner','-loglevel','warning','-nostdin','-n',
            '-i',str(original),'-map','0:v:0','-map','0:a:0','-c','copy',
            '-bsf:v','setts=pts=round(PTS/1000)*1000:dts=(N-2)*1000:duration=1000:time_base=1/60000',
            '-video_track_timescale','60000','-movflags','+faststart',str(target)]
        with log.open('w',encoding='utf8')as stream:
            subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT,check=True)
        after=packets(target);v=after['video'];new_rows=v['rows']
        assert len(new_rows)==total and v['timeBase']=='1/60000'and Fraction(v['averageRate'])==60
        assert sorted(r[0]for r in new_rows)==list(range(0,total*1000,1000))
        assert all(r[1]==(i-2)*1000 and r[2]==1000 for i,r in enumerate(new_rows))
        assert v['payloadSha256']==video['payloadSha256']
        assert after['audio']==before['audio'],'Original AAC packets and clock must be identical'
        records.append(dict(kind=kind,original=rel(original),originalSha256=sha(original),
            file=rel(target),sha256=sha(target),bytes=target.stat().st_size,frames=total,
            originalMaxPresentationErrorTicks=max(abs(p-i*1000)for i,p in enumerate(ordered)),
            videoPacketPayloadSha256=v['payloadSha256'],audioPacketPayloadSha256=after['audio']['payloadSha256'],
            videoPayloadUnchanged=True,audioPayloadAndClockUnchanged=True,
            presentationClock='frame index /60',decodeClock='(packet index -2)/60',
            durationSeconds=total/60,averageRate='60',noReencoding=True))
    report=dict(schemaVersion=1,implementation=rel(Path(__file__)),implementationSha256=sha(Path(__file__)),
        reason='Normalize stream-copy concat branding/native-scene B-frame clocks; preserve original masters.',
        outputs=records,decodedPixels='Unchanged encoded packets; exact scene rawRGB proofs and full PTS/decode checked separately.',
        audioWholeAsr='Reuse single complete actual AAC recognition with packet/clock identity binding; do not recognize identical AAC again.')
    save(O/'edit/packet-clock.json',report)
    data=read(build);data['prePacketClockBuild']=dict(file=rel(old_build),sha256=sha(old_build))
    data['postMuxPacketClock']=dict(file=rel(O/'edit/packet-clock.json'),sha256=sha(O/'edit/packet-clock.json'))
    data['outputs']=[{k:r[k]for k in ['kind','file','sha256','bytes']}for r in records]
    save(build,data)
    print(json.dumps(dict(outputs=data['outputs'],videoAndAudioPacketPayloadsPreserved=True)),flush=True)

if __name__=='__main__':main()
