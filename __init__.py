# -*- coding: utf-8 -*-
"""
Anki Due Auto-Foreground & Unminimize (macOS)
到期自动置顶唤醒与程序坞解收缩插件

Author: XiaKaiYang
License: MIT
"""

import subprocess
import time
from aqt import mw
from aqt.gui_hooks import profile_did_open
from aqt.qt import QTimer, QAction
from aqt.utils import tooltip

def get_config():
    """获取用户自定义配置，若未配置则读取默认值"""
    default_conf = {
        "check_interval_seconds": 25,
        "cooldown_seconds": 300,
        "sound": "Glass",
        "enable_dock_unminimize": True
    }
    if mw and mw.addonManager:
        conf = mw.addonManager.getConfig(__name__)
        if conf:
            default_conf.update(conf)
    return default_conf

last_due_count = 0
last_alert_time = 0

def is_anki_frontmost():
    """
    判断当前 Anki 是否处于前台聚焦状态（无论是主界面、复习界面、还是浏览/添加窗口）。
    当 Anki 处于前台聚焦时，用户已在操作或观看 Anki，无需任何弹窗、声音或 Dock 置顶唤醒打扰。
    """
    if not mw:
        return False

    # 1. 如果主窗口被最小化到 Dock 栏，则必然不是前台聚焦
    try:
        if mw.isMinimized():
            return False
    except Exception:
        pass

    # 2. Qt 层多窗口全局聚焦状态检查（覆盖 Reviewer、Browser、AddCards 及各子对话框）
    try:
        from aqt.qt import Qt, QApplication
        app = mw.app or QApplication.instance()
        if app:
            # ApplicationActive: 应用程序处于最前端且拥有系统焦点
            if app.applicationState() == Qt.ApplicationState.ApplicationActive:
                # 确认活跃窗口未被最小化
                active_win = app.activeWindow()
                if active_win and not active_win.isMinimized():
                    return True
                # 若 activeWindow 为 None，但拥有焦点控件或主窗口可见且未最小化
                if app.focusWidget() or (mw.isVisible() and not mw.isMinimized()):
                    return True
    except Exception:
        pass

    # 3. macOS 系统层 NSWorkspace 深度核验（毫秒级，最权威的 OS 级前台判定）
    try:
        from AppKit import NSWorkspace
        front_app = NSWorkspace.sharedWorkspace().frontmostApplication()
        if front_app:
            proc_name = (front_app.localizedName() or "").lower()
            bundle_id = (front_app.bundleIdentifier() or "").lower()
            if ("anki" in proc_name or "anki" in bundle_id) and not mw.isMinimized():
                return True
    except Exception:
        pass

    # 4. 传统兜底检查
    try:
        if mw.isActiveWindow() and not mw.isMinimized():
            return True
    except Exception:
        pass

    return False

def trigger_foreground(count, force=False):
    """
    双重保险唤醒机制：
    无论 Anki 是被最小化到 Dock（程序坞）、被黄色按钮收缩、还是隐藏（Cmd+H）或置于后台，
    都能 100% 自动解开最小化并强行弹到屏幕最前端！
    （当 Anki 已在前台聚焦时，自动静默退出，不打扰用户）
    """
    if not force and is_anki_frontmost():
        return

    conf = get_config()
    sound_name = conf.get("sound", "Glass")
    enable_unminimize = conf.get("enable_dock_unminimize", True)

    # 1. Qt 原生层还原窗口（自身即刻解开最小化）
    try:
        if enable_unminimize and mw.isMinimized():
            mw.showNormal()
        else:
            mw.show()
        mw.raise_()
        mw.activateWindow()
    except Exception as e:
        print(f"[DueReminder] Qt showNormal error: {e}")

    # 2. macOS 系统层深度唤醒（解决 Dock 栏最小化、隐藏与焦点置顶）
    unminimize_script = '''
            set visible to true
            repeat with w in windows
                try
                    if (value of attribute "AXMinimized" of w) is true then
                        set value of attribute "AXMinimized" of w to false
                    end if
                end try
            end repeat
    ''' if enable_unminimize else ''

    applescript = f'''
    tell application "System Events"
        if exists (process "Anki") then
            tell process "Anki"
                {unminimize_script}
            end tell
        end if
    end tell
    tell application "Anki"
        reopen
        activate
    end tell
    display notification "你有 {count} 张卡片已刷新到期，已自动从 Dock 弹出！" with title "Anki 刷题提醒" sound name "{sound_name}"
    '''
    try:
        subprocess.Popen(["osascript", "-e", applescript])
    except Exception as e:
        print(f"[DueReminder] AppleScript activation error: {e}")

def check_due_cards():
    """后台定时检查逻辑"""
    global last_due_count, last_alert_time

    if not mw or not mw.col or not mw.col.db:
        return

    try:
        # 查询当前所有已到期的卡片（新卡 + 学习中到期卡，排除已挂起）
        due_cards = mw.col.find_cards("is:due -is:suspended")
        due_count = len(due_cards)
    except Exception:
        return

    # ⭐ 核心防打扰：若 Anki 当前正处于前台聚焦状态（未最小化），则静默更新状态，绝不打扰
    if is_anki_frontmost():
        last_due_count = due_count
        last_alert_time = time.time()
        return

    conf = get_config()
    cooldown = conf.get("cooldown_seconds", 300)
    current_time = time.time()
    should_alert = False

    # 核心判断逻辑：
    # 1. 刚才卡片刷完（last_due_count == 0），现在到期刷新出新卡片（due_count > 0）
    # 2. 或者距上次提醒已超过冷却时间且仍有到期卡片未刷
    if due_count > 0:
        if last_due_count == 0:
            should_alert = True
        elif (current_time - last_alert_time) >= cooldown:
            should_alert = True

    last_due_count = due_count

    if should_alert:
        last_alert_time = current_time
        try:
            # 刷新 Anki 主界面，使牌组数字与列表立刻更新
            mw.reset()
        except Exception:
            pass

        trigger_foreground(due_count)

def test_trigger():
    """供用户测试：点击后有 5 秒时间把 Anki 最小化到 Dock 栏，5 秒后见证自动弹出"""
    tooltip("⚡ 测试启动：你有 5 秒钟时间点击黄色按钮将 Anki 最小化到 Dock 栏...", period=4500)
    QTimer.singleShot(5000, lambda: trigger_foreground(1, force=True))

def init_addon():
    conf = get_config()
    interval = conf.get("check_interval_seconds", 25)

    # 注册定时器
    if not hasattr(mw, "_due_reminder_timer"):
        timer = QTimer(mw)
        timer.timeout.connect(check_due_cards)
        timer.start(interval * 1000)
        mw._due_reminder_timer = timer

    # 在菜单栏添加测试按钮
    if not hasattr(mw, "_due_reminder_action"):
        action = QAction("⚡ 测试：从 Dock 自动还原并置顶唤醒", mw)
        action.triggered.connect(test_trigger)
        mw.form.menuTools.addAction(action)
        mw._due_reminder_action = action

# 绑定生命周期
profile_did_open.append(init_addon)

# 若此时 Profile 已开启，则立刻初始化
if mw and mw.col:
    init_addon()
