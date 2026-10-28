"""Plan D25/D26 visual-only Unity revisions without starting media jobs."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[4]
SLUGS = ['limited-color-world', 'computer-controlled-players']


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


# One coherent visual test bed returns between real-game cuts. These are our
# explanatory mechanisms, never measurements of the commercial game engine.
DETAILS = {
 'limited-color-world': {
  'cut002': ('color-same-shape', 'Keep two identical block meshes on a small game board; reduce their colour separation and reveal a short question mark between them. End in the ambiguous state inherited by the next overview.', 'Different types initially distinct → colour difference reduced → type can no longer be identified by colour.', ['block','crate']),
  'cut003': ('color-overview', 'Show the actual inspected Puyo, flower and Mario-gray frames as three large sequential evidence planes, with the same two Unity blocks in the first inset and an imported player looking toward the currently selected target. No prose list.', 'Puzzle distinction → flower/route target → same-screen monochrome inspection.', ['actor','block']),
  'cut004': ('color-converge', 'Close view of two equal-shaped blocks on a playable-looking shelf. During the exact phrase about reducing colour differences, animate only material hue toward equal muted ochre. Their silhouettes and positions stay identical. No extra third type.', 'Two colours → same shape and near-equal colour → lost type information.', ['block','crate']),
  'cut006': ('theme-combinations', 'Split the same two blocks between a bright forest-themed board and a dark stone-themed board. Change the background behind each once while leaving shape and identity fixed; draw useful boundary highlights only after the visual failure.', 'Same block identity → two background/theme combinations → readable or merged edges.', ['block','foliage','crate']),
  'cut008': ('color-two-comparisons', 'At this late phrase show two small views of the same Unity board: block-to-block and block-to-background. Attach circles to the actual pair and boundary; keep short labels, not a three-box flow.', 'Colour distinction already reduced → compare pair and boundary → the different inspection targets are visible.', ['block','crate']),
  'cut009': ('color-check-types', 'Retain canonical Protanopia-type and Deuteranopia-type names but put each beside a populated Unity test-board view. The two check routes light in narration order. Do not invent Photoshop controls or label arbitrary desaturation as a physiologically accurate simulator.', 'Same test board → inspect both named colour-vision conditions → two required checks, not only one.', ['block','crate']),
  'cut010': ('retain-factual-screen', 'Retain actual independently inspected Puyo colour-adjustment menu and corrected type-row callout. This is the exact game option being discussed; do not replace it with a fictional Unity menu.', 'Game setting shown → type row selected → player sees the actual available filter option.', []),
  'cut011': ('lightness-separate', 'Same two blocks now appear with similar hue. Raise one block lightness while the other remains dark; a visible gap in grayscale lightness is the result. Avoid camera/light changes that could falsely create the difference.', 'Similar hue → change only one material lightness → useful boundary contrast.', ['block','crate']),
  'cut013': ('lightness-background', 'Place the now-dark block against a dark portion of the imported stone/wood environment. Let its outline disappear; move a restrained contrast bracket to the boundary. Raise only target lightness slightly so its edge returns while identity stays fixed.', 'Dark target on dark background → edge becomes hard to locate → compare target-background separation.', ['block','crate']),
  'cut015': ('redundant-shape-cues', 'Three front-facing blocks have circle, triangle and stripe symbols actually attached to the face, revealed at locally measured first-list cues within this 244-frame cut. Brief desaturation leaves these three marks readable. Show the same symbol on repeated instances of each kind.', 'Colour-only blocks → attach circle/triangle/stripe → shape remains when colour distinction drops.', ['block','crate']),
  'cut022': ('retain-factual-screen', 'Preserve the same inspected Mario screenshot and matching grayscale comparison with identical framing. Improve focus if needed, but the narration explicitly says the same actual game screen, not an unrelated new Unity world.', 'Same Mario picture → colour removed → luminance layout remains.', []),
  'cut027': ('visual-hierarchy', 'In a compact Unity forest test bed, hold an imported articulated player and a treasure/goal in foreground; fade background-only contrast while keeping the path and target clear. Draw a single progressive player→path→goal guide, labelled explanatory model.', 'Distracting background → reduce background contrast → foreground route and actionable target lead attention.', ['actor','foliage','chest']),
  'cut029': ('different-checks', 'Use the same blocks left and same forest/goal right. Left highlights between-type distinction; right presents monochrome foreground/background hierarchy. Labels remain only colour information / luminance hierarchy.', 'Two visual questions → two matching inspected views → complementary checks.', ['block','actor','foliage','chest']),
  'cut030': ('fresh-view', 'Show the prior forest/path illustration on an easel-like screen and smoothly mirror the screen content horizontally once, exposing an off-centre distracting prop. Keep left/right frame order and camera stable; end with the changed view. Do not imply this replaces actual player testing.', 'Familiar illustration → horizontal mirror → imbalance is noticed afresh.', ['foliage','chest']),
 },
 'computer-controlled-players': {
  'cut001': ('retain-factual-screen', 'Preserve the 70-frame actual Smash hit-result freeze that completes the opening before/action/result. The current same-game hit frame is stronger evidence than a new illustration here.', 'Actual close attack → contact → inspected hit result.', []),
  'cut007': ('ai-context', 'Two imported rigged actors stand on a clear arena with a gap/hazard. First actor swings at empty air, then walks toward the edge; next the opponent/edge are marked and actor stops at safe range. Use real limb animation, not only token translation.', 'Unconditioned motion → empty swing / hazardous walk → decisions need observed context.', ['actor','opponent','sword']),
  'cut009': ('ai-instant-reaction', 'Use the same two actors with an attack cue and an instantly raised guard in the opposing actor. One concise 0-frame response marker makes the unfair-feeling timing visible; this is our illustration, not a claim of actual CP frame counts.', 'Attack cue → immediate model response → no readable opening.', ['actor','opponent','sword']),
  'cut014': ('retain-factual-screen', 'Retain Dicey Dungeons actual equipment screenshot and die so the narrator game-specific reference is grounded. Replace the long summary prose with a concise attached die→equipment arrow if enhancement is needed.', 'Actual die result → available equipment → expected opponent action.', []),
  'cut017': ('ai-dice-trust', 'Two imported actors face a visible die on a tabletop. The die roll and action-selection branches feed one transparent computer/process housing, then feed the opponent. After a high die, player turns toward the process with a question mark; label both processes without fabricating game statistics or proving cheating.', 'Roll and action selection share a computer → favourable result → player suspicion can arise despite fair rules.', ['actor','opponent','dice','table']),
  'cut021': ('ai-observations', 'Same arena actors. Attach position marker and a short status bar to opponent, then reveal lines to a compact decision node and finally to own actor footstep arrow. Data values are our model values only.', 'Visible model position/status → decision → next movement.', ['actor','opponent']),
  'cut023': ('ai-technique-conditions', 'Show own attack arc, its launch marker and endpoint ghost; show opponent arc in a different labelled role colour. Advance the arcs once so distance, timing and travel are physical relationships rather than boxes.', 'Own move range/timing/travel → compare opponent move → choose a response.', ['actor','opponent','sword']),
  'cut024': ('ai-range', 'Front three-quarter arena, five evenly spaced one-unit ground tiles, own actor at0 and opponent at3. Mark range2. Swing at the spoken miss, end short of opponent; walk one unit at the spoken approach; swing again so the reach touches the opponent. Keep units and labels aligned with actual model coordinates.', 'Range2, separation3 → swing misses → advance1 → same attack reaches.', ['actor','opponent','sword']),
  'cut026': ('ai-current-state', 'Side-by-side same actors and range: left opponent approaches, right opponent has already started attack. One action path per side reveals how current state changes the response; no new jargon or fabricated commercial-game measurement.', 'Same distance → different opponent state → different viable decision.', ['actor','opponent','sword']),
  'cut029': ('ai-conditional-intensity', 'Same model opponent shows lead/strength condition with a single small gauge; aggression path and caution path both light as the conditions overlap. Move directly into priority conflict next cut without resetting stage.', 'Changed match condition → intensity adjusted → overlapping decisions become possible.', ['actor','opponent']),
  'cut030': ('ai-priority', 'Imported actor physically takes a half-step forward then back between attack and danger arrows, demonstrating oscillation. At priority phrase give danger the first numbered position and disable forward arrow; actor retreats a clear single unit and then holds, showing a defined state-change threshold.', 'Approach and retreat simultaneously valid → hesitation → explicit priority chooses one stable action.', ['actor','opponent','sword']),
  'cut032': ('ai-reaction-delay', 'A labelled model frame timeline sits above two actors. A small cue illuminates at model frame0; response trigger is exactly frame12 at60fps and the actor raises guard. Display the equation12/60=0.2s with numbers anchored to the timeline. Additional timeline reveal is editorial presentation, not slow-motion claimed as real game footage.', 'Notice cue → twelve model frames elapse → response begins0.2s later.', ['actor','opponent']),
  'cut033': ('ai-reversed-input', 'Same actor and safety-edge arena. A right input arrow briefly causes left movement when reverse-state icon appears; actor pauses in a thinking pose then remaps to intended right motion and stops safely before edge. There is one short confusion then recovery, not an endless fall.', 'Control reversal → brief wrong movement → adapts and regains safe action.', ['actor','opponent']),
 },
}


def main():
    for slug in SLUGS:
        project = ROOT/'projects'/slug
        old_plan = project/'production/batch-v1/edit-plan.json'
        plan = json.loads(old_plan.read_text('utf-8-sig'))
        manifest = json.loads((project/'project.json').read_text('utf-8-sig'))
        narration = json.loads((ROOT/manifest['paths']['script']).read_text('utf-8-sig'))
        text_by_id = {f"{s['id']}-p{i+1:02}":line for s in narration['scenes'] for i,line in enumerate(s['lines'])}
        records=[]
        for cut in plan['cuts']:
            if cut['kind']!='explanation': continue
            variant, action, mechanism, assets=DETAILS[slug][cut['id']]
            records.append({
                'id':cut['id'], 'scene':cut['scene'], 'startFrame':cut['startFrame'],
                'endFrame':cut['endFrame'],'frames':cut['frames'],
                'startSeconds':cut['startFrame']/60, 'endSeconds':cut['endFrame']/60,
                'variant':variant,'operation':'preserve-evidence-screen' if variant=='retain-factual-screen' else 'replace-explanation-visual',
                'narrationParagraphIds':cut.get('paragraphIds',[]),
                'narration':[text_by_id[p] for p in cut.get('paragraphIds',[])],
                'speechCueSecondsWithinCut':cut.get('visualCues',[]),
                'negativeCueMeaning':'Already active at cut start; do not replay spoken event or add pause.',
                'visualTreatment':action,'beforeActionResult':mechanism,
                'assetsByRole':assets,'renderer':'Unity' if assets else 'preserve native evidence / existing compositor',
                'kind':'explanation','actualGameplayReplacement':False,
                'illustrationNotMeasuredGameOutput':True,
                'scenePath':f'unity/VideoEditing/Assets/VideoScenes/{slug}/unity-visual-v2/{cut["scene"]}.unity' if assets else None,
                'sceneSaveStatus':'planned-not-yet-saved',
                'priorRenderedSource':cut['renderedSource'],'priorRenderedStartFrame':cut['renderedStartFrame'],
                'sourceScreenshots':cut.get('images',[]),
                'qa':['Narrated object/action/result visible at cue','No model/label overlap or hidden limbs','Unchanged1920x1080@60fps and cut frame count','Fixed caption protected rectangle clear','Actual375px readability','Compare first/action/result/end frames and inspect animation transitions'],
            })
        frozen=[]
        for key in ['script','scriptEn','scriptSpoken','videoBurnedCaptions','videoClean','captionsKo','captionsEn']:
            p=ROOT/manifest['paths'][key]
            frozen.append({'key':key,'path':manifest['paths'][key],'sha256':sha(p),'bytes':p.stat().st_size})
        result={
            'schemaVersion':1,'slug':slug,'revision':'unity-visual-v2','status':'visual-design-prepared',
            'authorization':{'userMessage':'전반적으로 잘만들었어 이야기 구성이나 순서는 설명 ppt 부분이 조금 글로만 되어있어서 공감이 잘안되 비디오에디팅 유니티 켜뒀어 에셋 안에 졸라많이 넣었으니까 잘 골라서 설명 ppt 부분 보완해주고 다시 만들어줘~ 영상전부','dateKst':'2026-10-28','scope':'D25–D30 six local visual revisions only; this file covers one selected video.'},
            'preservation':{'narrationStoryOrder':True,'sourcePcmAndEncodedAac':True,'koEnCaptionsBytes':True,'actualGameplayCutsAndMarks':True,'cutClocks':True,'totalFrames':plan['totalFrames'],'actualFrames':plan['actualFrames'],'explanationFrames':plan['explanationFrames'],'introFrames':120,'outroFrames':600,'newTts':False,'upload':False},
            'baseEditPlan':{'path':str(old_plan.relative_to(ROOT)).replace('\\','/'),'sha256':sha(old_plan)},
            'frozenInputs':frozen,
            'renderSpecification':{'width':1920,'height':1080,'fps':60,'background':'research-black-v1','text':'white body, warm yellow heading, minimal object-attached labels','captionProtectedRect':plan['captionProtectedRect'],'defaultTopRightKind':'설명 모형','perSceneSavedEditableRequired':True,'importedAssets':'Use shared model/rig/material references; no vendor modification or duplication. Parent finalizes exact license/GUID records and native capture.'},
            'cuts':records,
            'counts':{'explanationCuts':len(records),'proposedUnityCuts':sum(r['operation']=='replace-explanation-visual' for r in records),'retainedEvidenceScreens':sum(r['operation']=='preserve-evidence-screen' for r in records)},
            'reviewedEvidence':{'fullNarrationDirectRead':True,'baseEditPlanDirectRead':True,'priorEncodedSampleBoardsViewed':['D25 boundaries-640-02','D26 boundaries-640-04'],'actualUserWholeViewingClaimed':False},
            'openChecks':['Parent native asset selection/rights/rig check','Native saved scenes and captures','Final composite pixels1080/375','Final AAC packet equality and unchanged SRT/frame clocks']
        }
        folder=project/'production/unity-visual-v2';folder.mkdir(parents=True,exist_ok=True)
        (folder/'visual-plan.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
        print(slug,result['counts'])


if __name__=='__main__': main()
