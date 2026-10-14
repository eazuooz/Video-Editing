"""All ten changed-input cue boundaries/midpoints, local-only review images."""
from pathlib import Path
import importlib.util,json
from PIL import Image,ImageDraw,ImageFont
spec=importlib.util.spec_from_file_location('m',Path(__file__).with_name('review-media-common-v15.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
R=m.ROOT;P=R/'projects/game-lighting-history-04/production'
ep=P/'part1-texture-preview-execution-v343.json';ex=m.read(ep);assert ex['status']=='complete-awaiting-direct-review'
plan=m.read(P/'part1-final-input-plan-v309.json');out=R/'production/research/game-lighting-history/local/part1-texture-preview-cues-v343b';sp=P/'part1-texture-preview-cues-execution-v343b.json'
assert not out.exists() and not sp.exists();resources=m.resources();out.mkdir()
state=dict(startedAt=m.stamp(),status='running',worker=m.worker(),active=None,resources=resources,commands=[],images=[],boards=[],newGitImages=0,directlyReviewed=False)
m.save(sp,state)
try:
    for r in ex['results']:
        video=R/r['preview']['path'];assert m.sha(video)==r['preview']['sha256']
        qs=[q for q in plan['koCues'] if q['entryId']==r['id'].split(':')[0]];assert len(qs)==5
        points={0,r['frames']-1}
        for q in qs:
            a,b=q['fromFrame']-r['fromFrame'],q['toFrame']-r['fromFrame']
            points.update(f for f in [a-1,a,(a+b-1)//2,b-1,b] if 0<=f<r['frames'])
        slug=r['id'].split(':')[0];fd=out/slug;fd.mkdir();filt=fd/'select.filter'
        filt.write_text('select='+'+'.join(f'eq(pts\\,{f*1500})' for f in sorted(points))+'\n','utf8')
        m.run([m.FF,'-n','-v','error','-threads','2','-filter_threads','2','-i',video,'-filter_script:v',filt,'-fps_mode','vfr','-an','-threads','2',fd/'frame-%05d.png'],slug+'-cue-pixels',state,sp,out)
        files=sorted(fd.glob('frame-*.png'));assert len(files)==len(points)
        for file,frame in zip(files,sorted(points)):
            visible=[q for q in qs if q['fromFrame']-r['fromFrame']<=frame<q['toFrame']-r['fromFrame']]
            with Image.open(file) as im:assert im.size==(1920,1080)
            state['images'].append(dict(index=len(state['images'])+1,path=m.rel(file),sha256=m.sha(file),id=r['id'],frame=frame,globalFrame=frame+r['fromFrame'],cueIds=[q['id'] for q in visible],text=[q['text'] for q in visible]))
    font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',22)
    for i in range(0,len(state['images']),6):
        group=state['images'][i:i+6];board=Image.new('RGB',(2880,1204),(25,25,25));draw=ImageDraw.Draw(board)
        for k,p in enumerate(group):
            x,y=k%3*960,k//3*602
            with Image.open(R/p['path']) as im:board.paste(im.resize((960,540),Image.Resampling.LANCZOS),(x,y+62))
            draw.text((x+10,y+8),f"#{p['index']} {p['id']} f{p['frame']}",font=font,fill='white')
            draw.text((x+10,y+34),f"global{p['globalFrame']} cue{p['cueIds']}",font=font,fill='#e5c873')
        dest=out/f'board-{i//6+1:03d}.png';board.save(dest)
        state['boards'].append(dict(board=i//6+1,path=m.rel(dest),sha256=m.sha(dest),imageIndices=[p['index'] for p in group],directlyRead=False))
    state.update(status='complete',exitCode=0,active=None,completedAt=m.stamp(),previewExecutionSha256=m.sha(ep),allTenCuesPlanned=True,allPixelsApproved=False)
    m.save(sp,state);print(json.dumps(dict(images=len(state['images']),boards=len(state['boards']),approved=False)))
except BaseException as e:
    state.update(status='failed',exitCode=1,error=repr(e),active=None,failedAt=m.stamp());m.save(sp,state);raise
