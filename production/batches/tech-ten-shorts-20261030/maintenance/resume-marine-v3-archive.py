"""Resume only the already prepared Marine-v3 archive prerequisite after the game exits."""
from pathlib import Path
import importlib.util, sys
B=Path('D:/Github/VideoEditing/production/batches/tech-ten-shorts-20261030');sys.path.insert(0,str(B))
spec=importlib.util.spec_from_file_location('runner',B/'run-batch.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
slug='shorts-starcraft2-marine-random-firing-delay';ctx=r.make_context(slug);ctx['guard']();local=ctx['LOCAL'].resolve();folder=local/'label-v3-preparation';prepared=r.read(folder/'prepared.json')
assert prepared['newFingerprint']==r.fingerprints(ctx['P'])
assert not(folder/'native-archive-receipt.json').exists()
original=local/'unity-capture';archive=folder/'native-v2-preserved'
assert original.resolve()==local/'unity-capture' and archive.resolve().parent==folder.resolve() and not archive.exists()
rows=r.read(folder/'native-v2-original-tree.json');assert sorted(str(p.resolve()) for p in original.rglob('*') if p.is_file())==sorted(x['path'] for x in rows)
with r.SerialJobLock(slug,'prepare-native-archive'):
 r.safe_resources(ctx,'prepare-native-archive');r.verify(rows);original.rename(archive);mapped=[]
 for item in rows:
  target=archive/Path(item['path']).relative_to(original);r.verify([{**item,'path':str(target)}]);mapped.append({'originalPath':item['path'],'archivedPath':str(target),'bytes':item['bytes'],'sha256':item['sha256']})
 prior=r.read(local/'label-v2-preparation/native-archive-receipt.json')
 for item in prior['preservedFiles']:r.verify([{'path':item['archivedPath'],'bytes':item['bytes'],'sha256':item['sha256']}])
 source=r.read(ctx['P']/'production/label-v3-source-manifest.json')
 r.save(folder/'native-archive-receipt.json',{'slug':slug,'archivedAt':r.now(),'variantSourceTreeSHA256':source['variantSourceTreeSHA256'],'preservedFiles':prior['preservedFiles']+mapped,'originalReceiptBytesUnmodified':True,'pathRelocationMapRequiredForOriginalReceipt':True,'newNativeCapturePerformed':False})
 state_path=local/'finite-pipeline-v1/state.json';state=r.read(state_path);assert state['fingerprints']==prepared['newFingerprint'];state['pendingNativeArchive'].update(completed=True,archiveReceipt=str(folder/'native-archive-receipt.json'),archiveReceiptSHA256=r.sha(folder/'native-archive-receipt.json'));state['updatedAt']=r.now();r.save(state_path,state)
print('Marine v2 native preserved; v3 capture prerequisite complete. No new capture or readiness approval performed.')
