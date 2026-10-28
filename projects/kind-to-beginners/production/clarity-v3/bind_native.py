"""Bind only completed, frozen D29 native captures to the isolated edit.

This reads receipts and container metadata; it does not render or encode.
"""
from pathlib import Path
from fractions import Fraction
import datetime, hashlib, json, subprocess
from storage_paths import ROOT, HERE, LOCAL, repo_path, relative

EXPECTED = 'e4e88d3e52264064532f142ca7494ba835ccc890048ecbc54d8b330a7b2791d7'

def read(p): return json.loads(p.read_text('utf-8-sig'))
def save(p, d): p.write_text(json.dumps(d, ensure_ascii=False, indent=2)+'\n', 'utf-8')
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''): h.update(b)
    return h.hexdigest()

def main():
    plan_path=HERE/'edit-plan.json'; plan=read(plan_path)
    jobs_path=HERE/'capture-jobs.json'; jobs=read(jobs_path)
    assert jobs['timingLocked'] is True
    indexed={j['cutId']:j for j in jobs['jobs']}
    records=[]; checked={}
    for cut in plan['cuts']:
        if cut['kind']!='explanation': continue
        j=indexed[cut['id']]
        assert j['frames']==cut['frames'] and j['stageClass']=='D29ClarityStage'
        folder=LOCAL/'render/measured-v1'/cut['id']
        movie=folder/'unity.mp4'; request_path=folder/'request.json'; proof_path=folder/'render-success.json'
        request=read(request_path); proof=read(proof_path)
        assert request['command']=='render' and request['expectedFingerprint']==EXPECTED
        assert request['slug']==plan['slug'] and request['cutId']==cut['id']
        assert request['frames']==cut['frames'] and request['jobsSha256']==sha(jobs_path)
        assert proof['status']=='complete' and not proof.get('error')
        assert proof['compiledSourceFingerprint']==EXPECTED
        assert proof['completed']==proof['frames']==cut['frames']
        assert proof['cutId']==cut['id'] and proof['slug']==plan['slug']
        assert Path(proof['output']).resolve()==folder.resolve()==Path(request['output']).resolve()
        for source in request['sourceFiles']:
            p=repo_path(source['path'])
            if str(p) not in checked: checked[str(p)]=sha(p)
            assert checked[str(p)]==source['sha256'],source['path']
        scene=ROOT/'unity/VideoEditing'/proof['scene']
        assert scene.is_file() and scene.with_suffix('.unity.meta').is_file()
        streams=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(movie)]))['streams']
        video=[s for s in streams if s['codec_type']=='video']
        assert len(streams)==len(video)==1
        v=video[0]
        assert (v['width'],v['height'])==(1920,1080) and Fraction(v['avg_frame_rate'])==60
        assert int(v['nb_frames'])==cut['frames']
        assert abs(float(v['duration'])-cut['frames']/60)<1/60
        record={'cutId':cut['id'],'frames':cut['frames'],'compiledFingerprint':EXPECTED,
                'movie':relative(movie),'movieSha256':sha(movie),
                'request':relative(request_path),'requestSha256':sha(request_path),
                'successReceipt':relative(proof_path),'successSha256':sha(proof_path),
                'scene':scene.relative_to(ROOT).as_posix(),'sceneSha256':sha(scene),
                'stageAssemblyMvid':proof['stageAssemblyMvid'],'sourceFiles':request['sourceFiles'],
                'fullDecode':'pending final compositor validation','nativeMovingPixels':'pending full-capture sample review'}
        records.append(record)
        cut.update(renderedSource=record['movie'],renderedStartFrame=0,
                   renderedSourceSha256=record['movieSha256'],nativeCapture=record)
    assert len(records)==len(indexed)==22
    before=HERE/'edit-plan.before-native-binding.json'
    if not before.exists(): before.write_bytes(plan_path.read_bytes())
    save(plan_path,plan)
    save(HERE/'native-binding.json',{'status':'all-native-receipts-and-container-metadata-bound',
        'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'compiledFingerprint':EXPECTED,
        'editPlanSha256':sha(plan_path),'jobsSha256':sha(jobs_path),'captures':records,
        'savedScenePaths':[r['scene'] for r in records],'nativePixels':'preflight reviewed; full-capture sampled transitions pending'})
    production_path=HERE/'production-plan.json'; production=read(production_path)
    proposal=HERE/'production-plan.before-native-binding.json'
    if not proposal.exists(): proposal.write_bytes(production_path.read_bytes())
    timing={c['id']:c for c in read(HERE/'timing-lock.json')['cuts']}
    corrected_visuals={
        '07-01':'A Short Hike actual path traversal while explaining the problem of dictating the next action; no player intention inferred.',
        '07-03-a':'Actual character walks along the island path as walking is introduced.',
        '07-03-b':'Actual character ascends the cliff face during the spoken climbing example.',
        '07-03-c':'Actual character takes off and glides while gliding is introduced.',
        '08-01-a':'Actual approach to an island edge; changing surroundings carry the final first-interest point.',
        '08-01-b':'Actual stairs and cabin arrival complete the walk; no repeated source range or idle padding.'}
    production['cuts']=[]
    for cut in plan['cuts']:
        taught={k:v for k,v in timing[cut['id']].items() if k not in ['provisionalDurationSeconds','timingState','annotations']}
        taught.update(cut)
        if cut['id'] in corrected_visuals: taught['visual']=corrected_visuals[cut['id']]
        taught['timingState']='locked-to-measured-continuous-narration'
        taught['annotations']=cut.get('marks',[])
        production['cuts'].append(taught)
    production['status']='measured-native-captures-bound-final-assembly-pending'
    production['unity']['savedScenePaths']=[r['scene'] for r in records]
    production['unity']['sceneSaveStatus']='22 files and meta confirmed; exact capture receipt and saved scene hashes in native-binding.json'
    production['unity']['compiledFingerprint']=EXPECTED
    production['bodyRatio'].update(measuredBodyFrames=sum(c['frames'] for c in plan['cuts']),
        measuredActualFrames=sum(c['frames'] for c in plan['cuts'] if c['kind']=='independent-gameplay'),
        measuredActualShare=sum(c['frames'] for c in plan['cuts'] if c['kind']=='independent-gameplay')/sum(c['frames'] for c in plan['cuts']))
    production['quality']['technicalReview']='native preflight and source/audio preparation passed; final encoded movie pending'
    production['finalEditPlan']={'path':relative(plan_path),'sha256':sha(plan_path)}
    save(production_path,production)
    print('Bound 22 exact frozen native captures; no encoding performed.')

if __name__=='__main__': main()
