from pathlib import Path
R=Path(__file__).resolve().parents[3];U=R/'unity/VideoEditing/Assets/VideoScenes/distinctive-shorts-20261024'
p=U/'Editor/BatchCapture.cs';s=p.read_text(encoding='utf8');s=s.replace('static void Perspective(){Floor','static void Perspective(){Floor')
needle='for(int i=-1;i<=1;i+=2)Line("Same apparent height rays"'
a=s.index(needle);b=s.index('\n }',a)
s=s[:b]+'''
 demo.guideRoot=new GameObject("Illustrative surface ray samples").transform;
 for(int i=0;i<5;i++)for(int j=0;j<4;j++)Line("Surface sample",new[]{Vector3.zero,Vector3.one},teal,.014f,demo.guideRoot);
''' +s[b:]
s=s.replace('if(!s.id.StartsWith("game")&&job.topic=="superliminal")Picture(Path.Combine(job.output,"player",f.ToString("D5")+".jpg"),player);', '''if(!s.id.StartsWith("game")&&job.topic=="superliminal")Picture(Path.Combine(job.output,"player",f.ToString("D5")+".jpg"),player);
 if(s.id=="compare"&&job.topic=="ghost"){demo.section="off";demo.Apply();Picture(Path.Combine(job.output,"player",f.ToString("D5")+".jpg"),cam);demo.section=s.id;demo.Apply();}''')
p.write_text(s,encoding='utf8')
p=U/'DemoState.cs';s=p.read_text(encoding='utf8');n='player.fieldOfView=43;';s=s.replace(n,n+'''
    if(guideRoot){guideRoot.gameObject.SetActive(section=="rays");int i=0;foreach(var line in guideRoot.GetComponentsInChildren<LineRenderer>(true)){int x=i%5,y=i/5;line.SetPosition(0,player.transform.position);line.SetPosition(1,pawn.position+new Vector3((x-2)*.09f*scale,(y-1.5f)*.18f*scale,-.16f*scale));i++;}}
''');p.write_text(s,encoding='utf8')
