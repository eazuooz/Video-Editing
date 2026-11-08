"""A15-only extension approved by parent: three complete native passes.

No narration is lengthened or cut. Replace the former two music-only passes
with three full passes, and use the following body for narrated slow analysis.
All other episodes and the shared renderer definitions remain unchanged.
"""
from sources import *
from config import OVERRIDES
import render_rows as rr
from copy import deepcopy

def prepare():
    plan=read(H/'replacement-plan.json');e=next(e for e in plan['episodes']if e['id']=='A15')
    old=[r for r in e['rows']if r['key']=='keys'and r['mode']=='native'];assert len(old)==2
    definition=source('A15','keys')['definition']
    for animation in definition['animations']:
        for bone,track in animation['tracks'].items():
            if bone.endswith('_r')and bone.startswith(('thumb','index','middle','ring','pinky')):
                assert np.array_equal(track['q'][129],track['q'][-1]),('finger endpoint incomplete at129',bone)
    old.sort(key=lambda r:r['relationFrameStart']);assert old[0]['relationFrameEnd']==old[1]['relationFrameStart']
    output=B/'local/contrast-v5/explanation-plates/A15/full-keys';output.mkdir(parents=True,exist_ok=True)
    relative=lambda p:str(p.relative_to(R)).replace('\\','/')
    spec={'schemaVersion':1,'episode':'A15','status':'planned','fps':60,'relationCoordinate':'Unchanged relations-v4 baseline, before any parent speech/gameplay edits; ends exclusive.',
        'reason':'Existing native passes cut the continuous finger change at107F; actual motion changes until122F. Show source frames0..129 at1x, then18-frame final-pose hold, three times.',
        'audioPolicy':'Extend only the old music-only observation window. Keep all original narrated PCM unchanged. Parent rebases later picture/caption/audio positions and carries music through the longer observation.',
        'motionFramesPerPass':130,'extraFinalPoseHoldFrames':18,'framesPerPass':148,'passCount':3,'newFrames':444,
        'relationBaselineStartFrame':old[0]['relationFrameStart'],'relationBaselineEndFrame':old[-1]['relationFrameEnd'],
        'pacingBaselineStartFrame':old[0]['pacingFrameStart'],'pacingBaselineEndFrame':old[-1]['pacingFrameEnd'],
        'originalInsertionAtFrame':old[0]['insertionAtBaselineFrame'],'deltaFrames':444-sum(r['frames']for r in old),
        'overridesBaseRows':[r['id']for r in old],
        'output':relative(output/'three-complete-passes.mp4'),'bodyOverrides':[],
        'precedence':'Apply the length-changing observation replacement instead of the two base native rows, then these same-length body overrides instead of the corresponding base rows. All source ranges use the old baseline clock.',
        'source':input_receipt('A15','keys'),'finalStages':[12,65,130],'humanReviewed':False}
    for r in e['rows']:
        if r['key']=='keys'and r['mode']=='analysis':
            q=deepcopy(r);q['nativeLeadFrames']=0;q['showLegend']=False;q['output']=relative(output/(r['id']+'.mp4'));spec['bodyOverrides'].append(q)
    assert spec['deltaFrames']==230
    (H/'pacing-extension.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n','utf8')
    return spec

def execute():
    ctrl=read(R/'shared/publishing/video-production-control.json')['animationContrastRevision20261108'];assert ctrl['renderAuthorized']and'A15'in ctrl['episodes']
    spec=prepare();key='A15-keys';c=list(OVERRIDES[key]);c[2]=[12,65,130];OVERRIDES[key]=tuple(c)
    def state(ep,row,i):
        assert ep=='A15'and row['key']=='keys'
        # Frames130..147 are the actually captured stationary endpoint. Keep
        # their native clock rather than freezing a mid-motion image.
        if row['mode']=='native':return min(147,i),'native'
        f=i+row.get('cutOffset',0);end=round(row['originalCutFrames']*.7)if row.get('phaseModeAtTail')else row['originalCutFrames']
        if row.get('phaseModeAtTail')and f>=end:return 130,'stages'
        return round(12+118*np.clip(f/max(1,end-1),0,1)),'compare'
    rr.state=state
    code=hashlib.sha256(Path(__file__).read_bytes()+b''.join((H/n).read_bytes()for n in ('compose.py','sources.py','config.py','render_rows.py'))).hexdigest()
    dest=R/spec['output'];passes=[]
    for i in range(3):
        row={'id':f'A15-keys-complete-pass-{i+1}','key':'keys','mode':'native','frames':148,'originalCutFrames':148,'passIndex':i+1,'output':str(dest.with_name(f'pass-{i+1}.mp4').relative_to(R)).replace('\\','/')}
        signature=hashlib.sha256(json.dumps({'code':code,'row':row,'source':spec['source']},sort_keys=True).encode()).hexdigest()
        print(rr.render('A15',row,signature),row['id'],flush=True);passes.append(R/row['output'])
    concat=dest.with_suffix('.ffconcat');concat.write_text('ffconcat version 1.0\n'+''.join("file '"+f.name+"'\n"for f in passes),'utf8')
    subprocess.run(['ffmpeg','-v','error','-nostdin','-y','-f','concat','-safe','0','-i',str(concat),'-c','copy','-movflags','+faststart',str(dest)],check=True)
    for row in spec['bodyOverrides']:
        signature=hashlib.sha256(json.dumps({'code':code,'row':row,'source':spec['source']},sort_keys=True).encode()).hexdigest()
        print(rr.render('A15',row,signature),row['id'],flush=True)
        row['sha256']=sha(R/row['output'])
    stream=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(dest)]))['streams']
    assert len(stream)==1 and int(stream[0]['nb_frames'])==444 and stream[0]['avg_frame_rate']=='60/1'
    subprocess.run(['ffmpeg','-v','error','-threads','2','-i',str(dest),'-f','null','-'],check=True)
    spec.update(status='rendered-current-silent-override',sha256=sha(dest),codeSHA256=code,fullDecode='passed444frames',bodyOverrideCount=len(spec['bodyOverrides']))
    (H/'pacing-extension.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n','utf8')
    print('A15 complete native repetition extension ready',flush=True)
if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--render',action='store_true');a=ap.parse_args()
    execute()if a.render else prepare()
