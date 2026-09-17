# 打包可行性验证 Spike（阶段零 · 并行线 · 阶段一开工前提）

> **目的不是"做出一个能跑的包"，而是拿到四个数字、回答一个是否**（PRD 第七章附录）。
> 定位：验不过（体积失控 / 打不出包 / 冷启动不可接受），桌面端方案必须重谈。

## 验证架构（与 PRD 12.6 定案一致）

```
┌─ Tauri 外壳（Rust，极薄：只管窗口/sidecar 生命周期/通信） ─┐
│  ┌─ WebView2：静态 index.html（计时界面 + pandoc 测试） ─┐ │
│  └───────────────────────────────────────────────────────┘ │
│        │ invoke(进程启动时刻)      │ fetch http://127.0.0.1  │
│  ┌─────▼──────── sidecar ─────────▼──────────────────────┐ │
│  │  scimate-kernel.exe（PyInstaller onefile，纯标准库）    │ │
│  │  · /status  内核就绪     · /metrics 启动计时落盘        │ │
│  │  · /pandoc  调用随包分发的 pandoc.exe（结论一）          │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
安装包资源：pandoc.exe（3.11，静态大二进制）→ resources/pandoc/
```

## 目录

| 路径 | 内容 |
|---|---|
| `kernel/kernel.py` | Python 内核（标准库实现 HTTP 服务） |
| `kernel/pandoc/pandoc.exe` | 随包分发的 pandoc（开发态位置） |
| `app/ui/index.html` | 前端计时界面（无框架、无 npm 依赖） |
| `app/src-tauri/` | Tauri v2 外壳（sidecar 配置、WebView2 引导安装） |
| `REPORT.md` | **验证结果：四个数字 + 两项结论** |

## 复现步骤

```bash
# 1. Python 内核 → 单文件 exe（需 Python 3.13 + pyinstaller）
cd kernel
python -m venv .venv-build && .venv-build/Scripts/pip install pyinstaller
.venv-build/Scripts/python -m PyInstaller --onefile --name scimate-kernel \
    --distpath dist --workpath build_tmp --specpath build_tmp kernel.py

# 2. 放入 sidecar 位置（带目标三元组后缀）
mkdir -p ../app/src-tauri/binaries
cp dist/scimate-kernel.exe ../app/src-tauri/binaries/scimate-kernel-x86_64-pc-windows-msvc.exe

# 3. 图标（占位图标已生成；换正式图标时替换 icons-src/icon.png 重跑）
cd ../app && npx tauri icon src-tauri/icons-src/icon.png

# 4. 出 Windows 安装包（NSIS，currentUser 安装，WebView2 downloadBootstrapper）
npx tauri build

# 5. 安装并启动，读计时
#    界面显示两个冷启动秒数；同时落盘 %TEMP%\scimate-spike-metrics.log
```

## 测量口径

| 数字 | 口径 |
|---|---|
| 安装包体积 | NSIS 产物 `.exe` 的磁盘大小（内核含 pandoc，不含科学计算库） |
| 冷启动 → 界面可用 | 前端脚本执行时刻 − Rust 记录的外壳进程启动时刻（epoch ms 差） |
| 冷启动 → 内核就绪 | 前端首次成功 GET `/status` 时刻 − 外壳进程启动时刻 |
| WebView2 引导安装 | 本机已装 WebView2，只能验证打包配置正确；干净机器实测后补 |
