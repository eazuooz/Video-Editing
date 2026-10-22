from common import *
src=R/'output/private-math-source-review/m06.html'
s=src.read_text(encoding='utf8')
a=s.index('<button');b=s.index('<p id="state">',a)
s=s[:a]+'<button data-i="0">M07 cabinet and exit doors · 7–15.5초</button>'+s[b:]
a=s.index('const shots=');b=s.index(';const v=',a)
shots=[dict(id='M07 cabinet and exit doors',source='shared/output/private-math-concept-fit-20261023/sources/escape-simulator-official/ES_LevelEditor_v3.mp4',start=7,end=15.5)]
s=s[:a]+'const shots='+json.dumps(shots)+s[b:]
(src.parent/'m07.html').write_text(s,encoding='utf8')
