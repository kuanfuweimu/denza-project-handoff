from pathlib import Path
from PIL import Image
import numpy as np,json
p=Path(__file__).parent
settings=json.loads((p/'reference-settings.json').read_text(encoding='utf-8'))
gains=[];measurements=[]
for i in range(1,10):
    a=np.asarray(Image.open(p/f'previews/reference-v2-full-{i}.png').convert('RGB').resize((1920,1080))).astype(float)/255
    peak=float(np.quantile(a,.99));target=.88
    gain=float(np.clip(target*(1-peak)/max(.001,peak*(1-target)),1.,3.8))
    gains.append(round(gain,3));measurements.append({'scene':i,'beforeP99':round(peak,4),'gain':round(gain,3)})
settings['exportExposureCompensation']=gains
settings['notes']+=' Per-scene export exposure compensation aligns bright wire highlights to the reference (target P99 around 0.88); this is additional to the screenshot base Exposure 3.0.'
(p/'reference-settings.json').write_text(json.dumps(settings,ensure_ascii=False,indent=2),encoding='utf-8')
(p/'brightness-calibration.json').write_text(json.dumps(measurements,indent=2),encoding='utf-8')
print(measurements)
