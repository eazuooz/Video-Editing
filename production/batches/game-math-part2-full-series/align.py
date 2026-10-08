"""Align spoken Korean math and retain the repository's93% coverage gate.

Normalize written numerals versus spoken numerals without editing audio or ASR
words/timestamps. Review the unnormalized ASR transcript separately for meaning.
"""
from pathlib import Path
import sys,re,json,shutil
ROOT=Path(__file__).resolve().parents[3];slug=sys.argv[1];sys.path.insert(0,str(ROOT/'qwen3-tts'))
import align_project_subtitles as a
original=a.normalized
digits=dict(zip('영일이삼사오육칠팔구','0123456789'))
def number(s):
 if not any(c in s for c in '십백천'):return ''.join(digits[c] for c in s)
 total=0;current=0
 for c in s:
  if c in digits:current=int(digits[c])
  else:total+=(current or 1)*{'십':10,'백':100,'천':1000}[c];current=0
 return str(total+current)
def normalized(s):
 s=s.lower()
 # Current raw read-back writes these fully spoken acronyms as the exact
 # matching Latin letters. Timing normalization only; keep the raw transcript
 # and distinguish reflection, transmission, same-position and two-position models.
 for spoken,latin in [('비에스에스알디에프','bssrdf'),('비알디에프','brdf'),('비티디에프','btdf'),('비에스디에프','bsdf')]:s=s.replace(spoken,latin)
 # Spoken quaternion component/algebra names versus the same Latin labels.
 # Keep signs and multiplication order intact; raw ASR is reviewed separately.
 s=s.replace('더블유','w')
 for spoken,latin in [('아이','i'),('제이','j'),('케이','k')]:
  s=re.sub(r'(?<![가-힣])'+spoken+r'(?=\s|[,.;:]|는|를|지만|와|과|의|곱|$)',latin,s)
 s=re.sub(r'(?<![가-힣])세(?=\s*(?:개|성분))','3',s)
 s=re.sub(r'(?<![가-힣])네(?=\s*(?:성분|숫자|회전))','4',s)
 # Observed read-back spellings of the spoken function names. Preserve the
 # raw ASR and audio; this only matches the same names for caption timing.
 for x,y in [('코사인','cos'),('싸인','sin'),('사인','sin'),('에이탄 투','atan2'),('에이탄투','atan2'),('에이탄2','atan2'),('a탄2','atan2'),('하이폿','hypot'),('하이포트','hypot'),('하이포스','hypot'),('하이팟','hypot'),('마이너스','-'),('루트','sqrt'),('다섯','5'),('셋','3'),('둘','2'),('네 칸','4칸'),('세 칸','3칸'),('엑스','x'),('와이','y'),('제트','z'),('에이','a')]:s=s.replace(x,y)
 s=re.sub(r'(?<![가-힣])알(?=\s|[,.;:]|은|을|의|에|이|와|과|$)','r',s)
 s=re.sub(r'(?<![가-힣])비(?=\s|[,.;:]|를|로|$)','b',s)
 # Geometry read-back writes t/s and metres as Latin labels, and attaches
 # Korean particles to otherwise identical numerals. This is timing-only;
 # a wrong numeral (e.g.1 versus2) still remains a mismatch for raw review.
 s=re.sub(r'알파벳\s+오','알파벳 o',s)
 for spoken,latin in [('티','t'),('에스','s')]:
  s=re.sub(r'(?<![가-힣])'+spoken+r'(?=\s|[,.;:]|가|를|에|는|의|곱|값|$)',latin,s)
 s=s.replace('미터','m')
 s=re.sub(r'(?<![가-힣])([영일이삼사오육칠팔구십백천]+)(?=\s|[,.;:]|도|칸|초|으로|에서|부터|만큼|보다|입니다|이면|이라고|이고|인|을|를|의|이므로|곱|나누기|와|과|로|$)',lambda m:number(m[1]),s)
 # Decimal point only between numerals. A sentence such as "점 변환" is
 # a geometric point, including when it follows the previous joined line.
 s=re.sub(r'(?<=\d)\s+점\s+(?=\d)', '.', s)
 return original(s)
a.normalized=normalized
original_partition=a.partition_fixed
def partition_preserving_normalized_tokens(text,width,count):
 chunks=original_partition(text,width,count)
 whole=normalized(text)
 if ''.join(normalized(c) for c in chunks)==whole:return chunks
 # A decimal phrase such as "오십삼 점 일 삼" must not be cut before 점:
 # it otherwise becomes a geometric-point noun when matched in isolation.
 # Retain every original word and the same bilingual cue count/width gates.
 from functools import lru_cache
 words=text.split();target=sum(a.weight(w) for w in words)/count
 prefix=[normalized(' '.join(words[:i])) for i in range(len(words)+1)]
 @lru_cache(None)
 def solve(start,remaining):
  if not remaining:return (0.,()) if start==len(words) else (float('inf'),())
  best=(float('inf'),())
  for end in range(start+1,len(words)-remaining+2):
   segment=' '.join(words[start:end]);token=normalized(segment)
   if len(a.wrapped_lines(segment,width))>2:break
   if not whole.startswith(prefix[start]+token) or prefix[end]!=prefix[start]+token:continue
   future,rest=solve(end,remaining-1)
   cost=(a.weight(segment)-target)**2+future
   if segment.endswith(('.', '?', '!', ',', ';')):cost-=target**2*.35
   if cost<best[0]:best=(cost,(segment,*rest))
  return best
 score,chunks=solve(0,count)
 if not __import__('math').isfinite(score):raise ValueError('Cannot preserve spoken token boundaries within bilingual caption width')
 assert ' '.join(chunks)==' '.join(words) and ''.join(normalized(c) for c in chunks)==whole
 return list(chunks)
a.partition_fixed=partition_preserving_normalized_tokens
if __name__=='__main__':
 # Selected-scene GPU retakes intentionally defer full assembly. Refresh the
 # current scene origins on CPU before aligning either language; no model load.
 lease=ROOT/'shared/output/GPU_HANDOFF.json'
 if lease.exists():
  state=json.loads(lease.read_text(encoding='utf-8-sig'))
  if state.get('project')==slug and state.get('state')=='tts_running':raise RuntimeError('Finish the current TTS batch before assembling its checkpoints')
 import numpy as np
 import soundfile as sf
 import render_narration as r
 r.np=np;r.sf=sf;r.configure_project(slug);r.assemble_outputs(r.load_jobs())
 sys.argv=[sys.argv[0],'--project',slug];a.main()
 m=json.loads((ROOT/f'projects/{slug}/project.json').read_text(encoding='utf8'))
 for lang in ['ko','en']:shutil.copy2(ROOT/m['paths']['captions'+lang.title()],ROOT/f'projects/{slug}/script/voice-aligned.{lang}.srt')
