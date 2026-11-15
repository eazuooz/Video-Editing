"""Supplemental realized motion and 375px evidence from the encoded master."""
from subject_revision import *
from PIL import ImageDraw


def main(eid,sid):
    e=EPISODES[eid];p=work(e);enc=read(p/'encoded.json');movie=Path(enc['files']['captioned']['path']);s=next(x for x in e['scenes'] if x['scene']==sid)
    out=p/'motion-qa'/sid;out.mkdir(parents=True,exist_ok=True);previous=out/'evidence.json'
    if previous.exists():
        assert read(previous)['movieSha256']==sha(movie),'Preserve and archive old motion evidence before sampling a different encode'
        return
    assert not any(out.glob('sample-*.png')),'Partial samples must be archived before a retry'
    start=round(s['start']*60)/60;frames=round((s['end']-start)*60);step=max(1,round((frames-1)/11))
    subprocess.run([str(FF),'-v','error','-nostdin','-n','-threads','1','-ss',str(start),'-i',str(movie),'-t',str(frames/60),'-vf',f'select=not(mod(n\\,{step})),scale=480:270','-fps_mode','vfr','-frames:v','12','-threads','1',str(out/'sample-%02d.png')],check=True,creationflags=prior.CREATE)
    files=sorted(out.glob('sample-*.png'));board=Image.new('RGB',(1440,294*math.ceil(len(files)/3)),'black');d=ImageDraw.Draw(board)
    for index,f in enumerate(files):
        x=index%3*480;y=index//3*294;board.paste(Image.open(f),(x,y));d.text((x+5,y+273),f'{eid}/{sid} @ {start+index*step/60:.2f}s',fill='white')
    target=out/'sequence.jpg';board.save(target,quality=95)
    time=(s['start']+s['end'])/2
    subprocess.run([str(FF),'-v','error','-nostdin','-n','-threads','1','-ss',str(time),'-i',str(movie),'-frames:v','1','-vf','scale=375:-2','-threads','1',str(out/'mobile.png')],check=True,creationflags=prior.CREATE)
    save(previous,dict(episode=eid,scene=sid,movieSha256=sha(movie),nativePictureSequence=True,method='Twelve actual encoded positions sampled on the original 60fps clock, plus 375px output. This is sampled motion evidence, not uninterrupted full viewing.',board=str(target),mobile=str(out/'mobile.png'),actuallyInspected=False))
    print(target,flush=True)


if __name__=='__main__':
    import sys
    main(*sys.argv[1:])
