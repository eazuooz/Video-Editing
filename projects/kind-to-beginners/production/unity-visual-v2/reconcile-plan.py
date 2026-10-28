"""Record realized Unity scenes against frozen narration and editorial clocks."""
from pathlib import Path
import argparse,json,re,hashlib

ROOT=Path(__file__).resolve().parents[4]
MEDIA=Path('C:/Users/1/.codex/video-production/design-25-30-unity-v2-20261028')
BATCH=ROOT/'production/batches/design-25-30-unity-v2-20261028'
STAGE=ROOT/'unity/VideoEditing/Assets/VideoScenes/design-25-30-unity-v2/D29D30Stage.cs'
def load(p):return json.loads(Path(p).read_text('utf-8-sig'))
def save(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n','utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

DESCRIPTIONS={
'race-start':'A detailed imported car follows the corner from start to exit; its travel shows the first success of continuing a race.',
'race-burden':'The car keeps travelling while the acceleration input changes from held to assisted; direction and item tasks remain visible.',
'race-steering':'At 3.05s the car actually moves toward the outside edge; from 4.25s steering corrects its path inward. At 6.65s the antenna appears and an inspected official game still shows the corresponding real feature.',
'race-acceleration':'The acceleration input is released at 2.4s while the car keeps moving. The button state and resulting uninterrupted motion are visible together.',
'race-turbo':'The car runs with its assist antenna while stage labels distinguish the first two turbo stages from the unavailable third stage; the preserved narration supplies the exact feature condition.',
'arcade':'Two imported articulated players stand at opposite sides of back-to-back original arcade cabinets. A diagonal camera shows that screens separate their sightlines.',
'intent':'Two articulated people face each other with different intended experiences, before play begins; the narrator distinguishes the same match from the same expectation.',
'read-person':'The experienced person approaches the silent newcomer and pauses rather than repeating the previous attack; their different expectations stay visible.',
'pressure':'An experienced fighter repeatedly punches at contact distance and the newcomer visibly reacts to hits before learning a defensive action.',
'agreement':'Both people approach each other and assume fighting stances after their matching willingness is shown.',
'block-goal':'The attacker approaches; a brief input cue precedes a defensive pose and shield arc that visibly stops the attack.',
'block-feedback':'The same defensive action succeeds, then the shield cue clears to leave room for the newcomer to decide the next action.',
'distance':'At close distance the same input produces a short punch. When the opponent is farther away a visible projectile travels to the opponent instead.',
'distance-flow':'The near/far comparison repeats with the same input marker, showing that distance judgment remains while command burden is reduced.',
'overload':'The newcomer faces unfamiliar controls and two paths; they first walk one clear route to a visible chest instead of reading a paragraph of instructions.',
'step':'One newcomer performs one walk-to-object action and sees its result before the next action is introduced.',
'try':'A guide remains behind while the newcomer walks to a chest and sees the result of their own movement.',
'handoff':'The guide stays behind; the newcomer follows a branch toward an imported crystal, preserving an independent decision after receiving limited help.',
'orders':'The guide stays immediately ahead and the newcomer follows the prescribed chest path; the alternative branch is not offered.',
'discovery':'The newcomer reaches a fork and independently takes the other path toward a visible crystal; the chosen destination changes.',
'release':'The guide remains behind as the newcomer chooses the branch and walks to a self-selected discovery.',
'commitment':'A newcomer starts toward a leisure activity but stops when a visible sequence of time blocks accumulates; a clock with actual moving hands and the hypothetical 300-hour label explain the up-front commitment.',
'calendar':'Three hundred day cells fill progressively beside an imported character, ending with the hypothetical calculation 300 hours divided by one hour per day equals 300 days.',
'opportunity':'The person chooses between a screen/chair activity and a friend/table activity; movement toward one leaves the other unused while the same clock runs.',
'value':'The person chooses an activity and reaches the friend rather than simply standing beside a prose list; the clock conveys their limited evening.',
'return':'Two fighters act at contact distance, then the short result cue shows the choice to play again after enjoying the previous round.',
'knockback':'With the same attacker and camera, the opponent is displaced a short distance with low accumulated damage, then a longer distance with higher damage. This is an explicitly labelled illustration, not measured game data.',
'result':'A detailed cup moves from an imported chest to a table; the visible result creates the next possible object choice.',
'cost':'Time blocks accumulate under a hypothetical +100-hour quantity while the character approaches the activity; the unchanged scene separates added quantity from experiential value.',
'alternatives':'The person walks toward the screen/chair activity while a visible friend/table alternative remains available, demonstrating competition for the same evening.',
'pleasures':'An imported person directs an illustrative water stream across a dirty table surface; the clean region grows, showing a different kind of concentration from the preceding combat example.',
'wash':'A moving water stream targets the edge of a dirty surface. The dirt shrinks only behind the stream, leaving a visibly clean table surface.',
'phone':'A handheld screen changes visible contents cues from text to photos to video while the person remains in place, showing immediately accessible leisure options.',
'barriers':'The person moves toward the prepared chair as time, environment and concentration indicators activate sequentially. No single universal measured barrier value is claimed.',
'place':'A cup is selected from a chest, travels to a chosen table location and remains there; the changed room is the visible consequence.',
'timeline-before':'The hypothetical one-minute timeline reveals control 40s at 6.8s, waiting 20s at 9.36s and 40/60=2/3 at 13.36s. The character completes the same cup-placement action and then waits.',
'timeline-after':'The waiting bar shrinks from 20s to 10s while the same 40s of control remains. Whole duration 50s is called out at 4.2s, unchanged control at 6.48s and 40/50=80% at 8.56s.',
'menu':'The character remains still while the selection moves from cup to ornament; the ornament then moves into the room, making the menu input and result visible.',
'waiting':'While the previous cup placement transitions, the next ornament can already be selected and is then placed beside the cup. The choice indicator responds during the waiting interval.',
'comparison':'The same hypothetical 300-hour quantity changes role from time demanded before starting to time accumulated after enjoyable choices; its color and short label change while the person proceeds toward the activity.'
}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--capture-version',required=True);ap.add_argument('--phase',choices=['preflight','render'],default='preflight');args=ap.parse_args()
 code=STAGE.read_text('utf-8');rights=load(BATCH/'asset-provenance.json');records={a['path']:a for a in rights['assets']}
 for slug,key in [('kind-to-beginners','D29'),('respect-player-time','D30')]:
  path=ROOT/'projects'/slug/'production/unity-visual-v2/visual-plan.json';plan=load(path)
  section=re.search(r' '+key+r' = new Dictionary<string,string> \{(.*?)\n        \};',code,re.S).group(1)
  modes=dict(re.findall(r'\{"([0-9-]+)","([a-z-]+)"\}',section))
  all_assets={};fingerprints=set()
  for cut in plan['explanationCuts']:
   cut_id=cut['cutId'];mode=modes[cut_id]
   candidates=sorted((MEDIA/slug/args.phase).glob('v*/'+cut_id+'/'+args.phase+'-success.json'),key=lambda p:int(p.parents[1].name[1:]))
   allowed=[p for p in candidates if int(p.parents[1].name[1:])<=int(args.capture_version[1:])]
   receipt=load(allowed[-1]) if allowed else None
   cut.setdefault('initialVisualProposal',{'sceneType':cut['sceneType'],'beforeActionResult':cut['beforeActionResult'],'candidateProductIds':cut.get('candidateProductIds',[])})
   cut['sceneType']=mode;cut['beforeActionResult']=DESCRIPTIONS[mode]
   cut['scenePath']='Assets/VideoScenes/'+slug+'/unity-visual-v2/'+cut_id+'.unity'
   cut['sceneSaved']= (ROOT/'unity/VideoEditing'/cut['scenePath']).exists()
   cut['stageClass']='D29D30Stage';cut['status']='native-preflight-reviewed-awaiting-full-render' if args.phase=='preflight' else 'rendered-awaiting-final-composite-review'
   if receipt:
    cut['nativeReceipt']=str(allowed[-1]);cut['nativeReceiptSha256']=sha(allowed[-1]);cut['unityVersion']=receipt['unity']
    cut['compiledSourceFingerprint']=receipt['compiledSourceFingerprint'];fingerprints.add(receipt['compiledSourceFingerprint'])
    unknown=[p for p in receipt['assets'] if p not in records and '/Generated/ReferenceImages/' not in p]
    assert not unknown,unknown
    cut['assetRecords']=[records[p] for p in receipt['assets'] if p in records];cut['sharedAssetPaths']=receipt['assets'];cut['sharedAnimationPaths']=receipt['animations']
    cut['sharedStillPaths']=[p for p in receipt['assets'] if '/Generated/ReferenceImages/' in p]
    cut['candidateProductIds']=sorted({a['productId'] for a in cut['assetRecords']})
    all_assets.update({a['path']:a for a in cut['assetRecords']})
   cut['capture']={'resolution':[1920,1080],'fps':60,'frames':cut['frames'],'frameClock':'unchanged baseline cut-local seconds','pipeline':'Universal Render Pipeline','nativeSpeed':True,'kind':'our illustrative implementation'}
   cut['visualCueBasis']='Frozen final Korean caption intervals in speech; parent lesson narration/order and actual gameplay cuts are unchanged.'
   cut['preserveActualStillEvidence']=slug=='kind-to-beginners' and cut_id=='05-01'
   if cut['preserveActualStillEvidence']:cut['stillEvidence']={'path':'projects/kind-to-beginners/production/local/batch-v1/sources/mk8-official-035.jpg','url':'https://www.nintendo.com/jp/ichikara/aabpa/photo/01/035.jpg','cue':[6.65,cut['seconds']],'purpose':'Actual MK8 Smart Steering antenna, displayed beside the original illustrative vehicle','sourceRecord':'baseline production-plan officialStillEvidence and retained source review; not a library asset','crop':'full image; preserved aspect ratio','sourceKind':'official gameplay still used only as explanation evidence'}
  plan['status']='native-visual-preflight-reviewed-awaiting-render' if args.phase=='preflight' else 'native-capture-complete-awaiting-final-review'
  plan['unity']['licenseReview']='Exact realized assets reconciled against parent asset-provenance.json; vendor originals unchanged; animation runtime and seven states per cut directly inspected.'
  plan['assetRecords']=list(all_assets.values());plan['sharedAssetPaths']=list(all_assets)
  plan['realization']={'stageSource':str(STAGE.relative_to(ROOT)).replace('\\','/'),'stageSourceSha256':sha(STAGE),'latestCaptureVersion':args.capture_version,'receiptPhase':args.phase,'compiledFingerprintsObserved':sorted(fingerprints),'independentScenePerCut':True,'noNewNarration':True,'noGameplayReplacement':True,'humanWholeReview':'pending'}
  save(path,plan)
  print(slug,len(plan['explanationCuts']),len(all_assets),'recorded')
if __name__=='__main__':main()
