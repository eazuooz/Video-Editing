from pathlib import Path
import json,hashlib,datetime
H=Path(__file__).resolve().parent;R=H.parents[3];L=H.parent/'local/fighters-v3'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
j=load(H/'lesson-retention-plan.json')
j['additionalExamples']=[
 {'after':'01-p02','game':'KOF XV','character':'Shermie','role':'Observe arm lift, torso turn, strike and recovery','observedSource':'jdpFemQmbeA68.2–69.4','boundary':'Torso force → observed Shermie movement → why the screen size matters'},
 {'after':'02-p01','game':'Guilty Gear -Strive-','character':'Giovanna','role':'Horizontal and rising body silhouettes; native first then slow analysis','observedSource':'_8V7pd2k1zc56.6–57.4 and60.6–61.4','boundary':'Small play size → attack direction seen in the body silhouette → controlled size/amplitude comparison'},
 {'after':'04-p02','game':'KOF XV','character':'Shermie','role':'Preparation, airborne rotation and landing as one motion','observedSource':'jdpFemQmbeA245.0–246.6; second demonstration249.8–251.5','boundary':'Whole-motion reading → concrete shoulder/pelvis rotation → how a movement settles'}]
j['constraints']['playbackSpeed']={'native':1,'explicitAnalyticalReplay':.25,'noGlobalRuleChange':True}
j['rendererDecision']={'userSelection':'Unreal Game Animation Sample','engine':'5.8.4','mesh':'/Game/Characters/UEFN_Mannequin/Meshes/SKM_UEFN_Mannequin','basePose':'/Game/Characters/UEFN_Mannequin/Animations/Idle/M_Neutral_Stand_Idle_Loop','ownedVariant':'Bone-space authored shoulder/torso comparison, not a claimed packaged punch clip','implementation':'Two-bone IK; same hand target; left shoulder fixed; right shoulder22cm forward/8cm up, chest28degrees','sourceAssetsUnchanged':True,'retainedNonHumanoidUnity':'Linear overshoot and shape-expansion demonstrations remain unchanged'}
j['readThrough']={'koAndEnAll17ParagraphsReadWithoutHeadings':True,'original14ExactRetention':all(x['retainedUnchanged'] for x in j['originalParagraphs']),'noNewCreatorFraming':True,'noDefensiveMetaExplanationAdded':True,'originalOrderPreserved':True}
save(H/'lesson-retention-plan.json',j)
q=load(H/'qwen-voice-record.json');save(H/'voice-generation-record.json',q)
checkpoint={'episode':'A02','revision':'fighters-v3','status':'native-unreal-render-and-final-composition','updatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'completed':['Independent female-fighter FHD recordings inspected; native-first/slow-motion edit prepared','Three local Qwen own-voice paragraphs generated, normalized and ASR compared','All14 original lesson paragraphs and original PCM retained','Six editable Unreal levels/animation sequences saved; frames being captured'],'nextAction':'Finish Unreal captures and final paired encode; inspect frames/audio and deliver four local files','durationSeconds':364.1166666667,'humanFinalReview':False,'platformMutation':False,'sourceEditorTouched':False}
save(H/'checkpoint.json',checkpoint)
print('Current source, voice and renderer choices recorded')
