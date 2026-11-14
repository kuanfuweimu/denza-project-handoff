import json
import os
import re
import shutil
import subprocess
import time
import urllib.request
from pathlib import Path

TD_BIN = Path(r"D:\Derivative\TouchDesigner.2025.32460\bin")
TD_EXE = TD_BIN / "TouchDesigner.exe"
STARTER_TOE = Path(r"D:\Codex\workspace\td-mcp-bootstrap\work\Starter.toe")
OUT_DIR = Path(r"D:\Kuanfuweimu\2-Commission\VJ Commission\DENZA N\td_wall_floor_pops")
PREVIEW_DIR = OUT_DIR / "td_live_previews"
PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
TARGET_TOE = OUT_DIR / "DENZA_Z_WallFloor_Mapping_POPs.toe"
PORT = 13319
URL = f"http://127.0.0.1:{PORT}/mcp"

# 1. Prepare fresh TARGET_TOE from Starter.toe (build 2025.32460)
for p in list(OUT_DIR.glob("DENZA_Z_WallFloor_Mapping_POPs*")):
    if p.is_dir():
        shutil.rmtree(p, ignore_errors=True)
    else:
        p.unlink(missing_ok=True)

shutil.copy2(STARTER_TOE, TARGET_TOE)
subprocess.run([str(TD_BIN / "toeexpand.exe"), str(TARGET_TOE)], capture_output=True)
exp_dir = Path(str(TARGET_TOE) + ".dir")
parm_path = exp_dir / "TDMCP.parm"
parm_txt = parm_path.read_text(encoding="utf-8")
parm_txt = re.sub(r"^Port\s+\d+\s+\d+$", f"Port 0 {PORT}", parm_txt, flags=re.M)
parm_path.write_text(parm_txt, encoding="utf-8")
(exp_dir / ".parm").write_text("?\nperformonminimize 0 on\n?\n", encoding="utf-8")
subprocess.run([str(TD_BIN / "toecollapse.exe"), str(TARGET_TOE)], capture_output=True)
shutil.rmtree(exp_dir, ignore_errors=True)
Path(str(TARGET_TOE) + ".toc").unlink(missing_ok=True)

opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}

def rpc(method, params, ident=1, timeout=30):
    payload = {"jsonrpc": "2.0", "id": ident, "method": method, "params": params}
    req = urllib.request.Request(URL, data=json.dumps(payload).encode("utf-8"), headers=headers)
    with opener.open(req, timeout=timeout) as resp:
        session = resp.headers.get("Mcp-Session-Id")
        if session:
            headers["Mcp-Session-Id"] = session
        body = resp.read().decode("utf-8")
    if body.startswith("event:") or body.startswith("data:"):
        messages = [json.loads(line[5:].strip()) for line in body.splitlines() if line.startswith("data:")]
        result = next(m for m in messages if m.get("id") == ident)
    else:
        result = json.loads(body)
    if "error" in result:
        raise RuntimeError(str(result["error"]))
    return result["result"]

startup = subprocess.STARTUPINFO()
startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
startup.wShowWindow = 0
proc = subprocess.Popen([str(TD_EXE), str(TARGET_TOE)], cwd=str(OUT_DIR), startupinfo=startup)
print(f"Launched TouchDesigner helper PID={proc.pid} on {TARGET_TOE}...", flush=True)

try:
    deadline = time.monotonic() + 45
    while time.monotonic() < deadline:
        try:
            rpc("initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "denza-mcp-builder", "version": "1.0"}
            }, 1, timeout=4)
            break
        except Exception:
            time.sleep(1.0)

    notif = urllib.request.Request(URL, data=json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}).encode("utf-8"), headers=headers)
    with opener.open(notif, timeout=5):
        pass

    # Execute td_build_all.py inside TouchDesigner via MCP execute_code
    code_str = (OUT_DIR / "td_build_all.py").read_text(encoding="utf-8")
    exec_res = rpc("tools/call", {"name": "execute_code", "arguments": {"code": code_str}}, 2, timeout=60)
    print("Execute result:", exec_res["content"][0]["text"], flush=True)

    # Render live previews from TouchDesigner TOPs for verification
    snap_code = f"""
import os
prev_dir = r"{PREVIEW_DIR}"
P = op('/project1/z_dance_pops')
M = op('/project1/mapping_wall_floor')

# Force cook and save previews for Chapter 1, Chapter 3 (Orange), Chapter 5 (Z-Grid)
def cook_all():
    for op_p in [
        '/project1/z_dance_pops/null_pops_wall',
        '/project1/z_dance_pops/null_pops_floor',
        '/project1/mapping_wall_floor/null_content_wall',
        '/project1/mapping_wall_floor/null_content_floor',
        '/project1/mapping_wall_floor/null_out_WALL',
        '/project1/mapping_wall_floor/null_out_FLOOR',
        '/project1/mapping_wall_floor/sim_preview/render_sim',
        '/project1/mapping_wall_floor/null_sim_preview',
    ]:
        op(op_p).cook(force=True)

for ch_idx, ch_tag in [(0, 'ch1_axis'), (2, 'ch3_orange'), (4, 'ch5_zgrid')]:
    P.par.Chapter.menuIndex = ch_idx
    M.par.Testpattern = False
    cook_all()
    P.op('null_pops_wall').save(os.path.join(prev_dir, f'td_pops_wall_{{ch_tag}}.jpg'))
    P.op('null_pops_floor').save(os.path.join(prev_dir, f'td_pops_floor_{{ch_tag}}.jpg'))
    M.op('null_sim_preview').save(os.path.join(prev_dir, f'td_sim_3d_{{ch_tag}}.jpg'))

# Also save UV Template calibration preview
M.par.Testpattern = True
cook_all()
M.op('null_out_WALL').save(os.path.join(prev_dir, 'td_proj1_wall_uv_cal.jpg'))
M.op('null_out_FLOOR').save(os.path.join(prev_dir, 'td_proj2_floor_uv_cal.jpg'))
M.op('null_sim_preview').save(os.path.join(prev_dir, 'td_sim_3d_uv_cal.jpg'))

# Leave in live POPs Chapter 5 (Z-Matrix & Tether Grid) mode for immediate use
M.par.Testpattern = False
P.par.Chapter.menuIndex = 4
print("Saved live TD TOP snapshots to", prev_dir)
"""
    snap_res = rpc("tools/call", {"name": "execute_code", "arguments": {"code": snap_code}}, 3, timeout=60)
    print("Snapshot result:", snap_res["content"][0]["text"], flush=True)

    # Check errors across /project1
    errs = rpc("tools/call", {"name": "get_errors", "arguments": {"path": "/project1"}}, 4, timeout=20)
    print("Errors check:", errs["content"][0]["text"], flush=True)

    # Save project to DENZA_Z_WallFloor_Mapping_POPs.toe
    save_res = rpc("tools/call", {"name": "save_project", "arguments": {"path": str(TARGET_TOE)}}, 5, timeout=30)
    print("Save result:", save_res["content"][0]["text"], flush=True)

finally:
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()
    for bkp in OUT_DIR.glob("*.1.toe"):
        bkp.unlink(missing_ok=True)
    print("Done.", flush=True)
