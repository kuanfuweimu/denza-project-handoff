import json,subprocess,concurrent.futures
from pathlib import Path
HERE=Path(__file__).parent
items=json.loads((HERE/'music-report.json').read_text(encoding='utf-8'))
def check(item):
    p=item['video'];stem=Path(p).stem
    meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',p]))
    v=next(s for s in meta['streams'] if s['codec_type']=='video');a=next(s for s in meta['streams'] if s['codec_type']=='audio')
    assert (v['width'],v['height'],v['r_frame_rate'],v['nb_frames'])==(3840,2160,'60/1','1800')
    assert abs(float(v['duration'])-30)<.02 and abs(float(a['duration'])-30)<.05
    assert a['channels']==2 and a['sample_rate']=='48000'
    md5=HERE/(stem+'-motion.md5')
    if not md5.exists():subprocess.run(['ffmpeg','-hide_banner','-v','error','-n','-i',p,'-map','0:v:0','-vf',"select='between(mod(n,200),60,69)'",'-fps_mode','passthrough','-f','framemd5',str(md5),'-map','0:a:0','-f','null','-'],check=True)
    rows=[r for r in md5.read_text().splitlines() if r and not r.startswith('#')]
    hashes=[r.rsplit(',',1)[1].strip() for r in rows]
    assert len(rows)==90 and len(set(hashes))==90
    aud=subprocess.run(['ffmpeg','-hide_banner','-i',p,'-vn','-af','loudnorm=I=-17:TP=-1.5:LRA=9:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
    stats=json.JSONDecoder().raw_decode(aud.stderr[aud.stderr.rfind('{'):])[0]
    assert float(stats['input_tp'])<0 and float(stats['input_i'])>-22
    return {'file':p,'resolution':[v['width'],v['height']],'fps':v['r_frame_rate'],'frames':v['nb_frames'],'seconds':v['duration'],'audio':{'codec':a['codec_name'],'sampleRate':a['sample_rate'],'channels':a['channels'],'integratedLUFS':stats['input_i'],'truePeakDBTP':stats['input_tp']},'fullDecode':'passed','sampledMotionFrames':len(rows),'uniqueMotionFrames':len(set(hashes)),'bytes':Path(p).stat().st_size}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(check,items))
(HERE/'validation.json').write_text(json.dumps(results,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(results,indent=2,ensure_ascii=False))
