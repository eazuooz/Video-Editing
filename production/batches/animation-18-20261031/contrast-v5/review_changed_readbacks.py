"""Exact comparisons plus explicitly reviewed ASR spelling equivalences.
No voice listening or automatic acceptance of arbitrary semantic differences.
"""
from pathlib import Path
import json,hashlib,sys
H=next(p for p in Path(__file__).resolve().parents if p.name=='contrast-v5');R=H.parents[3];L=H/'local/asr-changed'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def norm(s):return ''.join(c.lower()for c in s if c.isalnum())
RULES={
 ('A01','002'):({'시프':'시푸'},'Sifu title vowel spelling differs only; identity is unambiguous from expected text and game evidence. This permits caption alignment but does not prove perfect pronunciation.'),
 ('A01','050'):({'오치에':'오치의'},'Possessive 의 is transcribed 에 after Oatchi; a permitted spoken realization of the particle, with the same owner/contact meaning.'),
 ('A01','056'):({'10후':'시푸','시프':'시푸'},'ASR writes the unfamiliar Sifu name as 10후 or 시프; no quantitative ten is claimed. Identity is clear, while the title vowel remains a focused-listening candidate.'),
 ('A02','028'):({'3':'쓰리'},'Game installment number3 and spoken 쓰리 identify the same Splatoon3; no number change.'),
 ('A04','002'):({'2':'투'},'Hades2 and spoken 하데스 투 identify the same installment; no number change.'),
 ('A04','012'):({'2':'투','엑스':'액스'},'Hades2 number spelling and Moonstone Axe vowel spelling only. Same weapon/action; Axe pronunciation remains an ASR ambiguity rather than confirmed wrong audio.'),
 ('A04','038'):({'처음에':'처음의'},'Possessive 의 can be spoken 에. Both refer back to the opening training-area scene in this context.'),
 ('A05','001'):({'러쉬':'러시'},'Hi-Fi RUSH title has alternate ASR Korean spelling 러쉬; expected canonical display 러시 is retained.'),
 ('A05','002'):({'일키죠':'읽히죠'},'The current regenerated take is transcribed with the standard spoken form 일키죠. National Institute of Korean Language lists 읽히다 pronunciation 일키다: https://krdict.korean.go.kr/eng/dicSearch/SearchView?ParaWordNo=24586 . This rule does not accept the earlier ambiguous 일기죠 take.'),
 ('A05','039'):({'차이에':'차이의'},'Possessive 의 can be spoken 에. The subject is the same opening guitar attack by Chai; no action or meaning changes.'),
 ('A07','035'):({'3':'쓰리','전시는':'전신은'},'The game installment number is the same. 전신+은 is pronounced 전시는 by standard liaison (NIKL pronunciation rule13); this is a phonetic spelling, not a missing body-size concept. Primary rule: https://www.korean.go.kr/front/onlineQna/onlineQnaView.do?mn_id=216&pageIndex=1&qna_seq=315088 .'),
 ('A08','001'):({'원을':'I를'},'Current source explicitly gives spokenKo 원을 for the Roman numeral I pose name while preserving canonical display I를. This does not accept the earlier letter-name 아이 take.'),
 ('A08','066'):({'위에':'위의'},'Possessive 의 can be spoken 에. Both identify the same ring held above the head; the silhouette explanation is unchanged.'),
 ('A09','010'):({'렌처':'랜처','2':'투'},'Slime Rancher title vowel spelling and installment-number notation only. Distance change versus body-outline change is fully retained; ASR does not certify the title vowel pronunciation.'),
 ('A09','017'):({'2':'투'},'Slime Rancher2 and spoken 랜처 투 are the same game installment; no numerical or action change.'),
 ('A12','038'):({'옵스키르':'옵스퀴르','33':'삼십삼','룬에는':'루네는'},'Expedition33 title spelling and digit notation only. 룬에는 is a homophonic liaison spelling of 루네는, preserving the canonical character Lune; no person/action change. The French title vowel remains an ASR ambiguity, not certified perfect pronunciation.'),
 ('A13','009'):({'2':'투','DJ':'디제이'},'Super Street Fighter2 Turbo uses the same installment number. DJ and 디제이 are the same spoken character name Dee Jay; no character or action change.'),
 ('A13','019'):({'DJ':'디제이','앞쪽에':'앞쪽의'},'DJ is the same spoken character name. Possessive 의 can be spoken 에; both identify the white lettering on the front of the trousers, with the facing-direction lesson preserved.'),
 ('A13','020'):({'4':'포','3차원':'삼차원','DJ':'디제이'},'Street Fighter4 installment, three-dimensional rendering and Dee Jay retain identical numerical/name meanings. 반대쪽에 서도 and 반대쪽에서도 differ only in ASR spacing here.'),
 ('A13','042'):({'DJ':'디제이'},'DJ is the same spoken character name Dee Jay. The visible MAXIMUM word, vertical placement and opposite-facing comparison are all retained.'),
 ('A13','050'):({'DJ':'디제이'},'DJ is the same spoken character name. 향해 서는 and 향해서는 differ only in ASR spacing here; the two facing poses and silhouette criteria are retained.'),
 ('A14','001'):({'화를':'활을'},'활+을 is pronounced 화를 by ordinary liaison; the same bow-aiming action is retained, not an anger claim. Full neighboring weapon/body-motion context matches.'),
 ('A14','043'):({'FC':'에프씨','25':'이십오'},'FC25 letters and Arabic installment number equal the spoken Korean title. Both small body lean and complete running-direction turn are retained.'),
 ('A14','046'):({'3':'쓰리'},'Splatoon3 and spoken 스플래툰 쓰리 name the same installment. Movement while aiming two guns and body-part role separation are fully retained.'),
 ('A17','001'):({'암제의':'암즈의'},'ASR spells the unfamiliar ARMS title 암제. Ribbon Girl and the complete extending-arm/outline explanation retain the same game identity. This permits semantic alignment while title pronunciation remains uncertain without listening.'),
 ('A17','024'):({'컵패드에':'컵헤드의','일킵니다':'읽힙니다'},'Cala Maria establishes the same Cuphead identity despite unfamiliar-title ASR spelling 컵패드; title pronunciation remains uncertain. 읽힙니다 has the standard 일킵니다 spoken spelling (읽히다 [일키다]); unlike 일으킵니다, no extra vowel is present. Arm outline, two joints and elbow question are retained.'),
 ('A10','003'):({'6':'식스','줄이는':'주리는'},'Street Fighter6 installment number is equivalent. Juri+는 is recognized as the common verb 줄이는, an equivalent Korean sound sequence in context; the character identity is preserved.'),
}
s=read(H/'narration/source-verified-revisions.json');changes={(e['id'],c['id']):c for e in s['episodes']for c in e['changes']+[x for x in s['existingApprovedChanges']if x['episode']==e['id']]};expected={k:c['ko']for k,c in changes.items()}
maprows={(x['episode'],x['sentence']):x for x in read(H/'narration/released-tts-map.json')['entries']}
entries=[];issues=[]
for file in sorted((L/'raw').glob('*.json')):
 r=read(file);key=(r['episode'],r['sentenceId']);wav=R/r['audio']
 c=changes[key];m=maprows.get(key)
 if m and(m.get('ko')!=c['ko']or m.get('en')!=c['en']or m.get('text')!=c.get('spokenKo',c['ko'])):m=None
 active=('A10S'+key[1])if key[0]=='A10'else(m['key']if m else key[0]+'S'+key[1]+'X'+hashlib.sha256(c.get('spokenKo',c['ko']).encode()).hexdigest()[:10])
 if r['key']!=active:continue
 if not wav.exists()or sha(wav)!=r['audio_sha256']:continue
 actual=r['text'];target=expected[key];aliases,reason=RULES.get(key,({},'Independent normalized text is exact; only spacing/punctuation may differ.'))
 canonical=actual
 for old,new in aliases.items():canonical=canonical.replace(old,new)
 accepted=norm(canonical)==norm(target)
 row={'episode':key[0],'sentenceId':key[1],'audioSha256':r['audio_sha256'],'asrPath':file.relative_to(R).as_posix(),'asrSha256':sha(file),
  'expected':target,'recognized':actual,'acceptedForCaptionAlignment':accepted,'alignmentAliases':aliases if accepted else{},
  'semanticContentPreserved':accepted,'reason':reason if accepted else'Unreviewed difference; do not infer missing or correct speech from similarity alone.',
  'reviewScope':'Explicit model text-equivalence review for listed aliases; otherwise exact normalized mechanical comparison. No audio listening.',
  'retakeRequiredFromCurrentEvidence':False,'humanListening':False}
 if not accepted:issues.append(row)
 if key in [('A01','002'),('A01','056'),('A04','012'),('A09','010'),('A12','038'),('A17','001'),('A17','024')]:row['pronunciationUncertainty']='Proper-name vowel/ASR spelling ambiguity; actual voice quality not certified by ASR.'
 entries.append(row)
save={'reviewScope':'Full expected text versus independent ASR; no human listening','entries':entries,'pendingDifferences':issues,'humanListening':False}
(L/'text-review.json').write_text(json.dumps(save,ensure_ascii=False,indent=2)+'\n','utf8')
print('Reviewed',len(entries),'accepted',sum(r['acceptedForCaptionAlignment']for r in entries),'pending',len(issues))
for q in issues:print(q['episode'],q['sentenceId'],'\nEXPECTED',q['expected'],'\nACTUAL',q['recognized'])
