from capture import sample, MEDIA
for shot in [False,True]:
    sample('map04',shot,track='LostSoul')
for name in ('one','two'):
    sample('map01',True,extra_map=MEDIA/(name+'.wad'),track='DoomImp')
