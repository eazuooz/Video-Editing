"""Check unchanged AAC packet payloads and exact first/last packet times."""
import json
from pathlib import Path
import subprocess
import argparse
from inventory import ROOT,HERE,read,save
from render_revision import FF,CREATE


def packets(path):
    raw=subprocess.check_output([str(FF.with_name('ffprobe.exe')),'-v','error','-select_streams','a:0',
        '-show_packets','-show_data_hash','sha256','-show_entries','packet=pts_time,dts_time,duration_time,size,data_hash',
        '-of','json',str(path)],creationflags=CREATE)
    return json.loads(raw)['packets']


def run(eid):
    e=next(e for e in read(HERE/'inventory.json')['episodes'] if e['id']==eid)
    folder=ROOT/'projects'/e['slug']/'production/local/teaching-sync-v2'
    record=read(folder/'encoded.json');assert not record['addedGameAudioIntervals']
    old=packets(e['baselineOutputs']['clean']);new=packets(record['files']['clean']['path'])
    first=None
    for i,(a,b) in enumerate(zip(old,new)):
        if a['data_hash']!=b['data_hash']:first=i;break
    shift=next((n for n in range(3) if len(old)==len(new)+n and all(a['data_hash']==b['data_hash'] for a,b in zip(old[n:],new))),None)
    result=dict(episode=eid,baselinePackets=len(old),newPackets=len(new),
        firstPayloadDifference=first,samePrefix=first is None,
        baselineFirst=old[0],baselineLast=old[-2:],newFirst=new[0],newLast=new[-2:],
        leadingPacketOffset=shift,packetCountDifference=len(old)-len(new),
        diagnosis='Input -ss 0 omitted the negative-PTS AAC priming packet; all audible packet payloads match' if shift==1 and float(old[0]['pts_time'])<0 else 'See exact packet comparison',humanListening=False)
    save(folder/'audio-packet-diagnostic.json',result);print(json.dumps(result,ensure_ascii=False))
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('episode');run(parser.parse_args().episode)
