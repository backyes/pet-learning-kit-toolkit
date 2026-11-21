# pet-learning-kit

把一篇英文原文变成一套**可读、可听、可练**的学习包：中英对照、CEFR 分级词汇注解、逐段朗读、听力题、拼写默写、错题本 —— 全部离线、零依赖、手机可读。

本仓库是这套方法的**公开版**：方法论（agent skill）、脚本，以及一个用公有领域文本跑通的完整示例。

> 🔗 在线示例：<https://backyes.github.io/pet-learning-kit/demo/alice-ch1.html>

---

## 这是什么

一套「读原著 + 备 PET」的工作流，包含两部分：

1. **`skills/english-reading-kit/`** —— 可复用的方法论
   9 步流水线：抓取 → 清洗 → 分段 → 1:1 翻译 → CEFR 分级 → 考试对齐 → TTS 音频 → 书页式排版 → 练习与打包。
   附 5 篇参考文档（排版 / 音频 / 考试 / 练习 / 验收）和 2 个脚本。

2. **`demo/alice-ch1.html`** —— 跑通的成品示例
   用《爱丽丝梦游仙境》第一章前五段（1865，公有领域）演示完整效果：
   连续书页式正文、浅色译文注脚、逐段朗读、8 个单词发音、60% 空缺的拼写默写。

---

## 快速看效果

```bash
git clone https://github.com/backyes/pet-learning-kit.git
cd pet-learning-kit/demo
open alice-ch1.html          # 或 python3 -m http.server 8765 后手机访问
```

在线版：<https://backyes.github.io/pet-learning-kit/demo/alice-ch1.html>

---

## 设计要点（都是踩过坑改出来的）

- **书页，不是卡片墙**：正文连续排版，译文降级为浅灰注脚，段落播放按钮放在页边（手机隐藏，改用「点读」模式）。早期版本给每段套卡片 + 独立按钮列，107 段变成 107 个小盒子，读不下去。
- **音频四粒度**：整篇 / 分节 / 逐段 / 单词。逐段是「点哪段读哪段」，单词服务于词汇和默写。
- **零 API key**：macOS `say` + `ffmpeg` 本地合成，英音 Daniel，64 kbps 单声道。
- **默写**：每个词遮住约 60% 字母（首尾必露），逐位报错（第几个字母、应为哪个、你写的是哪个）。
- **错题本**：`localStorage` 记录，答对一次消一格，清空即掌握，支持导出/导入。

---

## 目录

```
pet-learning-kit/
├── index.html                    入口页（GitHub Pages 首页）
├── demo/
│   ├── alice-ch1.html            完整示例
│   └── audio/                    para/ · words/ · full.mp3
└── skills/english-reading-kit/
    ├── SKILL.md
    ├── references/               layout · audio · exam · practice · verify
    └── scripts/                  make_audio.py · check_pages.py
```

---

## 自带检查

```bash
python3 skills/english-reading-kit/scripts/check_pages.py --root demo demo/alice-ch1.html
✓ demo/alice-ch1.html  9 audio refs, 1 scripts
```

检查项：HTML 标签平衡、音频引用是否存在、锚点是否有目标、内联 JS 是否可解析。

---

## 用法

把 `skills/english-reading-kit` 复制到 `~/.agents/skills/`，之后直接说「把这篇英文做成学习包」。或者手动按 `SKILL.md` 的流水线走一遍。

---

## 许可

- 代码、脚本、文档、译文与版式：MIT（见 [LICENSE](LICENSE)）
- 示例原文：Lewis Carroll, *Alice's Adventures in Wonderland* (1865)，公有领域

不应包含任何仍受版权保护的原文。完整的中英对照练习（含某部当代小说的章节）属于个人学习材料，不在本仓库中。
