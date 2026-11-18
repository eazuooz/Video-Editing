"""Replace only order2 in the immutable prior exact12 review manifest/page."""
from pathlib import Path
import argparse,copy,hashlib,html,json,re
H=Path(__file__).resolve().parent;M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def pin(p):
 p=Path(p)
 with p.open('rb')as f:return dict(path=str(p.resolve()),sha256=hashlib.file_digest(f,'sha256').hexdigest(),bytes=p.stat().st_size)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--mobile-url',required=True);a=ap.parse_args();assert a.mobile_url.startswith('https://drive.google.com/file/d/')
 oldp=H/'local-final-review-manifest-v5.json';old=read(oldp);d=copy.deepcopy(old);bp=M/'shorts-mario64-lakitu-camera/camera-paired-v164/local-review-v6-r171/bundle-v6.json';b=read(bp);assert b['localFinalBundleComplete']and b['titleKo']=='3D 게임의 판도를 바꾼 마리오64'
 files={k:pin(r['path'])for k,r in b['artifacts'].items()}
 for k,r in files.items():assert r['sha256']==b['artifacts'][k]['sha256']
 row=d['projects'][1];oldtitle=row['titleKo'];row.update(titleKo=b['titleKo'],version=b['version'],bundle=pin(bp),artifacts=files,actualMixSeconds=93.2,checks=dict(newTechnicalEvidence=b['evidence'],sameAcceptedVoiceAndBgmAac=True,actualNewFixedCameraUnity=True,actualRealtimePlayback=False,actualFullListening=False,humanApproval=False),mobileReviewUrl=a.mobile_url)
 d.update(schemaVersion=6,selectedRevision='order2-title-and-simultaneous-fixed-player-camera',previousDeliveredManifest=pin(oldp),selectedOrders=[2],preservedOrders=[1,3,4,5,6,7,8,9,10,11,12],completedSelectedRevisions=1,pendingSelectedRevisions=0,request=pin(H/'user-camera-paired-revision-v164.json'),mobileSelectedRevisionUrl=a.mobile_url,allArtifactHashesVerified=True,deliveryPostedInChat=False)
 assert all(d['projects'][i]==old['projects'][i]for i in range(12)if i!=1)
 for r in d['projects']:
  for f in r['artifacts'].values():assert pin(f['path'])['sha256']==f['sha256']
 mp=H/'local-final-review-manifest-v6.json';assert not mp.exists();mp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
 E=html.escape;uri=lambda p:Path(p).as_uri();text=(H/'local-final-review-v5.html').read_text('utf8');text=text.replace('검수표 v5','검수표 v6').replace(oldtitle,b['titleKo'])
 text=text.replace('2번: 바이오하자드2 원작의 고정 카메라와 마리오64의 카메라 조작 비교. 전12편: 배경음악 음량 수정.','2번: 새 제목과 실제 게임·Unity 좌우 카메라 비교를 반영했습니다. 기존 음성·배경음악과 나머지11편은 보존했습니다.')
 text=text.replace('<p><a class="button" href="'+old['mobileFolder']+'">폰으로 수정본12편 열기</a></p>','<p><a class="button" href="'+E(a.mobile_url)+'">폰으로 최신2번 좌우 비교본 보기</a></p><p><a href="'+old['mobileFolder']+'">기존12편 폰 검수 폴더</a> · 이 폴더의 이전2번은 보존돼 있습니다.</p>')
 section=f'<section id="v2"><h2>02. {E(b["titleKo"])}</h2><p class="tag">{E(b["version"])} · 93.20초 · 1080×1920 / 60fps · 사람 검수 대기</p><p><a class="button" href="{E(a.mobile_url)}">폰으로 이 수정본 보기</a></p><video controls playsinline preload="none" src="{E(uri(files["captioned"]["path"]))}"></video><p>같은 캐릭터와 장면을 고정 구도와 시점 조작으로 나란히 비교합니다. 실제 게임 비교와 자체 Unity 시연을 구분해 표시했습니다.</p><p>'
 labels=dict(clean='클린 영상',subtitlesKo='KO 자막',subtitlesEn='EN 자막',metadataKo='KO 제목·설명',metadataEn='EN 제목·설명');section+=' · '.join(f'<a href="{E(uri(files[k]["path"]))}">{v}</a>'for k,v in labels.items());section+='</p><details><summary>파일 버전·SHA256</summary>'
 for k,f in files.items():section+=f'<p>{k} · {f["bytes"]:,} bytes<br><code>{f["sha256"]}</code></p>'
 section+='</details><p><a href="#v3">다음 영상으로</a></p></section>'
 text,count=re.subn(r'<section id="v2">.*?</section>',lambda _:section,text,count=1,flags=re.S);assert count==1
 text=text.replace(uri(oldp),uri(mp)).replace(uri(H/'local-final-review-v4.html'),uri(H/'local-final-review-v5.html')).replace('이전 검수표 v4','이전 검수표 v5');p=H/'local-final-review-v6.html';assert not p.exists();p.write_text(text,'utf8');print(json.dumps(dict(page=pin(p),manifest=pin(mp),onlyOrder2Revised=True,otherElevenPreserved=True)))
if __name__=='__main__':main()
