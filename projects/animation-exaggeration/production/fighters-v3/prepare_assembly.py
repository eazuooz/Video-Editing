"""Reuse checked PCM/caption assembly without changing the delivered revision."""
from pathlib import Path
H=Path(__file__).resolve().parent;old=H.parent/'fighters-v2'
s=(old/'build_revision.py').read_text(encoding='utf-8').split(' # Actual gameplay and retained exact native implementation captures.')[0]
s=s.replace('fighters-v2','fighters-v3').replace('additional-sample-b.wav','additional-qwen.wav')
a=s.index(' # Measured silent gaps:');b=s.index(' insert_at=',a)
s=s[:a]+" bounds=load(H/'qwen-voice-record.json')['boundsFrames']\n"+s[b:]
s=s.replace("aliases={'킹오프파이터스15':'킹오브파이터즈피프틴','쏠도':'솔도'}","aliases={'킹오브파이터즈15':'킹오브파이터즈피프틴','킹오브파이터스15':'킹오브파이터즈피프틴','길티기어스트라이브':'길티기어스트라이브','셜미':'셸미','쉘미':'셸미'}")
s+=" from build_cut_plan import build\n build(baseline,inserts,total,body,out)\n print('Assembly prepared',total/60,'seconds',len(out),'caption cues')\nif __name__=='__main__':main()\n"
(H/'build_revision.py').write_text(s,encoding='utf-8')
s=(old/'annotate_and_mix.py').read_text(encoding='utf-8')
s=s.replace('fighters-v2','fighters-v3');a=s.index(' for cid in');b=s.index(" source=L/'edit/final-mix.wav'")
s=s[:a]+s[b:];s=s.replace("print('Three source-anchored guides and measured delivery normalization prepared.')","print('Measured delivery normalization prepared.')")
(H/'normalize_mix.py').write_text(s,encoding='utf-8')
print('Voice assembly and normalization helpers prepared')
