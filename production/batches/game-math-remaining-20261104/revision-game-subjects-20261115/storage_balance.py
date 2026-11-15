"""Storage for this finite render: prior authorized uploaded-local cleanup.

Only redundant Clean copies of M05–M20 (or separately selected M03/M04) qualify. Every corresponding
captioned master stays locally, along with all source/narration and M21–M33.
No online mutation and no reliance on an inferred current cloud visibility.
"""
from subject_revision import *
import psutil

RECEIPT=ROOT/'production/batches/private-math-publishing-20261026/checkpoint.json'
AUDIT=HERE/'redundant-uploaded-clean-audit.json'
IDS={f'M{i:02}' for i in range(5,21)}

def used_paths(obj):
 if isinstance(obj,dict):return set().union(*(used_paths(v) for v in obj.values())) if obj else set()
 if isinstance(obj,list):return set().union(*(used_paths(v) for v in obj)) if obj else set()
 if isinstance(obj,str) and obj.lower().endswith(('.mp4','.wav','.mkv','.mov')):
  return {str(Path(obj).resolve()).replace('\\','/').lower()}
 return set()

def stream(f):
 return json.loads(subprocess.check_output([str(FF.with_name('ffprobe.exe')),'-v','error','-select_streams','v:0','-show_entries','stream=width,height,nb_frames,r_frame_rate,duration','-of','json',str(f)],creationflags=prior.CREATE))['streams'][0]

def audit():
 entries=read(RECEIPT)['entries'];rows=[];skips=[];protected=used_paths(list(EPISODES.values()))|used_paths(read(OLD/'game-additions.json'))|used_paths(read(HERE/'sources.json'))
 for item in entries:
  if item['id'] not in IDS:continue
  alias=ROOT/'output'/(item['slug']+'-actual-abstract-v6')/(item['slug']+'.captioned.mp4')
  cap=Path(item['file']).resolve();clean=cap.with_name(cap.name.replace('.captioned.mp4','.clean.mp4'))
  try:
   assert item.get('hdProcessed') and item.get('scheduleVerified')
   assert Path(item['file']).absolute()==alias.absolute(),'Unexpected workspace delivery alias'
   migrated=Path(os.environ['USERPROFILE'])/'.codex/video-render-cache/private-math-abstracts-20261025/deliveries'/item['slug']
   assert cap.parent in (alias.parent,migrated.resolve()),'Unexpected resolved delivery outside its exact workspace/cache folder'
   assert clean.parent==cap.parent and clean!=cap and not clean.is_symlink() and clean.exists()
   assert not clean.samefile(cap),'Clean is a hardlink to retained captioned master; no storage to reclaim'
   assert str(clean).replace('\\','/').lower() not in protected
   assert not any(e['slug'] in clean.parent.name for e in EPISODES.values())
   assert sha(cap)==item['sha256'],'Captioned file no longer equals actual upload receipt'
   needle=str(clean).replace('\\','/').lower()
   assert not any(needle in ' '.join(p.info['cmdline'] or []).replace('\\','/').lower() for p in psutil.process_iter(['cmdline'])),'In-use file'
   a,b=stream(cap),stream(clean)
   assert all(a[k]==b[k] for k in ('width','height','nb_frames','r_frame_rate'))
   assert abs(float(a['duration'])-float(b['duration']))<.018
   audio=prior.packet_hash(cap,'a');assert prior.packet_hash(clean,'a')==audio
   rows.append(dict(episode=item['id'],slug=item['slug'],workspaceAlias=str(alias.with_name(clean.name)),path=str(clean),bytes=clean.stat().st_size,sha256=sha(clean),pairedCaptioned=str(cap),pairedCaptionedSha256=item['sha256'],uploadVideoId=item['videoId'],uploadReceipt=str(RECEIPT),video=a,audioBitstreamHash=audio))
  except (AssertionError,FileNotFoundError) as error:skips.append(dict(episode=item['id'],reason=str(error)))
 report=dict(status='audited-not-deleted',authorization='User previously requested deletion of local videos/WAVs already uploaded and scheduled/published to free D drive; this narrower cleanup retains every captioned copy and all audio.',eligible=rows,skipped=skips,bytes=sum(r['bytes'] for r in rows),currentM21M33Protected=True,allCaptionedMastersProtected=True,narrationAndFootageProtected=True,platformChanges=False,remoteVisibilityNotInferred=True)
 save(AUDIT,report);print(len(rows),'verified redundant Clean copies;',round(report['bytes']/2**30,2),'GiB; no deletion yet')

def apply():
 report=read(AUDIT);assert report['status']=='audited-not-deleted'
 report['freeBefore']={drive:shutil.disk_usage(drive+'/').free for drive in ('C:','D:')}
 for row in report['eligible']:
  clean=Path(row['path']).resolve();cap=Path(row['pairedCaptioned']).resolve()
  alias=ROOT/'output'/(row['slug']+'-actual-abstract-v6')/(row['slug']+'.clean.mp4')
  migrated=Path(os.environ['USERPROFILE'])/'.codex/video-render-cache/private-math-abstracts-20261025/deliveries'/row['slug']
  assert Path(row['workspaceAlias']).absolute()==alias.absolute() and alias.resolve()==clean
  assert clean.parent in (alias.parent,migrated.resolve())
  assert clean.name.endswith('.clean.mp4') and cap.name.endswith('.captioned.mp4') and clean.parent==cap.parent
  assert sha(cap)==row['pairedCaptionedSha256'] and sha(clean)==row['sha256']
  assert not any(e['slug'] in clean.parent.name for e in EPISODES.values())
  needle=str(clean).replace('\\','/').lower()
  assert not any(needle in ' '.join(p.info['cmdline'] or []).replace('\\','/').lower() for p in psutil.process_iter(['cmdline']))
  clean.unlink();row['status']='redundant-clean-removed-captioned-retained';save(AUDIT,report)
 report['status']='redundant-clean-copies-pruned-all-captioned-retained'
 report['freeAfter']={drive:shutil.disk_usage(drive+'/').free for drive in ('C:','D:')};save(AUDIT,report)
 print('Reclaimed',round(report['bytes']/2**30,2),'GiB in workspace delivery cache; every captioned master, current thirteen, narration and original recording retained')

if __name__=='__main__':
 import sys
 if '--rotation-redundancy' in sys.argv:
  IDS={'M03-original','M04'};AUDIT=HERE/'redundant-uploaded-rotation-clean-audit.json'
 apply() if '--apply' in sys.argv else audit()
