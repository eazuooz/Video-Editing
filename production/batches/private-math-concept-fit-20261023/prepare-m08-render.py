from common import *
def adapt(s):return s.replace('M06','M08').replace('m06','m08').replace('game-math-quaternion-calculations-v3','game-math-rotation-conversions-v2')
s=adapt((B/'render-m06.py').read_text(encoding='utf8')).replace("sha(B/'m05-scenes.py')","sha(B/'m05-scenes.py')+sha(B/'m06-scenes.py')")
(B/'render-m08.py').write_text(s,encoding='utf8')
(B/'preflight-m08.py').write_text(adapt((B/'preflight-m06.py').read_text(encoding='utf8')),encoding='utf8')
for name in ['m08-scenes.py','render-m08.py','preflight-m08.py']:compile((B/name).read_text(encoding='utf8'),name,'exec')
print('M08 render scripts ready; no third concurrent renderer started')
