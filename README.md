# Anki Due Auto-Foreground & Unminimize (macOS)
### ⚡ Anki 到期卡片自动唤醒与程序坞（Dock）解最小化插件

[![GitHub release](https://img.shields.io/github/v/release/XiaKaiYang/anki-due-auto-foreground?style=flat-square)](https://github.com/XiaKaiYang/anki-due-auto-foreground/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![Platform: macOS](https://img.shields.io/badge/Platform-macOS-lightgrey.svg?style=flat-square&logo=apple)](https://www.apple.com/macos)
[![Anki: 2.1 / 23+ / 24+ / 25+](https://img.shields.io/badge/Anki-2.1%20%7C%2023%2B%20%7C%2024%2B%20%7C%2025%2B-blueviolet?style=flat-square)](https://apps.ankiweb.net)

---

## 📖 痛点与背景 (Background & Problem)

很多考生在使用 Anki 复习（公考、考研、法考、医考、语言学习）时，经常遇到一个非常令人抓狂的场景：
1. 一批卡片刚刚全部刷完，提示“恭喜！当前牌组已学完”；
2. 此时随手点击黄色按钮把 Anki **最小化缩进 Dock 栏（程序坞）**，去浏览网页、看视频或写代码；
3. 按照记忆算法（如学习阶段步长 10 分钟、15 分钟），新卡片在几分钟后已悄悄**刷新到期**；
4. **但 macOS 下的 Anki 安静无声，缩在 Dock 栏里毫无动静，导致你完全错过最佳复习节奏！**

即使市面上有些简单的提醒脚本，也因为 macOS 严格的安全沙箱机制，无法真正把缩在 Dock 栏里的窗口弹出来。

本插件专为 **macOS 用户** 深度定制开发，彻底攻克这一痛点！

---

## ✨ 核心特性 (Key Features)

* 🚀 **从 Dock 栏全自动解最小化并弹至屏幕最前**：
  采用独创的 **【Qt 内部还原 + macOS 系统底层 AppleScript `reopen`】双保险机制**。即使窗口已被黄色按钮收缩至 Dock 栏，一旦有题到期，也能 100% 自动解开最小化，跃升至屏幕最前并获取焦点！
* ⏱️ **精准监听“刷完 $\rightarrow$ 刷新到期”生命周期**：
  后台静默检测，只有当你的待复习卡片数从 $0$ 变为 $>0$（新批次到期）时才会精准触发唤醒。
* 🔇 **智能防打扰 & 5分钟防轰炸冷却**：
  * 如果你当前正处于 Anki 界面操作，插件绝对保持静默，不重复弹窗抢焦点；
  * 自动唤醒后设置了 5 分钟冷却期，避免频繁强占屏幕焦点。
* 🔔 **系统级原生通知 & 提示音**：
  弹出窗口的同时，在 macOS 右上角推送原生系统通知，并播放清脆的 `Glass` 提示音。
* 🧪 **菜单栏内置一键自测工具**：
  顶部菜单栏提供 **【工具】$\rightarrow$【⚡ 测试：从 Dock 自动还原并置顶唤醒】**，自带 5 秒倒计时，让你亲眼见证从 Dock 栏自动弹出的效果。

---

## 🛠️ 安装方法 (Installation)

### 方式 1：下载 Release 离线包安装（推荐）
1. 前往 [Releases 页面](https://github.com/XiaKaiYang/anki-due-auto-foreground/releases) 下载最新的 `anki-due-auto-foreground.ankiaddon`；
2. 双击该文件，或在 Anki 菜单栏选择 **【工具】$\rightarrow$【附加组件】$\rightarrow$【从文件安装...】**；
3. 重启 Anki 即可启用！

### 方式 2：手动克隆 / 解压到插件目录
打开 Mac 终端，执行以下命令：
```bash
git clone https://github.com/XiaKaiYang/anki-due-auto-foreground.git ~/Library/Application\ Support/Anki2/addons21/due_reminder
```
重启 Anki 即可。

---

## ⚙️ 个性化配置 (Configuration)

在 Anki 菜单栏点击 **【工具】$\rightarrow$【附加组件】**，选中 `到期自动置顶唤醒` 并点击 **【设置】**：

```json
{
  "check_interval_seconds": 25,     // 检测频率（秒），默认 25 秒
  "cooldown_seconds": 300,          // 提醒冷却时间（秒），默认 5 分钟
  "sound": "Glass",                 // macOS 提示音（可填 Ping, Glass, Hero, Submarine 等）
  "enable_dock_unminimize": true    // 是否在最小化到 Dock 时自动还原窗口
}
```

---

## 📄 开源许可 (License)

本项目基于 [MIT License](LICENSE) 开源。欢迎提 Issue 与 PR！
