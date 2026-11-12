"""Render the project's actual GLSL offline; no browser or desktop control."""
import os,sys,subprocess,shutil,json,time,math
from pathlib import Path
import numpy as np
import moderngl as m
from PIL import Image,ImageDraw

HERE=Path(__file__).parent
PROJECT=Path('D:/Kuanfuweimu/2-Commission/VJ Commission/DENZA N/strings-space')
DELIVERY=Path('D:/Kuanfuweimu/2-Commission/VJ Commission/DENZA N/_work/strings-space-render/previews')
PREVIEW='--preview' in sys.argv
SETTINGS=json.loads((HERE/'reference-settings.json').read_text(encoding='utf-8'))
DEST=PROJECT/'out'/'strings-space_showcase_30s_4k60_subject_only.mp4'
if not PREVIEW and DEST.exists(): raise RuntimeError('Output exists; refusing to overwrite an existing video')
print('Free disk GB:',round(shutil.disk_usage(PROJECT).free/1e9,2),flush=True)
if shutil.disk_usage(PROJECT).free<600_000_000:raise RuntimeError('Need at least 600 MB free for this export')

# Reuse the already verified native runner and shader extraction, not screenshots.
runner=(HERE/'render_check.py').read_text(encoding='utf-8')
setup=runner[:runner.index('centers=[]')].replace('w,h=1920,1080','w,h=3840,2160')
exec(compile(setup,str(HERE/'render_check.py'),'exec'),globals())
G.update(SETTINGS['look']);G.update(SETTINGS['motion']);active=round(4000*G['density'])
render_code=runner[runner.index('def view_at('):runner.index('timings={}')] 
# These globals are supplied for each shot below.
view=np.eye(4,dtype='f4').flatten();eye=np.array([0,0,4.],dtype='f4');floor=DATA['FLOOR'];T=0.;fade=1.
render_code=render_code.replace("uDim=1.","uDim=fade").replace("uAmt=float(P[26])","uAmt=float(P[26])*(1-.75*float(Pe[20]))")
render_code=render_code.replace('uAmb=1.,uMetal=1.,uRange=.18',"uAmb=G['ambient'],uMetal=G['metal'],uRange=.18/G['lrange']**2")
render_code=render_code.replace('uRange=.18,uAmt=',"uRange=.18/G['lrange']**2,uAmt=")
render_code=render_code.replace('tuple(float(P[i]) for i in range(26,30))',"tuple(max(0.,min(1.5,float(P[26+i])*min(G[k],1)+max(G[k]-1,0))) for i,k in enumerate(['gfloor','arch','lattice','beams']))")
render_code=render_code.replace('uWhite=.88',"uWhite=G['white']")
render_code=render_code.replace('math.radians(25)',"math.radians(G['fov']/2)")
# Export-only isolation: keep lit dynamic strands, remove all stage draw calls.
render_code='\n'.join(line for line in render_code.splitlines() if not any(token in line for token in ["structtex.use", "lines(.45", "fp,fv=programs['floor']", "fv.render", "dp,dv=programs['dot']", "for mirror in [.45,0.]"]))+'\n'
assert all(token not in render_code for token in ["structtex.use", "lines(.45", "programs['floor']", "programs['dot']"])
exec(compile(render_code,str(HERE/'render_check.py'),'exec'),globals())
blend_program=ctx.program(vertex_shader=source('VS_FULL'),fragment_shader='''#version 330
uniform sampler2D uNew,uOld; uniform vec2 uInv; uniform float uMix; out vec4 o;
void main(){vec2 uv=gl_FragCoord.xy*uInv;o=mix(texture(uOld,uv),texture(uNew,uv),uMix);}
''')
blend_vao=ctx.vertex_array(blend_program,[]);blended=target(w,h,'f1')
previous_tail=[target(w,h,'f1') for _ in range(12)]
next_tail=[target(w,h,'f1') for _ in range(12)]

ffmpeg=shutil.which('ffmpeg');assert ffmpeg
fflog=(HERE/'subject-only-ffmpeg.log').open('w',encoding='utf-8')
command=[ffmpeg,'-hide_banner','-loglevel','warning','-n','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{w}x{h}','-framerate','60','-i','pipe:0',
  '-vf','vflip,scale=in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p',
  '-an','-c:v','h264_nvenc','-preset','p6','-rc','vbr','-cq','16','-b:v','0','-maxrate','100M','-bufsize','200M',
  '-color_range','tv','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-movflags','+faststart',
  '-metadata','title=STRINGS SPACE - 30 second showcase',str(DEST)]
encoder=None if PREVIEW else subprocess.Popen(command,stdin=subprocess.PIPE,stderr=fflog,stdout=subprocess.DEVNULL)
frames_written=0;shots=[];started=time.monotonic()
try:
  for shot in range(9):
    SC=DATA['SCENES'][shot];P=np.array(SC['P'],dtype='f4');Pe=P.copy();Pe[15]*=G['width'];Pe[0]*=G['turb'];Pe[19]*=G['expo']*SETTINGS.get('exportExposureCompensation',[1]*9)[shot]
    initial=np.zeros((rows,sw,4),dtype='f4');initial[:,:,3]=-1
    simA[0].write(initial.tobytes());simB[0].write(initial.tobytes());del initial
    T=shot*37.;acc=0.;frame_counter=0;light_time=0.;camera_angle=.6+shot
    def step(dt):
      global simA,simB,T,acc,frame_counter,light_time,camera_angle
      T+=dt;frame_counter+=1;light_time+=dt;camera_angle+=dt*float(P[23])*G['orbit'];acc+=dt*float(P[16])
      shift=0.
      if acc>=1:acc=min(acc-1,1);shift=1.
      ctx.disable(m.DEPTH_TEST|m.BLEND);simB[1].use();ctx.viewport=(0,0,sw,rows);p,vao=programs['sim'];simA[0].use(0)
      uniforms(p,uS=0,uT=T,uDt=dt,uShift=shift,uSeed=(frame_counter%9973)*.37+1.,uMode=float(SC['mode']),uActive=float(active),uP=Pe)
      vao.render(m.TRIANGLES,vertices=3);simA,simB=simB,simA
    print(f'Scene {shot+1}/9 {SC["name"]}: warming 22 s',flush=True)
    for _ in range(660):step(G['speed']/30)
    tracking=shot in (1,7)
    center=np.array(head_center(),dtype='f4');focus=center[:3].copy();track_target=focus.copy()
    frame_count=212 if shot<8 else 200
    for frame_index in range(frame_count):
      step(G['speed']/60)
      cd=float(P[21])*G['cameraDistance'];fish=float(Pe[20]);cam_y=max(floor+.12,float(P[22])+.3*math.sin(T*.021)*(1-fish))
      eye=np.array([math.sin(camera_angle)*cd,cam_y,math.cos(camera_angle)*cd],dtype='f4')
      aim=np.array([0,float(P[24]),0],dtype='f4')
      if tracking:
        if frame_index%6==0:
          sample=head_center()
          if sample[3]>.01:track_target=np.clip(sample[:3],[-4,-1.4,-4],[4,4,4])
        focus+=(track_target-focus)*(1-math.exp(-1/60/1.8))
        offset=(focus-aim)*.8;aim+=offset;eye+=offset*.7;eye[1]=max(floor+.12,eye[1])
      view=view_at(eye,aim);t=light_time
      lights=np.array([1.7*math.sin(.23*t),.35+.5*math.sin(.31*t),1.7*math.cos(.23*t),3.,-2.6*math.sin(.17*t+1),floor+.45+.25*math.sin(.4*t),2.6*math.cos(.17*t+1),2.4,.9*math.sin(.13*t+3),1.5+.4*math.sin(.21*t),-.9*math.cos(.13*t+3),2.],dtype='f4')
      lights[3::4]*=G['light']
      G['width']=.4+.08*(.5-.5*math.cos(2*math.pi*frame_index/frame_count))
      fade=1.
      if shot==0 and frame_index<12:fade=(frame_index/11)**2*(3-2*frame_index/11)
      if shot==8 and frame_index>=188:
        a=(199-frame_index)/11;fade=a*a*(3-2*a)
      if PREVIEW and frame_index!=100:continue
      render(False)
      if frame_index==100:
        pixels=np.frombuffer(final[1].read(components=3,alignment=1),dtype='u1').reshape(h,w,3)
        thumb=Image.fromarray(pixels[::-1]).resize((640,360),Image.Resampling.LANCZOS)
        shots.append((SC['name'],thumb));thumb.save(DELIVERY/f'subject-only-scene-{shot+1}.jpg',quality=94)
        if PREVIEW:Image.fromarray(pixels[::-1]).save(DELIVERY/f'subject-only-full-{shot+1}.png')
      if PREVIEW:continue
      if frame_index>=200:
        ctx.copy_framebuffer(next_tail[frame_index-200][1],final[1]);continue
      output=final[1]
      if shot>0 and frame_index<12:
        blended[1].use();ctx.viewport=(0,0,w,h);final[0].use(0);previous_tail[frame_index][0].use(1)
        a=(frame_index+.5)/12;a=a*a*(3-2*a)
        uniforms(blend_program,uNew=0,uOld=1,uInv=(1/w,1/h),uMix=a);blend_vao.render(m.TRIANGLES,vertices=3);output=blended[1]
      encoder.stdin.write(output.read(components=3,alignment=1));frames_written+=1
      if frame_index%60==0:print(f'Scene {shot+1}: {frame_index}/{frame_count}; output {frames_written}/1800; elapsed {time.monotonic()-started:.1f}s',flush=True)
    previous_tail,next_tail=next_tail,previous_tail
  if encoder:encoder.stdin.close()
  code=encoder.wait(timeout=120) if encoder else 0
  if code:raise RuntimeError(f'FFmpeg failed ({code}), see {HERE}/showcase-ffmpeg.log')
  assert PREVIEW or frames_written==1800
finally:
  if encoder and encoder.poll() is None:encoder.kill();encoder.wait()
  fflog.close()
sheet=Image.new('RGB',(1920,3*390),(12,12,12));draw=ImageDraw.Draw(sheet)
for index,(name,img) in enumerate(shots):
  x=(index%3)*640;y=(index//3)*390;sheet.paste(img,(x,y));draw.text((x+12,y+365),f'{index+1}  {name.split()[0]}',fill=(220,220,220))
sheet.save(DELIVERY/'subject-only-contact-sheet.jpg',quality=94)
report={'file':str(DEST),'frames':frames_written,'width':w,'height':h,'fps':60,'seconds':30,'scenes':[s['name'] for s in DATA['SCENES']],'transitionFrames':12,'material':'reference-settings.json','density':G['density'],'settings':SETTINGS,'trackingScenes':[2,8],'elapsedSeconds':round(time.monotonic()-started,2),'renderBackend':'Project GLSL rendered by standalone OpenGL; fixed 1/60 s simulation for final frames','bytes':DEST.stat().st_size if not PREVIEW else 0}
(HERE/('subject-only-preview-report.json' if PREVIEW else 'subject-only-report.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False),flush=True)
