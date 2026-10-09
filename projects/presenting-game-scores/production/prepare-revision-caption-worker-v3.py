"""Derive the literal-caption candidate using only already-reviewed current ASR."""
from pathlib import Path
P=Path(__file__).parent
src=P/'prepare-literal39-captions-v7.py';dst=P/'prepare-revision-literal-captions-v3.py';assert not dst.exists()
t=src.read_text('utf-8')
t=t.replace("DEST=BASE/'caption-candidate-v7'", "DEST=BASE/'revision-balatro60-v2/caption-candidate-v3'")
t=t.replace("PLAN=BASE/'measured-timeline-candidate-v7.json'", "PLAN=BASE/'revision-balatro60-v2/measured-editorial-candidate-v3.json'")
t=t.replace("currentVoiceSelectionSha256", "voiceSelectionSha256").replace("currentVoiceSelection", "voiceSelection").replace("voices['currentVoiceApproved']", "voices['currentCompleteVoiceApproved']")
t=t.replace("BASE.parent/f'script/current-voice-v7.{lang}.json'", "BASE/f'revision-balatro60-v2/script/narration-v2.{lang}.json'")
t=t.replace("'141':'백사십일'", "'141':'백사십일','7':'칠','3':'세','6':'육','560':'오백육십','1327':'천삼백이십칠','704':'칠백사','1200':'천이백'")
old=""" if sid.startswith(('04-','08-')):p=BASE/'observation-candidates-contexts-asr-v3'/f'{sid}-complete-candidate-join.json'
 elif int(sid[:2])>=11 and not sid.startswith('24-'):p=BASE/'observation-candidates-contexts-asr-v3'/f'{sid}-complete-independent.json'
 elif sid.startswith('24-'):p=BASE/'named-guide-contexts-asr-v6/24-complete-named-guide-independent.json'
 else:p=BASE/'current-whole-asr-v1'/f'{sid}.json'"""
new=""" if sid.startswith('01-'):p=BASE/'revision-balatro60-v2/voice-whole-asr-v3/r01-overview.json'
 elif sid.startswith('10-'):p=BASE/'revision-balatro60-v2/voice-joined-asr-v3'/f'{sid}.json'
 elif sid.startswith(('04-','05-','07-','09-')):p=BASE/'revision-balatro60-v2/voice-joined-asr-v1'/f'{sid}.json'
 elif sid.startswith(('13-','14-','18-','19-','24-')):p=BASE/'revision-balatro60-v2/voice-whole-asr-v1'/f'r{sid}-p1.json'
 elif sid.startswith('08-'):p=BASE/'observation-candidates-contexts-asr-v3'/f'{sid}-complete-candidate-join.json'
 elif int(sid[:2])>=11:p=BASE/'observation-candidates-contexts-asr-v3'/f'{sid}-complete-independent.json'
 else:p=BASE/'current-whole-asr-v1'/f'{sid}.json'"""
assert old in t;t=t.replace(old,new)
t=t.replace("if sid=='06-relative-gap' and pi==2:", "if sid in ['06-relative-gap','09-feedback-hierarchy','10-audit-and-close'] and pi==2:")
t=t.replace("eparts=english.split(' In a later shot, ',1);eparts[1]='In a later shot, '+eparts[1]", "eparts=english.split('. ',1);eparts[0]+='.';assert len(eparts)==2")
t=t.replace("len(chunks)==40", "len(chunks)==42")
t=t.replace("original30ParagraphsRetained=True", "unchangedApprovedParagraphPcmRetained=True,allCurrent39ParagraphsPreserved=True")
t=t.replace("allLiteralKoEn39ParagraphsPreserved=True", "allLiteralKoEn39ParagraphsPreserved=True")
t=t.replace("semanticChunks=40", "semanticChunks=len(chunks)")
dst.write_text(t,'utf-8')
print('Prepared current-caption worker; no ASR/model/media regeneration.')
