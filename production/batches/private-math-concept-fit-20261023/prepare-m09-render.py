from common import *
def adapt(s):return s.replace('M06','M09').replace('m06','m09').replace('game-math-quaternion-calculations-v3','game-math-lines-circles-v2')
s=adapt((B/'render-m06.py').read_text(encoding='utf8')).replace("+sha(B/'m05-scenes.py')",'')
(B/'render-m09.py').write_text(s,encoding='utf8');(B/'preflight-m09.py').write_text(adapt((B/'preflight-m06.py').read_text(encoding='utf8')),encoding='utf8')
for name in ['m09-scenes.py','render-m09.py','preflight-m09.py']:compile((B/name).read_text(encoding='utf8'),name,'exec')
print('M09 six replacement diagrams prepared')
