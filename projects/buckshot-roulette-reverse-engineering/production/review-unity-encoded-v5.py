"""Extract actual encoded Unity frames; does not mark them visually reviewed."""
from pathlib import Path
import hashlib,json,subprocess,math,argparse
from PIL import Image,ImageDraw,ImageFont
import assemble_documentary as asm

P=Path(__file__).resolve().parents[1];U=P/'production/local/unity-v5'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--id');args=parser.parse_args()
    plan=read(P/'production/local/documentary-v5/timeline.json')
    build=read(U/'build.json');spec=read(P/'production/unity-workflow-v5-cues.json')
    font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',17);index=[]
    for row in spec['entries']:
        if args.id and args.id!=row['id']:continue
        d=U/row['id']/'render';v=d/'unity.mp4';receipt=read(d/'render-success.json')
        assert receipt['status']=='complete' and receipt['fingerprint']==build['fingerprint']
        meta=asm.probe(v,plan,count=True);stream=asm.video_stream(meta)
        assert stream['width']==1920 and stream['height']==1080 and stream['avg_frame_rate']=='60/1'
        assert int(stream['nb_read_frames'])==row['frames']
        digest=asm.digest(v);out=d/'review'/digest[:12];out.mkdir(parents=True,exist_ok=True)
        # Each change is observed before/on/after its cue, including adjacent
        # encoded frames. No continuous full-playback review is inferred.
        frames={0,row['frames']-1}
        for c in row['cues']:
            for offset in [-2,12,24,36,60]:frames.add(min(row['frames']-1,max(0,round(c['time']*60)+offset)))
        frames=sorted(frames)
        from final_visual_qa import balanced_sum
        expr=balanced_sum([f'eq(n\\,{n})' for n in frames])
        asm.command([asm.tool('ffmpeg',plan),'-v','error','-y','-threads','2','-filter_threads','1','-i',str(v),'-an','-vf','select='+expr,'-fps_mode','vfr','-threads','1',str(out/'frame-%04d.png')],out/'decode.log')
        images=sorted(out.glob('frame-*.png'));assert len(images)==len(frames)
        pages=[]
        for offset in range(0,len(images),12):
            batch=images[offset:offset+12];canvas=Image.new('RGB',(1500,math.ceil(len(batch)/4)*245),'#171717');draw=ImageDraw.Draw(canvas)
            for i,path in enumerate(batch):
                x=i%4*375;y=i//4*245;im=Image.open(path).convert('RGB').resize((375,211),Image.Resampling.LANCZOS)
                canvas.paste(im,(x,y));draw.text((x+4,y+215),f'{row["mode"]} F{frames[offset+i]:05}',font=font,fill='white')
            path=out/f'page-{offset//12+1:02}.jpg';canvas.save(path,quality=95);pages.append(str(path))
        producer={'sha256':digest,'actualFrames':row['frames'],'width':1920,'height':1080,'fps':60,'renderSuccess':str(d/'render-success.json'),'renderSuccessSha256':asm.digest(d/'render-success.json'),'fingerprint':build['fingerprint'],'scene':receipt['scene'],'probe':meta}
        save(d/'producer-receipt.json',producer)
        evidence={'id':row['id'],'mode':row['mode'],'sha256':digest,'fingerprint':build['fingerprint'],'frames':frames,'images':[str(x) for x in images],'pages':pages,'humanViewing':False,'status':'extracted-not-yet-reviewed'}
        save(out/'index.json',evidence);index.append(evidence)
    save(U/('encoded-review-'+args.id+'.json' if args.id else 'encoded-review-index.json'),{'sources':index,'fingerprint':build['fingerprint']})
    print(json.dumps({'sources':len(index),'pages':sum(len(r['pages']) for r in index)}))
if __name__=='__main__':main()
