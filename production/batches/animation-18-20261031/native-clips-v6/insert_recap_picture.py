"""Keep complete original GOPs and encode only the final recap/ending bridge."""
import json
import subprocess

from finish_episode import ff, VENC


def stream(path):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0',
        '-show_streams','-of','json',str(path)]))['streams'][0]


def insert(source, recap, frames, folder, label):
    end_body=frames-600
    keyframes=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0',
        '-skip_frame','nokey','-show_entries','frame=best_effort_timestamp_time','-of','json',str(source)]))['frames']
    possible=[round(float(f['best_effort_timestamp_time'])*60) for f in keyframes
              if 'best_effort_timestamp_time' in f and float(f['best_effort_timestamp_time'])*60<=end_body-30]
    cut=max(possible)
    assert 120<cut<end_body
    prefix=folder/('original-prefix-'+label)
    bridge=folder/('recap-bridge-'+label)
    ff('-i',source,'-map','0:v:0','-an','-c:v','copy','-frames:v',cut,
       '-video_track_timescale',60000,prefix)
    info=stream(prefix)
    assert int(info['nb_frames'])==cut and abs(float(info['start_time']))<1/60000
    assert abs(float(info['duration'])-cut/60)<1/60000
    relative_insert=end_body-cut
    filters=(f'[0:v]split=2[b][e];[b]trim=end_frame={relative_insert},setpts=PTS-STARTPTS[b0];'
             f'[e]trim=start_frame={relative_insert}:end_frame={frames-cut},setpts=PTS-STARTPTS[e0];'
             '[1:v]trim=end_frame=600,setpts=PTS-STARTPTS[s0];[b0][s0][e0]concat=n=3:v=1:a=0[v]')
    ff('-ss',cut/60,'-threads',2,'-i',source,'-i',recap,'-filter_complex',filters,
       '-map','[v]','-an','-frames:v',frames-cut+600,*VENC,'-bf',0 if not info['has_b_frames'] else 3,bridge)
    assert int(stream(bridge)['nb_frames'])==frames-cut+600
    playlist=folder/('recap-'+label+'.ffconcat')
    playlist.write_text("ffconcat version 1.0\nfile '"+prefix.as_posix()+"'\nduration "+f'{cut/60:.9f}'+
                        "\nfile '"+bridge.as_posix()+"'\n",encoding='utf-8')
    result=folder/('joined-'+label)
    ff('-f','concat','-safe',0,'-i',playlist,'-map','0:v:0','-an','-c:v','copy',
       '-video_track_timescale',60000,'-movflags','+faststart',result)
    final=stream(result)
    assert int(final['nb_frames'])==frames+600
    assert final['avg_frame_rate']=='60/1'
    assert abs(float(final['duration'])-(frames+600)/60)<1/60000
    return result, {'copiedOriginalFrames':cut,'encodedBridgeFrames':frames-cut+600,
                    'totalFrames':frames+600,'fullDecodeRequired':True}
