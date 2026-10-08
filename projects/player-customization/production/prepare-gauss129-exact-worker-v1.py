"""Prepare a guarded worker for only the newly obtained source."""
from pathlib import Path
root=Path(__file__).resolve().parent
p=root/'inspect-gauss129-exact-crop-v1.py'
assert not p.exists()
s=(root/'inspect-yareli155-exact-crop-v1.py').read_text('utf-8')
changes={
 'yareli155':'gauss129','exact-yareli':'exact-gauss',
 'yareli-devstream155-v1/8eUfnQ8mWXs-yareli-2721-3087.mp4':'gauss-devstream129-v1/h7qntXMufKk-gauss-2244-2683.mp4',
 "windows=[[112,138],[142,154],[157,164],[169,191],[208,212],[218,236],[239,247],[273,282]]":"windows=read(BASE/'gauss129-native-direct-review-v1.json')['candidateInspectionWindows']",
 "sourceVideoId='8eUfnQ8mWXs'":"sourceVideoId='h7qntXMufKk'",
 'crop=dict(x=550,y=25,w=1216,h=684)':'crop=dict(x=426,y=140,w=1440,h=810)',
 'yareli-devstream155-native-v1/native-frame-pts.json':'gauss-devstream129-native-v1/native-frame-pts.json',
 'crop=1216:684:550:25':'crop=1440:810:426:140',
 'sourceSeconds=2721+pts[n]':'sourceSeconds=2244+pts[n]',
 'Yareli155 window':'Gauss129 window'}
for a,b in changes.items():
    assert a in s,a
    s=s.replace(a,b)
assert 'yareli-devstream' not in s and '8eUfnQ8mWXs' not in s
p.write_text(s,'utf-8')
print('Prepared guarded new-source worker; no extraction or approval.')
