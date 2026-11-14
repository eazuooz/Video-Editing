"""Serialize the exact selected input fixes after the current unchanged-body jobs."""
from pathlib import Path
import shutil
import time

from prepare import HERE,WORK,OUTPUT,read,save
from run_selected_queue import run
from finish_episode import sha


def main():
    deadline=time.monotonic()+1800
    while time.monotonic()<deadline:
        if (OUTPUT/'A16/delivery.json').is_file():break
        time.sleep(3)
    else:
        raise TimeoutError('Retained native assembly has not finished; no other job was stopped.')
    rejected=WORK/'rejected-auditions/hand-floor-intersection'
    rejected.mkdir(parents=True,exist_ok=True)
    build=read(WORK/'anim_GrabValve_R-build.json')
    if len(build.get('yaws',[]))>1:
        for suffix in ('.mp4','-capture.json','-build.json'):
            source=WORK/('anim_GrabValve_R'+suffix)
            dest=rejected/source.name
            if source.exists() and not dest.exists():shutil.copyfile(source,dest)
        save(rejected/'reason.json',{'adopted':False,'reason':'The audition lowered the character through the stage floor. Preserve original actor height and place a single camera at hand height; never alter the animation to hide a staging error.'})
    audition=WORK/'native-hand-audition.json'
    audited=read(audition) if audition.exists() else {}
    reusable=audited.get('visualAuditionPassed') and all(
        sha(WORK/(key+'.mp4'))==audited['inputs'][key]['movieSha256'] and
        read(WORK/(key+'-build.json'))['builderSha256']==audited['inputs'][key]['definitionSha256']
        for key in ('anim_GrabValve_R','anim_OpeningValve_R'))
    if not reusable:
        run('prepare_native.py','--only','anim_GrabValve_R','anim_OpeningValve_R')
        for key in ('anim_GrabValve_R','anim_OpeningValve_R'):
            run('capture_native.py',key)
    from prepare import VOICE_LOCAL
    verified=WORK/'narration-patches-checked.json'
    expected=read(HERE/'narration-patches.json')['records']
    prior={r['id']:r for r in read(verified)['records']} if verified.exists() else {}
    current=all(r['id'] in prior and prior[r['id']]['ko']==r['ko'] and
                prior[r['id']].get('rawAudioSha256')==sha(VOICE_LOCAL/'patch-voice/chunks'/(r['id']+'-scene.wav'))
                for r in expected)
    if not current:run('render_recaps.py','--manifest','patches-manifest.json','--only-missing')
    run('check_narration_patches.py')
    run('finish_episode.py','A09')
    run('assemble_delivery.py','A09')
    run('sample_final_outputs.py','A09')
    save(WORK/'selected-input-status.json',{'stage':'native-hands-and-sentence-readback-ready',
        'visualAuditionRequired':True,'humanReviewed':False})
    print('Native hand inputs and narration corrections ready for internal moving-picture inspection.',flush=True)


if __name__=='__main__':main()
