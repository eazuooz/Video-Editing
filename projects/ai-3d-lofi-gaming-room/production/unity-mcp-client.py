"""Call the installed official Unity CLI MCP stdio server for this room only."""
from pathlib import Path
import argparse, datetime, json, queue, subprocess, threading, time

ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / "unity/LofiGamingRoomWeb"
CLI = Path("C:/Program Files/Unity Hub/resources/unity.exe")

def call(tool, arguments, timeout=55):
    process = subprocess.Popen(
        [str(CLI), "mcp", "--project-path", str(PROJECT), "--no-banner"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, encoding="utf-8", bufsize=1)
    responses = queue.Queue()
    threading.Thread(target=lambda: [responses.put(x) for x in process.stdout], daemon=True).start()
    def send(value):
        process.stdin.write(json.dumps(value) + "\n")
        process.stdin.flush()
    def receive(identity, seconds=55):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            try:
                line = responses.get(timeout=1)
            except queue.Empty:
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                continue
            if value.get("id") == identity:
                return value
        raise TimeoutError("Unity MCP response timed out")
    try:
        send({"jsonrpc":"2.0","id":1,"method":"initialize","params":{
            "protocolVersion":"2024-11-05","capabilities":{},
            "clientInfo":{"name":"yamyam-lofi-production","version":"1.0"}}})
        init = receive(1)
        if "error" in init:
            raise RuntimeError(init["error"])
        send({"jsonrpc":"2.0","method":"notifications/initialized","params":{}})
        send({"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":tool,"arguments":arguments}})
        result = receive(2, timeout)
        record = {"transport":"MCP stdio", "server":init["result"].get("serverInfo"),
                  "project":str(PROJECT), "tool":tool, "arguments":arguments, "response":result}
        out = ROOT / "projects/ai-3d-lofi-gaming-room/production/local"
        out.mkdir(parents=True, exist_ok=True)
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S")
        path = out / ("mcp-" + stamp + "-" + tool + ".json")
        path.write_bytes((json.dumps(record, ensure_ascii=False, indent=2) + "\n").encode())
        return path, result
    finally:
        process.stdin.close()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.terminate()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("tool")
    parser.add_argument("--arguments", default="{}")
    args = parser.parse_args()
    path, result = call(args.tool, json.loads(args.arguments))
    print(json.dumps({"record":str(path), "result":result}, ensure_ascii=False)[:10000])
