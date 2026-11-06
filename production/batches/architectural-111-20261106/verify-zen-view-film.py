"""Pure CPU fixtures: no external programs, native media, model or output writes."""
import copy,importlib.util,json,subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('zen_film_fixture',HERE/'render-zen-view-film.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
passed=[]
def check(name,fn):fn();passed.append(name)
def yes(value):
    if not value:raise AssertionError('Expected true')
def rejects(fn):
    try:fn()
    except (ValueError,KeyError):return
    raise AssertionError('Expected contract rejection')
def native(id,a,b,mode='narrow',first=0,count=None,layout='singlePlayer',hold=False):
    return dict(id=id,startFrame=a,endFrameExclusive=b,kind='native',native=dict(mode=mode,layout=layout,startNativeFrame=first,frameCount=count if count is not None else b-a,playbackRate=1,holdPolicy=dict(frame=first,reason='Explain the center-ray alignment')if hold else None),guideParts=[])
def fixture():
    return dict(schemaVersion='07-04-final-timeline-v1',topicId='07.04',format=dict(width=1080,height=1920,fps=60),totalFrames=1080,sections=[native('narrow-a',0,240),native('narrow-explain',240,360,first=239,count=1,hold=True),native('narrow-b',360,600,first=240),native('wide',600,1080,'wide')],captions=dict(ko=[],en=[]),catCues=[])
def mutate(fn):
    t=fixture();fn(t);return t
def invalid(fn):rejects(lambda:m.validate_structure(mutate(fn)))

check('split native clock with explicit held239 preserves all480 once',lambda:yes(m.validate_structure(fixture())['movingNativeFrames']==dict(narrow=480,wide=480)))
check('native hold remains exact239 across its output interval',lambda:yes(m.native_frame(fixture()['sections'][1],359)==239))
check('native moving resumes at240 rather than replaying held239',lambda:yes(m.native_frame(fixture()['sections'][2],360)==240))
check('end-exclusive cuts choose next scene exactly at cut',lambda:yes(m.section_at(fixture(),240)['id']=='narrow-explain'))
check('outside output frame never wraps',lambda:rejects(lambda:m.section_at(fixture(),1080)))
check('native missing source frame rejected',lambda:invalid(lambda t:t['sections'][2]['native'].update(startNativeFrame=241,frameCount=239)))
check('repeated native frame rejected',lambda:invalid(lambda t:t['sections'][2]['native'].update(startNativeFrame=239)))
check('moving clock cannot be silently held to fill duration',lambda:invalid(lambda t:t['sections'][0]['native'].update(frameCount=239)))
check('explanatory hold without teaching reason rejected',lambda:invalid(lambda t:t['sections'][1]['native']['holdPolicy'].update(reason='')))
check('30fps source cadence preserved at60fps without invented interpolation',lambda:yes([m.source_index([0,1/30,2/30],f/60)for f in range(5)]==[0,0,1,1,2]))
check('missing source before first actual PTS rejected',lambda:rejects(lambda:m.source_index([.5,1],.4)))
check('unknown visual guide part rejected',lambda:invalid(lambda t:t['sections'][1].update(guideParts=['hidden-target-box'])))
check('progressive centerline-only and mouths-only accepted',lambda:yes(m.validate_structure(mutate(lambda t:(t['sections'][0].update(guideParts=['centerline']),t['sections'][1].update(guideParts=['mouths']))))['sections']==4))

def cat(layout):
    t=fixture();t['sections'][1]['native']['layout']=layout;t['catCues']=[dict(startFrame=250,endFrameExclusive=300,pose='realize',easeInFrames=7,easeOutFrames=9)];return t
check('approved largecat accepted only on single-player',lambda:yes(m.validate_structure(cat('singlePlayer'))['sections']==4))
check('dual camera cat overlap rejected',lambda:rejects(lambda:m.validate_structure(cat('dual'))))
check('same-clock AB cat overlap rejected',lambda:rejects(lambda:m.validate_structure(cat('sameClockAB'))))
def term_cat():
    t=cat('singlePlayer');t['sections'][1]['termChips']=[dict(english='Zen View',korean='젠 뷰',meaning='이동 중 잠깐 보이는 풍경',presentation='definition')];return t
check('term definition and largecat cannot overlap',lambda:rejects(lambda:m.validate_structure(term_cat())))
def chip_cat():
    t=term_cat();t['sections'][1]['termChips'][0]['presentation']='chip';return t
check('collapsed upper termchip permits single-player largecat below',lambda:yes(m.validate_structure(chip_cat())['sections']==4))

def source_timeline(freeze=False):
    s=dict(id='actual',startFrame=0,endFrameExclusive=150,kind='observation-freeze'if freeze else'gameplay',sourceId='verified-hl2',sourcePath='fixture-source.mp4',sourceSHA256='a'*64)
    if freeze:s.update(sourceFrameIndex=150,sourceLocalPts=2.5,holdReason='Inspect the visible CF sign',label='관찰용 정지')
    else:s.update(sourceLocalInPts=.5,rate=1)
    return dict(schemaVersion='07-04-final-timeline-v1',topicId='07.04',format=dict(width=1080,height=1920,fps=60),totalFrames=150,sections=[s],captions=dict(ko=[],en=[]),catCues=[])
check('observation frame150/PTS2.5 exact identity accepted',lambda:yes(m.validate_structure(source_timeline(True))['observationFreezes']==1))
def wrong_freeze():
    t=source_timeline(True);t['sections'][0]['sourceFrameIndex']=149;return t
check('unverified observation still frame rejected',lambda:rejects(lambda:m.validate_structure(wrong_freeze())))
def repeat_game():
    t=source_timeline();t['totalFrames']=300;t['sections'].append(dict(t['sections'][0],id='reused',startFrame=150,endFrameExclusive=300));return t
check('same gameplay interval cannot repeat as padding',lambda:rejects(lambda:m.validate_structure(repeat_game())))
def actual_cat():
    t=source_timeline();t['catCues']=[dict(startFrame=0,endFrameExclusive=50,pose='puzzled',easeInFrames=7,easeOutFrames=9)];return t
check('cat cannot cover actual source evidence',lambda:rejects(lambda:m.validate_structure(actual_cat())))
check('foreign output root rejected',lambda:rejects(lambda:m.output_root('D:/other')))
check('caption emphasis cannot cross wrapped lines',lambda:rejects(lambda:m.emphasis(dict(text='one two',lines=['one','two'],emphasis=[dict(start=2,end=5,role='term')]))))

def cut_clearing():
    """Same-source/other-source cuts dispose exact decoder and clear held picture."""
    class D:
        def __init__(self):self.index=0;self.selected=[0];self.closed=[]
        def close(self,failed=False):self.closed.append(failed)
    r=m.FrameRouter.__new__(m.FrameRouter);r.t=dict(totalFrames=2,sections=[native('A',0,1,count=1,hold=True),native('B',1,2,count=1,hold=True)],captions=dict(ko=[]),catCues=[])
    r.current='A';r.freeze='old actual still';r.decoder=D();old=r.decoder
    from PIL import Image
    r.native_picture=lambda section,frame:(Image.new('RGB',(2,2)),dict(nativeFrame=0))
    r.compose(1)
    yes(old.closed==[False]and r.freeze is None and r.current=='B'and r.decoder is None)
check('cut clears prior held picture/decoder without carrying annotations',cut_clearing)

def inset():
    t=source_timeline(True);t['sections'][0]['detailInset']=dict(sourceCropXYXY=[1500,280,1740,500],destinationXYWH=[70,1010,360,330],label='창밖 표지판 확대');return t
check('same frozen source detail inset preserves crop aspect',lambda:yes(m.validate_structure(inset())['sections']==1))
def wrong_inset():
    t=inset();t['sections'][0]['detailInset']['sourceCropXYXY'][0]=1400;return t
check('unreviewed alternate inset crop rejected',lambda:rejects(lambda:m.validate_structure(wrong_inset())))
def unowned_launch():
    try:m.owned_popen(['ffmpeg'])
    except RuntimeError:return
    raise AssertionError('Unowned process unexpectedly allowed')
check('unowned process launch fails before Popen',unowned_launch)

class Runtime:
    @staticmethod
    def ours(r):return r.get('owner')=='selected'and r.get('token')=='known'
    @staticmethod
    def alive(r):return bool(r and r.get('alive'))
    @staticmethod
    def identity(pid=None):return dict(pid=pid or 1,createTime=1)
def recover_fixture():
    import sys,types
    old=sys.modules.get('psutil');sys.modules['psutil']=types.SimpleNamespace(process_iter=lambda fields:[],NoSuchProcess=type('Gone',(Exception,),{}),AccessDenied=type('Denied',(Exception,),{}))
    try:
        rt=Runtime();r=dict(owner='selected',token='known',child=None,children=[])
        yes(m.reclaimable_lease(r,{'known'},rt))
        yes(not m.reclaimable_lease(dict(r,owner='foreign'),{'known'},rt))
        yes(not m.reclaimable_lease(r,{'unproven'},rt))
        yes(not m.reclaimable_lease(dict(r,children=[dict(alive=True)]),{'known'},rt))
        sys.modules['psutil'].process_iter=lambda fields:[types.SimpleNamespace(info=dict(cmdline=['ffmpeg','exact-cut'],create_time=20))]
        yes(m.pending_child(dict(r,pendingCommand=['ffmpeg','exact-cut'],pendingAfter=19.9),rt))
        yes(not m.pending_child(dict(r,pendingCommand=['ffmpeg','other-cut'],pendingAfter=19.9),rt))
    finally:
        if old is None:del sys.modules['psutil']
        else:sys.modules['psutil']=old
check('lease recovery preserves foreign/unproven/livechildren and exact launchgap',recover_fixture)

def failed_launch():
    old=(m.fresh_authorization,m.save,m.read,m.subprocess.Popen)
    records=[];worker=type('W',(),dict(update=lambda self,**k:None))();rt=Runtime();rt.LEASE='fixture-no-file'
    m.fresh_authorization=lambda:None;m.save=lambda p,r:records.append(copy.deepcopy(r));m.read=lambda p:dict(owner='selected',token='known')
    def fail(*a,**k):raise OSError('fixture cannot launch')
    m.subprocess.Popen=fail
    rec=dict(owner='selected',token='known',children=[]);controller=m.OwnedController(rt,worker,rec)
    try:
        try:controller.launch(['ffmpeg','fixture'])
        except OSError:pass
        yes(rec['pendingCommand']==['ffmpeg','fixture']and records[-1]['phase']=='launching'and not controller.handles)
    finally:m.fresh_authorization,m.save,m.read,m.subprocess.Popen=old
check('failed Popen preserves exact pending-command ownership evidence',failed_launch)

def foreign_write():
    old=(m.read,m.save);m.read=lambda p:dict(owner='foreign',token='foreign');m.save=lambda *a:(_ for _ in()).throw(AssertionError('foreign lease mutated'))
    rt=Runtime();rt.LEASE='fixture-no-file';c=m.OwnedController(rt,None,dict(owner='selected',token='known'))
    try:
        try:c.write()
        except RuntimeError:return
        raise AssertionError('Foreign lease not rejected')
    finally:m.read,m.save=old
check('lease update cannot overwrite changed foreign ownership',foreign_write)

print(json.dumps(dict(passed=len(passed),checks=passed,externalProcessesStarted=False,mediaReadOrWritten=False,gpuUsed=False,actualRenderVerified=False),ensure_ascii=False))
