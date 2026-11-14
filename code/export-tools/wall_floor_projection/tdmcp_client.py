import json
import urllib.request

URL = "http://127.0.0.1:13316/mcp"
HEADERS = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}

def rpc(method, params, ident=1):
    payload = {"jsonrpc": "2.0", "id": ident, "method": method, "params": params}
    req = urllib.request.Request(URL, data=json.dumps(payload).encode("utf-8"), headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as resp:
        session = resp.headers.get("Mcp-Session-Id")
        if session:
            HEADERS["Mcp-Session-Id"] = session
        body = resp.read().decode("utf-8")
    if body.startswith("event:") or body.startswith("data:"):
        messages = [json.loads(line[5:].strip()) for line in body.splitlines() if line.startswith("data:")]
        result = next(m for m in messages if m.get("id") == ident)
    else:
        result = json.loads(body)
    if "error" in result:
        raise RuntimeError(str(result["error"]))
    return result["result"]

init_res = rpc("initialize", {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {"name": "denza-wall-floor-builder", "version": "1.0"}
}, 1)
notif = urllib.request.Request(URL, data=json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}).encode("utf-8"), headers=HEADERS)
with urllib.request.urlopen(notif, timeout=5):
    pass

tools = rpc("tools/list", {}, 2)
tool_names = [t["name"] for t in tools.get("tools", [])]
print("Tools:", tool_names)

info = rpc("tools/call", {"name": "project_info", "arguments": {}}, 3)
print("Project Info:", json.dumps(info, ensure_ascii=False, indent=2))
