"""Prepare adapted workers without executing any dependent production."""
from pathlib import Path
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[2]
ref=ROOT/'projects/presenting-game-scores/production'
out=BASE/'build-character-final-mix-v1.py';assert not out.exists()
text=(ref/'build-reviewed-final-mix-v1.py').read_text('utf-8')
for a,b in [('presenting-game-scores','character-parameters'),('(18332,19052,6388323)','(22677,23397,8430001)'),('6388323','8430001'),('18452','22797'),('all19CurrentPcmSamplesIdentical','all12CurrentPcmSamplesIdentical'),("voice_selection['currentVoiceApproved']","voice_selection['currentCompleteVoiceReadyForMeasuredPlanning']"),("len(voice_selection['scenes'])==19","len(voice_selection['scenes'])==12"),('mixed10 whole chapters and21','mixed12 whole chapters and12'),("['node',","['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe',")]:
 assert a in text,a;text=text.replace(a,b)
out.write_text(text,'utf-8')
out=BASE/'prepare-character-pair-caption-clock-v1.py';assert not out.exists();text=(ref/'prepare-current-pair-caption-clock-v1.py').read_text('utf-8')
for a,b in [('presenting-game-scores','character-parameters'),('(168,68)','(201,95)'),('18452','22797'),('koCueCount=168,enCueCount=68','koCueCount=201,enCueCount=95'),('dict(ko=168,en=68','dict(ko=201,en=95'),('width<=1570','width<=924 and x>485 and x+width+14<1460')]:
 assert a in text,a;text=text.replace(a,b)
out.write_text(text,'utf-8')
print('Prepared mix and caption clock only; not executed')
