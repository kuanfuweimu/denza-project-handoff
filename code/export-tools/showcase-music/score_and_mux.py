"""Original synthesized contemporary-dance sketches. No external samples/music."""
from pathlib import Path
import numpy as np
import subprocess,json,wave,time,sys
HERE=Path(__file__).parent
ROOT=HERE.parent.parent
SR=48000;DURATION=30;N=SR*DURATION;BEAT=60/72;BAR=4*BEAT
def hz(m):return 440*2**((m-69)/12)
def savewav(p,a):
    with wave.open(str(p),'wb') as f:
        f.setnchannels(2);f.setsampwidth(2);f.setframerate(SR)
        f.writeframes((np.clip(a,-1,1)*32767).astype('<i2').tobytes())
def compose(kind):
    rng=np.random.default_rng(2817+kind)
    dry=np.zeros((N,2));wet=np.zeros_like(dry)
    def add(sig,start,gain=1,pan=0,send=.4):
        start=round(start*SR);lo=max(0,start);hi=min(N,start+len(sig))
        if hi<=lo:return
        stereo=sig[lo-start:hi-start,None]*np.array([np.sqrt((1-pan)/2),np.sqrt((1+pan)/2)])*gain
        dry[lo:hi]+=stereo;wet[lo:hi]+=stereo*send
    # D minor / suspended voicings, harmonic movement every two shots.
    chords=[[50,57,64,65],[50,57,62,69],[46,53,60,65],[46,57,62,65],[48,55,62,67],[48,55,60,64],[45,52,59,62],[45,57,62,64],[50,57,62,64]]
    energy=[.55,.7,.9,.48,.6,.8,1.,.85,.45]
    for bar,ch in enumerate(chords):
        pos=bar*BAR
        # Slow breathing partials, pitch drift, no hard sawtooth or club supersaw.
        t=np.arange(round((BAR+2)*SR))/SR
        env=np.minimum(t/.8,1)*np.minimum((t[-1]-t)/1.8,1)
        env=np.maximum(env,0)**1.4
        for j,note in enumerate(ch):
            f=hz(note);phase=2*np.pi*f*t+.055*np.sin(2*np.pi*.23*t+j)
            sig=(np.sin(phase)+.18*np.sin(2*phase+.3)+.06*np.sin(3*phase))*env
            sig*=.9+.1*np.sin(2*np.pi*.31*t+j)
            add(sig,pos-.45,.046*energy[bar]*(1.15 if kind==2 else 1),(-.65+j*.43),.6)
        # Resonant soft struck notes; asymmetry leaves room for physical movement.
        offsets=[0,1.5,2.75] if kind!=2 else [.5,2.5]
        for k,b in enumerate(offsets):
            note=ch[(bar+k)%4]+(12 if (bar+k)%3==0 else 0)
            t=np.arange(round(2.8*SR))/SR;f=hz(note)
            e=(1-np.exp(-t/.012))*np.exp(-t/(.55+.18*k))
            sig=np.sin(2*np.pi*f*t+.75*np.exp(-t/.18)*np.sin(2*np.pi*f*2*t))
            sig+=.12*np.sin(2*np.pi*f*3.002*t)*np.exp(-t/.25)
            add(sig*e,pos+b*BEAT,.105*energy[bar],rng.uniform(-.7,.7),.65)
        # Low rounded pulse with an intentionally sparse/non-four-on-the-floor rhythm.
        beats=[0,2.5] if kind==0 else ([0,1.75,3] if kind==1 else [0])
        if bar in [3,8]:beats=[0]
        for b in beats:
            t=np.arange(round(.7*SR))/SR
            phase=2*np.pi*(42*t+31*.028*(1-np.exp(-t/.028)))
            e=(1-np.exp(-t/.004))*np.exp(-t/.16)
            add(np.sin(phase)*e,pos+b*BEAT,.26*energy[bar]*(.7 if kind==2 else 1),0,.05)
        # Dry brushed texture, quiet enough to read as breath rather than a hi-hat loop.
        for k,b in enumerate([.75,2.,3.5] if kind!=2 else [1.5]):
            t=np.arange(round(.18*SR))/SR
            n=rng.standard_normal(len(t));n=np.convolve(n,np.ones(12)/12,'same')
            e=(1-np.exp(-t/.006))*np.exp(-t/.035)
            add(n*e,pos+b*BEAT,.065*energy[bar],(-1)**k*.55,.25)
        # Air swells across selected cuts, unlike a repeated impact at every edit.
        if bar in [1,4,6]:
            t=np.arange(round(1.8*SR))/SR;n=rng.standard_normal(len(t))
            freq=np.fft.rfftfreq(len(n),1/SR)
            band=np.exp(-.5*((freq-1400)/700)**2)
            breath=np.fft.irfft(np.fft.rfft(n)*band,len(n))
            add(breath*np.sin(np.pi*t/t[-1])**2,pos+BAR-1.5,.035,(-1)**bar*.3,.8)
    # Diffuse stereo room: early reflections plus a decaying sparse noise tail.
    length=round(SR*3.8);rt=np.arange(length)/SR
    size=1<<((N+length-2).bit_length())
    for c in range(2):
        ir=rng.standard_normal(length)*np.exp(-rt/0.72)
        ir*=rng.random(length)<.08
        ir[:int(.035*SR)]=0
        ir=np.convolve(ir,np.ones(9)/9,'same')
        ir/=max(np.linalg.norm(ir),1e-9);ir*=.42
        for d,g in [(.071,.16),(.137,.12),(.229,.1),(.383,.06)]:ir[int((d+c*.007)*SR)]+=g
        dry[:,c]+=np.fft.irfft(np.fft.rfft(wet[:,c],size)*np.fft.rfft(ir,size),size)[:N]
    dry-=dry.mean(axis=0)
    t=np.arange(N)/SR
    envelope=np.minimum(t/.65,1)*np.minimum((30-t)/1.65,1)
    dry*=np.maximum(envelope,0)[:,None]
    dry=np.tanh(dry*1.3)
    dry*=.82/max(np.abs(dry).max(),1e-9)
    raw=HERE/f'score-{kind+1}-mix.wav';master=HERE/f'score-{kind+1}-master.wav'
    savewav(raw,dry)
    subprocess.run(['ffmpeg','-hide_banner','-v','warning','-n','-i',str(raw),'-af','highpass=f=28,loudnorm=I=-17:TP=-1.5:LRA=9','-ar',str(SR),'-c:a','pcm_s24le',str(master)],check=True)
    return master
sources=[ROOT/'strings-web/out/strings-web_showcase_30s_4k60.mp4',ROOT/'strings-space/out/strings-space_showcase_30s_4k60_reference_v2.mp4',ROOT/'strings-space/out/strings-space_showcase_30s_4k60_subject_only.mp4']
report=[]
for k,src in enumerate(sources):
    print(f'Composing original score {k+1}/3',flush=True)
    audio=HERE/f'score-{k+1}-master.wav'
    if '--mux-only' not in sys.argv:audio=compose(k)
    if '--compose-only' in sys.argv:continue
    dest=src.with_name(src.stem+'_music.mp4')
    assert src.exists(),f'Video not ready: {src}'
    subprocess.run(['ffmpeg','-hide_banner','-v','warning','-n','-i',str(src),'-i',str(audio),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','320k','-ar',str(SR),'-t','30','-movflags','+faststart','-metadata','comment=Original synthesized electronic contemporary-dance score; 72 BPM; no third-party samples',str(dest)],check=True)
    report.append({'video':str(dest),'source':str(src),'music':str(audio),'tempo':72,'bars':9,'seconds':30,'videoEncoding':'copied without re-encoding','musicOrigin':'Original procedural composition, no external samples'})
    print(f'Finished {dest.name}',flush=True)
if report:(HERE/'music-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
