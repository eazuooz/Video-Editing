"""Actual bounded filesystem regression in installed Unity Mono; no Unity Editor/GPU.

Requires --execute. Writes only a fresh C-media proof directory, never the failed
attempt or original/staged projects. Tests the same File.WriteAllBytes operation
at the actual failed mode-folder length, with canonical flat-path storage.
"""
import argparse,datetime,hashlib,json,subprocess,uuid
from pathlib import Path

HERE=Path(__file__).resolve().parent
MEDIA=Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106/shorts-leveldesign-06-02')
EDITOR=Path('C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Data')
FAILED=MEDIA/'closeup-attempts/20261107-072622-8b16eeced4/baseline'
CANONICAL='Assets/VideoScenes/architectural-111-20261106/06-02-closeup/S02-ProspectRefuge-Closeup-Baseline.unity.meta'
CS=r'''using System;
using System.IO;
using System.Text;
using System.Security.Cryptography;
class SnapshotIoProbe {
 static string Sha(byte[] bytes) {using(var h=SHA256.Create())return BitConverter.ToString(h.ComputeHash(bytes)).Replace("-","").ToLowerInvariant();}
 static int Main(string[] args) {
  if(args.Length!=3)throw new ArgumentException("mode directory, canonical source path, payload file required");
  string output=Path.GetFullPath(args[0]),canonical=args[1];var bytes=File.ReadAllBytes(args[2]);
  Console.WriteLine("MODE_LENGTH="+output.Length);Console.WriteLine("PAYLOAD_SHA256="+Sha(bytes));
  string old=Path.Combine(output,"editable-source/"+canonical);Console.WriteLine("OLD_LENGTH="+old.Length);
  Directory.CreateDirectory(Path.GetDirectoryName(old));Console.WriteLine("OLD_PARENT_EXISTS="+Directory.Exists(Path.GetDirectoryName(old)));
  try {File.WriteAllBytes(old,bytes);Console.WriteLine("OLD_WRITE=success");}
  catch(Exception e){Console.WriteLine("OLD_WRITE="+e.GetType().FullName);Console.WriteLine("OLD_ERROR="+e.Message);}
  string relative="editable/"+Sha(Encoding.UTF8.GetBytes(canonical))+".bin";
  string target=Path.Combine(output,relative);Console.WriteLine("FLAT_RELATIVE="+relative);Console.WriteLine("FLAT_LENGTH="+target.Length);
  Directory.CreateDirectory(Path.GetDirectoryName(target));
  if(File.Exists(target))throw new InvalidOperationException("Preserve existing snapshot");
  File.WriteAllBytes(target,bytes);var actual=File.ReadAllBytes(target);
  if(Sha(actual)!=Sha(bytes)||actual.LongLength!=bytes.LongLength)throw new InvalidOperationException("Content changed");
  Console.WriteLine("FLAT_SHA256="+Sha(actual));Console.WriteLine("FLAT_BYTES="+actual.LongLength);Console.WriteLine("FLAT_WRITE=success");return 0;
 }
}'''

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def invoke(argv,folder,name):
 result=subprocess.run([str(x)for x in argv],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=45,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
 (folder/name).write_bytes(result.stdout)
 assert result.returncode==0,f'{name} exited {result.returncode}'
 return result.stdout.decode('utf8',errors='replace')

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--execute',action='store_true');a=p.parse_args()
 mono=EDITOR/'MonoBleedingEdge/bin/mono.exe';dotnet=EDITOR/'NetCoreRuntime/dotnet.exe';csc=EDITOR/'DotNetSdk/sdk/8.0.318/Roslyn/bincore/csc.dll';refs=EDITOR/'MonoBleedingEdge/lib/mono/4.5'
 assert all(x.is_file()for x in[mono,dotnet,csc,refs/'mscorlib.dll',refs/'System.dll',refs/'System.Core.dll'])
 if not a.execute:print(json.dumps(dict(ready=True,executionRequired=True,unityEditorLaunched=False,gpuStarted=False)));return
 folder=MEDIA/'closeup-mono-io'/(datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:4]);folder.mkdir(parents=True,exist_ok=False)
 needed=len(str(FAILED.resolve()))-len(str(folder.resolve()))-3
 assert needed>=1,'Proof root cannot match actual mode directory length'
 mode=folder/('m'*needed)/'b';assert len(str(mode.resolve()))==len(str(FAILED.resolve()))
 source=folder/'SnapshotIoProbe.cs';source.write_text(CS,encoding='utf8');exe=folder/'SnapshotIoProbe.exe';payload=folder/'payload.bin'
 payload.write_bytes(b'fileFormatVersion: 2\nguid: cpu-filesystem-proof-only\n')
 compile_argv=[dotnet,csc,'/noconfig','/nostdlib+','/target:exe','/out:'+str(exe)]+['/r:'+str(refs/name)for name in['mscorlib.dll','System.dll','System.Core.dll']]+[source]
 invoke(compile_argv,folder,'compile.log');version=invoke([mono,'--version'],folder,'mono-version.log')
 argv=[mono,exe,mode,CANONICAL,payload];output=invoke(argv,folder,'io.log');values={line.split('=',1)[0]:line.split('=',1)[1]for line in output.splitlines()if'='in line}
 expected='editable/'+hashlib.sha256(CANONICAL.encode('utf8')).hexdigest()+'.bin';actual=mode/expected
 assert values['FLAT_WRITE']=='success'and values['FLAT_RELATIVE']==expected and values['FLAT_SHA256']==sha(payload)==sha(actual)
 assert int(values['MODE_LENGTH'])==len(str(FAILED.resolve()))==139 and int(values['OLD_LENGTH'])==262 and int(values['FLAT_LENGTH'])==217
 proof=dict(schemaVersion='06.02-closeup-mono-filesystem-regression-v1',scope='Actual standalone C# filesystem IO on installed Unity Mono; not Editor/import/native capture/visual QA',failedModeFolder=str(FAILED),failedModeFolderUnchanged=True,probeModeFolder=str(mode),canonicalSourcePath=CANONICAL,snapshotRelativePath=expected,observed=values,oldFailureReproduced=values['OLD_WRITE']=='System.IO.DirectoryNotFoundException',flatWriteVerified=True,mono=dict(path=str(mono),sha256=sha(mono),version=version),compileCommand=[str(x)for x in compile_argv],runCommand=[str(x)for x in argv],inputs=[dict(path=str(x),sha256=sha(x))for x in[source,payload,HERE/'prospect-refuge-closeup-source/Editor/ProspectRefugeCloseupBuilder.cs',HERE/'run-prospect-refuge-closeup.py',Path(__file__)]],proofFiles=[dict(path=str(x),sha256=sha(x))for x in[exe,folder/'compile.log',folder/'io.log',folder/'mono-version.log',actual]],unityEditorLaunched=False,gpuStarted=False)
 out=folder/'filesystem-proof.json';out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(dict(proof=str(out),sha256=sha(out),observed=values,oldFailureReproduced=proof['oldFailureReproduced'],flatWriteVerified=True)))
if __name__=='__main__':main()
