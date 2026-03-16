# Public Release Copy (Bilingual)

This file contains ready-to-post copy for:
- GitHub
- X
- Discord communities

Repo: <https://github.com/Harlan66/open-wispr-intelligence-layer>

---

## 1) GitHub / Long Post

### 中文
我把最近围绕 `open-wispr` 的一套方法整理成了公开仓库：
<https://github.com/Harlan66/open-wispr-intelligence-layer>

这个项目不是“再做一个语音转录器”，而是解决一个更现实的问题：

> **纯本地文字转录经常不够智能。**

本地转录的优点是快、稳、隐私好，但它也有典型短板：
- 技术术语归一化不稳定
- 中英混合容易错
- 难以区分“真实纠错”和“语义重写”
- 从编辑记录直接学习时容易污染词表

这套方案的核心是 **local-first intelligence layer**：
- 主路径继续本地转录
- 本地脚本先做夜间粗筛与防污染
- 只把少量高价值歧义样本交给 agent 做语义复核
- 远程失败时支持网络恢复后自动补跑

目标不是“看起来更复杂”，而是：
**更智能、无感、静默、稳定。**

如果你也在做本地 ASR / 听写 / 双语输入增强，这个仓库应该有参考价值。

### English
I open-sourced part of my `open-wispr` workflow here:
<https://github.com/Harlan66/open-wispr-intelligence-layer>

This project is not about building another transcription tool.
It focuses on a more practical problem:

> **pure local transcription is often not intelligent enough.**

Local systems are great for speed, privacy, and control, but they often struggle with:
- technical term normalization
- mixed Chinese/English correction
- distinguishing true correction from semantic rewrite
- safe learning without contaminating the dictionary

The approach here is a **local-first intelligence layer**:
- keep transcription local as the primary path
- use local nightly filtering + contamination control
- send only small high-value ambiguous samples to an agent
- auto-retry remote review after transient failures

The goal is simple:
**smarter, silent, stable improvement without babysitting.**

If you are working on local ASR / dictation / bilingual input enhancement, this may be useful.

---

## 2) X / Short Post

### 中文
开源了一个 `open-wispr` 的 intelligence layer：
<https://github.com/Harlan66/open-wispr-intelligence-layer>

不是重做转录器，而是解决“本地转录不够智能”的老问题。

方法：
- 主链路本地
- 本地粗筛 + 防污染
- 少量难样本给 agent 做语义复核
- 远程失败自动补跑

### English
I open-sourced an intelligence layer for `open-wispr`:
<https://github.com/Harlan66/open-wispr-intelligence-layer>

Not another transcription app—this targets a practical gap:
local transcription is often not intelligent enough.

Approach:
- local-first primary path
- local filtering + contamination control
- agent review for hard cases only
- automatic retry after transient failures

---

## 3) Discord / Community Intro

### 中文
我把 `open-wispr` 相关的一套方法整理成公开仓库了：
<https://github.com/Harlan66/open-wispr-intelligence-layer>

重点不是重做语音转录器，而是解决：
**本地转录不够智能，但纯云端又不够稳。**

方案是 local-first：
- 本地主链路
- 夜间本地粗筛
- 少量歧义样本交给 agent 语义复核
- 远程失败支持自动恢复补跑

如果你也在做 local ASR / dictation / bilingual 输入增强，欢迎交流。

### English
I turned part of my `open-wispr` workflow into a public repo:
<https://github.com/Harlan66/open-wispr-intelligence-layer>

Focus: not “another transcription app”, but this gap:
**local transcription is often not intelligent enough, while full cloud dependence is fragile.**

Method:
- local-first primary path
- local nightly coarse filtering
- agent semantic review for ambiguous cases only
- auto-retry after transient remote failures

Happy to discuss with anyone building local ASR / dictation / bilingual voice workflows.

---

## 4) One-line Tagline Options

- Smarter local transcription without giving up privacy or stability.
- A local-first intelligence layer for practical dictation quality upgrades.
- Keep transcription local. Add intelligence only where it matters.

#huanyuan
