import json, sys, urllib.request
URL = "http://127.0.0.1:13316/mcp"
_id = [0]
def rpc(method, params=None):
    _id[0] += 1
    body = json.dumps({"jsonrpc": "2.0", "id": _id[0], "method": method, "params": params or {}}).encode("utf-8")
    req = urllib.request.Request(URL, body, {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"})
    with urllib.request.urlopen(req, timeout=170) as r:
        return json.loads(r.read().decode("utf-8"))
def call(name, **args):
    r = rpc("tools/call", {"name": name, "arguments": args})
    if "error" in r:
        return "ERROR " + json.dumps(r["error"], ensure_ascii=False)
    return "\n".join(c.get("text", "") for c in r["result"].get("content", []))
if __name__ == "__main__":
    rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "claude-direct", "version": "1"}})
    if sys.argv[1] == "list":
        for t in rpc("tools/list")["result"]["tools"]:
            print(t["name"], "-", json.dumps(list(t.get("inputSchema", {}).get("properties", {}).keys())))
    else:
        print(call(sys.argv[1], **json.loads(sys.argv[2] if len(sys.argv) > 2 else "{}")))
