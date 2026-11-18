"""Lock original-RE2 comparison footage and the eight added spoken units."""
from pathlib import Path
import ast,copy,hashlib,json,re
H=Path(__file__).resolve().parent;ROOT=H.parents[2];P=ROOT/'projects/shorts-mario64-lakitu-camera'
M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115');C=M/'camera-music-revision-v139'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def pin(p):return dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def save(p,d):
 if p.exists():assert read(p)==d,p;return
 p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
 primary=[dict(url=u,snapshot=pin(C/f'primary-source-v147-{i}.bin'))for i,u in enumerate(['https://longplays.org/infusions/faq/faq.php?cat_id=1','https://longplays.org/infusions/forum/viewthread.php?thread_id=16081','https://www.nintendo.co.jp/wii/vc/vc_sm64/vc_mb_01.html'])]
 primary.append(dict(url='https://www.capcom.co.jp/ir/english/data/pdf/annual/2013/annual_2013_01.pdf',scope='Capcom annual report release-year passage dates ResidentEvil2 to1998; verified in web extraction. Direct raw PDF request returned403; no local PDF or complete-PDF reading claimed.'))
 transfer=M/P.name/'sources/re2-source-transfer-v141.json'
 source=P/'planning/camera-comparison-source-review-v147.json'
 save(source,dict(request=pin(H/'user-camera-music-revision-v139.json'),primarySources=primary,recording=pin(transfer),sourceFile=read(transfer)['output'],observedSourceContacts=[pin(C/x)for x in ['re2-source-contact-v145.jpg','re2-bus-cut-dense-v147.jpg','mario-source-contact-v145.jpg']],findings=['The adopted original1998 RE2 game runs on PS5,2870x2160 HEVC at approximately60 recorded frames per second. This is not the2019 remake or an AI reconstruction.','The bus view stays anchored while characters move; dense24.0–29.5s samples show a discrete shot change between25.5 and26.0s. No input telemetry or combat-damage cause is inferred.','Mario82–88s shows a close high view and a return to a wider view. The retained authored native camera models explain the documentedC-button rules and are labelled as models.','Mario64 is1996 and originalRE2 is1998: compare different camera designs in the same era; do not claim that1998 preceded1996 or that Mario introduced all game camera systems.'],rights=dict(permissionSource=primary[0]['url'],sourcePage=primary[1]['url'],allowed='Edited extracts for an original explanation/review, with website, channel and longplayer credited in picture and description.',requiredPictureCredit='World of Longplays · longplays.org · Spazbo4',recorder='Spazbo4',channel='World of Longplays',sourceAudioAdopted=False,publicPublishingAuthorized=False),actualContinuousPlayback=False,humanApproval=False,semanticScopeComplete=True))
 old=read(P/'planning/narration-camera-v5.json');vp=M/P.name/'voice-edit-v5/voice-generation-complete-proof.json';voice=read(vp)
 additions=[('p000','비슷한 시기의 두 게임은, 카메라를 다르게 사용합니다.','Two games from the same era use their cameras differently.'),('p000','바이오하자드 이 원작의 장면입니다.','This is the original Resident Evil2.'),('p000','캐릭터가 움직여도, 카메라 자리는 고정되어 있죠.','The character moves, while the camera stays in its fixed position.'),('p000','장면은 미리 정해진 다른 구도로 전환됩니다.','The view switches to another predefined camera angle.'),('p000','마리오 육십사는, 보는 방향도 플레이어가 직접 바꿉니다.','Super Mario64 also lets the player choose where to look.'),('p003b','고정된 구도에서는, 화면 밖의 모습을 바로 돌려 볼 수 없습니다.','A fixed shot does not let you turn the view to inspect what is off screen.'),('p003b','마리오는 같은 자리에서도, 다른 방향을 살펴볼 수 있죠.','Mario can look in another direction while staying in the same place.'),('p003b','움직이기 전에 직접 둘러볼 수 있다는 점이, 중요한 변화입니다.','Being able to look around before moving is the important change.')]
 new=[dict(id=f'c147u{i+1:03d}',paragraph=para,ko=ko,en=en)for i,(para,ko,en)in enumerate(additions)];retained=[]
 for u,raw in zip(old['units'],voice['rawChunks']):
  if 'sourceRaw'in u:assert u['sourceRaw']['sha256']==raw['sha256']
  assert pin(Path(raw['path']))['sha256']==raw['sha256'];retained.append(dict(u,sourceRaw=raw))
 def para(pid):
  us=[u for u in new if u['paragraph']==pid];return dict(id=pid,ko=' '.join(u['ko']for u in us),unitIds=[u['id']for u in us],previousEnglishMeaning=' '.join(u['en']for u in us))
 units=[u for u in new if u['paragraph']=='p000'];paras=[para('p000')]
 for p in old['paragraphs']:
  units.extend(u for u in retained if u['paragraph']==p['id']);paras.append(p)
  if p['id']=='p003':units.extend(u for u in new if u['paragraph']=='p003b');paras.append(para('p003b'))
 assert len(units)==29 and len(retained)==21 and len(new)==8 and len(paras)==8
 locked=dict(schemaVersion=1,slug=P.name,origin=pin(P/'planning/narration-camera-v5.json'),sourceVoice=pin(vp),sourceAsr=old['sourceAsr'],sourceLevels=old['sourceLevels'],sourceInputs=[pin(source),pin(H/'user-camera-music-revision-v139.json'),pin(P/'planning/source-action-review-v2.json')],units=units,newUnits=new,reuseUnits=retained,newEnglish=[],paragraphs=paras,narrationLocked=True,approvedForTts=True,sourceOrderPreserved=True,reason='User requested originalRE2 fixed-camera comparison. Preserve all21 approved Mario utterances and add8 concrete comparison utterances before the existing overview and beside the viewpoint explanation.',humanApproval=False,voiceAcceptedForFilm=False,headingFreeReadThroughCompleted=True,rawInternalLevelThresholdsUnchanged=True)
 save(P/'planning/narration-repair-v147.json',locked)
 clauses=copy.deepcopy(read(P/'planning/caption-clauses-camera-v5.json'));oldparas={x['id']:x for x in clauses['paragraphs']};clauses['source']=pin(P/'planning/narration-repair-v147.json');clauses['paragraphs']=[oldparas[x['id']]if x['id']in oldparas else dict(id=x['id'],clauses=[[u['ko'],u['en']]for u in new if u['paragraph']==x['id']])for x in paras];save(P/'planning/caption-clauses-repair-v147.json',clauses)
 script=P/'script/narration.repair-v147.json';save(script,dict(title=P.name,scenes=[dict(id=u['id'],title=u['paragraph'],lines=[u['ko']])for u in new]))
 d=copy.deepcopy(read(ROOT/'projects/shorts-returnal-particle-tentacles/production/tts-manifest-repair-v105.json'));d.update(slug=P.name,revision='original-re2-camera-comparison-v147');d['paths']['script']=str(script.relative_to(ROOT)).replace('\\','/');d['tts']['outputDir']=f'shared/output/original-tech-twelve-20261115/{P.name}/voice-repair-v147';d['tts']['filenameStem']='camera-comparison-v147';save(P/'production/tts-manifest-repair-v147.json',d)
 for oldname,newname in [('run-selected-clarity-voice-v105.py','run-camera-comparison-voice-v147.py'),('run-selected-clarity-asr-v105.py','run-camera-comparison-asr-v147.py')]:
  s=(H/oldname).read_text('utf8').replace('v105','v147');s=re.sub(r'^SLUGS=.*$',"SLUGS=['shorts-mario64-lakitu-camera']",s,flags=re.M);assert "SLUGS=['shorts-mario64-lakitu-camera']"in s;ast.parse(s);p=H/newname;assert not p.exists();p.write_text(s,encoding='utf8')
 print(json.dumps(dict(newUnits=8,retainedUnits=21,paragraphs=8,rightsVerified=True,actualFhdFootageAcquired=True)))
if __name__=='__main__':main()
