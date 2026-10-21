"""Finite original-clock full render, with unchanged recovered audio packets."""
import shutil
import common as c
DEST=c.R/'output/game-math-euler-axis-angle-private-polish'
NAME='game-math-euler-axis-angle'

def preserve_full_audio():
 # A frame-limited encoding pass can omit the final AAC packet. This lossless
 # mux has no frame/shortest limit and retains the complete recovered audio.
 c.authorized()
 for kind in ['clean','captioned']:
  path=DEST/f'{NAME}.{kind}.mp4';temp=DEST/f'{NAME}.{kind}.mux-tmp.mp4'
  c.ff(['-i',path,'-i',c.O/'baseline-audio.m4a','-map','0:v:0','-map','1:a:0',
        '-map_metadata','0','-c','copy','-movflags','+faststart',temp],f'full-audio-{kind}.log')
  temp.replace(path)

def main():
 c.authorized();DEST.mkdir(parents=True,exist_ok=True)
 order=[('intro',120)]+[(s['id'],s['frames']) for s in c.T['scenes']]+[('outro',600)]
 assert sum(n for _,n in order)==c.T['frames']==67885
 records=[]
 for sid,n in order:
  path=c.O/'clips'/f'{sid}.mp4';v=c.video(path)
  assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1920,1080,'60/1',n),(sid,v)
  records.append({'scene':sid,'frames':n,'file':c.rel(path),'sha256':c.sha(path)})
 concat=c.O/'concat.txt';concat.write_text('\n'.join("file '"+(c.R/r['file']).as_posix()+"'" for r in records)+'\n',encoding='utf8')
 inputs={'timelineSha256':c.sha(c.P/'production/timeline.json'),'scenes':records,
   'audioSha256':c.sha(c.O/'baseline-audio.m4a'),'captionAssSha256':c.sha(c.O/'captions.ko.ass')}
 c.save(c.H/'assembly.json',inputs)
 graph='[0:v]settb=expr=1/60,setpts=N,setsar=1,split=2[vclean][vin];[vin]ass=captions.ko.ass[vcaptioned]'
 args=['-reinit_filter','0','-f','concat','-safe','0','-i',concat,'-i',c.O/'baseline-audio.m4a','-filter_complex',graph]
 for kind in ['clean','captioned']:
  args+=['-map',f'[v{kind}]','-map','1:a','-frames:v',c.T['frames'],*c.ENC,
         '-color_range','tv','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709',
         '-c:a','copy',DEST/f'{NAME}.{kind}.mp4']
 c.ff(args,'full-pair.log',c.O)
 preserve_full_audio()
 for lang in ['ko','en']:shutil.copy2(c.O/f'captions.{lang}.srt',DEST/f'{NAME}.{lang}.srt')
 outputs=[]
 for path in sorted(DEST.glob(NAME+'.*')):
  if path.suffix not in ['.mp4','.srt']:continue
  row={'path':c.rel(path),'sha256':c.sha(path),'bytes':path.stat().st_size}
  if path.suffix=='.mp4':
   v=c.video(path);assert int(v['nb_frames'])==67885;row['video']=v
  outputs.append(row)
 c.save(c.H/'outputs.json',{'revision':'private-baseline-visual-polish-v1','outputs':outputs,
  'durationSeconds':c.T['seconds'],'frames':67885,'fullReviewStatus':'internal-QA-in-progress','humanReview':'pending',
  'noUpload':True,'originalUploadedVersionPreserved':True})
 (DEST/'index.html').write_text('''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>게임수학 · 기존 강의 시각 보강</title>
<style>body{max-width:1100px;margin:36px auto;padding:0 20px;background:#121915;color:#f6f8f6;font:18px/1.65 system-ui}h1{font-size:30px;color:#ffdf73}a{color:#8cdbbc}video{width:100%;background:#000}nav{display:flex;gap:24px;flex-wrap:wrap;margin:20px 0}small{color:#becbc2}button{background:#233a2c;color:white;border:1px solid #608771;border-radius:5px;padding:8px 14px;font:inherit;cursor:pointer}.chips{display:flex;gap:8px;flex-wrap:wrap}</style>
<h1>오일러 각과 축·각 — 기존 강의 시각 보강</h1><p>원래 대본·음성·26개 장면·18분 51.4초의 순서를 유지했습니다. 실제 게임의 관찰 표식, Unity 회전 모형, 코드 가독성을 보강했습니다.</p>
<video id="v" controls preload="metadata" src="game-math-euler-axis-angle.captioned.mp4"></video>
<nav><a href="game-math-euler-axis-angle.captioned.mp4">전체 자막 영상</a><a href="game-math-euler-axis-angle.clean.mp4">무자막 영상</a><a href="game-math-euler-axis-angle.ko.srt" download>한국어 자막</a><a href="game-math-euler-axis-angle.en.srt" download>영어 자막</a></nav>
<div class="chips"><button data-t="42">게임 위 안내선</button><button data-t="112">몸체 축 회전</button><button data-t="267">회전 순서 비교</button><button data-t="384">짐벌락</button><button data-t="595">코드 색과 현재 줄</button><button data-t="716">축·각</button><button data-t="840">중심점과 위치 변화</button></div>
<p><a href="../../docs/GAME_MATH_PRIVATE_POLISH.md">17편 작업 진행표</a></p><small>1920×1080 · 60fps. 새 TTS 없이 기존 업로드에서 복구한 압축 음성을 사용했습니다. 원본 PCM과 동일하다는 뜻은 아닙니다. 기존 업로드는 그대로 보존했으며, 이 수정본은 로컬 검수용입니다.</small>
<script>document.querySelectorAll('button').forEach(b=>b.onclick=()=>{v.currentTime=Number(b.dataset.t);v.play()})</script></html>''',encoding='utf8')
 print('Full clean/captioned pair and original bilingual captions ready for QA.',flush=True)

if __name__=='__main__':main()
