from pathlib import Path
R=Path(__file__).resolve().parents[3]
U=R/'unity/VideoEditing/Assets/VideoScenes/distinctive-shorts-20261024'
p=U/'DemoState.cs';s=p.read_text(encoding='utf8').replace('Quaternion.Euler(0,0,-(t<0?before:20))','Quaternion.Euler(0,0,+(t<0?before:20))').replace('Quaternion.Euler(0,0,-angle)','Quaternion.Euler(0,0,+angle)');p.write_text(s,encoding='utf8')
p=U/'Editor/BatchCapture.cs';s=p.read_text(encoding='utf8')
s=s.replace('var g=new GameObject(name);if(parent)', 'var g=new GameObject(name);g.layer=8;if(parent)')
s=s.replace('demo.observer=cam;demo.player=player;', 'demo.observer=cam;demo.player=player;player.cullingMask=~(1<<8);')
a=s.index('Part("Viewer lens"');b=s.index('\n static Mesh LeafMesh',a)
s=s[:a]+'''var lens=Part("Viewer lens",PrimitiveType.Cylinder,new Vector3(0,1.55f,-.18f),new Vector3(.26f,.18f,.26f),Mat("Viewer",teal));lens.layer=8;lens.transform.rotation=Quaternion.Euler(90,0,0);
 for(int i=-1;i<=1;i+=2)Line("Same apparent height rays",new[]{new Vector3(0,1.55f+i*.405f,2),new Vector3(0,1.55f,0),new Vector3(0,1.55f+i*1.215f,6)},yellow,.025f);
 }
 static Mesh FlameMesh(){string path=Root+"/Meshes/Flame.asset";var old=AssetDatabase.LoadAssetAtPath<Mesh>(path);if(old)return old;var mesh=new Mesh{name="Authored tapered flame"};var v=new List<Vector3>();var t=new List<int>();const int n=12,layers=9;for(int j=0;j<layers;j++){float y=j/(float)(layers-1);float radius=Mathf.Sin(Mathf.PI*Mathf.Pow(y,.7f))*.34f+.005f;for(int i=0;i<n;i++){float a=i*2*Mathf.PI/n;v.Add(new Vector3(Mathf.Cos(a)*radius+Mathf.Sin(y*5)*y*.2f,y,Mathf.Sin(a)*radius*.6f));}}for(int j=0;j<layers-1;j++)for(int i=0;i<n;i++){int a=j*n+i,b=j*n+(i+1)%n;t.AddRange(new[]{a,b,a+n,b,b+n,a+n});}mesh.SetVertices(v);mesh.SetTriangles(t,0);mesh.RecalculateNormals();AssetDatabase.CreateAsset(mesh,path);return mesh;}
 static void Flames(){for(int i=0;i<7;i++){var g=new GameObject("Flame tongue "+i);g.transform.position=new Vector3((i%4-1.5f)*.22f,.27f,(i/4-.5f)*.22f);g.transform.localScale=new Vector3(1, .75f+(i%3)*.23f,1);g.AddComponent<MeshFilter>().sharedMesh=FlameMesh();g.AddComponent<MeshRenderer>().sharedMaterial=Mat("Fire"+i,i%2==0?new Color(1,.28f,.015f):new Color(1,.73f,.08f));}}
''' +s[b:]
a=s.index('for(int i=0;i<5;i++)Part("Flame"');b=s.index('\n demo.windGuides',a);s=s[:a]+'Flames();'+s[b:]
s=s.replace('public Vector3 focus,secondary,origin;', 'public Vector3 focus,secondary,origin,shoulderA,handA,handB;')
s=s.replace('origin=Screen(player.transform.position)};', 'origin=Screen(player.transform.position),shoulderA=Screen(demo.armA?demo.armA.position:Vector3.zero),handA=Screen(demo.armA?demo.armA.TransformPoint(Vector3.down*.83f):Vector3.zero),handB=Screen(demo.armB?demo.armB.TransformPoint(Vector3.down*.83f):Vector3.zero)};')
# Skip expensive world rendering during independent-gameplay frames. Keep readback complete.
s=s.replace('Picture(Path.Combine(job.output,"frames",f.ToString("D5")+".jpg"),cam);if(job.topic=="superliminal")', 'if(!s.id.StartsWith("game"))Picture(Path.Combine(job.output,"frames",f.ToString("D5")+".jpg"),cam);if(!s.id.StartsWith("game")&&job.topic=="superliminal")')
p.write_text(s,encoding='utf8')
for p in U.rglob('*'):
 if p.suffix in ['.cs','.shader','.unity','.mat','.meta','.asset']:
  try:s=p.read_text(encoding='utf8');p.write_text('\n'.join(x.rstrip() for x in s.splitlines())+'\n',encoding='utf8')
  except UnicodeError:pass
