"""Bounded actual C# model fixtures and static Unity-reference compilation.

--execute launches only Roslyn and a console-only Mono fixture, never Unity.
Default reports source paths without starting any process.
"""
import argparse,datetime,hashlib,json,pathlib,subprocess,uuid
HERE=pathlib.Path(__file__).resolve().parent;SOURCE=HERE/'solution-path-unity-source'
MEDIA=pathlib.Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106/shorts-leveldesign-11-05')
EDITOR=pathlib.Path('C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Data')
REFERENCE_RSP=MEDIA.parent/'shorts-leveldesign-06-02/unity-cpu-preflight/compile-final.rsp'
CS=r'''using System;using System.Text;using Yamyam.Architectural111.SolutionPath;
public static class ModelFixture {
 static int checks;static void Check(bool x,string name){if(!x)throw new Exception(name);checks++;Console.WriteLine("PASS "+name);}
 static string Route(Graph g){return string.Join(",",g.mandatoryRoute);}
 static string Edges(Graph g){var x=new StringBuilder();foreach(var e in g.edges)x.Append(e.a+"-"+e.b+":"+e.role+";");return x.ToString();}
 public static void Main(){
  var a=GraphModel.Generate(173,0,0);var same=GraphModel.Generate(173,0,0);var b=GraphModel.Generate(173,1,0);var t=GraphModel.Generate(173,0,1);var broken=GraphModel.Generate(173,0,0,true);
  Check(Route(a)=="1,5,6,7,11,10,9,8,12,13,14","selected seeded route actual C# values");
  Check(Route(a)==Route(same)&&Edges(a)==Edges(same),"deterministic same seed");
  Check(a.entrance==1&&a.exit==14&&a.exit==a.mandatoryRoute[a.mandatoryRoute.Length-1],"exit derived at bottom terminus");
  Check(Route(a)==Route(b)&&Edges(a)!=Edges(b),"side layout changes while route fixed");
  Check(Edges(a)==Edges(t)&&Route(a)==Route(t),"template variant preserves all ports");
  bool allFlip=true;for(int i=0;i<16;i++)allFlip&=a.roomVariants[i]!=t.roomVariants[i];Check(allFlip,"template A/B changes actual internal variant ids");
  Check(a.Reachable(a.entrance)[a.exit]&&!broken.Reachable(broken.entrance)[broken.exit],"one missing mandatory edge disconnects tree");
  Check(a.edges.Length-broken.edges.Length==1&&Route(a)==Route(broken),"negative changes only one connector");
  Check(!a.Reachable(a.entrance,a.mandatoryRoute.Length-2)[a.exit]&&a.Reachable(a.entrance,a.mandatoryRoute.Length-1)[a.exit],"actual BFS changes when final required port opens");
  int sealedCount=0,dead=0;for(int i=0;i<16;i++){if(a.roomRoles[i]=="sealed"){sealedCount++;if(a.Degree(i)!=0)throw new Exception("sealed room has opening");}if(a.roomRoles[i]=="side"&&a.Degree(i)==1)dead++;}Check(sealedCount>=1&&dead>=1,"selected graph contains sealed room and connected side deadend");
  bool invalid=false;var first=a.edges[0];a.edges[0]=new Edge(0,15,"bad");try{a.Validate();}catch(InvalidOperationException){invalid=true;}a.edges[0]=first;Check(invalid,"nonadjacent false connector rejected");
  int runs=0;for(int seed=1;seed<=1000;seed++){var g=GraphModel.Generate(seed,seed%2,seed%2);g.Validate();if(!g.Reachable(g.entrance)[g.exit])throw new Exception("seed route lost");foreach(var e in g.edges)if(!g.Has(e.a,e.b)||!g.Has(e.b,e.a))throw new Exception("nonreciprocal");var n=GraphModel.Generate(seed,seed%2,seed%2,true);if(n.Reachable(n.entrance)[n.exit])throw new Exception("negative still connected");runs++;}Check(runs==1000,"1000 actual C# seeded graphs positive/negative reciprocal reachability");
  Console.WriteLine("CHECKS="+checks);Console.WriteLine("SEEDS="+runs);Console.WriteLine("ROUTE="+Route(a));Console.WriteLine("SEALED="+sealedCount);Console.WriteLine("DEADENDS="+dead);
 }
}'''
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def pin(p):return dict(path=str(pathlib.Path(p).resolve()),sha256=sha(p))
def invoke(command,out,name):
 r=subprocess.run([str(x)for x in command],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=45,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0));(out/name).write_bytes(r.stdout)
 if r.returncode:raise RuntimeError(name+' exit '+str(r.returncode)+': '+r.stdout.decode('utf8',errors='replace'))
 return r.stdout.decode('utf8',errors='replace')
def execute():
 out=MEDIA/'unity-cpu-preflight'/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:6]);out.mkdir(parents=True,exist_ok=False)
 files=[SOURCE/'GraphModel.cs',SOURCE/'Experiment.cs',SOURCE/'Editor/EditorBuilder.cs'];dotnet=EDITOR/'NetCoreRuntime/dotnet.exe';csc=EDITOR/'DotNetSdk/sdk/8.0.318/Roslyn/bincore/csc.dll';mono=EDITOR/'MonoBleedingEdge/bin/mono.exe';refs=EDITOR/'MonoBleedingEdge/lib/mono/4.5'
 rows=REFERENCE_RSP.read_text(encoding='utf8').splitlines();rows=[r for r in rows if not(r.startswith('"D:')or r.startswith('/out:'))];rows+=['/out:"'+str(out/'SolutionPathStatic.dll')+'"']+['"'+str(p)+'"'for p in files];rsp=out/'compile.rsp';rsp.write_text('\n'.join(rows)+'\n',encoding='utf8');invoke([dotnet,csc,'/noconfig','@'+str(rsp)],out,'static-compile.log')
 fixture=out/'ModelFixture.cs';fixture.write_text(CS,encoding='utf8');exe=out/'ModelFixture.exe';invoke([dotnet,csc,'/noconfig','/nologo','/nostdlib+','/target:exe','/out:'+str(exe)]+['/r:'+str(refs/n)for n in['mscorlib.dll','System.dll','System.Core.dll']]+[files[0],fixture],out,'model-compile.log');text=invoke([mono,exe],out,'actual-model-tests.log');assert 'CHECKS=12' in text and 'SEEDS=1000' in text
 sourceHashes={str(p.relative_to(SOURCE)).replace('\\','/'):sha(p)for p in files};x=dict(schemaVersion='11-05-solution-path-static-compiler-v1',staticCompilationPassed=True,compilerExitCode=0,sourceHashes=sourceHashes,sourceInputs=[pin(p)for p in files],config=pin(SOURCE/'config.json'),referenceResponseFile=pin(REFERENCE_RSP),actualResponseFile=pin(rsp),compiler=pin(csc),dotnet=pin(dotnet),mono=pin(mono),actualCSharpModelFixture=pin(fixture),actualModelTestLog=pin(out/'actual-model-tests.log'),modelChecks=12,seedsTested=1000,unityEditorLaunched=False,projectStaged=False,assetsChanged=False,gpuStarted=False,actualSceneSaved=False,actualRuntimePhysicsValidated=False,actualVisualQA=False,actualHumanReview=False)
 p=out/'compile-receipt.json';p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf8');print(json.dumps(dict(ready=True,receipt=pin(p),sourceHashes=sourceHashes,modelChecks=12,seedsTested=1000,editorLaunched=False)))
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--execute',action='store_true');a=p.parse_args()
 if a.execute:execute()
 else:print(json.dumps(dict(defaultReadOnly=True,sourceInputs=[pin(SOURCE/n)for n in['GraphModel.cs','Experiment.cs','Editor/EditorBuilder.cs','config.json']],noProcessStarted=True)))
