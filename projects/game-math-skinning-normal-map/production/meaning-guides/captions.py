from prepare import *
def main():
 # The recorded genitive after '본' is ambiguous to ASR. Trigger on the
 # immediately following, clearly measured action ("apply the matrix").
 bp=P/'planning/scene-bindings.json';bn=read(bp);row=bn['scenes'][10]
 row['speechPhaseAnchors']=[dict(phrase=p,position=v,character=row['speech'].index(p)) for p,v in ANCHORS[10]]
 for idx,title,ko,meaning in [
  (11,'Bind-to-Current Transform','기준 자세에서 현재 자세로','팔꿈치에 붙은 단추가 새 자세를 따라갑니다'),
  (28,'Tangent Basis from UVs','UV로 찾는 접선 기저','같은 이동을 모델과 UV 삼각형에서 함께 따라갑니다')]:
  bn['scenes'][idx]['shot'].update(englishTerm=title,koreanTerm=ko,meaning=meaning)
 save(bp,bn)
 path=P/'planning/bilingual-caption-map.json';m=read(path)
 for i,rows in ROWS.items():
  groups=[];ki=ei=0
  for k,e in rows:
   n=len(re.split(r'(?<=[.!?])\s+',k));t=len(re.split(r'(?<=[.!?])\s+',e));groups.append(dict(koStart=ki,koCount=n,enStart=ei,enCount=t,ko=k,en=e));ki+=n;ei+=t
  m['scenes'][i]['groups']=groups
 save(path,m)
 path=P/'planning/caption-reading-adjustments.json';j=read(path)
 j['koPrintedForms']={'엔 크로스 티':'N × T','법선 엔':'법선 N','접선 티':'접선 T','법선이 엔':'법선이 N','비탄젠트 비':'비탄젠트 B','비를 바이노멀':'B를 바이노멀','비는 그 부호':'B는 그 부호','더블유 성분':'w 성분','큐 일':'q₁','큐 이':'q₂','에스 일':'s₁','에스 이':'s₂','티 일':'t₁','티 이':'t₂','유의 차이':'u의 차이','브이의 차이':'v의 차이','브이의 증가':'v의 증가','유가 늘어':'u가 늘어','유가 줄어':'u가 줄어','브이가 늘어':'v가 늘어','유 방향':'u 방향','브이 방향':'v 방향','플러스 일 또는 마이너스 일':'＋1 또는 −1','마이너스 일':'−1','유브이':'UV','여덟 비트':'8비트'}
 save(path,j)
if __name__=='__main__':main()

