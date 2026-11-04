"""Build a finite M21 capture queue from verified actual-word timing only."""
from pathlib import Path
import argparse,json,math,hashlib
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];S=P/'production/unity-staging'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--revision',default='render-v1');a=ap.parse_args()
    assert a.revision.startswith('render-') and all(c.isalnum() or c=='-' for c in a.revision)
    control=read(ROOT/'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104']
    assert control['productionAllowedNow'] and P.name in control['projectSlugs']
    timeline=read(P/'production/local/edit-v1/word-aligned-timeline.json')
    assert not timeline['flags'],'Resolve real transcript/anchor differences before full production'
    assert timeline['bindingsSha256']==sha(P/'planning/scene-bindings.json')
    assert timeline['narrationSha256']==sha(P/'production/local/audio-v1/narration.wav')
    sandbox=S/'LocalUnity-v6';marker=read(sandbox/'M21_SANDBOX.json')
    out=P/'production/local'/a.revision
    assert not out.exists(),'Use a new revision; never replace capture evidence'
    out.mkdir(parents=True)
    jobs=[];cuts=[]
    for row in timeline['scenes']:
        sid=row['id'];cue=dict(row['cue']);cue['id']='m21-body-'+sid
        frames=row['endFrame']-row['startFrame'];assert frames>0
        game=row.get('actualGamePart');gameframes=0
        if game:
            gameframes=min(frames,math.floor(game['duration']*60+.0001))
            assert gameframes>=60,'A game example cannot become a token flash'
            cuts.append({'scene':sid,'kind':'actual-gameplay','sourceId':game['sourceId'],'sourceIn':game['sourceIn'],'sourceOut':game['sourceIn']+gameframes/60,'frames':gameframes,'globalStartFrame':row['startFrame'],'nativeSpeed':True,'freeze':False,'loop':False,'originalSelectedOut':game['sourceOut'],'review':'Validate cut still contains observed action/result and tracked target'})
        if sid=='000' and gameframes==frames:continue
        job={'id':cue['id'],'command':'render','expectedFingerprint':marker['fingerprint'],'cueFile':str(out/'cues'/(sid+'.json')),'output':str(out/'unity'/sid),'frames':frames,'sampleFrames':[0,frames//2,frames-1],'ffmpeg':'C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin/ffmpeg.exe','sceneId':sid}
        if sid=='078':
            job['comparisonDependencies']=[{'scene':scene,'label':label,'sourceKind':kind} for scene,label,kind in [('001','표면 한 점의 반사','우리 조명 구현'),('037','면 · 정점 · 픽셀','우리 셰이더 구현'),('074','고정된 배치의 베이크','Unity 실제 베이크'),('076','움직이는 물체의 조명','Unity 라이트 프로브')]]
        save(Path(job['cueFile']),cue);jobpath=out/'jobs'/(sid+'.json');save(jobpath,job);jobs.append(str(jobpath))
        if frames>gameframes:cuts.append({'scene':sid,'kind':'explanation','file':str(Path(job['output'])/'unity.mp4'),'sourceIn':gameframes/60,'frames':frames-gameframes,'globalStartFrame':row['startFrame']+gameframes})
    ordered=sorted(cuts,key=lambda x:x['globalStartFrame']);cursor=0
    for cut in ordered:assert cut['globalStartFrame']==cursor;cursor+=cut['frames']
    assert cursor==timeline['scenes'][-1]['endFrame']
    save(out/'queue.json',{'project':P.name,'sandbox':str(sandbox),'fingerprint':marker['fingerprint'],'unity':'C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Unity.exe','jobs':jobs,'wordAlignment':str(P/'production/local/edit-v1/word-aligned-timeline.json'),'wordAlignmentSha256':sha(P/'production/local/edit-v1/word-aligned-timeline.json'),'bodyFrames':cursor,'cuts':ordered,'actualGameplayFrames':sum(x['frames'] for x in ordered if x['kind']=='actual-gameplay'),'automation':False,'nextProject':False,'finalReviewReady':False})
    print(f'Prepared {len(jobs)} Unity captures and {len(cuts)} continuous cuts; no rendering started')
if __name__=='__main__':main()
