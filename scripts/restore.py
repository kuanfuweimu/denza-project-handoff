"""Download authenticated Release assets, verify SHA256 and restore project files safely."""
import argparse,hashlib,json,shutil,subprocess,zipfile
from pathlib import Path,PurePosixPath
REPO=Path(__file__).resolve().parents[1]
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
    return h.hexdigest()
def contained(root,relative):
    rel=PurePosixPath(relative)
    if rel.is_absolute() or '..' in rel.parts or any(':' in p for p in rel.parts):raise ValueError(f'Unsafe relative path: {relative}')
    dest=(root/Path(*rel.parts)).resolve()
    if not dest.is_relative_to(root.resolve()):raise ValueError(f'Path escapes destination: {dest}')
    return dest
def selected(e,scope):
    if scope=='all':return True
    p=PurePosixPath(e['path']);parts=p.parts
    if parts[0]=='DENZA 2':
        return len(parts)==3 or (len(parts)>3 and parts[2].startswith(('00_','01_','02_','03_')))
    return parts[0]=='DENZA N' and len(parts)==2
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--scope',choices=['all','projection'],default='projection')
    ap.add_argument('--destination',type=Path,required=True)
    ap.add_argument('--archives-dir',type=Path)
    ap.add_argument('--list',action='store_true')
    ap.add_argument('--verify-only',action='store_true')
    a=ap.parse_args();m=json.loads((REPO/'inventory/manifest.json').read_text(encoding='utf-8'))
    entries=[e for e in m['files'] if selected(e,a.scope)]
    needed={e['archive'] for e in entries};archives=[x for x in m['archives'] if x['name'] in needed]
    print(json.dumps({'scope':a.scope,'files':len(entries),'logicalBytes':sum(e['bytes'] for e in entries),'archiveBytes':sum(x['bytes'] for x in archives),'archives':[x['name'] for x in archives]},ensure_ascii=False),flush=True)
    if a.list:return
    dest=a.destination.resolve()
    cache=(a.archives_dir or dest/'DENZA N/_work/handoff-downloads').resolve()
    pending=[]
    for e in entries:
        p=contained(dest,e['path'])
        if p.exists():
            if p.is_file() and p.stat().st_size==e['bytes'] and sha(p)==e['sha256']:continue
            raise RuntimeError(f'Existing file differs; refusing overwrite: {p}')
        if a.verify_only:raise RuntimeError(f'Missing file: {p}')
        pending.append(e)
    if a.verify_only or not pending:
        print(f'All {len(entries)} files verified; no writes needed.');return
    cache.mkdir(parents=True,exist_ok=True)
    needed={e['archive'] for e in pending}
    for ar in archives:
        if ar['name'] not in needed:continue
        p=cache/ar['name']
        if not p.exists():
            if a.archives_dir:raise FileNotFoundError(f'Offline archive missing: {p}')
            subprocess.run(['gh','release','download',m['releaseTag'],'--repo',m['repository'],'--pattern',ar['name'],'--dir',str(cache)],check=True)
        if p.stat().st_size!=ar['bytes'] or sha(p)!=ar['sha256']:raise RuntimeError(f'Archive checksum mismatch: {p}')
        with zipfile.ZipFile(p) as z:
            for e in (e for e in pending if e['archive']==ar['name']):
                target=contained(dest,e['path']);target.parent.mkdir(parents=True,exist_ok=True)
                member=e['member'];contained(dest,member)
                with z.open(member) as src,target.open('xb') as out:
                    shutil.copyfileobj(src,out,8*1024*1024)
                if target.stat().st_size!=e['bytes'] or sha(target)!=e['sha256']:raise RuntimeError(f'File checksum mismatch: {target}')
        print(f'Restored and verified {ar["name"]}',flush=True)
    print(f'Complete: {len(entries)} files verified/restored into {dest}',flush=True)
if __name__=='__main__':main()
