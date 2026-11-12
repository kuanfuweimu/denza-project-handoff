import os,sys,json,subprocess,time
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
HERE=Path(__file__).parent
ROOT=HERE.parent.parent
OUT=ROOT/'strings-web/out'
DEST=OUT/'strings-web_showcase_30s_4k60.mp4'
assert not DEST.exists(), 'Refusing to overwrite'
sources=sorted(OUT.glob('[0-9][0-9]_*.mp4'))
assert len(sources)==9
for src in sources:
    meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(src)]))
    v=next(s for s in meta['streams'] if s['codec_type']=='video')
    assert (v['width'],v['height'],v['r_frame_rate'])==(3840,2160,'60/1')
    assert float(meta['format']['duration'])>=7
w,h=3840,2160
log=(HERE/'encode.log').open('w')
enc=subprocess.Popen(['ffmpeg','-hide_banner','-v','warning','-n','-f','rawvideo','-pix_fmt','rgb24','-s','3840x2160','-r','60','-i','pipe:0','-an','-vf','scale=in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p','-c:v','h264_nvenc','-preset','p6','-rc','vbr','-cq','16','-b:v','0','-maxrate','100M','-bufsize','200M','-color_range','tv','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-movflags','+faststart',str(DEST)],stdin=subprocess.PIPE,stderr=log)
tail=[];count=0;shots=[];start=time.monotonic()
try:
    for shot,src in enumerate(sources):
        n=212 if shot<8 else 200
        newtail=[]
        with (HERE/f'decode-{shot+1}.log').open('w') as dl:
            dec=subprocess.Popen(['ffmpeg','-hide_banner','-v','error','-ss','3','-i',str(src),'-frames:v',str(n),'-an','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],stdout=subprocess.PIPE,stderr=dl)
            try:
                for f in range(n):
                    raw=dec.stdout.read(w*h*3)
                    assert len(raw)==w*h*3, f'Short decode {src} frame {f}'
                    a=np.frombuffer(raw,dtype=np.uint8).reshape(h,w,3)
                    if f==100:shots.append((src.stem,Image.fromarray(a).resize((640,360),Image.Resampling.LANCZOS)))
                    if f>=200:newtail.append(a);continue
                    if shot>0 and f<12:
                        mix=(f+.5)/12;mix=mix*mix*(3-2*mix)
                        a=np.clip(tail[f].astype('f4')*(1-mix)+a.astype('f4')*mix,0,255).astype('u1')
                    if (shot==0 and f<12) or (shot==8 and f>=188):
                        fade=f/11 if shot==0 else (199-f)/11
                        a=(a.astype('f4')*(fade*fade*(3-2*fade))).astype('u1')
                    enc.stdin.write(a.tobytes());count+=1
                dec.stdout.close()
                assert dec.wait(timeout=30)==0
            finally:
                if dec.poll() is None:dec.kill();dec.wait()
        tail=newtail
        print(f'{src.name}: {count}/1800 output frames; {time.monotonic()-start:.1f}s',flush=True)
    enc.stdin.close();assert enc.wait(timeout=120)==0
finally:
    if enc.poll() is None:enc.kill();enc.wait()
    log.close()
assert count==1800
sheet=Image.new('RGB',(1920,1170),(10,10,10));d=ImageDraw.Draw(sheet)
for i,(name,img) in enumerate(shots):
    x=(i%3)*640;y=(i//3)*390;sheet.paste(img,(x,y));d.text((x+10,y+365),name,fill='white')
sheet.save(HERE/'contact-sheet.jpg',quality=94)
(HERE/'report.json').write_text(json.dumps({'output':str(DEST),'frames':count,'fps':60,'seconds':30,'sourceStartSeconds':3,'crossfadeFrames':12,'sources':[str(s) for s in sources],'elapsedSeconds':time.monotonic()-start},indent=2),encoding='utf-8')
print(str(DEST),flush=True)
