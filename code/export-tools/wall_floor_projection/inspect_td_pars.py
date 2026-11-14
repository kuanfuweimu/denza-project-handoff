import json
import subprocess
import time
import urllib.request
from pathlib import Path

TD_EXE = Path(r"D:\Derivative\TouchDesigner.2025.32460\bin\TouchDesigner.exe")
OUT_DIR = Path(r"D:\Kuanfuweimu\2-Commission\VJ Commission\DENZA N\td_wall_floor_pops")
TARGET_TOE = OUT_DIR / "DENZA_Z_WallFloor_Mapping_POPs.toe"
PORT = 13319
URL = f"http://127.0.0.1:{PORT}/mcp"

opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}

def rpc(method, params, ident=1, timeout=20):
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

try:
    deadline = time.monotonic() + 45
    while time.monotonic() < deadline:
        try:
            rpc("initialize", {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "denza-help", "version": "1.0"}}, 1, timeout=4)
            break
        except Exception:
            time.sleep(1.0)
    notif = urllib.request.Request(URL, data=json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}).encode("utf-8"), headers=headers)
    with opener.open(notif, timeout=5):
        pass

    res = rpc("tools/call", {"name": "execute_code", "arguments": {"code": """
import json
ops = [linePOP, copyPOP, circlePOP, gridPOP, noisePOP, transformPOP, lineMAT, annotateCOMP]
out = {}
for t in ops:
    o = op('/project1').create(t, '_tmp_inspect')
    out[t.__name__] = [(p.name, p.label, p.default) for p in o.pars()]
    o.destroy()
print(json.dumps(out, indent=2, default=str))
"""}}, 2, timeout=20)
    print(res["content"][0]["text"])
finally:
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except Exception:
        proc.kill()
