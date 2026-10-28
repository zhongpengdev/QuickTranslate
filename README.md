# QuickTranslate (极速桌面翻译字典)

一款专为桌面效率打造的极速翻译与词典工具（Raycast / Spotlight 极简浮窗风格）。支持自定义全局快捷键瞬间唤醒、鼠标光标自动聚焦、回车即刻翻译，提供英美标准发音、词性划分、详细释义与经典双语例句。

---

## ✨ 核心特性

1. **全局快捷键随时唤醒 (Hotkey Wake-up)**
   - 默认快捷键 `Ctrl+Alt+T`（可在设置中自定义为 `Alt+Space`、`F4`、`Ctrl+Shift+D` 等任意快捷键）。
   - 按下快捷键即可从后台瞬间呼出并置顶浮窗，再次按下或按 `ESC` 键即可一秒收起。
2. **光标自动聚焦 (Auto Focus)**
   - 唤醒时自动选中输入框并全选已有文本，无需手动点击鼠标，直接敲击键盘即可翻译。
3. **回车直接翻译 (Enter to Translate)**
   - 输入单词、短语、长句或段落后，直接按回车 `Enter` 触发极速并行翻译。
4. **全面专业的翻译内容**
   - 🔊 **标准发音 (Pronunciation)**：英式音标（UK）、美式音标（US）、拼音（Pinyin），支持一键点击播放原声真人朗读。
   - 📖 **词性分类与详细释义 (Explanations & POS)**：按名词 (n.)、动词 (v.)、形容词 (adj.) 等清晰划分，释义详尽准确。
   - 📝 **经典双语例句 (Example Sentences)**：自动高亮关键词，附带权威地道的中英文双语对照例句。
   - 💬 **长句整句翻译**：智能区分单词与长句，针对段落提供精准流畅的机器翻译与整句 TTS 朗读。
5. **100% 免费服务 (Fully Free Services)**
   - 集成有道词典开放 Web 端点与 Google Translate 免费端点，双引擎智能聚合与无缝容灾。
   - 无需申请注册任何收费 API Key，即开即用。
6. **极速与精准 (Speed & Precision)**
   - **多线程并行并发**：Youdao 与 Google 引擎后台异步并行请求，毫秒级返回结果，UI 从不卡顿。
   - **本地 SQLite 零延迟缓存**：查询过的词条自动沉淀到本地数据库，二次查询 0ms 瞬间显示。
7. **独立桌面程序打包 (Packaged Desktop App)**
   - 已使用 PyInstaller 编译为原生 Linux 可执行程序，并生成 `.desktop` 快捷方式，集成进系统应用菜单和系统托盘。

---

## 🚀 启动与运行

### 方式一：直接运行打包好的桌面端程序 (推荐)

```bash
# 启动可执行程序
./dist/QuickTranslate/QuickTranslate

# 或者在系统应用菜单 (GNOME / KDE) 中搜索 "QuickTranslate" 点击启动
```

### 方式二：通过 Python 源码运行

```bash
cd /home/zhongpeng/Projects/PythonProject/QuickTranslate
source venv/bin/activate
python3 run.py
```

---

## ⌨️ 快捷键指南

| 快捷键 | 功能描述 |
| :--- | :--- |
| **`Ctrl+Alt+T`** | 全局唤醒 / 隐藏窗口（可在设置中自定义） |
| **`Enter`** | 在输入框中直接触发翻译 |
| **`ESC`** | 隐藏翻译窗口至后台/系统托盘 |
| **`Ctrl + L`** | 快速聚焦搜索框并全选内容 |
| **`Ctrl + ,`** | 打开偏好设置对话框 |

---

## 🛠️ 项目目录结构

```
QuickTranslate/
├── assets/
│   └── icon.png                  # 应用高清图标
├── dist/
│   └── QuickTranslate/           # PyInstaller 打包产物目录
│       └── QuickTranslate        # 原生独立可执行二进制文件
├── quick_translate/
│   ├── config.py                 # 配置管理器 (JSON 持久化与热加载)
│   ├── hotkey.py                 # 全局快捷键监听 (pynput + Qt 信号)
│   ├── app.py                    # 应用程序主入口 & 事件循环
│   ├── translator/
│   │   ├── models.py             # 释义、例句与音标数据结构
│   │   ├── cache.py              # SQLite 极速持久化缓存
│   │   ├── audio.py              # 发音音频下载与非阻塞播放
│   │   ├── youdao.py             # 有道词典客户端 (音标/发音/词性/双语例句)
│   │   ├── google.py             # 谷歌翻译客户端 (整句翻译/多语种)
│   │   └── engine.py             # 双引擎智能聚合器
│   └── ui/
│       ├── styles.py             # 暗夜深色 / 浅色极简主题 QSS
│       ├── widgets.py            # 搜索框、音频胶囊按钮、词性徽章
│       ├── result_view.py        # 结构化卡片渲染视图
│       ├── settings_dialog.py    # 快捷键与偏好设置窗口
│       ├── tray_icon.py          # 系统托盘菜单管理
│       └── main_window.py        # 浮窗主界面与交互逻辑
├── tests/
│   └── test_app.py               # 自动化单元测试
├── build.py                      # 一键打包编译与安装脚本
├── quicktranslate.desktop        # Linux 桌面快捷方式
├── requirements.txt              # 依赖库列表
└── run.py                        # Python 启动脚本
```

---

## 📦 重新打包构建

如修改了源码需重新构建打包：

```bash
venv/bin/python3 build.py
```
构建脚本将自动重新生成二进制并更新 `~/.local/share/applications/quicktranslate.desktop`。
