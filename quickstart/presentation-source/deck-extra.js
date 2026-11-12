(()=>{
 const modal=document.getElementById('media-modal'), content=modal.querySelector('.modal-content');
 let returnFocus=null;
 function size(){document.documentElement.style.setProperty('--deck-scale',Math.min(innerWidth/1920,Math.max(1,innerHeight-64)/1080));}
 size();addEventListener('resize',size);
 const presenterButton=document.getElementById('ppt-presenter-btn');if(presenterButton)document.body.appendChild(presenterButton);
 const count=document.getElementById('page-count');count.textContent=((window.__currentSlideIndex||0)+1)+' / '+document.querySelectorAll('#deck>.slide').length;
 document.getElementById('slide-prev').onclick=()=>window.go((window.__currentSlideIndex||0)-1);
 document.getElementById('slide-next').onclick=()=>window.go((window.__currentSlideIndex||0)+1);
 document.getElementById('deck-fullscreen').onclick=async()=>{try{if(document.fullscreenElement)await document.exitFullscreen();else await document.documentElement.requestFullscreen();}catch{document.getElementById('deck-fullscreen').textContent='请横屏查看';}};
 function close(){modal.hidden=true;content.replaceChildren();returnFocus?.focus();}
 function open(button){returnFocus=button;modal.hidden=false;modal.querySelector('.modal-close').focus();document.querySelectorAll('#deck video').forEach(v=>v.pause());}
 document.addEventListener('click',e=>{
  const image=e.target.closest('.image-open');
  if(image){const full=document.createElement('img');full.src=image.dataset.image;full.alt=image.querySelector('img')?.alt||'参考图';content.replaceChildren(full);open(image);return;}
  const play=e.target.closest('.play-remote');
  if(play){const frame=document.createElement('iframe');frame.src=play.dataset.video;frame.title=play.dataset.title;frame.allow='autoplay; fullscreen; picture-in-picture';frame.allowFullscreen=true;
   const link=document.createElement('a');link.href=play.dataset.url;link.target='_blank';link.rel='noopener noreferrer';link.textContent=play.dataset.url;
   const note=document.createElement('p');note.textContent='若视频未加载，可打开上方原始链接；返回页面仍可查看参考图。';content.replaceChildren(frame,link,note);open(play);}
 });
 modal.querySelector('.modal-close').onclick=close;
 modal.addEventListener('click',e=>{if(e.target===modal)close();});
 document.addEventListener('keydown',e=>{if(!modal.hidden){if(e.key==='Escape'){e.preventDefault();close();}if(e.key==='Tab'){const focusable=[...modal.querySelectorAll('button,a,iframe')];const first=focusable[0],last=focusable.at(-1);if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus();}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus();}}e.stopImmediatePropagation();}},true);
 document.addEventListener('wheel',e=>{if(!modal.hidden||(matchMedia('(orientation:portrait) and (max-width:900px)').matches)){e.stopImmediatePropagation();}},true);
})();
