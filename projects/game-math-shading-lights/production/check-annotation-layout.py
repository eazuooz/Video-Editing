"""Small CPU-decoded layout proof, not final timing or human listening."""
from pathlib import Path
import importlib.util,json,subprocess
P=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('composer',P/'production/compose-lecture.py');M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
W=P/'production/local/annotation-layout-v5';W.mkdir(exist_ok=True)
sources={x['id']:x for x in M.read(P/'planning/footage-audit.json')['sources']}
proof=[]
for sid,name in M.ANNOTATIONS.items():
    mark=M.read(P/'production/local/annotation-refined-v2'/(name+'.json'));src=sources[mark['sourceId']]
    cut={'scene':sid,'sourceIn':mark['start'],'sourceOut':mark['end'],'frames':round((mark['end']-mark['start'])*60)}
    record=M.annotation_ass(cut,src,W/(sid+'.ass'))
    # A literal clause from the scene is only a caption-clearance fixture.
    phrase=mark['label']+'을 함께 살펴보겠습니다.'
    M.C.caption_ass(W/(sid+'-caption.ass'),[{'start':0,'end':cut['frames']/60,'text':phrase,'id':1}],0,{'1':{'text':mark['label'],'role':'term'}})
    for label,dt in [('reveal',.0834),('held',min(.8,(mark['end']-mark['start'])/2))]:
        target=W/(sid+'-'+label+'.png')
        if not target.exists():
            vf=f'scale=1536:864:force_original_aspect_ratio=decrease:flags=lanczos,pad=1536:864:(ow-iw)/2:(oh-ih)/2:black,pad=1920:1080:192:48:black,setsar=1,setpts=PTS-STARTPTS+{dt}/TB,ass={sid}.ass,ass={sid}-caption.ass'
            subprocess.run([str(M.FF),'-hide_banner','-loglevel','error','-nostdin','-n','-threads','2','-ss',str(mark['start']+dt),'-i',str(M.R/src['file']),'-vf',vf,'-frames:v','1','-threads','1',str(target)],cwd=W,check=True,creationflags=M.CREATE)
        record[label]=str(target.relative_to(P))
    proof.append(record)
from PIL import Image,ImageDraw
for label in ['reveal','held']:
    contact=Image.new('RGB',(375*4,236*2),'#080808');draw=ImageDraw.Draw(contact)
    for i,row in enumerate(proof):
        im=Image.open(P/row[label]).convert('RGB');im.thumbnail((375,211),Image.Resampling.LANCZOS)
        x=(i%4)*375;y=(i//4)*236;contact.paste(im,(x,y));draw.text((x+10,y+214),row['scene']+' '+label,fill='white')
    contact.save(W/(label+'-375px.png'))
M.save(W/'geometry-check.json',{'frames':proof,'captionFixtureOnly':True,'actualCaptionTiming':False,'directVisualReview':False})
print(json.dumps({'generated':len(proof)*2,'mobileSheets':2,'path':str(W)}))
