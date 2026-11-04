"""Make bounded M22/M23 runtime preview instructions; do not launch an editor."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[3]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
c=read(R/'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104'];assert c['productionAllowedNow']
for slug,episode,factory,indices in [('game-math-skinning-normal-map','M22','SkinNormalSceneBuilder',{1,3,5,6,9,13,15,18,22,27,32,35}),('game-math-pipeline-shaders','M23','PipelineSceneBuilder',None)]:
    assert slug in c['projectSlugs'];S=R/'projects'/slug/'production/unity-staging';W=S/'local-preflight-v1';assert not W.exists(),'Preserve prepared queue';W.mkdir()
    plan=read(S/'module-plan.json');sandbox=read(S/'sandbox-preparation.json');rows=plan.get('shots',plan.get('beats'))
    if indices is None:indices=set(plan['rootMustRun']['preflightBeats'])
    jobs=[]
    for row in rows:
        shot=row.get('shot');
        if not shot or row['renderer']!='Unity' or shot['beatIndex'] not in indices:continue
        sid=row['sceneId'];shot=dict(shot,durationSeconds=8,stepSeconds=[])
        cue=W/(sid+'.shot.json');save(cue,shot)
        job={'id':episode.lower()+'-preflight-v1-'+sid,'projectSlug':slug,'command':'preflight','output':str(W/sid),'ffmpeg':'C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin/ffmpeg.exe','expectedFingerprint':sandbox['fingerprint'],'shotFile':str(cue),'factoryType':factory,'frames':480,'sampleFrames':[0,120,240,420],'speechTimingVerified':False}
        jp=W/(sid+'.job.json');save(jp,job);jobs.append(str(jp))
    save(W/'queue.json',{'project':slug,'episode':episode,'sandbox':sandbox['sandbox'],'fingerprint':sandbox['fingerprint'],'unity':'C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Unity.exe','jobs':jobs,'actualSpeech':False,'scope':'Selected module visual/runtime samples, never final timing or media approval','rigValidationRequired':episode=='M22'})
    print(episode,len(jobs),'preview instructions prepared; no Unity started')
