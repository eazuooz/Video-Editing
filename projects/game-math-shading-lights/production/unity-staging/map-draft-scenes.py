"""Record source-beat coverage without guessing narration durations or approving footage."""
from pathlib import Path
import json,hashlib
S=Path(__file__).resolve().parent
P=S.parents[1]
source=P/'script/draft-narration.ko.json'
data=json.loads(source.read_text(encoding='utf-8'))
integrated=P/'script/narration.ko.json'
integrated_data=json.loads(integrated.read_text(encoding='utf-8')) if integrated.exists() else {}
scene_lookup={s['sourceBeatId']:s['id'] for s in integrated_data.get('scenes',[])}
patches={
 '007-spec-observe':{'variable':'viewAzimuth','from':-20,'to':20,'components':{'x':0,'y':1,'z':.03,'w':0}},
 '008-vectors':{'normalArrow':True,'lightArrow':True,'viewArrow':True},
 '009-reflection-build':{'normalArrow':True,'lightArrow':True,'reflectionArrow':True},
 '011-phong':{'model':0,'reflectionArrow':True,'viewArrow':True},
 '012-exponent':{'model':0,'variable':'exponent','from':2,'to':32},
 '013-spec-color-map':{'variable':'specularStrength','from':.1,'to':1},
 '014-light-color':{'lightType':3,'cookie':True,'goboKind':'window'},
 '016-halfway':{'model':1,'halfArrow':True,'viewArrow':True},
 '017-blinn':{'model':1,'halfArrow':True,'viewArrow':True},
 '018-diffuse-start':{'components':{'x':1,'y':0,'z':0,'w':0},'variable':'viewAzimuth','from':-20,'to':20},
 '019-lambert-area':{'components':{'x':1,'y':0,'z':0,'w':0},'variable':'normalTilt','from':0,'to':60},
 '020-lambert-calc':{'components':{'x':1,'y':0,'z':0,'w':0},'variable':'normalTilt','from':0,'to':120},
 '022-brdf-return':{'brdfNormalizedDiffuse':True,'components':{'x':1,'y':0,'z':0,'w':0}},
 '023-brdf-normalization':{'brdfNormalizedDiffuse':True},
 '025-ambient-equation':{'variable':'ambientStrength','from':0,'to':1},
 '026-emission':{'variable':'emissionStrength','from':0,'to':1,'emission':{'r':1,'g':.3,'b':.04,'a':1}},
 '029-visibility':{'diagram':'visibility'},
 '030-half-lambert':{'diffuseModel':1,'components':{'x':1,'y':0,'z':0,'w':0},'variable':'normalTilt','from':0,'to':120},
 '034-shadow-limit':{'diagram':'visibility'},
 '035-fresnel-retro':{'diagram':'fresnel'},
 '036-anisotropy':{'diagram':'anisotropy'},
 '038-flat':{'shading':1},
 '039-gouraud':{'shading':2},
 '040-gouraud-highlight':{'shading':2,'variable':'lightAzimuth','from':-25,'to':25},
 '041-phong-shading':{'shading':0,'variable':'lightAzimuth','from':-25,'to':25},
 '048-point':{'lightType':1},
 '049-spot':{'lightType':2,'innerAngle':28,'outerAngle':50},
 '050-projector':{'lightType':3,'cookie':True,'goboKind':'window'},
 '051-directional':{'lightType':0},
 '052-delta':{'diagram':'delta'},
 '053-attenuation-start':{'lightType':1,'attenuation':1,'referenceDistance':1,'variable':'lightDistance','from':1,'to':2},
 '058-linear-falloff':{'lightType':1,'attenuation':2,'innerRange':2,'range':6,'variable':'lightDistance','from':1,'to':7},
 '059-spot-falloff':{'lightType':2,'attenuation':2,'innerRange':2,'range':6},
 '061-doom-textures':{'lightType':1,'volumeMode':1,'cookie':True,'goboKind':'circle','falloffKind':'symmetric'},
 '062-doom-coordinate':{'lightType':1,'volumeMode':1,'cookie':True},
 '063-doom-omni':{'lightType':1,'volumeMode':1,'cookie':True,'falloffKind':'symmetric'},
 '064-doom-omni-worked':{'lightType':1,'volumeMode':1,'cookie':True,'volumeSize':{'x':4,'y':4,'z':6}},
 '065-doom-spot':{'lightType':2,'volumeMode':2,'cookie':True,'goboKind':'circle','falloffKind':'frontToBack'},
 '066-doom-borders':{'lightType':1,'volumeMode':1,'cookie':True},
 '067-doom-fake-spot':{'lightType':1,'volumeMode':1,'cookie':True,'goboKind':'fakeSpot','falloffKind':'symmetric'},
 '070-lightmap':{'diagram':'lightmap'},
 '071-vertex-bake':{'diagram':'vertexBake'},
 '073-direction-basis':{'diagram':'sh','diagramVariant':1},
 '076-probes':{'diagram':'probe'}
}
rows=[]
for beat in data['segments']:
 key=beat['id'].removeprefix('M21-')
 patch=patches.get(key,{})
 row={'sourceBeatId':beat['id'],'sourceSection':beat['section'],'title':beat['title'],'sourceScreenPlan':beat['screenPlan'],'candidateCuePatch':patch,'durationSeconds':None,'finalTimingRequired':True,'sourceFormulaBlocks':beat.get('sourceFormulaBlocks',[]),'status':'cpu-staged-needs-visual-and-timing-review' if patch else 'needs-source-specific-overlay-or-footage','renderableNow':False,'gameplayIsNotSubstitutedByThisStage':True}
 if beat['id'] in scene_lookup:row['integratedSceneId']=scene_lookup[beat['id']];row['candidateCaptureCueId']='m21-'+scene_lookup[beat['id']]
 if key in ['000-abstract','007-spec-observe','026-emission','034-shadow-limit','049-spot','060-doom-scope','076-probes','078-close']:row['independentGameFootageRequiredOrPlanned']=True
 if key=='035-fresnel-retro':row['secondCueRequired']={'diagram':'retroreflection'}
 if key=='073-direction-basis':row['additionalCueVariants']=[{'diagram':'sh','diagramVariant':i} for i in [0,2,3]]
 if key=='027-emission-gi':row['blocker']='An actual GI bake variant has not been implemented; cannot label arbitrary companion light as GI.'
 if key in ['074-bake-selection','075-mixed-lighting']:row['blocker']='Needs real bake/dynamic comparison or explicitly approved illustrative treatment; no fake baked renderer output.'
 if key=='077-probe-direction':row['blocker']='SH diffuse versus reflection-probe cubemap/prefilter diagram still to build.'
 rows.append(row)
out={'source':str(source),'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'status':'draft-coverage-only','beatCount':len(rows),'stagedCuePatchCount':sum(bool(r['candidateCuePatch']) for r in rows),'notes':['Preserve article order; renderer rows are not a reordered script.','All durations await actual narration and gameplay.','No row is human-reviewed or visually approved.','The same toy robot/lamp was selected from licensed owned assets; replace only if actual preview shows poor concept visibility.'],'beats':rows}
if integrated.exists():out['integratedNarration']={'path':str(integrated),'sha256':hashlib.sha256(integrated.read_bytes()).hexdigest(),'mappedSceneCount':len(scene_lookup)}
(S/'draft-scene-coverage.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'beats':len(rows),'cuePatches':out['stagedCuePatchCount']},ensure_ascii=False))
