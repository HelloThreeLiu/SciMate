#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SciMate 执行内核 —— 阶段零打包验证 Spike 版

这个内核只做三件事，全部用标准库（对应 PRD 12.6「内核保持轻量」纪律）：
1. /status   —— 报告内核就绪（冷启动计时用）
2. /metrics  —— 接收前端上报的启动计时，落盘到 %TEMP%\\scimate-spike-metrics.log
3. /pandoc   —— 调用随包分发的 pandoc.exe 做 Markdown -> HTML 转换（验证结论一：
                「含大二进制的组件打包后能否正常运行」）

计时约定：
- 内核进程启动即记录 KERNEL_START_MS（epoch 毫秒），stdout 打印一行 JSON（外壳可读）；
- 前端在 UI 就绪与内核就绪两个时点各上报一次，Rust 侧把进程启动时刻传给前端。
"""

import json
import os
import subprocess
import sys
import tempfile
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

PORT = int(os.environ.get("SCIMATE_KERNEL_PORT", "17890"))
KERNEL_START_MS = int(time.time() * 1000)
METRICS_LOG = os.path.join(tempfile.gettempdir(), "scimate-spike-metrics.log")


def find_pandoc():
    """在几个候选位置找 pandoc（开发态 / PyInstaller onefile / 安装包目录）。
    注意：Tauri NSIS 的 resources 映射可能把文件放在安装根目录且无 .exe 扩展名，一并兼容。"""
    names = ["pandoc.exe", "pandoc"] if os.name == "nt" else ["pandoc"]
    here = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, "frozen", False) else __file__))
    candidates = [os.environ.get("SCIMATE_PANDOC", "")]
    for n in names:
        candidates += [
            os.path.join(here, n),
            os.path.join(here, "pandoc", n),
            os.path.join(here, "..", "resources", "pandoc", n),
            os.path.join(here, "resources", "pandoc", n),
            os.path.join(here, "..", "..", "resources", "pandoc", n),
        ]
    for c in candidates:
        if c and os.path.isfile(c):
            return os.path.abspath(c)
    return None


PANDOC = find_pandoc()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):  # 安静模式
        pass

    def _json(self, obj, code=200):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/status":
            self._json({
                "ready": True,
                "kernel_start_ms": KERNEL_START_MS,
                "uptime_ms": int(time.time() * 1000) - KERNEL_START_MS,
                "python": sys.version.split()[0],
                "pandoc_found": bool(PANDOC),
            })
        elif path == "/pandoc":
            q = parse_qs(urlparse(self.path).query)
            text = q.get("text", ["# hello\n\n**SciMate spike** from pandoc inside packaged app."])[0]
            if not PANDOC:
                self._json({"ok": False, "error": "pandoc.exe not found"}, 500)
                return
            t0 = time.perf_counter()
            try:
                r = subprocess.run(
                    [PANDOC, "--from", "markdown", "--to", "html"],
                    input=text.encode("utf-8"), capture_output=True, timeout=30)
                dt = (time.perf_counter() - t0) * 1000
                if r.returncode == 0:
                    self._json({"ok": True, "html": r.stdout.decode("utf-8"),
                                "pandoc": PANDOC, "elapsed_ms": round(dt)})
                else:
                    self._json({"ok": False, "error": r.stderr.decode("utf-8", "replace")}, 500)
            except Exception as e:  # noqa: BLE001
                self._json({"ok": False, "error": str(e)}, 500)
        else:
            self._json({"error": "not found"}, 404)

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/metrics":
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length) or b"{}")
            data["received_ms"] = int(time.time() * 1000)
            with open(METRICS_LOG, "a", encoding="utf-8") as f:
                f.write(json.dumps(data, ensure_ascii=False) + "\n")
            self._json({"logged": True})
        else:
            self._json({"error": "not found"}, 404)


def main():
    print(json.dumps({"event": "kernel_started", "kernel_start_ms": KERNEL_START_MS,
                      "port": PORT, "pandoc_found": bool(PANDOC)}), flush=True)
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(json.dumps({"event": "kernel_listening", "elapsed_ms":
                      int(time.time() * 1000) - KERNEL_START_MS}), flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
