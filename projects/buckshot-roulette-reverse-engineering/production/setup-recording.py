"""Create an independent OBS recording profile/collection while OBS is closed."""
from pathlib import Path
import configparser,copy,json,uuid,datetime,subprocess
from PIL import Image,ImageDraw,ImageFont
R=Path('D:/Github/VideoEditing');P=R/'projects/buckshot-roulette-reverse-engineering';L=P/'production/local/setup'
L.mkdir(parents=True,exist_ok=True)
proc=subprocess.check_output(['powershell','-NoProfile','-Command',"@(Get-Process obs64 -ErrorAction SilentlyContinue).Count"],text=True).strip()
assert proc=='0','OBS must be closed; do not change a running profile'
obs=Path('C:/Users/1/AppData/Roaming/obs-studio');profileName='Yamyam-Buckshot-RE'
profile=obs/'basic/profiles'/profileName;collection=obs/'basic/scenes'/f'{profileName}.json'
assert not profile.exists() and not collection.exists(),'Do not overwrite existing settings'
record=P/'captures/recordings';record.mkdir(parents=True,exist_ok=True)
setup=P/'captures/setup';setup.mkdir(parents=True,exist_ok=True)
im=Image.new('RGB',(1920,1080),'#0B0D0C');d=ImageDraw.Draw(im)
font='C:/Windows/Fonts/malgunbd.ttf'
for y,text,size,color in [(220,'얌얌코딩 · 작업 과정 녹화',66,'#FFD166'),(360,'벅샷 룰렛 리버스 엔지니어링',58,'#FFFFFF'),(490,'1920 × 1080  /  60 fps  /  MKV',46,'#A7E8DC'),(650,'준비 완료 후 “시작해” 지시에 착수합니다.',42,'#D9DFDC')]:
    f=ImageFont.truetype(font,size);d.text((120,y),text,font=f,fill=color)
d.rectangle((24,24,1895,1055),outline='#FFD166',width=4)
slate=setup/'recording-check.png';im.save(slate)
c=configparser.ConfigParser(interpolation=None);c.optionxform=str
c.read(obs/'basic/profiles/제목 없음/basic.ini',encoding='utf-8-sig')
for sec,values in {'General':{'Name':profileName},'Output':{'Mode':'Simple','FilenameFormatting':'buckshot-process-%CCYY-%MM-%DD_%hh-%mm-%ss'},'Video':{'BaseCX':'1920','BaseCY':'1080','OutputCX':'1920','OutputCY':'1080','FPSType':'0','FPSCommon':'60','FPSInt':'60','FPSNum':'60','FPSDen':'1'},'SimpleOutput':{'FilePath':record.as_posix(),'RecFormat2':'mkv','RecEncoder':'nvenc','RecQuality':'Small','RecTracks':'1','ABitrate':'192','RecRB':'false'},'Audio':{'SampleRate':'48000','ChannelSetup':'Stereo'}}.items():
    if not c.has_section(sec):c.add_section(sec)
    for k,v in values.items():c[sec][k]=v
# Never inherit streaming or user shortcut bindings into this local-recording setup.
for sec in ['Hotkeys','Stream1']:c.remove_section(sec)
profile.mkdir(parents=True)
with (profile/'basic.ini').open('w',encoding='utf8') as f:c.write(f,space_around_delimiters=False)
old=json.loads((obs/'basic/scenes/제목 없음.json').read_text(encoding='utf-8-sig'))
monitor=copy.deepcopy(next(s for s in old['sources'] if s['id']=='monitor_capture'))
monitor.update(name='작업 모니터',uuid=str(uuid.uuid4()),hotkeys={});monitor['settings']['capture_cursor']=True
def source(name,id,settings):return dict(name=name,uuid=str(uuid.uuid4()),id=id,versioned_id=id,settings=settings,mixers=0,sync=0,flags=0,volume=1.0,balance=0.5,enabled=True,muted=False,hotkeys={},private_settings={})
image=source('녹화 설정 점검','image_source',{'file':slate.as_posix(),'unload':False})
def scene(name,src):
    item={'name':src['name'],'source_uuid':src['uuid'],'visible':True,'locked':True,'rot':0.0,'align':5,'bounds_type':2,'bounds_align':0,'bounds_crop':False,'crop_left':0,'crop_top':0,'crop_right':0,'crop_bottom':0,'id':1,'pos':{'x':0.0,'y':0.0},'pos_rel':{'x':-1.7777777778,'y':-1.0},'scale':{'x':1.0,'y':1.0},'scale_rel':{'x':1.0,'y':1.0},'scale_ref':{'x':1920.0,'y':1080.0},'bounds':{'x':1920.0,'y':1080.0},'bounds_rel':{'x':3.5555555556,'y':2.0},'scale_filter':'disable','blend_method':'default','blend_type':'normal','show_transition':{'duration':0},'hide_transition':{'duration':0},'private_settings':{}}
    return source(name,'scene',{'id_counter':1,'custom_size':False,'items':[item]})
test=scene('녹화 점검',image);work=scene('작업 화면',monitor)
desktop=source('게임·작업 소리','wasapi_output_capture',{'device_id':'default'});desktop.update(mixers=1,monitoring_type=0,volume=1.0)
j={'name':profileName,'DesktopAudioDevice1':desktop,'sources':[monitor,image,test,work],'groups':[],'scene_order':[{'name':test['name']},{'name':work['name']}],'current_scene':test['name'],'current_program_scene':test['name'],'canvases':[],'current_transition':'Fade','transition_duration':250,'transitions':[],'quick_transitions':[],'saved_projectors':[],'preview_locked':True,'scaling_enabled':False,'resolution':{'x':1920,'y':1080},'migration_resolution':{'x':1920,'y':1080},'version':old.get('version',1)}
collection.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
receipt={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'profile':str(profile),'collection':str(collection),'recordingDirectory':str(record),'resolution':'1920x1080','fps':60,'container':'mkv','encoder':'nvenc-h264','microphoneEnabled':False,'desktopAudio':'default output device','previousProfileAndSceneFilesUnmodified':True,'startedRecording':False,'obsSettingsVerifiedByPlayback':False}
(P/'production/recording-setup.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(receipt,ensure_ascii=False))
