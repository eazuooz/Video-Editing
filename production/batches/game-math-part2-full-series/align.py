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
if __name__=='__main__':
 sys.argv=[sys.argv[0],'--project',slug];a.main()
 m=json.loads((ROOT/f'projects/{slug}/project.json').read_text(encoding='utf8'))
 for lang in ['ko','en']:shutil.copy2(ROOT/m['paths']['captions'+lang.title()],ROOT/f'projects/{slug}/script/voice-aligned.{lang}.srt')
