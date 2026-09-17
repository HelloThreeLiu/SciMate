// SciMate 打包验证 Spike —— Rust 外壳
// 纪律（PRD 12.6 第五节）：Rust 侧保持极薄，只做窗口、sidecar 生命周期、
// 通信转发、系统集成四件事，不写业务逻辑。本文件全部行为：
// 1) 记录进程启动时刻（冷启动计时基准）；
// 2) 启动并守护 Python 内核 sidecar；
// 3) 向前端暴露进程启动时刻；
// 4) 退出时回收内核进程。

#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::time::{SystemTime, UNIX_EPOCH};

use tauri::Manager;
use tauri_plugin_shell::process::{CommandChild, CommandEvent};
use tauri_plugin_shell::ShellExt;

struct AppState {
    process_start_ms: u64,
    kernel_child: std::sync::Mutex<Option<CommandChild>>,
}

#[tauri::command]
fn get_process_start_ms(state: tauri::State<AppState>) -> u64 {
    state.process_start_ms
}

fn main() {
    let process_start_ms = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_millis() as u64)
        .unwrap_or(0);

    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .setup(move |app| {
            let sidecar = app.shell().sidecar("scimate-kernel").expect("sidecar 未配置");
            let (mut rx, child) = sidecar.spawn().expect("无法启动 Python 内核 sidecar");
            app.manage(AppState {
                process_start_ms,
                kernel_child: std::sync::Mutex::new(Some(child)),
            });
            tauri::async_runtime::spawn(async move {
                while let Some(event) = rx.recv().await {
                    match event {
                        CommandEvent::Stdout(line) => {
                            println!("[kernel] {}", String::from_utf8_lossy(&line))
                        }
                        CommandEvent::Stderr(line) => {
                            eprintln!("[kernel-err] {}", String::from_utf8_lossy(&line))
                        }
                        _ => {}
                    }
                }
            });
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![get_process_start_ms])
        .build(tauri::generate_context!())
        .expect("构建 Tauri 应用失败")
        .run(|app_handle, event| {
            if let tauri::RunEvent::Exit = event {
                if let Some(child) = app_handle
                    .state::<AppState>()
                    .kernel_child
                    .lock()
                    .unwrap()
                    .take()
                {
                    let _ = child.kill();
                }
            }
        });
}
