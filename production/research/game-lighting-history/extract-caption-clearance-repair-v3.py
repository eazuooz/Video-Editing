"""Inspect only changed explanations against the unchanged final caption events."""
import importlib.util
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
p=Path(__file__).with_name('review-media-common-v15.py')
s=importlib.util.spec_from_file_location('review_media',p)
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
plan_path=m.PROD/'caption-clearance-repair-plan-v3.json';plan=m.read(plan_path)
proof_path=(m.ROOT/plan['output']).with_suffix('.verification.json');proof=m.read(proof_path)
assert proof['wholeDecode']['exitCode']==0 and proof['outputSha256']==m.sha(m.ROOT/plan['output'])
request=m.read(m.PROD/'encoded-pixel-review-request-v15.json')
layout=m.read(m.PROD/'local/captions-v15/caption-layout-measurement.json')
ass=m.ROOT/layout['ass']['path'];assert m.sha(ass)==layout['ass']['sha256']
points=[]
for c in plan['clips']:
    for q in request['points']:
        if c['fromFrame']<=q['frame']<c['toFrame']:
            points.append(dict(q,repairFrame=q['frame']-c['fromFrame']+c['repairFromFrame']))
assert len({q['repairFrame']for q in points})==len(points)
points.sort(key=lambda q:q['repairFrame'])
out=m.ROOT/'production/research/game-lighting-history/local/caption-clearance-pixel-qa-v3'
assert not out.exists(),'Preserve existing extraction'
observation=m.resources();out.mkdir();(out/'frames').mkdir()
ass_filter=ass.as_posix().replace(':',r'\:')
count=len(plan['clips']);lines=[f"[0:v]split={count}"+''.join(f'[s{i}]'for i in range(count))+';']
for i,c in enumerate(plan['clips']):
    lines.append(f"[s{i}]trim=start_frame={c['repairFromFrame']}:end_frame={c['repairToFrame']},settb=1/90000,setpts=(N+{c['fromFrame']})*1500,ass='{ass_filter}',setpts=N*1500[c{i}];")
select='+'.join(f'eq(n\\,{q["repairFrame"]})'for q in points)
lines.append(''.join(f'[c{i}]'for i in range(count))+f'concat=n={count}:v=1:a=0,settb=1/90000,setpts=N*1500,select={select}[out]')
filters=out/'repair-captions.filter';filters.write_text('\n'.join(lines)+'\n','utf-8')
state_path=m.PROD/'caption-clearance-pixel-execution-v3.json'
state=dict(startedAt=m.stamp(),status='extracting',worker=m.worker(),active=None,resourceObservation=observation,
           points=points,images=[],boards=[],source=plan['output'],sourceSha256=proof['outputSha256'],
           originalCaptionAssSha256=layout['ass']['sha256'],cpuThreads=2,gpuJobs=0,newGitImages=0,allFinalPixelsReviewed=False)
m.save(state_path,state)
try:
    extraction=m.run([m.FF,'-n','-v','error','-threads','2','-filter_complex_threads','2','-reinit_filter','0','-i',m.ROOT/plan['output'],
                      '-filter_complex_script',filters,'-map','[out]','-an','-fps_mode','vfr','-threads','2',out/'frames/frame-%05d.png'],
                     'caption-clearance-extraction',state,state_path,out)
    files=sorted((out/'frames').glob('frame-*.png'));assert len(files)==len(points),(len(files),len(points))
    font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',22)
    for i,(f,q)in enumerate(zip(files,points)):
        with Image.open(f)as im:assert im.size==(1920,1080)
        state['images'].append(dict(q,index=i+1,path=m.rel(f),sha256=m.sha(f)))
    for i in range(0,len(files),6):
        group=state['images'][i:i+6];board=Image.new('RGB',(2880,1204),(25,25,25));draw=ImageDraw.Draw(board)
        for j,q in enumerate(group):
            x=(j%3)*960;y=(j//3)*602
            with Image.open(m.ROOT/q['path'])as im:board.paste(im.resize((960,540),Image.Resampling.LANCZOS),(x,y+62))
            draw.text((x+10,y+6),f"#{q['index']} / original f{q['frame']} / {q['input']}",font=font,fill='white')
            draw.text((x+10,y+32),'unchanged fixed caption / '+','.join(map(str,q['visibleCueIds'])),font=font,fill='#e5c873')
        b=out/f'board-{i//6+1:03d}.png';board.save(b)
        state['boards'].append(dict(path=m.rel(b),sha256=m.sha(b),imageIndices=[q['index']for q in group],directlyRead=False))
    state.update(status='complete',exitCode=0,completedAt=m.stamp(),extraction=extraction,allFinalPixelsReviewed=False)
    m.save(state_path,state);print(m.json.dumps(dict(images=len(files),boards=len(state['boards']),finalApproval=False)),flush=True)
except BaseException as e:
    state.update(status='failed',exitCode=1,error=str(e),failedAt=m.stamp());m.save(state_path,state);raise
