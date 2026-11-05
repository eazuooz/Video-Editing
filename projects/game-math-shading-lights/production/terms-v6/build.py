"""Recompose the verified local M21 shots with bilingual headings and typeset math."""
import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from PIL import ImageFont

from voice import PROJECT, ROOT, WORK, read, write
sys.path.append(str(PROJECT/'production/sphere-v5'))
import delivery as original
from notation import TERMS, PAIRS
from layout import overlays, TITLES

SLUG=PROJECT.name
OUTPUT=ROOT/'output'/(SLUG+'-render-v6')
EDIT=WORK/'edit'
TABLE=original.Q['cuts']
V5=original.DEST
for folder in [OUTPUT,EDIT]:folder.mkdir(parents=True,exist_ok=True)
MAP_PATH=WORK/'voice/timing-maps.json'
MAPS=[np.array(x['anchors']) for x in read(MAP_PATH)] if MAP_PATH.is_file() else []
def retimed(seconds):
    for anchors in MAPS:
        if anchors[0,0]<seconds<anchors[-1,0]:
            return float(np.interp(seconds,anchors[:,0],anchors[:,1]))
    return seconds
def captions():
    words=sorted(TERMS,key=lambda term:-len(term[0]));lookup=dict(words)
    pattern=re.compile('|'.join(re.escape(k) for k,_ in words))
    seen=set();result=[]
    for row in original.KO:
        def rendered(match):
            word=match[0];term=lookup[word];first=term not in seen;seen.add(term)
            return f'{term} ({word})' if first else term
        text=pattern.sub(rendered,row['text'])
        text=re.sub(r'(BRDF(?: \(양방향 반사 분포 함수\))?)[, ]+(?:BRDF|비알디에프)',r'\1',text)
        text=re.sub(r'(Spherical Harmonics(?: \(구면 조화 함수\))?)[, ]+(?:SH|에스에이치)',r'\1',text)
        text=text.replace('비알디에프','BRDF')
        if int(row['scene'])==2 and '좀 더 정확한 말로는' in text:
            text='좀 더 정확한 말로는 양방향 반사 분포 함수,'
        result.append(dict(row,text=text,start=retimed(row['start']),end=retimed(row['end'])))
    return result
KO=captions()
def sidecars():
    for lang in ('ko','en'):
        src=V5/(SLUG+'.'+lang+'.srt')
        rows=original.CAP.read_srt(src)
        if lang=='ko':assert len(rows)==len(KO)
        for i,row in enumerate(rows):
            row['start']=retimed(row['start']-2)+2;row['end']=retimed(row['end']-2)+2
            if lang=='ko':row['text']=KO[i]['text']
        original.CAP.write_srt(OUTPUT/src.name,rows,0)
def make_layers():
    receipts=[]
    for cut in TABLE:
        if cut['kind']!='explanation':continue
        states=overlays(cut);name=cut['scene'];n=cut['frames'];lines=['ffconcat version 1.0']
        for i,(start,png) in enumerate(states):
            stop=states[i+1][0] if i+1<len(states) else n
            us=round(stop*1e6/60)-round(start*1e6/60)
            lines.extend(["file '"+png.as_posix()+"'",'option framerate 60',f'duration {us/1e6:.6f}'])
        lines.extend(["file '"+states[-1][1].as_posix()+"'",'option framerate 60'])
        (EDIT/(name+'.layers')).write_text('\n'.join(lines)+'\n',encoding='utf-8')
        receipts.append(dict(scene=name,frameCount=n,heading=TITLES[int(name)],formula=PAIRS[int(name)].equation if int(name) in PAIRS else None,states=[t for t,_ in states]))
    write(WORK/'layers.json',receipts)
def ff(args):
    subprocess.run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-y',*map(str,args)],cwd=EDIT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
def options():
    return ['-c:v','libx264','-preset','ultrafast','-crf','16','-threads','3','-pix_fmt','yuv420p','-bf','0','-g','120','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-video_track_timescale','90000']
def render(item):
    i,c=item;name=f'{i:03}-'+c['scene'];proof=EDIT/(name+'.json')
    n=c['frames'];start=c['globalStartFrame']/60;sid=int(c['scene'])
    raw=original.D/(name+'.mp4');clean=EDIT/(name+'.mp4');cap=EDIT/(name+'-cap.mp4')
    rows=[dict(a,start=max(0,a['start']-start),end=min(n/60,a['end']-start)) for a in KO if a['end']>start+1e-7 and a['start']<start+n/60-1e-7]
    highlights={}
    for row in rows:
        term=next((en for _,en in TERMS if row['text'].count(en)==1),None)
        if term:highlights[str(row['id'])]=dict(text=term,role='term')
        elif (v:=original.HL.get(str(row['id']))) and row['text'].count(v['text'])==1:highlights[str(row['id'])]=v
    face=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',48)
    bold=ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',48)
    for row in rows:
        key=str(row['id']);term=highlights.get(key,{}).get('text')
        if not term:continue
        def measure(line):
            return face.getlength(line)+(bold.getlength(term)-face.getlength(term) if term in line else 0)
        if not any(term in line for line in original.CAP.wrap_caption(row['text'],face,measure)):
            highlights.pop(key)
    layout=original.CAP.caption_ass(EDIT/(name+'.ass'),rows,0,highlights)
    assert all(len(a['lines'])<=2 for a in layout)
    inputs=hashlib.sha256((original.sha(EDIT/(name+'.ass'))+original.sha(original.D/(name+'.done.json'))+('gobo-inset' if sid==65 else '')).encode())
    if c['kind']=='explanation':
        layerlist=EDIT/(c['scene']+'.layers');inputs.update(layerlist.read_bytes())
        for path in sorted(set(re.findall("^file '(.+)'$",layerlist.read_text('utf-8'),re.M))):
            inputs.update(Path(path).read_bytes())
    stamp=inputs.hexdigest()
    if proof.is_file() and read(proof).get('inputs')==stamp and clean.exists() and cap.exists():return
    if c['kind']=='actual-gameplay':
        shutil.copyfile(raw,clean)
        old_rows=[original.KO[a['id']-1]['text'] for a in rows]
        if old_rows==[a['text'] for a in rows]:shutil.copyfile(original.D/(name+'-cap.mp4'),cap)
        else:ff(['-threads','2','-i',raw,'-an','-vf','ass='+name+'.ass','-frames:v',n,*options(),cap])
    else:
        layers=EDIT/(c['scene']+'.layers')
        # For moving readouts retain the actual V5 values in a clear line under the paired notation.
        live={11:(1186,363,650,66),20:(1186,437,660,69),65:(1038,427,741,194)}.get(sid)
        base='[0:v]' if not live else '[main]'
        graph='' if not live else '[0:v]split=2[main][values];'
        graph+=base+'[1:v]overlay=0:0:eof_action=repeat'
        if live:
            x,y,w,h=live
            resized=',scale=350:92' if sid==65 else ''
            origin='1515:788' if sid==65 else '1020:839'
            graph+=f'[pg];[values]crop={w}:{h}:{x}:{y}{resized}[value];[pg][value]overlay={origin}'
        graph+=' ,split=2[clean][sub];[sub]ass='+name+'.ass[cap]'
        ff(['-threads','2','-i',raw,'-threads','1','-f','concat','-safe','0','-i',layers,'-filter_complex_threads','2','-filter_complex',graph,'-map','[clean]','-an','-frames:v',n,*options(),clean,'-map','[cap]','-an','-frames:v',n,*options(),cap])
    assert original.frames(clean)==n==original.frames(cap)
    write(proof,dict(frames=n,scene=c['scene'],source=c['kind'],layoutCues=len(rows),inputs=stamp,clean=original.sha(clean),captioned=original.sha(cap)))
    print('Rendered',name,flush=True)
def mux(audio):
    total=original.Q['bodyFrames']+720
    for typ in ('clean','captioned'):
        entries=[(original.D/'brand.mp4',120)]+[(EDIT/(f'{i:03}-'+c['scene']+('-cap' if typ=='captioned' else '')+'.mp4'),c['frames']) for i,c in enumerate(TABLE)]+[(original.D/'member.mp4',600)]
        lst=EDIT/(typ+'-join.txt');lines=['ffconcat version 1.0'];frame=0
        for path,n in entries:
            us=round((frame+n)*1e6/60)-round(frame*1e6/60);lines+=["file '"+path.as_posix()+"'",f'duration {us/1e6:.6f}'];frame+=n
        assert frame==total
        lst.write_text('\n'.join(lines)+'\n',encoding='utf-8');target=OUTPUT/(SLUG+'.'+typ+'.mp4');temp=target.with_suffix('.joining.mp4')
        ff(['-f','concat','-safe','0','-i',lst,'-i',audio,'-map','0:v:0','-map','1:a:0','-c','copy','-video_track_timescale','90000','-movflags','+faststart',temp])
        assert original.frames(temp)==total;os.replace(temp,target)
if __name__=='__main__':
    args=argparse.ArgumentParser();args.add_argument('stage',choices=['layers','render','join']);args.add_argument('--only',type=int);args.add_argument('--audio',type=Path);opts=args.parse_args()
    if opts.stage=='layers':sidecars();make_layers()
    elif opts.stage=='render':
        jobs=list(enumerate(TABLE))
        if opts.only is not None:jobs=[x for x in jobs if int(x[1]['scene'])==opts.only]
        with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(render,jobs))
    else:mux(opts.audio or V5/(SLUG+'.clean.mp4'))
