// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

use tauri::Emitter;
use tauri_plugin_shell::ShellExt;



use tauri_plugin_shell::process::CommandEvent;

use std::sync::{Arc, Mutex};
use tauri::{State, Manager};
use tauri_plugin_shell::process::CommandChild;
use tauri_plugin_global_shortcut::{Code, Modifiers, Shortcut, ShortcutState};

struct SidecarHandle(Arc<Mutex<Option<CommandChild>>>);

#[tauri::command]
fn trigger_capture(state: State<SidecarHandle>) {
    if let Some(child) = state.0.lock().unwrap().as_mut() {
        let cmd = "{\"command\": \"capture\"}\n";
        let _ = child.write(cmd.as_bytes());
    }
}

#[tauri::command]
fn decompose_task(state: State<SidecarHandle>, text: String) {
    if let Some(child) = state.0.lock().unwrap().as_mut() {
        // Escaping might be needed if text contains quotes. 
        // Using serde_json is better but let's do manual compatible string for now to avoid dependency hell if possible.
        // Actually, tauri includes serde_json.
        let payload = serde_json::json!({
            "command": "decompose",
            "text": text
        });
        let mut cmd_str = payload.to_string();
        cmd_str.push('\n');
        let _ = child.write(cmd_str.as_bytes());
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let sidecar_handle = SidecarHandle(Arc::new(Mutex::new(None)));

    tauri::Builder::default()
        .manage(sidecar_handle)
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_opener::init())
        .plugin(
            tauri_plugin_global_shortcut::Builder::new()
                .with_shortcut(Shortcut::new(Some(Modifiers::ALT), Code::Space))
                .expect("Failed to register global shortcut")
                .with_handler(|app, shortcut, event| {
                    if event.state == ShortcutState::Pressed {
                        if shortcut.matches(Modifiers::ALT, Code::Space) {
                            if let Some(window) = app.get_webview_window("main") {
                                if window.is_visible().unwrap_or(false) {
                                    let _ = window.hide();
                                } else {
                                    let _ = window.show();
                                    let _ = window.set_focus();
                                }
                            }
                        }
                    }
                })
                // .build(), // Replaced by expect logic 
                .build(),
        )
        .invoke_handler(tauri::generate_handler![greet, trigger_capture, decompose_task])
        .setup(|app| {
            let handle = app.handle().clone();
            let state = app.state::<SidecarHandle>();
            let sidecar_arc = state.0.clone();

            tauri::async_runtime::spawn(async move {
                let (mut rx, child) = handle.shell().sidecar("phoenix-tracker")
                    .expect("failed to create sidecar")
                    .spawn()
                    .expect("failed to spawn sidecar");
                
                // Store child in state
                *sidecar_arc.lock().unwrap() = Some(child);

                while let Some(event) = rx.recv().await {
                    if let CommandEvent::Stdout(line) = event {
                        let line_str = String::from_utf8_lossy(&line);
                        // Emit to frontend (id: "telemetry")
                         let _ = handle.emit("telemetry", line_str.to_string());
                    }
                }
            });
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
