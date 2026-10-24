"""Record inspected source evidence and authorize only internal media production."""
import json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent
observed=[
('shorts-titanfall-time-shift',600,[215,235],214,229,'The same corridor alternates intact and ruined with wrist-device gestures; movement and facing continue. No actual internal coordinates inferred.'),
('shorts-superliminal-perspective',60,[35,55],38,144,'A small alphabet block is picked up, placed farther away and approached at larger size; nearby chess pawn provides another visible scale result.'),
('shorts-ghost-leaf-updraft',60,[10,18],10,None,'Golden-forest leaves move around the player. This is context only; historic unburnt-leaf bug and wind-emitter fix are reconstructed from the developer account, not claimed visible in this recording.'),
('shorts-gears-inertialization',1200,[33,45],34,None,'Armoured character moves from cover into a low run and into aiming; recording is game context, not proof of the internal transition algorithm.'),
('shorts-portal-recursion',300,[88,100],92,None,'A floor portal displays the incinerator area and a nested portal/opening view as the player changes viewing angle. This supports the question; stencil data itself is not extracted.')]
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for slug,offset,inspection,start,second,obs in observed:
 p=R/'projects'/slug;info=json.loads((p/'production/local/source.info.json').read_text(encoding='utf8'));probe=json.loads((p/'production/local/source-inspection/probe.json').read_text(encoding='utf8'));v=next(x for x in probe['streams'] if x['codec_type']=='video')
 assert 'Creative Commons' in info['license'] and v['width']>=1920 and v['height']>=1080
 record={'id':'gameplay','kind':'independent-gameplay','url':info['webpage_url'],'title':info['title'],'recorder':info['channel'],'license':info['license'],'licenseUrl':'https://creativecommons.org/licenses/by/3.0/','recordingLicenseEvidence':'Downloaded individual public-video metadata; CC-filter discovery independently verified.','nativeDimensions':[v['width'],v['height']],'nativeFrameRate':v['r_frame_rate'],'originalOffsetSeconds':offset,'localPath':f'projects/{slug}/production/local/gameplay.mp4','sha256':hashlib.sha256((p/'production/local/gameplay.mp4').read_bytes()).hexdigest(),'inspectionSeconds':inspection,'observation':obs,'plannedIntroStart':start,'plannedConfirmationStart':second,'speed':1,'audioAdopted':False,'audioReason':'Original licensed music/dialogue clearance not separately established; authored narration and licensed BGM only.','creditPlacement':'description-bottom; original embedded marks preserved','publisherRightsAssessment':'Short, directly discussed educational demonstration of the released game; recording creator CC BY independently verified. This does not assert ownership or an exclusive game-IP license.'}
 save(p/'sources/selected-footage.json',record)
 plan=json.loads((p/'planning/production-plan.json').read_text(encoding='utf8'));plan.update(independentFootageViewed=True,scriptFinalized=True,sourceInspection={'method':'Native decoded contact sheets, complete contiguous selected ranges at 1fps; final moving output still pending.','observation':obs},readThrough={'language':'KO/EN','status':'editorial-pass','scope':'One mechanism, causal transitions, no reference-creator framing, continuous paragraphs; necessary implementation limits retained.'},assetChoice={'libraryConsulted':'shared/assets/unity-asset-library.json; imported catalog','choice':'Reusable licensed KayKit Knight for articulated player/animation, independently authored measured props for other techniques.','reason':'Shared neutral articulated rig already runtime-used in our hitbox Short; commercial environment packs would obscure the one-variable demonstration.','license':'Assets/ThirdParty/KayKitAdventurers/LICENSE.txt — CC0'},scenePlan=json.loads((p/'production/section-plan.json').read_text(encoding='utf8')))
 plan['research']['productionStatus']='Independent FHD CC BY footage selected and viewed; implementation and final audiovisual QA pending.';save(p/'planning/production-plan.json',plan)
 for name in ['time-captions.py','finish-audio.py']:
  f=p/'production'/name;text=f.read_text(encoding='utf8')
  if name=='time-captions.py':text=text.replace("if control.get('selectedShortVideo')!=P.name or control.get('shortsDirectSelection',{}).get('selectedRevision')!=REVISION:","if P.name not in control.get('shortsBatchAuthorization',{}).get('slugs',[]):")
  else:
   a=text.index('def guard():');b=text.index('\ndef ',a+1);text=text[:a]+'def guard():\n    return revision_guard()\n\n'+text[b:]
  f.write_text(text,encoding='utf8')
print('Five individual source/native-dimension checks and editorial preflights recorded. Human review pending.')
