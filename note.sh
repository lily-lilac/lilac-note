#!/usr/bin/env bash
# 桌面便签控制脚本
# 用法：source 本文件后，使用 note start / stop / restart

PROJECT_DIR="$HOME/dev/lilac-note"
SCRIPT="$PROJECT_DIR/scripts/desktop_note.py"

note() {
    local action="${1:-start}"
    case "$action" in
        start)
            if pgrep -f "$SCRIPT" > /dev/null; then
                echo "📝 笔记已在运行中"
                return 0
            fi
            (uv run --project "$PROJECT_DIR" python "$SCRIPT" > /dev/null 2>&1 &)
            echo "✨ 笔记已启动"
            ;;
        stop)
            if pkill -f "$SCRIPT"; then
                echo "🛑 笔记已停止"
            else
                echo "笔记未在运行"
            fi
            ;;
        restart)
            pkill -f "$SCRIPT" 2>/dev/null
            sleep 0.3
            (uv run --project "$PROJECT_DIR" python "$SCRIPT" > /dev/null 2>&1 &)
            echo "🔄 笔记已重启"
            ;;
        *)
            echo "用法: note {start|stop|restart}"
            ;;
    esac
}
