"""Credit locally retained, cleared game recordings and preserve their exact native ranges."""
from prepare import *
def main():
 sources=read(HERE/'sources.json');plan=read(HERE/'plan.json')
 files=subprocess.check_output(['rg','--files','projects','shared/output/game-math-part2-full-series','production/batches/game-math-remaining-20261104','-g','*info.json'],cwd=ROOT,text=True).splitlines()
 used={s['source'] for e in plan['episodes'] for s in e['inserts']};evidence=[]
 offsets={'showroom':20,'beam':744,'maker':2960,'galaxy':480}
 for key in sorted(used):
  row=sources[key];sid=row['sourceId'];found=[]
  for p in files:
   if pathlib.Path(p).name.startswith(sid):found.append(ROOT/p)
  assert found,(key,sid,'metadata missing')
  meta=read(found[0]);assert meta['id']==sid
  license=meta.get('license');description=meta.get('description','');title=meta.get('title','')
  assert license and 'creative commons' in license.lower() or any(w in (title+' '+description).lower() for w in ('free to use','freetousegameplay','free-to-use')),(key,'no recorded reuse evidence')
  ranges=[dict(episode=e['id'],key=s['key'],localStart=s['sourceIn'],localEnd=s['sourceOut'],originalStart=s['sourceIn']+offsets.get(key,0),originalEnd=s['sourceOut']+offsets.get(key,0)) for e in plan['episodes'] for s in e['inserts'] if s['source']==key]
  evidence.append(dict(source=key,sourceSha256=row['sha256'],game=row['game'],url='https://www.youtube.com/watch?v='+sid,title=title,uploader=meta.get('uploader'),license=license,permission='Recorded Creative Commons reuse label' if license else 'Recorded explicit free-use description; not relabeled as Creative Commons',metadata=str(found[0]),metadataSha256=sha(found[0]),sourceTimestampOffset=offsets.get(key,0),ranges=ranges,publisherReview='Retains the previously reviewed instructional-game-video/publisher basis from the approved lesson inventory and footage review; no raw game assets redistributed.',changes='Native-speed continuous excerpts, scaled without crop, editorial headings / attention guides and our own teaching voice. No frozen or looped padding.'))
 save(HERE/'source-rights.json',dict(status='existing-source-evidence-verified',sources=evidence,externalSearchRejected='Unrelated music-only no-copyright search results were not treated as game-recording permission or used.',noNewUnlicensedRecordings=True))
 lines=['# 실제 게임 녹화 출처','', '기존 승인된 강의 출처를 이어서 사용합니다. 독립 녹화의 원래 재생 속도를 유지하고 교육용 해설과 표식을 추가했습니다. 게임 내부 공식을 이 영상만으로 측정·확정하지 않습니다.','']
 for x in evidence:lines.extend([f"- **{x['game']}** — {x['title']} / {x['uploader']}  ",f"  {x['url']}  ",f"  {x['license'] or x['permission']}"])
 (HERE/'CREDITS.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
 print('Recorder reuse evidence retained for',len(evidence),'sources')
if __name__=='__main__':main()
