"""Selected V6 timing aliases only; preserve raw speech and recognition text.

Install after the existing math helper. This is not a pronunciation approval
or a replacement for direct text review; meanings/signs/numerals stay checked
against the untouched full transcripts.
"""
import re
ALIASES=[
 ('엑스트린식 로테이션','extrinsic rotation'),('인트린식 로테이션','intrinsic rotation'),
 ('액시스 앵글 리프리젠테이션','axis angle representation'),('오리엔테이션','orientation'),
 ('랩 파이','wrappi'),('reppi','wrappi'),('리메인더','remainder'),('remain the','remainder'),
 ('에프모드','fmod'),('f모드','fmod'),('소문자 이','소문자 e'),
 ('기술을','기수를'),
 ('세타','theta'),('θ','theta'),('파이','pi'),('π','pi'),('타우','tau'),('타오','tau'),('τ','tau')]
def install(helpers):
 base=helpers['normalized']
 def normalized(text):
  text=text.lower()
  for source,target in ALIASES:text=text.replace(source,target)
  text=re.sub(r'(?<![가-힣])엔(?=\s|으로|에|이라는|을|$)','n',text)
  text=re.sub(r'아홉(?=\s*(?:칸|숫자))','9',text)
  text=re.sub(r'(?<![가-힣])([영일이삼사오육칠팔구십백천]*[십백천][영일이삼사오육칠팔구십백천]*)(?=에)',lambda m:helpers['number'](m[1]),text)
  text=re.sub(r'양해(?=\s*\d+\s*도)','양의',text)
  text=re.sub(r'회전으로\s+익습니다','회전으로 읽습니다',text)
  text=re.sub(r'중간\s+움직임도\s+이도와','중간 움직임도 의도와',text)
  text=re.sub(r'소문자\s*2(?=입니다|\s|$)','소문자 e',text)
  return base(text)
 helpers['a'].normalized=normalized
 return normalized
