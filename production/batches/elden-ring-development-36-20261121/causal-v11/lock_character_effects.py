"""Lock the two inspected character/effect lessons without changing prior media."""
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from make_approved_voice_v2 import read,save,sha

EN={
 '03':[
 'A facial scar is a colored mark, so why can lighting make it look indented? Compare it with color alone on the same face.',
 'Lighting needs to know which direction a surface faces. An arrow perpendicular to the surface is its normal. Changing only the color leaves that arrow unchanged, so the shading does not follow the scar relief.',
 'Elden Ring uses normal information as well as the scar mask and color. Changing the direction used in lighting produces bright and dark regions under the same light.',
 'Switch on the color, mask and normal layers separately in our demonstration. Move the light and watch the shading change on the side with normals. The face silhouette remains unchanged: the lighting direction makes the relief readable.'
 ],
 '10':[
 'Why does a spell look wrong if it appears before the character raises a hand? A striking effect alone does not complete the action of casting it.',
 'Let the same character raise a staff, but trigger the projectile early. The preparing body and the already launched effect look disconnected. Now align the launch with the staff rising.',
 'During Elden Ring production, events such as effects and sound were connected to animation timing. Preparation, release and recovery need to work together so the action is readable.',
 'Move the release marker on our demonstration timeline and watch the same motion change. Follow the moment when the hand, staff and projectile form one action. An effect matters both for how it looks and when it starts.'
 ]}

def main():
    manifest=Path('C:/Users/1/Videos/YamyamProduction/elden-ring-development-36/pc-review-v10/manifest.json')
    baseline=read(manifest);scripts=read(HERE/'narration-ko.json')
    reference=Path('D:/Github/VideoEditing/projects/shorts-mario-one-action/production/local/tts-execution.json')
    for n in ['03','10']:
        record=baseline['episodes'][n]['record'];source=Path(record['formatSources'][0]['source'])
        assert sha(source)==record['cuts'][0]['sha256']
        evidence=[{k:record['cuts'][i][k] for k in ['url','recorder','rights','sha256','size','start','end','observed']} for i in [0,2]]
        description=('Inspected expanded samples 332.3/337/342/348 and 345.3/350/355/361: scar/pattern selection and sliders on the same face. The 361s sample changes to eyepatch settings: exclude 358s onward. Actual menu footage is context, not a controlled normal-map toggle.' if n=='03' else
                     'Inspected expanded samples 16.3/21/26/32 and 26.3/31/36/42: staff rises, blue cast appears, enemy approaches and character recovers. Internal event keys are not visible. Use distinct contiguous intervals rather than replaying the same cast.')
        item=dict(id=n,version='causal-v11',scriptLockedForVoice=True,narrationKo=scripts[n],narrationEn=EN[n],
            claimEvidence=[dict(url=f'https://cgworld.jp/article/202206-cgw286-eldenring0{1 if n=="03" else 3}.html',reviewed='2026-11-28',
                scope='Developer-provided making-of: scar mask/normal layers; independent lighting comparison.' if n=='03' else 'Developer interview: animation timing to effects in Time Act Editor, motion followed by effect/sound production. Timing mismatch is our demonstration.')],
            footageEvidence=dict(retainedRights=evidence,sourceManifest=str(manifest),sampleReview=description,continuousPlaybackReviewed=False,
                audioUse='video only',timedFinalSelection='pending measured narration, no replay or extension into excluded menus'),
            demonstration=dict(nativeProject='unity/VideoEditing',sceneMethod='FaceLayersV8' if n=='03' else 'CastV8',
                pilotFingerprint='47f665555481861946ba29bb8456d94e3d1f64fa9787836003df77807e22776f',
                classification='independent principle model; not original game implementation',finalVoiceTimedCapture=False),
            inputs=[dict(path=str(p),sha256=sha(p)) for p in [source,manifest,reference]],humanReview='pending',finalRenderComplete=False)
        path=HERE/'locked'/f'{n}.json'
        if path.exists():assert read(path)==item
        else:save(path,item)
        print(n,sha(path))

if __name__=='__main__':main()
