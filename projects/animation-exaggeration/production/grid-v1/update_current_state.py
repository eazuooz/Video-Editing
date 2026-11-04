"""Record this episode's actual current production state without platform mutations."""
from pathlib import Path
from datetime import datetime,timezone
import json
import audio_pipeline as ap

H=Path(__file__).resolve().parent
P=H.parents[1]
R=H.parents[3]
L=H.parent/'local/grid-v1'

def save_state(path,value):
    allowed={P/'project.json',H/'checkpoint.json',R/'production/batches/animation-18-20261031/checkpoint.json'}
    assert path in allowed
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    now=datetime.now(timezone.utc).isoformat()
    if (L/'delivery/output/animation-exaggeration/delivery-manifest.json').exists():
        raise RuntimeError('A final delivery exists; use its delivery ledger instead of regressing production state.')
    complete=[p for p in (L/'render').glob('*/*/render-success.json') if ap.read(p).get('status')=='complete']
    phase='native-full-capture-in-progress' if len(complete)<23 else 'final-compositing-and-review'
    project=ap.read(P/'project.json')
    project['status']=phase
    project['voice'].update({'status':'generated-and-preserved','sourceAudio':ap.artifact(L/'voice/elevenlabs-sample-b-take-01.mp3'),
        'sourceReview':ap.artifact(H/'source-asr-review-v2.json'),'newGenerationNeeded':False})
    project['delivery']['status']='native-scenes-pending-final-pair'
    project['updatedAt']=now
    save_state(P/'project.json',project)
    save_state(H/'checkpoint.json',{
        'episode':'A02','status':phase,'updatedAt':now,
        'completed':['Preserved own-voice Sample B source; full CPU-ASR recovery reviewed',
            'Five source PCM chunks rejoin exactly; continuous284.366667s mix and100pairedKO/ENclauses',
            '31cut measured EDL with23native presentations;8independent-gameplay/still cuts composited',
            'Source-pixel-verified four stills and current captions reviewed in full text',
            'Source-to-stem/AAC continuity and BGM coverage passed'],
        'currentWork':f'{len(complete)}/23native captures complete. Final measured8-profile preflight and14-paragraph AAC text review passed.',
        'nextAction':'Complete native capture queue, then assemble paired masters and review encoded pixels.',
        'completedNativeCaptures':len(complete),
        'ttsGenerated':True,'newTtsRequired':False,'finalMasterRendered':False,
        'platformMutation':False,'userReviewed':False,
        'bindings':{'measuredPlan':ap.artifact(H/'measured-edit-plan.proposal.json'),
            'captionText':ap.artifact(H/'caption-text-review.json'),'audioBuild':ap.artifact(L/'edit/audio-build.json')}
    })
    bpath=R/'production/batches/animation-18-20261031/checkpoint.json'
    batch=ap.read(bpath)
    batch.update({'updatedAt':now,'currentEpisode':'A02','currentWork':[
        'A01 complete four-output local delivery; user review pending',
        f'A02 {len(complete)}/23native captures complete; captioned master not yet rendered',
        'A03 isolated six-scene readiness and independent-footage evidence refinement'],
        'nextAction':'Finish A02 full native capture queue, final pair and local review.'})
    batch['costlyJobSummary'].update({'currentJob':phase,
        'sourceAsr':'A01 and A02 full source and finalAAC ASR review complete','nativeFullCaptures':27+len(complete)})
    save_state(bpath,batch)
    print('Scoped A02 and finite-batch checkpoint refreshed; shared selection and platforms unchanged.')

if __name__=='__main__':main()
