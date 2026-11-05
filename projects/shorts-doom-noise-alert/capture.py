"""Record the stock Freedoom campaign in a headless software Doom game; compare two real saves from the same seed."""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

MEDIA=Path('C:/Users/1/Videos/YamyamProduction/daily-shorts-20261105/shorts-doom-noise-alert')
sys.path.insert(0,str(MEDIA/'tools'))
import vizdoom as vz
from PIL import Image
import math

RAW=MEDIA/'raw'
PACKAGE=Path(vz.__file__).parent
def dump(path,data):path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
def sample(level,fire,render=False,extra_map=None,ticks=245,seed=25,track=None):
    game=vz.DoomGame()
    game.set_doom_game_path(str(PACKAGE/'freedoom2.wad'))
    if extra_map:game.set_doom_scenario_path(str(extra_map))
    game.set_doom_map(level)
    game.set_seed(seed)
    game.set_doom_skill(3)
    game.set_screen_resolution(vz.ScreenResolution.RES_1920X1080 if render or track else vz.ScreenResolution.RES_320X180)
    game.set_screen_format(vz.ScreenFormat.RGB24)
    game.set_window_visible(False)
    game.set_sound_enabled(False)
    game.set_objects_info_enabled(True)
    if track:game.set_labels_buffer_enabled(True)
    game.set_render_hud(False)
    game.set_render_weapon(True)
    game.set_available_buttons([vz.Button.ATTACK])
    game.set_available_game_variables([vz.GameVariable.POSITION_X,vz.GameVariable.POSITION_Y,vz.GameVariable.ANGLE])
    game.set_episode_start_time(18)
    game.set_episode_timeout(ticks+90)
    game.add_game_args('+vid_renderer 0 +r_drawplayersprites 1')
    game.set_doom_config_path(str(MEDIA/'vizdoom.ini'))
    experiment='test-'+extra_map.stem+'-' if extra_map else 'campaign-'
    dest=RAW/(experiment+level+('-shot' if fire else '-quiet')+('-fhd' if render else '-scan'))
    dest.mkdir(exist_ok=True,parents=True)
    states=[]
    positions=[]
    writer=None
    try:
        game.init();game.new_episode()
        if render:
            assert (game.get_screen_width(),game.get_screen_height())==(1920,1080)
            writer=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-video_size','1920x1080','-pixel_format','rgb24','-framerate','35','-i','pipe:0','-an','-c:v','libx264','-threads','3','-preset','ultrafast','-crf','15','-pix_fmt','yuv420p',str(dest/'actual.mp4')],stdin=subprocess.PIPE)
        for tick in range(ticks):
            state=game.get_state()
            if state is None:break
            if track:
                seen=[a for a in state.labels if a.object_name==track]
                positions.append([{'id':a.object_id,'x':a.x,'y':a.y,'w':a.width,'h':a.height} for a in seen])
            if tick%7==0:
                states.append({'tick':tick,'player':state.game_variables.tolist(),'actors':{str(o.id):[o.name,round(o.position_x,2),round(o.position_y,2)] for o in state.objects}})
            if writer:
                writer.stdin.write(state.screen_buffer.tobytes())
                if tick in [0,37,45,79,115,165,210]:
                    Image.fromarray(state.screen_buffer).resize((768,432)).save(dest/f'{tick:03}.jpg')
            game.make_action([int(fire and tick==35)],1)
            if game.is_player_dead():break
    finally:
        if writer:
            writer.stdin.close()
            if writer.wait():raise RuntimeError('Actual capture encode failed.')
        game.close()
    if track:dump(RAW/(experiment+level+('-shot' if fire else '-quiet')+'-fhd')/'visible-object.json',positions)
    else:dump(dest/'states.json',states)
    return states
def compare(q,s):
    before=q[0];focus=[]
    for key,v in before['actors'].items():
        if key not in q[-1]['actors'] or key not in s[-1]['actors']:continue
        if v[0] in ('DoomPlayer','TeleportFog'):continue
        for left,right in zip(q,s):
            if left['tick']<35 or key not in left['actors'] or key not in right['actors']:continue
            a,b=left['actors'][key],right['actors'][key]
            if math.dist(a[1:],b[1:])>8:
                focus.append([v[0],key,left['tick'],math.dist(a[1:],v[1:]),math.dist(b[1:],v[1:])]);break
    return focus
if __name__=='__main__':
    opts=argparse.ArgumentParser();opts.add_argument('levels',nargs='+');opts.add_argument('--fhd',action='store_true');opts.add_argument('--map',type=Path);args=opts.parse_args()
    for level in args.levels:
        q=sample(level,False,args.fhd,args.map)
        s=sample(level,True,args.fhd,args.map)
        print(level,'player',q[0]['player'], 'ticks',q[-1]['tick'],s[-1]['tick'],'changed',compare(q,s)[:7],flush=True)
