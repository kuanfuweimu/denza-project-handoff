import json, re, math, time
from pathlib import Path
import numpy as np
import moderngl as m
from PIL import Image

HERE=Path(__file__).parent
DATA=json.loads((HERE/'scene.json').read_text(encoding='utf-8'))
OUT=Path('D:/Kuanfuweimu/2-Commission/VJ Commission/DENZA N/_work/strings-space-render/previews')
OUT.mkdir(parents=True,exist_ok=True)
ctx=m.create_standalone_context(require=330)
print('GPU:',ctx.info['GL_RENDERER'],flush=True)
def source(key):
    s=DATA[key].replace('#version 300 es','#version 330')
    return re.sub(r'precision\s+(?:highp|mediump|lowp)\s+\w+\s*;','',s)
programs={}
for name,vs,fs in [('sim','VS_FULL','FS_SIM'),('line','VS_LINE','FS_LINE'),('dot','VS_DOT','FS_DOT'),('floor','VS_FULL','FS_FLOOR'),('blur','VS_FULL','FS_GAUSS'),('comp','VS_FULL','FS_COMP'),('track','VS_FULL','FS_TRACK')]:
    p=ctx.program(vertex_shader=source(vs),fragment_shader=source(fs))
    programs[name]=(p,ctx.vertex_array(p,[]))
print('All seven shader programs compiled and linked',flush=True)
def uniform(p,k,v):
    if k not in p:return
    if isinstance(v,np.ndarray):p[k].write(v.astype('f4').tobytes())
    else:p[k].value=v
def uniforms(p,**values):
    for k,v in values.items():uniform(p,k,v)
def target(w,h,dtype='f2',depth=False):
    tex=ctx.texture((w,h),4,dtype=dtype);tex.filter=(m.LINEAR,m.LINEAR) if dtype!='f4' else (m.NEAREST,m.NEAREST)
    tex.repeat_x=tex.repeat_y=False
    return tex,ctx.framebuffer([tex],ctx.depth_renderbuffer((w,h)) if depth else None)
rows,seg=DATA['ROWS'],DATA['SEG'];sw=seg*4
initial=np.zeros((rows,sw,4),dtype='f4');initial[:,:,3]=-1
simA,simB=target(sw,rows,'f4'),target(sw,rows,'f4')
simA[0].write(initial.tobytes());simB[0].write(initial.tobytes());del initial
st=DATA['STRUCT'];structtex=ctx.texture((seg,st['n']),4,np.array(st['data'],dtype='f4').tobytes(),dtype='f4');structtex.filter=(m.NEAREST,m.NEAREST)
w,h=1920,1080
scene=target(w,h,depth=True)
multi=ctx.framebuffer([ctx.renderbuffer((w,h),components=4,samples=4,dtype='f2')],ctx.depth_renderbuffer((w,h),samples=4))
blur=[(target(w>>d,h>>d),target(w>>d,h>>d)) for d in [1,2,3]]
final=target(w,h,'f1');track=target(1,1,'f4')
G=DATA['G'];P=np.array(DATA['SCENES'][1]['P'],dtype='f4');Pe=P.copy();Pe[15]*=G['width']
active=12000
def simulate(frame):
    global simA,simB
    ctx.disable(m.DEPTH_TEST|m.BLEND);simB[1].use();ctx.viewport=(0,0,sw,rows)
    p,vao=programs['sim'];simA[0].use(0)
    uniforms(p,uS=0,uT=frame/30,uDt=1/30,uShift=1. if frame%3==0 else 0.,uSeed=(frame%9973)*.37+1.,uMode=1.,uActive=float(active),uP=Pe)
    vao.render(m.TRIANGLES,vertices=3);simA,simB=simB,simA
def head_center():
    track[1].use();ctx.viewport=(0,0,1,1);p,v=programs['track'];simA[0].use(0);uniforms(p,uS=0,uActive=active);v.render(m.TRIANGLES,vertices=3)
    return np.frombuffer(track[0].read(),dtype='f4').tolist()
centers=[]
for f in range(1,241):
    simulate(f)
    if f%60==0:
        centers.append(head_center());print('Simulated',f,'frames; tracked center:',centers[-1],flush=True)
ctx.finish()
T=8.;az=.6+T*float(P[23]);cd=float(P[21]);floor=DATA['FLOOR']
eye=np.array([math.sin(az)*cd,float(P[22])+.3*math.sin(T*.021),math.cos(az)*cd],dtype='f4')
def view_at(e,c):
    z=e-np.array(c);z=z/np.linalg.norm(z);x=np.cross([0,1,0],z);x=x/np.linalg.norm(x);y=np.cross(z,x)
    a=np.eye(4,dtype='f4');a[:3,:3]=np.array([x,y,z]);a[:3,3]=-a[:3,:3]@e
    return a.T.copy().flatten()
view=view_at(eye,[0,float(P[24]),0])
lights=np.array([1.7*math.sin(.23*T),.35+.5*math.sin(.31*T),1.7*math.cos(.23*T),3.,-2.6*math.sin(.17*T+1),floor+.45+.25*math.sin(.4*T),2.6*math.cos(.17*T+1),2.4,.9*math.sin(.13*T+3),1.5+.4*math.sin(.21*T),-.9*math.cos(.13*T+3),2.],dtype='f4')
def cam(p):uniforms(p,uV=view,uF=1/math.tan(math.radians(25)),uAspect=w/h,uFish=float(Pe[20]),uPx=h/1080,uFloorY=float(floor),uL=lights)
def render(legacy):
    multi.use();ctx.viewport=(0,0,w,h);multi.clear(0,0,0,1,depth=1);ctx.enable(m.DEPTH_TEST);ctx.depth_func='<=';ctx.disable(m.BLEND)
    p,v=programs['line'];cam(p)
    wireP=Pe.copy();wireP[15]=P[15]*(1. if legacy else G['width'])
    uniforms(p,uS=0,uRes=(w/2,h/2),uT=T,uP=wireP,uAmb=1.,uMetal=1.,uRange=.18,uLayer=tuple(float(P[i]) for i in range(26,30)),uLayerEnd=tuple(st['ends']),uLegacy=float(legacy))
    for key,param in {'uRoughness':'roughness','uAnisotropy':'anisotropy','uSpecular':'specular','uEnv':'env','uEnvAngle':'envAngle','uEnvWidth':'envWidth','uWarmth':'warmth','uEmission':'emission'}.items():uniform(p,key,float(G[param]))
    def lines(mirror,camera):
        uniforms(p,uMirror=mirror,uCam=tuple(float(x) for x in camera),uStruct=0.)
        simA[0].use(0);v.render(m.TRIANGLE_STRIP,vertices=4,instances=active*(seg-1))
        structtex.use(0);uniform(p,'uStruct',1.);v.render(m.TRIANGLE_STRIP,vertices=4,instances=st['n']*(seg-1))
    lines(.45,[eye[0],2*floor-eye[1],eye[2]])
    fp,fv=programs['floor'];cam(fp);uniforms(fp,uInv=(1/w,1/h),uCam=tuple(float(x) for x in eye),uRange=.18,uAmt=float(P[26]))
    ctx.enable(m.BLEND);ctx.blend_func=m.ONE,m.ONE;ctx.depth_func='1';fv.render(m.TRIANGLES,vertices=3);ctx.depth_func='<=';ctx.disable(m.BLEND)
    lines(0.,eye)
    dp,dv=programs['dot'];cam(dp);ctx.enable(m.BLEND|m.PROGRAM_POINT_SIZE);ctx.blend_func=m.ONE,m.ONE;ctx.depth_mask=False
    for mirror in [.45,0.]:uniform(dp,'uMirror',mirror);dv.render(m.POINTS,vertices=3)
    ctx.depth_mask=True;ctx.disable(m.DEPTH_TEST|m.BLEND);ctx.copy_framebuffer(scene[1],multi)
    bp,bv=programs['blur'];src=scene
    for a,b in blur:
        for old,new,sx,sy in [(src,a,0,0),(a,b,1,0),(b,a,0,1)]:
            new[1].use();tw,th=new[0].size;ctx.viewport=(0,0,tw,th);old[0].use(0);uniforms(bp,uTex=0,uInv=(1/tw,1/th),uStep=(sx/tw,sy/th));bv.render(m.TRIANGLES,vertices=3)
        src=a
    final[1].use();ctx.viewport=(0,0,w,h);cp,cv=programs['comp'];scene[0].use(0);blur[0][0][0].use(1);blur[2][0][0].use(2)
    uniforms(cp,uScene=0,uB1=1,uB3=2,uInv=(1/w,1/h),uExp=float(Pe[19])*2.6,uWhite=.88,uBloom=1. if legacy else G['bloom'],uDim=1.)
    cv.render(m.TRIANGLES,vertices=3)
timings={}
for name,legacy in [('original',True),('chrome',False)]:
    render(legacy);ctx.finish()
    with ctx.query(time=True) as query:render(legacy)
    timings[name]=query.elapsed/1e6
    raw=final[0].read();pixels=np.frombuffer(raw,dtype='u1').reshape(h,w,4)
    assert pixels[:,:,:3].max()>50 and np.isfinite(pixels).all()
    Image.fromarray(pixels[::-1,:,:3]).save(OUT/f'{name}-preview-1920x1080.png')
    print(name,'draw GPU ms:',timings[name],flush=True)
report={'backend':'Standalone OpenGL 3.3, original GLSL ES converted to desktop GLSL; not a browser benchmark','GPU':ctx.info['GL_RENDERER'],'resolution':[w,h],'activeStrings':active,'segments':seg,'programsCompiled':list(programs),'sampledHeadCenters':centers,'singleDrawGpuMs':timings,'previewDirectory':str(OUT)}
(HERE/'gpu-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('Saved',OUT,flush=True)
