"""Bounded actual-caption sample, preserving existing ASS timing and geometry."""
from sources import *
from PIL import Image

def main():
    ep='A02';rid='A02-cut-017-part-3'
    plan=read(H/'replacement-plan.json');row=next(r for e in plan['episodes']if e['id']==ep for r in e['rows']if r['id']==rid)
    src=R/row['output'];out=B/'local/contrast-v5/encoded-qa';out.mkdir(parents=True,exist_ok=True)
    ass=project(ep)/'production/local/relations-v4/captions.ass';rel=ass.relative_to(R).as_posix()
    start=row['relationFrameStart']/60;movie=out/'A02-actual-captions.mp4'
    subprocess.run(['ffmpeg','-v','error','-nostdin','-y','-threads','4','-i',str(src),'-vf',f'setpts=PTS+{start}/TB,ass={rel},setpts=PTS-STARTPTS','-frames:v',str(row['frames']),'-an','-threads','4','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p',str(movie)],cwd=R,check=True)
    subprocess.run(['ffmpeg','-v','error','-threads','4','-i',str(movie),'-f','null','-'],check=True)
    for t in (0.5,3,6):
        p=out/f'A02-actual-{t}.png';subprocess.run(['ffmpeg','-v','error','-nostdin','-y','-ss',str(t),'-i',str(movie),'-frames:v','1',str(p)],check=True)
        with Image.open(p)as im:im.resize((375,211),Image.Resampling.LANCZOS).save(p.with_name(p.stem+'-375.png'))
    receipt={'episode':ep,'row':rid,'sourceSha256':sha(src),'encodedSampleSha256':sha(movie),'assSha256':sha(ass),'actualCaptionClockStart':start,'frames':row['frames'],'fullDecode':'passed','sampleTimes':[0.5,3,6],'scope':'7.25-second encoded visual sample only; unchanged existing captions, no audio or full-video listening claim.','visualReview':'pending actual image inspection'}
    (out/'A02-sample-qa.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),'utf8')
    print(movie,flush=True)
if __name__=='__main__':main()
