import json
import os
import re
import shutil
import subprocess
import time
import urllib.request
from pathlib import Path

TD_BIN = Path(r"D:\Derivative\TouchDesigner.2025.32460\bin")
STARTER_TOE = Path(r"D:\Codex\workspace\td-mcp-bootstrap\work\Starter.toe")
OUT_DIR = Path(r"D:\Kuanfuweimu\2-Commission\VJ Commission\DENZA N\td_wall_floor_pops")
TARGET_TOE = OUT_DIR / "DENZA_Z_WallFloor_Mapping_POPs.toe"
PORT = 13319

# Clean any prior build attempt of TARGET_TOE
for p in [TARGET_TOE, Path(str(TARGET_TOE) + ".toc"), Path(str(TARGET_TOE) + ".dir")]:
    if p.is_dir():
        shutil.rmtree(p)
    elif p.is_file():
        p.unlink()

shutil.copy2(STARTER_TOE, TARGET_TOE)
subprocess.run([str(TD_BIN / "toeexpand.exe"), str(TARGET_TOE)], capture_output=True)
exp_dir = Path(str(TARGET_TOE) + ".dir")
assert (exp_dir / "TDMCP.parm").is_file(), "TDMCP.parm missing after toeexpand"

# Set TDMCP port to 13319 so it does not collide with 13316
parm_path = exp_dir / "TDMCP.parm"
parm_txt = parm_path.read_text(encoding="utf-8")
parm_txt = re.sub(r"^Port\s+\d+\s+\d+$", f"Port 0 {PORT}", parm_txt, flags=re.M)
parm_path.write_text(parm_txt, encoding="utf-8")

# Enable performonminimize on root (.parm) so hidden window cooks at 60fps!
root_parm = exp_dir / ".parm"
root_parm.write_text("?\nperformonminimize 0 on\n?\n", encoding="utf-8")

subprocess.run([str(TD_BIN / "toecollapse.exe"), str(TARGET_TOE)], capture_output=True)
shutil.rmtree(exp_dir, ignore_errors=True)
toc_file = Path(str(TARGET_TOE) + ".toc")
if toc_file.is_file():
    toc_file.unlink()

print("Prepared TARGET_TOE:", TARGET_TOE, "size:", TARGET_TOE.stat().st_size, flush=True)
