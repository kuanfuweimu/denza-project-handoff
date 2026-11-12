from pathlib import Path
import json,re,html,shutil

ROOT=Path(__file__).resolve().parents[3]
PROJECT=ROOT/'04_演示稿'/'denza-deck'
DIST=PROJECT/'dist'
WORK=Path(__file__).resolve().parent
SKILL=WORK/'template'
M=json.loads((DIST/'assets'/'media-manifest.json').read_text(encoding='utf-8'))
if isinstance(M,dict) and 'assets' in M:M=M['assets']
E=lambda x:html.escape(str(x),quote=True)
slides=[]
def img(key,caption='',cls=''):
 a=M[key]
 return f'<figure class="media {cls}"><button class="image-open" data-image="{E(a["src"])}" aria-label="放大图片"><img src="{E(a["src"])}" alt="{E(caption or key)}" loading="lazy" width="{a["width"]}" height="{a["height"]}"></button>{f"<figcaption>{E(caption)}</figcaption>" if caption else ""}</figure>'
def vid(key,caption):
 a=M[key]
 return f'<figure class="media"><video controls playsinline preload="none" poster="{E(a["poster"])}" aria-label="{E(caption)}"><source src="{E(a["src"])}" type="video/mp4"></video><figcaption>{E(caption)}</figcaption></figure>'
def source(url,label='原始来源'):
 return f'<a class="source" href="{E(url)}" target="_blank" rel="noopener noreferrer"><span>{E(label)} ↗</span><span class="source-url">{E(url)}</span></a>'
def add(id,title,body,subtitle='',section='',notes=None,layout='S22',cls=''):
 slides.append(dict(id=id,title=title,body=body,subtitle=subtitle,section=section,notes=notes or [title],layout=layout,cls=cls))
def para(s):return f'<p class="lead-copy">{E(s)}</p>'
def pair(*parts,cls=''):return f'<div class="media-grid cols-{len(parts)} {cls}">'+''.join(parts)+'</div>'
def yt(key,video_id,title,creator,description):
 return '<div class="reference-layout link-card">'+img(key,title+' · 视频封面')+'<aside><h3>'+E(creator)+'</h3>'+para(description)+source(f'https://www.youtube.com/watch?v={video_id}','YouTube 原片')+f'<button class="play-remote" data-video="https://www.youtube.com/embed/{E(video_id)}" data-url="https://www.youtube.com/watch?v={E(video_id)}" data-title="{E(title)}">播放原视频 ↗</button><p class="network-note">静帧可直接查看；原视频播放取决于 YouTube 访问情况。</p></aside></div>'

add('cover','DENZA Z','<div class="cover-copy"><h1>DENZA Z</h1><p>空间与动态视觉参考</p><div class="cover-topics">墙面双投影<br>吊顶投影<br>LED 棚</div></div>',section='概览',layout='S03',cls='cover')
add('three-scenes','三个场景',pair(
 '<div class="overview-item"><h3>墙面双投影</h3><p>墙面结构、线条生长<br>与人物关系</p></div>',
 '<div class="overview-item"><h3>吊顶投影</h3><p>顶部结构、吊挂装置<br>与多层介质</p></div>',
 '<div class="overview-item"><h3>LED 棚</h3><p>屏幕画布、舞者分镜<br>与拍摄配合</p></div>'),section='概览',layout='S05')
add('wall-projection','场景1  墙面双投影',img('projection_cover','双投影覆盖与吊顶遮挡示意'),section='墙面双投影')
add('wall-model','空间结构',pair(img('skp_iso','空间整体'),img('skp_front','墙面正视'),img('skp_top','俯视布局')),subtitle='由 SketchUp 几何生成的结构视图，保留原模型作为尺寸依据',section='墙面双投影',layout='S16')
add('td-preview','TouchDesigner 工程预览',img('td_preview','既有 TD 工程的存档预览画面'),subtitle='墙面双投影的映射与内容预览',section='墙面双投影')
add('mapping-coverage','机位与覆盖',pair(img('plan_c','存档方案 C 的机位平面'),'<div class="column">'+img('coverage_c','覆盖展开')+para('几何模拟覆盖约 86.1%，阴影约 13.9%。机位和投影机参数仍需现场复核。')+'</div>'),section='墙面双投影',layout='S08')
add('rope-growth','从 0 到 1 生长的绳子',img('rope_dance','用户补充的动态形态参考'),subtitle='线条出现、延伸、缠绕，逐步构成包围人物的形态',section='墙面双投影')
add('line-space','线条与人物尺度',pair(vid('line_video','线条投影视频参考'),img('line_still','同组空间画面')),subtitle='观察线条的方向、密度以及前后层次',section='墙面双投影',layout='S08')
add('light-flow','光流运动',vid('flow_video','用户提供的运动参考'),subtitle='以线条的速度、转向和聚散组织节奏',section='墙面双投影')
add('spatial-points','点阵与空间包围',vid('points_video','用户提供的空间点阵参考'),subtitle='观察顶部、墙面与柱体之间的连续关系',section='墙面双投影')
add('ring-lines','环幕线条参考',pair(*[img('ring'+str(i).zfill(2)) for i in [1,2,3]]),subtitle='线束延展、交织与结构密度',section='墙面双投影',layout='S16')
add('ring-transform','环幕形态变化',pair(*[img('ring'+str(i).zfill(2)) for i in [4,5,6]]),subtitle='旋转、汇聚与消散',section='墙面双投影',layout='S16')

refs=json.loads((WORK/'research-assets'/'reference_sources.json').read_text(encoding='utf-8'))['references']
keys=['monocolor_entangled','monocolor_noosphere','ouchhh_poetic','ouchhh_datamonolith']
for ref,key in zip(refs,keys):
 caption=ref['attribution']+('；官方项目视觉图' if 'not_site_photo' in ref['image_kind'] else '')
 body='<div class="reference-layout">'+img(key,caption)+'<aside><h3>'+E(ref['creator'])+'</h3>'+para(ref['description'])+'<p class="reference-note">参考方向<br>'+E(ref['application_note'])+'</p><div class="reference-links">'+source(ref['source_url'],'官方作品页')+source(ref['channel_or_site_url'],'频道 / 官网')+source(ref['play_url'],'作品视频')+'</div></aside></div>'
 add('ref-'+key.replace('_','-'),ref['title'],body,section='作品参考',notes=[ref['description'],ref['application_note'],'来源：'+ref['source_url']],layout='S08')

add('homeomorphism','HOMEOMORPHISM',yt('youtube_cern','eXduT_mdbQc','HOMEOMORPHISM · Dome A/V Performance_CERN','Ouchhh Studio','穹顶视听演出参考。重点观察点群、线状结构与包围式空间的视觉关系。'),subtitle='穹顶空间 / 数据影像',section='作品参考')
add('cinematique','Cinématique',yt('youtube_cinematique','CknHVdMZ5xg','Cinématique','Adrien M & Claire B','舞台表演与数字图形的关系参考。重点观察人物尺度、线条和空间形变之间的配合。'),subtitle='身体 / 数字图形 / 空间形变',section='作品参考')
add('hakanai','Hakanaï',yt('youtube_hakanai','xvJNia3z11I','Hakanaï','Adrien M & Claire B','舞者与立体投影空间的关系参考。重点观察网格的包围感，以及图形变化如何回应身体。'),subtitle='舞者 / 立体投影 / 网格空间',section='作品参考')
add('dance-grid','舞者与变形网格',img('dance_grid','用户补充的表演画面参考'),subtitle='人物移动与地面空间的形变关系',section='作品参考')
add('data-film','黑白数据影像',vid('data_video','用户提供的视频播放预览'),subtitle='观察点群、建筑轮廓和人物的显隐关系',section='作品参考')

add('ceiling-scene','场景2  吊顶投影',pair(img('scene2_original','原有场景图'),img('ceiling_pdf08','客户美术方案第 8 页')),subtitle='投影朝向吊顶表面，顶部结构与实际投射面需对应确认',section='吊顶投影',layout='S08')
add('ceiling-model','吊顶结构',pair(img('skp_ceiling','SketchUp 结构仰视'),img('ceiling_pdf09','客户美术方案第 9 页')),section='吊顶投影',layout='S08')
add('hanging-layers','吊挂装置与光幕',pair(img('hanging_layers','吊挂光幕参考'),img('layers_pdf30','客户美术方案第 30 页')),subtitle='参考光线在多层介质之间的叠加关系',section='吊顶投影',layout='S08')
add('scrim-depth','旋涡与前后层次',pair(img('hanging_vortex','旋涡光影'),img('scrim_depth','半透明幕的前后层次')),section='吊顶投影',layout='S08')
add('layer-dimensions','多层半透明屏尺寸',img('layers_dims','中央面约 7000 × 5000 mm；侧面标注 5040 / 3360 mm'),subtitle='具体场景归属、有效投射面和层数待确认',section='吊顶投影')

add('led-space','场景3  LED 棚',pair(img('led_photo','LED 棚现场'),img('led_plan','LED 棚与黑棚位置')),subtitle='场地资料标示 LED 棚约 1200㎡，黑棚约 1100㎡',section='LED 棚',layout='S08')
add('led-screens','LED 屏幕与画布','''<table class="spec-table"><thead><tr><th>屏幕</th><th>物理尺寸</th><th>像素尺寸</th></tr></thead><tbody><tr><td>顶屏</td><td>18.24 × 18.24 m</td><td>7296 × 7296</td></tr><tr><td>墙屏</td><td>24 × 7.68 m</td><td>9600 × 3072</td></tr><tr><td>右移动屏</td><td>3.84 × 4.30 m</td><td>1536 × 1720</td></tr><tr><td>左移动屏</td><td>5.44 × 5.28 m</td><td>2176 × 2112</td></tr></tbody></table><p class="bottom-note">顶屏离地 7.68 m。数据来自既有 D34 参数截图，本次使用配置需与场地方复核。</p>''',section='LED 棚',layout='S21')
add('led-storyboard','舞者线条分镜',img('led_storyboard','原始分镜标注：纯色背景 + LED，准备 LED 背景'),section='LED 棚')
add('led-spec-source','LED 参数原图',img('led_specs','既有 D34 场地参数截图'),subtitle='保留原始资料，便于与场地方核对本次配置',section='LED 棚')
add('schedule-prep','准备与前两天拍摄','''<div class="schedule"><article><h3>11 / 14</h3><p>棚内打光<br>道具陈设布</p></article><article><h3>11 / 15</h3><p>早上路跑（女生）<br>LED 车内驾驶（女生）<br>投影布独舞（女生）</p></article><article><h3>11 / 16</h3><p>道具陈设线<br>LED 三台车外观特写<br>moco 长臂<br>预计下午彩排群舞</p></article></div>''',subtitle='按当前提供的拍摄排期整理',section='拍摄配合',layout='S11')
add('schedule-final','群舞与男生独舞','''<div class="schedule two"><article><h3>11 / 17</h3><p>群舞（舞团）<br>LED 车内驾驶（舞团女主）</p></article><article><h3>11 / 18</h3><p>独舞圆环（男生）<br>LED 车内驾驶（男生）</p></article></div>''',section='拍摄配合',layout='S11')
add('production-check','制作条件确认','''<div class="overview-grid"><article><h3>投影</h3><p>实际投射面和材质<br>机位、镜头与遮挡<br>演员及车辆活动范围</p></article><article><h3>LED</h3><p>本次启用的屏幕<br>服务器拼接画布<br>帧率、同步与交付编码</p></article><article><h3>内容</h3><p>线条生长的节奏<br>与舞者动作的配合<br>各段落的时长和切换</p></article></div>''',section='拍摄配合',layout='S05')
linkset=[('MONOCOLOR 频道','https://www.youtube.com/c/monocolor'),('Ouchhh 官网','https://ouchhh.tv/'),('HOMEOMORPHISM','https://www.youtube.com/watch?v=eXduT_mdbQc'),('Cinématique','https://www.youtube.com/watch?v=CknHVdMZ5xg'),('Hakanaï','https://www.youtube.com/watch?v=xvJNia3z11I')]
thumbs=['monocolor_entangled','ouchhh_poetic','youtube_cern','youtube_cinematique','youtube_hakanai']
effects=['Entangled Structures 的线束与 NOOSPHERE 的点云空间','POETIC AI 的建筑投影与 AI DATAMONOLITH 的数据雕塑','穹顶视听演出 / 数据结构','舞者与数字图形 / 空间形变','舞者与立体投影 / 变形网格']
add('reference-links','链接与画面对照','<div class="source-list">'+''.join('<article class="source-card">'+img(k,t)+'<div>'+source(u,t)+'<p>'+E(d)+'</p></div></article>' for (t,u),k,d in zip(linkset,thumbs,effects))+'</div>',subtitle='每个链接旁保留对应作品图；频道与官网以已选作品示意',section='来源',layout='S19')

gallery_file=WORK/'reference-galleries.json'
galleries=json.loads(gallery_file.read_text(encoding='utf-8')) if gallery_file.exists() else {}
def gallery_items(url):
 items=galleries.get(url,[])
 return '<div class="reference-gallery">'+''.join(img(a['key'],a['caption']).replace('</figcaption>','<a href="'+E(a['source_url'])+'" target="_blank" rel="noopener noreferrer">'+E(a['source_url'])+'</a></figcaption>') for a in items)+'</div>'
cards=[]
for n,((title,url),fallback,description) in enumerate(zip(linkset,thumbs,effects)):
 images=gallery_items(url) if galleries.get(url) else img(fallback,title)
 cards.append('<article class="source-card" id="reference-'+str(n+1)+'"><div class="source-card-info">'+source(url,title)+'<p>'+E(description)+'</p></div>'+images+'</article>')
for s in slides:
 if s['id']=='reference-links':
  s['body']='<div class="source-list">'+''.join(cards)+'</div>'
  s['subtitle']='完整网址、对应作品图与视觉效果放在一起；点击任意图片可放大'
 if s['id']=='cover':s['body']+='<p class="scroll-cue">向下浏览 ↓</p>'

sections=[]
for s in slides:
 header='' if s['id']=='cover' else '<header><h2>'+E(s['title'])+'</h2>'+('<p>'+E(s['subtitle'])+'</p>' if s['subtitle'] else '')+'</header>'
 sections.append('<section class="denza '+s['cls']+'" id="'+E(s['id'])+'" data-slide-id="'+E(s['id'])+'"><div class="stage">'+header+'<div class="slide-content">'+s['body']+'</div></div></section>')
css=(WORK/'scroll.css').read_text(encoding='utf-8')
js=(WORK/'scroll.js').read_text(encoding='utf-8')
page='''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>DENZA Z · 空间与动态视觉参考</title><meta name="description" content="DENZA Z 的墙面双投影、吊顶投影、LED 棚与动态视觉参考。"><meta name="robots" content="noindex,nofollow"><link rel="canonical" href="https://www.kuanfuweimu.com/presentations/denza/"><style>'''+css+'''</style></head><body><div class="page-nav"><a href="#cover">DENZA Z</a><nav aria-label="本页目录"><a href="#wall-projection">墙面投影</a><a href="#ceiling-scene">吊顶投影</a><a href="#led-space">LED 棚</a><a href="#reference-links">参考链接</a></nav></div><main id="content">'''+''.join(sections)+'''</main><footer class="page-footer"><span>作品归属及原始来源见各参考图。</span><a href="#cover">回到顶部 ↑</a></footer><div id="media-modal" class="denza-modal" hidden role="dialog" aria-modal="true" aria-label="放大图片与视频"><button class="modal-close" aria-label="关闭">关闭 ×</button><div class="modal-content"></div></div><script>'''+js+'''</script></body></html>'''
(DIST/'index.html').write_text(page,encoding='utf-8')
plan=[{k:v for k,v in s.items() if k!='body'} for s in slides]
(PROJECT/'演示分页与来源.json').write_text(json.dumps({'format':'vertical-scroll','sections':plan,'links':linkset,'references':refs,'galleries':galleries},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'sections':len(slides),'gallery_counts':{url:len(items) for url,items in galleries.items()},'index':str(DIST/'index.html'),'bytes':(DIST/'index.html').stat().st_size},ensure_ascii=False))
