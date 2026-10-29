"""Original NEON CHAMBER assets. Run only in an isolated Blender background process.

No original game files, external meshes, textures, fonts or downloaded resources are read.
All dimensions in metres. Blender Z-up is converted to glTF/Godot Y-up on export.
"""
import bpy
import math
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'prototype/assets'
EVIDENCE = ROOT / 'production/local/asset-evidence'
OUT.mkdir(parents=True, exist_ok=True)
EVIDENCE.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0, roughness=.4, emission=None):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    if emission:
        p.inputs['Emission Color'].default_value = (*color, 1)
        p.inputs['Emission Strength'].default_value = emission
    return m

M = {
 'dark': material('Graphite powdercoat',(.018,.029,.035),.7,.32),
 'teal': material('Petrol enamel',(.016,.18,.18),.55,.27),
 'felt': material('Deep teal felt',(.016,.065,.064),0,.88),
 'brass': material('Brushed warm brass',(.57,.32,.095),.85,.31),
 'steel': material('Machined steel',(.30,.36,.38),.9,.24),
 'black': material('Recesses',(.005,.008,.010),.15,.6),
 'wood': material('Warm composite stock',(.20,.074,.035),.2,.46),
 'red': material('Live shell crimson',(.50,.035,.026),.3,.35),
 'mint': material('Blank shell mint',(.035,.65,.49),.25,.28),
 'white': material('Warm ceramic',(.73,.74,.66),.1,.42),
 'glow': material('Mint signal lamp',(.05,.8,.62),.15,.25,3),
 'amber': material('Amber indicator',(.95,.37,.035),.2,.3,2),
 'lens': material('Magnifier lens',(.08,.48,.49),.7,.14),
}
assets = {}
current = []

def finish(o,name,mat,parent=None):
    o.name=name
    if mat: o.data.materials.append(M[mat])
    if parent: o.parent=parent
    current.append(o)
    return o

def empty(name,location=(0,0,0),parent=None):
    o=bpy.data.objects.new(name,None)
    bpy.context.collection.objects.link(o)
    o.location=location
    return finish(o,name,None,parent)

def box(name,loc,scale,mat='dark',bevel=.035,parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object; o.dimensions=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        mod=o.modifiers.new('Manufactured edge radius','BEVEL'); mod.width=bevel; mod.segments=3
        o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
    return finish(o,name,mat,parent)

def cyl(name,loc,radius,depth,mat='steel',axis='Z',vertices=32,parent=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=loc)
    o=bpy.context.object
    if axis=='X': o.rotation_euler[1]=math.pi/2
    if axis=='Y': o.rotation_euler[0]=math.pi/2
    bevel=o.modifiers.new('Small bevel','BEVEL'); bevel.width=min(radius*.12,.012); bevel.segments=2
    o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return finish(o,name,mat,parent)

def sphere(name,loc,scale,mat='steel',parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,radius=1,location=loc)
    o=bpy.context.object; o.scale=scale
    for p in o.data.polygons:p.use_smooth=True
    return finish(o,name,mat,parent)

def torus(name,loc,major,minor,mat='brass',rot=(0,0,0),parent=None):
    bpy.ops.mesh.primitive_torus_add(major_segments=40,minor_segments=10,major_radius=major,minor_radius=minor,location=loc,rotation=rot)
    o=bpy.context.object
    for p in o.data.polygons:p.use_smooth=True
    return finish(o,name,mat,parent)

def link(name,a,b,radius=.045,mat='steel',parent=None):
    mid=(Vector(a)+Vector(b))/2; delta=Vector(b)-Vector(a)
    o=cyl(name,mid,radius,delta.length,mat,parent=parent)
    o.rotation_euler=delta.to_track_quat('Z','Y').to_euler()
    return o

def label(name,text,loc,size,mat='brass',rot=(0,0,0),parent=None):
    curve=bpy.data.curves.new(name,'FONT'); curve.body=text; curve.size=size
    curve.align_x='CENTER'; curve.align_y='CENTER'; curve.extrude=.0007
    o=bpy.data.objects.new(name,curve); bpy.context.collection.objects.link(o)
    o.location=loc;o.rotation_euler=rot
    finish(o,name,mat,parent)
    bpy.context.view_layer.objects.active=o;o.select_set(True)
    bpy.ops.object.convert(target='MESH');o.select_set(False)
    return o

def start(name):
    global current
    current=[]
    return empty(name)

def export(name,root,notes):
    bpy.ops.object.select_all(action='DESELECT')
    for o in current:o.select_set(True)
    bpy.context.view_layer.objects.active=root
    dest=OUT/(name+'.glb')
    bpy.ops.export_scene.gltf(filepath=str(dest),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_animations=False,export_cameras=False,export_lights=False)
    meshes=[o for o in current if o.type=='MESH']
    points=[o.matrix_world@Vector(c) for o in meshes for c in o.bound_box]
    bounds={k:[min(p[i] for p in points),max(p[i] for p in points)] for i,k in enumerate(['x','y','z'])}
    assets[name]={'file':str(dest.relative_to(ROOT)).replace('\\','/'),'rootNode':root.name,'namedNodes':[o.name for o in current],'blenderBounds':bounds,'notes':notes,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'bytes':dest.stat().st_size}
    for o in current:o.hide_render=True;o.hide_set(True)
    return list(current)

root=start('IndustrialTable')
box('Table_rim',(0,0,.91),(4.8,3.1,.18),'brass',.12,root)
box('Playing_surface',(0,0,1.015),(4.58,2.88,.07),'felt',.10,root)
box('Table_skirt',(0,0,.72),(4.45,2.75,.35),'dark',.08,root)
for x in [-2.05,2.05]:
    for y in [-1.18,1.18]:
        box('Leg',(x,y,.32),(.19,.19,.67),'teal',.035,root)
        cyl('Leg_foot',(x,y,.055),.15,.09,'brass',parent=root)
for x in [-2.17,2.17]:
    box('Side_rail_light',(x,0,1.06),(.018,2.2,.018),'glow',.006,root)
for y in [-1.23,1.23]:
    box('Inset_rail',(0,y,1.06),(3.9,.012,.012),'brass',.004,root)
for x in [-1.9,-.95,0,.95,1.9]:
    for y in [-1.38,1.38]:
        cyl('Rim_bolt',(x,y,1.025),.025,.012,'steel',vertices=8,parent=root)
label('Table_name','N E O N   C H A M B E R',(0,-.94,1.056),.13,'brass',parent=root)
for x in [-1.66,1.66]:
    torus('Cup_tray',(x,-.78,1.06),.15,.012,'brass',parent=root)
    cyl('Cup_tray_center',(x,-.78,1.054),.145,.01,'black',parent=root)
table=export('table',root,'Origin at floor; dimensions 4.8 x 3.1 m, tabletop Blender Z1.05 / Godot Y1.05. Front Blender -Y / Godot +Z.')

root=start('RobotDealer')
box('Pelvis',(0,0,.38),(.55,.35,.35),'dark',.08,root)
box('Torso',(0,0,.84),(.76,.42,.62),'teal',.13,root)
box('Chest_plate',(0,-.23,.87),(.52,.06,.36),'dark',.045,root)
for x in [-.16,0,.16]:cyl('Chest_lamp',(x,-.272,.88),.038,.014,'glow',axis='Y',parent=root)
label('Dealer_serial','D - 07',(0,-.274,.72),.065,'brass',(math.pi/2,0,0),root)
for x in [-.27,.27]:
    cyl('Hip_servo',(x,0,.37),.14,.12,'brass',axis='X',parent=root)
    link('Thigh',(x,0,.3),(x,.04,.04),.105,'dark',root)
neck=cyl('Neck_servo',(0,0,1.25),.11,.20,'brass',parent=root)
head=empty('HeadPivot',(0,0,1.42),root)
box('Head_shell',(0,0,.10),(.62,.40,.47),'teal',.10,head)
box('Dark_face',(0,-.215,.08),(.52,.04,.30),'black',.065,head)
for x in [-.145,.145]:
    box('Eye_slot',(x,-.242,.13),(.14,.02,.055),'glow',.012,head)
box('Mouth_grille',(0,-.243,-.035),(.22,.022,.045),'steel',.008,head)
for x in [-.07,0,.07]:box('Grille_gap',(x,-.258,-.035),(.012,.008,.035),'black',.002,head)
for x in [-.32,.32]:cyl('Ear_disk',(x,0,.11),.105,.05,'brass',axis='X',parent=head)
cyl('Antenna',(0,.07,.41),.018,.18,'steel',parent=head)
sphere('Antenna_tip',(0,.07,.51),(.032,.032,.032),'amber',head)
for sign,side in [(-1,'Left'),(1,'Right')]:
    shoulder=empty(side+'ArmPivot',(sign*.46,0,1.03),root)
    sphere(side+'_shoulder',(0,0,0),(.15,.15,.15),'brass',shoulder)
    link(side+'_upper',(0,0,0),(sign*.17,-.13,-.30),.083,'teal',shoulder)
    sphere(side+'_elbow',(sign*.17,-.13,-.30),(.105,.105,.105),'steel',shoulder)
    link(side+'_forearm',(sign*.17,-.13,-.30),(sign*.09,-.45,-.42),.075,'teal',shoulder)
    hand=empty(side+'HandPivot',(sign*.09,-.45,-.42),shoulder)
    box(side+'_palm',(0,-.05,0),(.18,.18,.08),'dark',.025,hand)
    for j in range(3):
        x=(j-1)*.06
        box(side+'_finger_'+str(j),(x,-.18,-.008),(.042,.13,.048),'brass',.012,hand)
        box(side+'_tip_'+str(j),(x,-.258,-.03),(.039,.055,.055),'steel',.012,hand)
    box(side+'_thumb',(-sign*.115,-.085,-.015),(.07,.10,.05),'brass',.015,hand)
dealer=export('dealer',root,'Original mechanical dealer; front +Z in Godot. HeadPivot and Left/RightArmPivot, Left/RightHandPivot remain separate transform nodes for animation. Root from feet/hip support, total height about1.95m.')

root=start('TabletopShotgun')
box('Receiver',(-.10,0,.11),(.43,.13,.20),'dark',.035,root)
box('Ejection_port',(-.06,-.071,.13),(.20,.012,.075),'steel',.008,root)
box('Ejection_inner',(-.055,-.08,.13),(.16,.008,.046),'black',.006,root)
cyl('Barrel',(.55,0,.15),.052,1.02,'steel',axis='X',parent=root)
cyl('Muzzle', (1.065,0,.15),.059,.04,'dark',axis='X',parent=root)
cyl('Muzzle_recess',(1.087,0,.15),.041,.006,'black',axis='X',parent=root)
cyl('Magazine_tube',(.43,0,.048),.038,.76,'dark',axis='X',parent=root)
box('Pump_grip',(.34,0,.045),(.34,.15,.13),'wood',.025,root)
for x in [.21,.265,.32,.375,.43]:
    box('Pump_rib',(x,0,.045),(.019,.164,.14),'black',.005,root)
stock=box('Stock',(-.59,0,.035),(.59,.17,.20),'wood',.06,root)
stock.rotation_euler[1]=-.16
box('Stock_pad',(-.89,0,-.015),(.045,.19,.235),'dark',.025,root)
link('Grip',(-.27,0,.03),(-.34,0,-.17),.055,'wood',root)
torus('Trigger_guard',(-.16,0,-.07),.083,.015,'brass',(math.pi/2,0,0),root)
link('Trigger',(-.12,0,-.01),(-.15,0,-.09),.012,'steel',root)
box('Front_sight',(.96,0,.212),(.025,.023,.032),'amber',.003,root)
for x in [-.24,.04]:cyl('Receiver_pin',(x,-.073,.13),.016,.009,'brass',axis='Y',vertices=12,parent=root)
gun=export('shotgun',root,'Original stylized fictional prop. Barrel points +X; length approx2m. Origin at receiver/table contact; no copied silhouette or textures.')

for name,color in [('shell_live','red'),('shell_blank','mint')]:
    root=start('LiveShell' if color=='red' else 'BlankShell')
    cyl('Casing',(0,0,.075),.042,.15,color,parent=root)
    cyl('Brass_base',(0,0,.018),.045,.036,'brass',parent=root)
    cyl('Rim',(0,0,.005),.049,.012,'brass',parent=root)
    cyl('Top_cap',(0,0,.153),.039,.009,color,parent=root)
    for ang in range(0,360,60):
        a=math.radians(ang)
        link('Crimp',(0,0,.158),(.033*math.cos(a),.033*math.sin(a),.158),.0015,'black',root)
    export(name,root,'Upright original shell; GodotY height. Distinct redLIVE and mintBLANK casing; gameplay UI must also label type, never rely on colour alone.')

root=start('Magnifier')
torus('Lens_frame',(0,0,.035),.13,.018,'brass',parent=root)
cyl('Lens',(0,0,.032),.117,.012,'lens',parent=root)
link('Handle',(0,-.13,.035),(0,-.39,.035),.032,'wood',root)
cyl('Handle_end',(0,-.4,.035),.035,.035,'brass',axis='Y',parent=root)
export('item_magnifier',root,'Flat magnifier, handle toward Godot+Z. Lens is an illustrative reflective material, not a transmission simulation.')

root=start('DrinkCan')
cyl('Can_body',(0,0,.15),.09,.29,'teal',parent=root)
for z in [.014,.289]:torus('Can_seam',(0,0,z),.085,.009,'steel',parent=root)
cyl('Can_lid',(0,0,.294),.084,.009,'steel',parent=root)
torus('Pull_tab',(0,-.015,.303),.023,.006,'dark',parent=root)
label('Can_label','EJECT',(0,-.091,.16),.041,'white',(math.pi/2,0,0),root)
export('item_drink',root,'Original EJECT can, optional mechanic-neutral prop label; GodotY height0.31m.')

root=start('HandSaw')
box('Saw_blade',(0,0,.03),(.52,.11,.016),'steel',.003,root)
for j in range(15):
    x=-.25+j*.035
    bpy.ops.mesh.primitive_cone_add(vertices=3,radius1=.026,radius2=0,depth=.016,location=(x,-.065,.03))
    o=bpy.context.object;o.rotation_euler=(math.pi/2,0,0);finish(o,'Saw_tooth','steel',root)
torus('Saw_handle',(-.34,0,.04),.085,.026,'wood',parent=root)
box('Handle_mount',(-.255,0,.035),(.07,.09,.03),'brass',.008,root)
export('item_saw',root,'Original small handsaw; long axisGodotX, flat on table.')

root=start('Cuffs')
for x in [-.125,.125]:
    torus('Cuff_ring',(x,0,.024),.075,.017,'steel',parent=root)
    box('Cuff_lock',(x,.07,.024),(.06,.06,.04),'brass',.008,root)
for x in [-.035,0,.035]:torus('Chain_link',(x,0,.027),.025,.007,'steel',(0,math.pi/2 if x==0 else 0,0),root)
export('item_cuffs',root,'Original paired restraint rings with linked chain; illustration only, no real engineering dimensions.')

root=start('HealingPacket')
box('Packet',(0,0,.045),(.21,.14,.08),'white',.016,root)
box('Packet_band',(0,0,.09),(.19,.05,.012),'teal',.004,root)
box('Medical_mark_a',(0,0,.099),(.07,.018,.006),'white',.002,root)
box('Medical_mark_b',(0,0,.10),(.018,.065,.006),'white',.002,root)
export('item_heal',root,'Original healing packet replaces cigarette presentation while preserving any explicitly chosen healing rule. Adaptation must be stated in project record.')

# Save reusable authored sources before building the evidence-only presentation.
bpy.ops.object.select_all(action='DESELECT')
source_blend=EVIDENCE/'neon_chamber_original_assets.blend'

# Real Blender beauty image: all displayed geometry is our own authored output.
for o in table+dealer+gun:o.hide_render=False;o.hide_set(False)
bpy.data.objects['RobotDealer'].location=(0,1.1,.65)
bpy.data.objects['TabletopShotgun'].location=(.05,-.25,1.10)
bpy.data.objects['TabletopShotgun'].rotation_euler[2]=-.16
for name,loc in [('LiveShell',(-.8,-.35,1.07)),('BlankShell',(-.64,-.35,1.07)),('Magnifier',(1.1,-.1,1.07)),('DrinkCan',(-1.4,.05,1.07)),('Cuffs',(.9,.55,1.07)),('HealingPacket',(-1.1,.5,1.07)),('HandSaw',(.8,-.66,1.07))]:
    r=bpy.data.objects[name];r.location=loc
    for o in [r]+list(r.children_recursive):o.hide_render=False;o.hide_set(False)
current=[]
box('Evidence_floor',(0,0,-.07),(200,200,.1),'black',0)
world=bpy.context.scene.world
world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.015,.025,.03,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.25
def area(name,loc,power,color,size,target=(0,0,1)):
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.color=color;d.shape='DISK';d.size=size
    o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);o.location=loc
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
area('Warm_key',(2,-3,6),1400,(1,.77,.50),5)
area('Teal_rim',(-3,2,4),1300,(.16,1,.75),3)
area('Front_fill',(-1,-4,3),650,(.45,.65,1),4)
bpy.ops.object.camera_add(location=(5,-6,4.5))
cam=bpy.context.object;cam.name='EvidenceCamera';cam.rotation_euler=(Vector((0,0,1.15))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=44
scene=bpy.context.scene;scene.camera=cam;scene.render.engine='CYCLES';scene.cycles.samples=48
scene.cycles.use_denoising=True
scene.render.resolution_x=1920;scene.render.resolution_y=1080;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(EVIDENCE/'neon-chamber-beauty.png')
bpy.ops.wm.save_as_mainfile(filepath=str(source_blend))
bpy.ops.render.render(write_still=True)
proof={
 'createdAt':datetime.now(timezone.utc).isoformat(),'blenderVersion':bpy.app.version_string,
 'method':'Actual Blender background Python construction, glTF export and Cycles PNG render. No UI/screen recording claimed.',
 'provenance':'Original procedural geometry/materials authored for this project. No extracted game models, textures, code or external asset downloads used.',
 'scope':'Original playable-prototype visual assets, not original commercial-game footage.',
 'coordinateSystem':{'blender':'Z-up,front -Y','gltfGodot':'Y-up,front +Z','conversion':'(x,y,z) -> (x,z,-y)'},
 'assets':assets,'editableBlend':str(source_blend.relative_to(ROOT)).replace('\\','/'),
 'sourceScript':'production/create_original_assets.py','beautyImage':str(Path(scene.render.filepath).relative_to(ROOT)).replace('\\','/'),
 'actualValidation':{'gltfExport':'succeeded','beautyRender':'succeeded','godotRuntime':'not tested by asset task','humanReview':False},
 'presentationChanges':['Healing packet represents same gameplay heal as independently chosen adaptation; original cigarette representation not copied.'],
}
(OUT/'provenance.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('ORIGINAL_ASSETS_COMPLETE '+json.dumps({k:v['bytes'] for k,v in assets.items()}))
