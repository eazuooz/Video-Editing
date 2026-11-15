"""Bind only approved-voice surgical edits and guided observation takes."""
from common import *
import shutil

def main():
 records=read(HERE/'narration-changes.json')['records']
 ids={'A04-gameplay-041','A05-gameplay-018','A16-gameplay-020','A16-gameplay-041','A18-gameplay-047'}
 for r in records:
  if r['id'] not in ids:continue
  source=HERE/'local/screen-match-voice/chunks'/(r['id']+'-scene.wav');assert source.is_file(),source
  target=HERE/'local/voice/chunks'/source.name
  if target.exists() and sha(target)!=sha(source):
   archive=HERE/'local/voice/superseded'/('pre-screen-match-'+target.name);archive.parent.mkdir(exist_ok=True)
   if not archive.exists():shutil.copy2(target,archive)
  if not target.exists() or sha(target)!=sha(source):shutil.copy2(source,target)
 layout_ids={'A08-gameplay-035','A10-gameplay-050','A11-gameplay-040','A16-gameplay-027'}
 for r in records:
  if r['id'] not in layout_ids:continue
  source=HERE/'local/layout-match-voice/chunks'/(r['id']+'-scene.wav');assert source.is_file(),source
  target=HERE/'local/voice/chunks'/source.name
  if target.exists() and sha(target)!=sha(source):
   archive=HERE/'local/voice/superseded'/('pre-layout-match-'+target.name);archive.parent.mkdir(exist_ok=True)
   if not archive.exists():shutil.copy2(target,archive)
  if not target.exists() or sha(target)!=sha(source):shutil.copy2(source,target)
 rows=[]
 for r in records:
  p=HERE/'local/voice/chunks'/(r['id']+'-scene.wav');assert p.is_file(),p
  rows.append(dict(id=r['id'],text=r['ko'],file=str(p),sha256=sha(p),kind='screen-matched-replacement'))
 for r in read(HERE/'guidance-changes.json')['records']:
  p=Path(r['audioFile']);assert p.is_file(),p
  rows.append(dict(id=r['id'],text=r['ko'],file=str(p),sha256=sha(p),kind='observation-guidance'))
 assert len(rows)==55
 save(HERE/'voice-index.json',dict(scope='39 screen-matched clause replacements and16 guided observation paragraphs; preserve baseline speech elsewhere.',
  aggregateFirstPassUnused=True,records=rows,voice='Approved Qwen3 clone; transcript-assisted15–35s reference; CPU4 while sharing',
  speechTimeCompression=False,actualMixReadback='pending',updatedAt=stamp()))
 print('Bound',len(rows),'voice takes')
if __name__=='__main__':main()
