from common import *
import importlib.util,zipfile
spec=importlib.util.spec_from_file_location('remotezip',B/'inspect-keen-presskit.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
url='https://teardowngame.com/download/presskit.zip';r=m.RemoteZip(url)
with zipfile.ZipFile(r) as z:items=[dict(name=i.filename,size=i.file_size,compressed=i.compress_size,compression=i.compress_type) for i in z.infolist()]
save(B/'teardown-presskit-inventory.json',dict(checkedAt=now(),officialEntry='https://teardowngame.com/',url=url,archiveBytes=r.size,downloadedBytes=r.bytes,items=items))
print(json.dumps(items,ensure_ascii=False))
