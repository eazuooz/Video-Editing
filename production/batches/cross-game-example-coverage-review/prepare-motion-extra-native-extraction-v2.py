from pathlib import Path
root=Path('D:/Github/Video-Editing');b=root/'production/batches/cross-game-example-coverage-review'
dst=b/'extract-motion-extra-native-v2.py';assert not dst.exists()
s=(b/'extract-motion-extra-native-v1.py').read_text('utf-8').replace('extra-native-v1','extra-native-v2').replace('extra-native-execution-v1','extra-native-execution-v2')
begin=s.index('sources=[');end=s.index('\nstate=dict(',begin)
replacement="sources=[dict(id='portal40-58',path='shared/output/game-math-part2-full-series/sources/yFRbGppLaUI.mp4',sha256='0d233cfcc3eb86b1e7722d257512ed6cfcc2b6276eac0b349fded54c516843bb',frames=[1199]+[round(t*30000/1001) for t in range(41,59)],ptsStep=1001,timeBase='1/30000',fps=30000/1001)]"
s=s[:begin]+replacement+s[end:]
dst.write_text(s,encoding='utf-8');print('Fresh19 Portal samples worker prepared; previous36 not repeated')
