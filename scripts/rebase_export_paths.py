"""Rewrite original project root only in restored export-tool scripts; make backups."""
from pathlib import Path
import argparse
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--base',type=Path,required=True);a=ap.parse_args()
old='D:/Kuanfuweimu/2-Commission/VJ Commission/DENZA N'
root=(a.base/'DENZA N').resolve()
for sub in ['strings-space-render','strings-web-edit','showcase-music']:
    folder=root/'_work'/sub
    if not folder.is_dir():continue
    for p in folder.iterdir():
        if p.suffix not in {'.py','.js'}:continue
        text=p.read_text(encoding='utf-8');new=text.replace(old,root.as_posix()).replace(old.replace('/','\\'),str(root)).replace(old.replace('/','\\\\'),str(root).replace('\\','\\\\'))
        if new!=text:
            backup=p.with_name(p.name+'.before-rebase')
            if backup.exists():raise RuntimeError(f'Backup already exists: {backup}')
            backup.write_bytes(p.read_bytes());p.write_text(new,encoding='utf-8');print(p)
