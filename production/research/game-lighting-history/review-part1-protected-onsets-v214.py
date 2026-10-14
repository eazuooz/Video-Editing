"""Recognize the two complete protected utterances without expected-text prompts."""
from pathlib import Path
source=Path(__file__).with_name('review-part1-onset-replacements-v209.py').read_text('utf-8')
start=source.index(" old=read(BASE/")
end=source.index(' import psutil',start)
replacement=""" ep=BASE/'part1-protected-onsets-tts-execution-v211.json';e=read(ep)
 reqpath=BASE/'part1-protected-onsets-tts-request-v211.json';req=read(reqpath)
 selectedpath=ep
 old=read(BASE/'part1-selected-actions-asr-execution-v182.json')
 if e.get('exitCode') not in (0,1) or not e.get('endedAt') or len(e['results'])!=2 or e['requestSha256']!=sha(reqpath):raise RuntimeError('Closed protected diagnostic generation required')
 if read(ROOT/'shared/output/gpu-handoff'/(e['leaseToken']+'.json'))['state']!='research_resume_verified':raise RuntimeError('GPU return required')
 script=read(ROOT/'projects/game-lighting-history-04/script/physical-part1-protected-onsets.ko.v211.json')
 literal=read(ROOT/'projects/game-lighting-history-04/script/physical-part1-guided-actions.koen.v175.json')
 jobs=[]
 for take in e['results']:
  ko=' '.join(next(s for s in script['scenes'] if s['id']==take['id'])['lines'])
  en=next(s for s in literal['scenes'] if s['id']==take['id'])['en']
  jobs.append(dict(label='whole-protected-'+take['id'],mode='whole',sources=[dict(id=take['id'],path=take['path'],sha256=take['sha256'],sampleRange=[0,take['samples']],ko=ko,en=en,kind='temporary-lead-in-plus-literal')]))
"""
source=source[:start]+replacement+source[end:]
source=source.replace('part1-onset-replacement-asr-execution-v209','part1-protected-onsets-asr-execution-v214').replace('part1-onset-replacement-asr-v209','part1-protected-onsets-asr-v214').replace('review-part1-onset-replacements-v209.py','review-part1-protected-onsets-v214.py').replace('expectedWindows=5','expectedWindows=2').replace("+'/5'","+'/2'").replace('five-replacement-windows-complete-awaiting-direct-review','two-protected-utterances-complete-awaiting-direct-review')
exec(compile(source,str(__file__),'exec'))
