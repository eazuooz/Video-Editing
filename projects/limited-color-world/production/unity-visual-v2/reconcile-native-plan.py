"""Record actual D25/D26 native scene provenance and observed preflight evidence."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[4]
M=Path('C:/Users/1/.codex/video-production/design-25-30-unity-v2-20261028')
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
provenance=read(R/'production/batches/design-25-30-unity-v2-20261028/asset-provenance.json')
assets={a['path']:a for a in provenance['assets']}
realized={
 'limited-color-world':{
  'cut002':'Already-active ambiguous-colour state: two same-shape blocks of different types converge to nearly identical colours; character provides familiar game context. Do not replay the earlier spoken change.',
  'cut003':'Three independently inspected screenshots reveal in the spoken order: Puyo distinction, Mario Wonder important target, grayscale Mario visual hierarchy. Preserve image aspect ratios; short labels state each purpose.',
  'cut004':'Same-shape red and green blocks visibly converge in colour while their type labels stay fixed. The variable is colour separation, not mesh shape.',
  'cut006':'The same coloured blocks sit against bright and dark theme panels, with imported tree/chest context. Reduce block separation to expose different background contrast.',
  'cut008':'A near-background-colour block loses its boundary. Reveal an inter-block leader followed by the disappearing block/background edge.',
  'cut009':'One test scene is shown twice with Protanopia-type and Deuteranopia-type condition labels activated in speech order. These are named test conditions, not a claimed physiological filter simulation. The following exact inspected Puyo menu shows the actual conditions.',
  'cut011':'Keep the left block dark and progressively lighten the right block, showing that brightness supplies a distinction beyond colour.',
  'cut013':'Both blocks initially disappear into the dark background; lighten the right block only to restore its silhouette while the left stays difficult to distinguish.',
  'cut015':'Reveal a circle, triangle and stripes on actual block faces with the three spoken examples. Then converge their colours while keeping all shapes visible.',
  'cut027':'Reuse a forest, player, path and chest. Dim background foliage while the player/path/goal remain readable in the narrated viewing order.',
  'cut029':'Compare similar-colour type blocks against the forest/player/path/chest hierarchy in monochrome materials. Two different questions stay visibly separate. All material slots are replaced on scene instances only, preserving vendor sources.',
  'cut030':'Carry the same forest/player/path/chest arrangement forward and mirror its horizontal positions once, giving a fresh view of a familiar layout without restarting the explanation.'},
 'computer-controlled-players':{
  'cut007':'Articulated actor punches empty space, approaches a marked hazard, then stops after reading the opponent and danger. Show the difference between animation and context-sensitive choice.',
  'cut009':'Two facing articulated actors begin the same attack response immediately after a signal, illustrating an opponent with no reaction delay.',
  'cut017':'An illustrative die settles while a miniature opponent chooses and performs an attack inside the same process frame. An arrow connects that selected action to the actual opponent: shared computer control can affect trust.',
  'cut021':'Position/state labels connect by a leader to the controlled actor, which advances after receiving the information: data → decision → movement.',
  'cut023':'Facing actors animate attacks above a common distance grid with separate reach indicators, supporting comparison of distance, timing and movement range.',
  'cut024':'The annotated example fixes attack reach at two cells and separation at three. Show the first miss, advance one cell, update separation to two and show the attack reaching. Values belong to our illustration, not measured commercial-game data.',
  'cut026':'Keep the same actors and grid while the opponent changes from approaching to attacking. The relevant input changes from location alone to action state.',
  'cut029':'Activate attack and retreat directions together beside the controlled actor, exposing conflicting conditions in one unchanged world.',
  'cut030':'The actor advances, retreats and oscillates while both conditions remain active; a priority rule then selects danger avoidance and the actor retreats consistently.',
  'cut032':'A visible twelve-frame bar begins with detection and the opposing actor begins its punch after twelve 60fps frames. Display 12 ÷ 60 = 0.2 seconds as the concrete worked example.',
  'cut033':'Reverse the illustrative input direction: the actor briefly travels the wrong way, pauses to adapt, then moves toward the intended target. Arrows and short state labels change with the action.'}
}
for slug,description in realized.items():
 p=R/'projects'/slug/'production/unity-visual-v2/visual-plan.json';v=read(p)
 verified=[];allassets={};animations=set();referenceimages=[]
 for c in v['cuts']:
  if c['operation']!='replace-explanation-visual':continue
  folder=M/slug/'preflight/v3'/c['id'];receipt=read(folder/'preflight-success.json');req=read(folder/'request.json')
  assert receipt['status']=='complete' and receipt['compiledSourceFingerprint']==req['expectedFingerprint']
  scene=R/'unity/VideoEditing'/receipt['scene'];assert scene.is_file()
  c['visualTreatment']=description[c['id']]
  c['scenePath']=str(scene.relative_to(R)).replace('\\','/')
  c['sceneSaveStatus']='saved-native-preflight-v3'
  c['sceneSha256AtPreflight']=sha(scene)
  c['sharedAssetPaths']=receipt['assets'];c['animationPaths']=receipt['animations']
  c['assetRecords']=[assets[a] for a in receipt['assets'] if a in assets]
  c['assetsByRole']=[a['key'] for a in c['assetRecords']]
  c['nativePreflight']={'revision':'v3','receipt':str(folder/'preflight-success.json'),'sha256':sha(folder/'preflight-success.json'),'compiledSourceFingerprint':receipt['compiledSourceFingerprint'],'stageAssemblyMvid':receipt['stageAssemblyMvid'],'samplesReviewed':7,'all375StatesDirectlyViewed':True,'captionedFinalReview':'pending'}
  for a in c['assetRecords']:allassets[a['path']]=a
  animations.update(receipt['animations'])
  for a in receipt['assets']:
   if 'Generated/ReferenceImages/' in a:referenceimages.append(read(R/'unity/VideoEditing'/(a+'.source.json')))
  if slug=='limited-color-world' and c['id']=='cut029':
   c['nativePreflight']['status']='needs-selective-v4-all-material-slots-fix'
   c['nativePreflight']['issue']='v3 chest wood retained brown because only material slot zero was replaced; owned SolidTint now replaces every slot.'
  else:c['nativePreflight']['status']='pass-temporal-sample-layout-review'
  verified.append(c['id'])
 v['status']='native-preflight-reviewed-final-capture-pending'
 v['assetRecords']=list(allassets.values())
 v['sharedAssetPaths']=list(allassets)
 v['animationPaths']=sorted(animations)
 v['referenceImageRecords']=referenceimages
 v['assetProvenanceAuthority']='production/batches/design-25-30-unity-v2-20261028/asset-provenance.json'
 v['renderSpecification'].update({'engine':'Unity','unityVersion':'6000.6.0f1','project':'unity/VideoEditing','pipeline':'Universal Render Pipeline','pipelineVersion':read(R/'unity/VideoEditing/Packages/packages-lock.json')['dependencies']['com.unity.render-pipelines.universal']['version'],'defaultTopRightKind':'해설용 시연','camera':'Orthographic; position (0,7,-14), look at (0,1,0), size 5.5; unchanged per cut','stageClass':'Yamyam.DesignVisualV2.D25D26Stage'})
 v['openChecks']=['Selective D25 cut029 material-slot correction preflight' if slug=='limited-color-world' else 'Full native capture with compiled fingerprint guard','Final captioned composite 1080/375 pixels and critical action frames','Final exact AAC packet identity, KO/EN SRT bytes, full decode and unchanged clocks']
 v['reviewedEvidence']['nativePreflightV3AllStatesViewed']=verified
 v['reviewedEvidence']['nativeCurrentSourceFacingAndRigActions']='Verified D26 v3 face-to-face skeleton punches and walking; stale v2 excluded from approval.'
 write(p,v)
 q=M/slug/'qa/preflight-v3'
 report={'slug':slug,'revision':'v3','compiledSourceFingerprint':'456cbbc8cd815d54be6343986692e048e564204902a508aee4b753c4bb2455cc','all23ApplicableCutsReviewed':False,'cutIds':verified,'samplesPerCut':7,'totalNativeSamples':len(verified)*7,'all375StatesDirectlyViewed':True,'boards':[{'path':str(q/(i+'-375.jpg')),'sha256':sha(q/(i+'-375.jpg'))} for i in verified],'nativeFullSizeDirectViews':['cut015/frame-00145.png'] if slug=='limited-color-world' else ['cut024/frame-00725.png'],'status':'D25-cut029-selective-correction-pending' if slug=='limited-color-world' else 'pass-temporal-sample-preflight','observations':['Labels are short and do not overlap the fixed caption region.','Actors have visible articulated limbs and imported materials, not cube substitutes.','Speech/order and frames preserved; model values are illustrative.','Current v3 compiled fingerprint is recorded, superseding stale v2 evidence.'],'finalCaptionedMotionReview':'pending','humanFullViewingOrListeningClaimed':False}
 if slug=='limited-color-world':report['observations'].append('All material slots require a monochrome replacement in cut029; SolidTint fix saved and selective v4 requested.')
 else:report['observations']+=['Actual face-to-face punch and walk deformation visible.','Miniature actor replaces arbitrary action chest.','Distance label changes 3→2 after one-cell advance.','Reaction-delay critical frames156–168 still require final encoded inspection.']
 write(R/'projects'/slug/'production/unity-visual-v2/preflight-v3-review.json',report)
print('Actual native scene paths, assets, animation receipts and v3 review evidence recorded.')
