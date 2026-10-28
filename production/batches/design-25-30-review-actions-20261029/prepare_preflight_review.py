"""Prepare bounded 375px proof sheets from completed native captures, never render.

This is evidence preparation, not semantic/caption QA approval. Full native PNGs
remain available for 1080 review. Captions are reviewed later on actual composition.
"""
from pathlib import Path
import argparse,datetime,hashlib,json,math
from PIL import Image,ImageDraw,ImageFont
from freeze_sources import R,H,STAGES,digest,read

M=Path('C:/Users/1/.codex/video-production/design-25-30-review-actions-20261029')
def main():
    p=argparse.ArgumentParser();p.add_argument('--slug',choices=list(STAGES),required=True);p.add_argument('--revision',required=True);p.add_argument('--cut');a=p.parse_args()
    import re
    assert re.fullmatch(r'[A-Za-z0-9_-]+',a.revision)
    source=M/a.slug/'clarity-v3/preflight'/a.revision
    target=M/a.slug/'clarity-v3/qa'/('preflight-'+a.revision)
    assert source.resolve().is_relative_to((M/a.slug/'clarity-v3').resolve())
    assert target.resolve().is_relative_to((M/a.slug/'clarity-v3').resolve())
    assert source.is_dir(),'No capture to review'
    folders=sorted(p for p in source.iterdir() if p.is_dir() and (not a.cut or p.name==a.cut));assert folders
    target.mkdir(parents=True,exist_ok=True)
    font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',14)
    records=[]
    for folder in folders:
        success=read(folder/'preflight-success.json');request=read(folder/'request.json')
        assert success['status']=='complete' and success['compiledSourceFingerprint']==request['expectedFingerprint']
        files=sorted(folder.glob('frame-*.png'));assert len(files)==success['completed']==len(request['sampleFrames'])
        observed=[]
        for fp in files:
            frame=int(fp.stem.split('-')[-1]);im=Image.open(fp);assert im.size==(1920,1080)
            assert frame in request['sampleFrames']
            observed.append({'frame':frame,'seconds':round(frame/60,4),'path':str(fp),'sha256':digest(fp),'dimensions':list(im.size)})
        assert sorted(x['frame'] for x in observed)==request['sampleFrames']
        pages=[]
        for offset in range(0,len(files),12):
            group=files[offset:offset+12];rows=math.ceil(len(group)/3);sheet=Image.new('RGB',(3*375,rows*242),(18,20,23));draw=ImageDraw.Draw(sheet)
            for n,fp in enumerate(group):
                im=Image.open(fp).convert('RGB').resize((375,211),Image.Resampling.LANCZOS);x=(n%3)*375;y=(n//3)*242;sheet.paste(im,(x,y));frame=int(fp.stem.split('-')[-1])
                draw.text((x+8,y+216),f'{folder.name} · f{frame} · {frame/60:.2f}s',fill='white',font=font)
            out=target/(folder.name+'-375-'+str(offset//12+1).zfill(2)+'.png')
            assert not out.exists(),'Existing review sheet preserved; choose another revision or inspect it'
            sheet.save(out);pages.append({'path':str(out),'sha256':digest(out),'eachFrameWidth':375,'frames':len(group)})
        records.append({'cutId':folder.name,'nativeFrames':observed,'sheets':pages,'nativeCompiledFingerprint':success['compiledSourceFingerprint'],
            'savedScene':success.get('scene'),'semanticReview':'pending-direct-inspection','actualCaptionReview':'pending-final-composite-not-present-in-native-preflight'})
    result={'slug':a.slug,'revision':a.revision,'preparedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'status':'review-material-prepared-not-reviewed','nativeCaptureStartedByThisTool':False,
        'renderResolution':[1920,1080],'mobileFrameWidth':375,'cuts':records,
        'reviewQuestions':['Does the visible object/action/result match the spoken cue?','Do all grayscale world objects lose chroma while the brand UI remains colored? (D25)','Are official photos and illustration labels accurate without presenting mock measurements?','Are all labels/actors visible with the fixed final caption region reserved?','Inspect actual final-composite captions later; native preflight cannot prove subtitle clearance alone.']}
    report=R/'projects'/a.slug/'production/clarity-v3'/('preflight-'+a.revision+'-review.json')
    assert not report.exists(),'Existing review result preserved'
    report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':result['status'],'cuts':len(records),'report':report.relative_to(R).as_posix(),'nativeCaptureStarted':False}))
if __name__=='__main__':main()
