"""Prepare local-only comparisons from already extracted native frames; no media rerun."""
from pathlib import Path
from PIL import Image, ImageDraw
import json, hashlib
ROOT=Path(__file__).resolve().parents[5]
BASE=Path(__file__).resolve().parent
OUT=BASE.parent/'research-local/additional-cross-source-comparison'
OUT.mkdir(exist_ok=True)
sources={}
for name in ['native-review-v1.json','native-review-rocket-v1.json','native-review-drill-v1.json','native-review-additional-measured-actions.json']:
    doc=json.loads((BASE/name).read_text(encoding='utf-8-sig'))
    for source in doc['sources']:sources[source['videoId']]=source['actionSamples']
cases=[
 ('Pepper cave','KWDk-csu460',[10.5,12,13.5],'o3Fomp9HdHs',[13,14,15]),
 ('Pepper column','KWDk-csu460',[14.5,16,18],'z4utn4Sm6SY',[17.5,18,18.5]),
 ('Pepper water','KWDk-csu460',[51,51.5,52],'z4utn4Sm6SY',[14.5,15,15.5]),
 ('Pepper cauldron','KWDk-csu460',[55,56,57],'z4utn4Sm6SY',[16,17,27]),
 ('Pepper green mech','KWDk-csu460',[42,42.5,43],'o3Fomp9HdHs',[57,58,59]),
 ('Plucky industrial lift','MJSMqtG0Kcs',[19,19.5,20],'JdNZo7E_hXU',[17,18,18.5]),
 ('Plucky city portal','MJSMqtG0Kcs',[26,27,28],'JdNZo7E_hXU',[91,92,93]),
 ('Plucky mug','MJSMqtG0Kcs',[38.5,39,39.5],'h27ZF-hKKYM',[27.5,29.5,31]),
 ('Plucky castle print','MJSMqtG0Kcs',[42.5,43,44],'WFIvd2HrMNY',[44,47,50]),
 ('Plucky rocket','MJSMqtG0Kcs',[55,55.5,56],'h27ZF-hKKYM',[72,75,77.5]),
 ('Plucky flags','MJSMqtG0Kcs',[56.5,57.5,58.5],'WFIvd2HrMNY',[58.5,60,61]),
 ('Plucky accordion stairs','MJSMqtG0Kcs',[53,53.5,53.5],'JdNZo7E_hXU',[100.5,101,101]),
]
rows=[]
for label,left,times,right,oldtimes in cases:
    for t,u in zip(times,oldtimes):
        a=min(sources[left],key=lambda v:abs(v['pts']-t));b=min(sources[right],key=lambda v:abs(v['pts']-u))
        rows.append(dict(case=label,newVideoId=left,newRequested=t,newNativeSample=a,oldVideoId=right,oldRequested=u,oldNativeSample=b,directlyReviewed=False))
sheets=[]
for start in range(0,len(rows),4):
    group=rows[start:start+4];canvas=Image.new('RGB',(1280,len(group)*390),'white');draw=ImageDraw.Draw(canvas)
    for i,row in enumerate(group):
        y=i*390
        for column,tag,key in [(0,'NEW','newNativeSample'),(1,'OLD','oldNativeSample')]:
            sample=row[key];p=ROOT/sample['path']
            assert hashlib.sha256(p.read_bytes()).hexdigest()==sample['sha256']
            image=Image.open(p).convert('RGB').resize((640,360))
            canvas.paste(image,(column*640,y+30))
            draw.text((column*640+3,y+2),f"{row['case']} {tag} {row['newVideoId'] if column==0 else row['oldVideoId']} n{sample['frame']} {sample['pts']:.3f}s",fill='black')
    path=OUT/f'comparison-{start//4+1:02}.jpg';canvas.save(path,quality=94)
    sheets.append(dict(path=path.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),rows=group,directlyRead=False))
result=dict(schemaVersion=1,method='Nearest already extracted native samples at three requested anchors per candidate; actual sampled PTS shown. Direct visual sequence comparison required; distances are not a duplicate verdict.',cases=len(cases),pairs=len(rows),sheets=sheets,newGitImages=0,approvedIntervals=[],approvedActualSeconds=0)
(BASE/'additional-cross-source-comparison.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'cases':len(cases),'pairs':len(rows),'localOnlySheets':len(sheets),'newGitImages':0}))
