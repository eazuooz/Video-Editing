"""V8 timing-only numeral/label equivalents; never an audio-content repair."""
import re,unicodedata
DIGITS=dict(zip('영일이삼사오육칠팔구',range(10)))
def korean_number(s):
 s=s.replace(' ','')
 if s.isdecimal():return int(s)
 for label,scale in [('억',100000000),('만',10000)]:
  if label in s:
   left,right=s.split(label,1)
   return (korean_number(left)if left else 1)*scale+(korean_number(right)if right else 0)
 if not any(c in s for c in '십백천'):return int(''.join(str(DIGITS[c])if c in DIGITS else c for c in s))
 total=0;current=0
 for ch in s:
  if ch in DIGITS:current=DIGITS[ch]
  elif ch.isdecimal():current=current*10+int(ch)
  else:total+=(current or 1)*{'십':10,'백':100,'천':1000}[ch];current=0
 return total+current
def normalized(text):
 s=unicodedata.normalize('NFKC',text).lower()
 # Latin read-back of the exact same spoken labels; no Euler/axis-angle
 # material, guessed engine coordinates or wrong-number substitutions.
 for a,b in [('orientation','오리엔테이션'),('attitude','애티튜드'),('object','오브젝트'),('upright','업라이트'),
  ('direction','디렉션'),('cosine','코사인'),('matrix','매트릭스'),('space','스페이스'),('prime','프라임'),
  ('api','에이피아이'),('mocap','모션캡처'),('byte','바이트'),('cos','코사인')]:s=s.replace(a,b)
 # ASR renders a spoken prime either as the word or as an apostrophe.
 s=re.sub(r"\b([pqr])\s*['′]",r'\1 프라임',s)
 s=re.sub(r'(?<=\d)\s*[x×]\s*(?=\d)','곱하기',s)
 for a,b in [('x','엑스'),('y','와이'),('z','제트'),('p','피'),('q','큐'),('r','알'),('a','에이'),('b','비'),('c','씨')]:
  s=re.sub(r'(?<![a-z])'+a+r'(?![a-z])',b,s)
 for a,b in [('열다섯','15'),('열두','12'),('아홉','9'),('여섯','6'),('다섯','5'),('사분의','4분의'),('이분의','2분의')]:s=s.replace(a,b)
 s=re.sub(r'오브젝트\s*2\s*업라이트','오브젝트 투 업라이트',s)
 s=re.sub(r'업라이트\s*2\s*오브젝트','업라이트 투 오브젝트',s)
 s=re.sub(r'(?<![가-힣])세(?=\s*(?:개|가지|기준|축|행|줄|성분|변화))','3',s)
 s=re.sub(r'(?<![가-힣])두(?=\s*(?:개|가지|축|행|줄|성분|변화|공간|방향|좌표계|벡터|길이))','2',s)
 # Converting a spaced compound numeral is intentionally atomic. Caption
 # splitting must test normalized prefix/substring additivity and must never
 # divide e.g. 십육만 이천 in the middle of that numeral.
 s=re.sub(r'(?<![가-힣0-9])([0-9영일이삼사오육칠팔구십백천만억]+(?:\s+[0-9영일이삼사오육칠팔구십백천만억]+)*)(?=\s|[,.;:]|도|개|칸|초|으로|에서|부터|만큼|보다|입니다|이면|이라고|이고|인|을|를|의|이므로|곱|나누기|와|과|로|바이트|킬로|비트|분의|$)',lambda m:str(korean_number(m[1])),s)
 s=re.sub(r'(?<=\d)\s*점\s*(?=\d)','. ',s)
 s=re.sub(r'(\d+)\s*/\s*(\d+)',r'\2분의\1',s)
 s=s.replace('마이너스','minus').replace('−','minus').replace('-','minus').replace('+','플러스')
 return re.sub('[^가-힣a-z0-9]','',s)
