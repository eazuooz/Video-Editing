"""Read-only FBX structure/provenance check. Does not invoke Unity or import assets."""
from pathlib import Path
import struct,zlib,json,hashlib,collections
P=Path(__file__).resolve().parent;ROOT=P.parents[3]
asset=ROOT/'unity/VideoEditing/Assets/ThirdParty/KayKitAdventurers'
data=(asset/'Knight.fbx').read_bytes();version=struct.unpack_from('<I',data,23)[0]
assert data.startswith(b'Kaydara FBX Binary'), 'Expected binary FBX'
header='<QQQB' if version>=7500 else '<IIIB';hs=struct.calcsize(header)
def prop(pos):
 typ=chr(data[pos]);pos+=1
 sizes={'Y':('h',2),'C':('?',1),'I':('i',4),'F':('f',4),'D':('d',8),'L':('q',8)}
 if typ in sizes:
  fmt,n=sizes[typ];return struct.unpack_from('<'+fmt,data,pos)[0],pos+n
 if typ in 'SR':
  n=struct.unpack_from('<I',data,pos)[0];raw=data[pos+4:pos+4+n];return raw.decode('utf8',errors='replace') if typ=='S' else None,pos+4+n
 if typ in 'fdilbc':
  n,enc,length=struct.unpack_from('<III',data,pos);start=pos+12;end=start+length
  raw=data[start:end];raw=zlib.decompress(raw) if enc else raw
  fmt={'f':'f','d':'d','i':'i','l':'q','b':'b','c':'b'}[typ]
  return struct.unpack('<'+str(n)+fmt,raw),end
 raise ValueError(typ)
def node(pos):
 end,n,bytes_,namelen=struct.unpack_from(header,data,pos)
 if end==0:return None,pos+hs
 pos+=hs;name=data[pos:pos+namelen].decode();pos+=namelen;props=[]
 for _ in range(n):
  value,pos=prop(pos);props.append(value)
 children=[]
 while pos<end-hs:
  child,pos=node(pos)
  if child is None:break
  children.append(child)
 return {'name':name,'p':props,'c':children},end
top=[];pos=27
while pos<len(data)-hs:
 n,pos=node(pos)
 if n is None:break
 top.append(n)
objects=next(n['c'] for n in top if n['name']=='Objects')
models={n['p'][0]:n for n in objects if n['name']=='Model'}
connections=next(n['c'] for n in top if n['name']=='Connections')
clusters=[n for n in objects if n['name']=='Deformer' and n['p'][-1]=='Cluster']
byid={n['p'][0]:n for n in objects if n['p'] and isinstance(n['p'][0],int)}
name=lambda n:n['p'][1].split('\x00')[0]
cluster_results=[]
for c in clusters:
 childs={n['name']:n['p'] for n in c['c']};idx=childs.get('Indexes',[()])[0];w=childs.get('Weights',[()])[0]
 links=[n['p'][1] for n in connections if len(n['p'])>=3 and n['p'][2]==c['p'][0] and n['p'][1] in models]
 cluster_results.append({'boneNames':[name(models[x]) for x in links],'vertexInfluences':len(idx),'weightMin':min(w) if w else None,'weightMax':max(w) if w else None,'fractionalWeightCount':sum(1 for x in w if 1e-5<x<.99999)})
cluster_results=[c for c in cluster_results if c['vertexInfluences']>0]
provenance=json.loads((asset/'provenance.json').read_text())
report={'status':'binary-structure-inspected-not-Unity-runtime-validation','fbxVersion':version,'assetGuid':'274e91da352f3104c8313348b836daf7','source':provenance,'hashVerification':[{ 'file':f['path'],'matches':hashlib.sha256((asset/f['path']).read_bytes()).hexdigest()==f['sha256']} for f in provenance['files']], 'boneNames':[name(n) for n in models.values() if n['p'][-1]=='LimbNode'],'animationStacks':[name(n) for n in objects if n['name']=='AnimationStack'],'clusters':cluster_results,'pending':['Imported clip names/durations and motion','SkinnedMeshRenderer bone order and bindposes','Readable mesh copy in isolated project','Material/culling/glyph/caption/mobile QA']}
(P/'rig-source-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'hashVerification':report['hashVerification'],'boneCount':len(report['boneNames']),'clipCount':len(report['animationStacks']),'nonemptyClusters':sum(c['vertexInfluences']>0 for c in cluster_results),'fractionalWeights':sum(c['fractionalWeightCount'] for c in cluster_results)},ensure_ascii=False,indent=2))
