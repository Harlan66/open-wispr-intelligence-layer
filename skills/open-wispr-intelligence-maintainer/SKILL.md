---
name: open-wispr-intelligence-maintainer
description: Maintain and operate the open-wispr-intelligence-layer workflow. Use this skill whenever a user asks to install, run, troubleshoot, or improve the local-first transcription intelligence pipeline (nightly review, safe candidate filtering, remote-review retry, launchd scheduling, and repo maintenance).
compatibility:
  tools: ["read", "write", "edit", "exec"]
---

# open-wispr-intelligence-maintainer

让下载本仓库的 agent 能稳定维护与使用该项目。

## 目标

你维护的是一条 **local-first transcription intelligence** 链路：

1. 主转录仍在本地（不改主输入体验）
2. 夜间本地脚本做保守筛选与防污染
3. 远端语义复核仅处理小样本高歧义候选
4. 网络/上游抖动时自动补跑

你的任务不是“让系统看起来更聪明”，而是：
- 保持稳定
- 防止词表被污染
- 让修复可恢复、可观测

---

## 何时触发这个技能

当用户提到以下任意场景时应触发：
- `open-wispr`、本地语音输入、听写纠错、转录智能增强
- nightly review、review_queue、候选纠错
- launchd 定时任务、网络恢复补跑、503 后自动重试
- “如何维护这个仓库/这条链路”
- “怎么验证它现在是不是正常在跑”

---

## 标准工作流（按顺序）

### 1) 先确认运行前提
- 确认存在：
  - `scripts/openwispr_nightly_review.py`
  - `scripts/network_recovery_retry.py`
  - `config/network_recovery_retry.example.json`
- 确认本地数据目录（默认）：`~/.config/open-wispr/`
- 确认 transcript 来源文件：`~/.config/open-wispr/transcripts.jsonl`

### 2) 运行夜间本地筛选（可手动）

```bash
python3 scripts/openwispr_nightly_review.py --config-dir ~/.config/open-wispr --hours 24
```

预期输出：
- `~/.config/open-wispr/nightly-review-latest.md`
- `~/.config/open-wispr/review_queue.jsonl`
- `~/.config/open-wispr/remote-review-input.jsonl`

### 3) 配置并运行恢复补跑 watcher

先从样例创建本地配置（不要把真实 jobId / 私有路径提交到仓库）：

```bash
cp config/network_recovery_retry.example.json ~/.config/open-wispr/network_recovery_retry.json
```

运行：

```bash
OWHR_CONFIG=~/.config/open-wispr/network_recovery_retry.json \
OWHR_STATE=~/.config/open-wispr/network-recovery-state.json \
python3 scripts/network_recovery_retry.py
```

### 4) launchd 持续化（macOS）
- 使用 `examples/launchd/*.plist` 作为模板
- 按本机路径改写后再 `launchctl bootstrap` / `kickstart`
- 日志必须落盘，避免“看起来在跑，实际上没跑”

### 5) 验证链路是否健康
至少检查：
- `nightly-review-latest.md` 是否更新
- `review_queue.jsonl` 是否只追加高置信小样本
- `remote-review-input.jsonl` 是否存在且规模受控
- watcher 状态是否更新：`network-recovery-state.json`
- 日志里是否出现连续失败（如 503、already-running、PATH 问题）

---

## 维护规则（硬约束）

1. **local-first 不可破坏**
   - 不要把主转录路径改成强依赖远端。

2. **防污染优先于召回**
   - 宁可少收候选，不要把 rewrite/style_edit 混进词表。

3. **默认静默运行**
   - 不要把夜间维护做成聊天刷屏流程。

4. **敏感数据不上仓库**
   - 禁止提交 `transcripts.jsonl`、`review_queue.jsonl`、`remote-review-input.jsonl`、本地日志与状态文件。

5. **改动先可观测再自动化**
   - 新增自动动作前，先确保有日志、状态文件和失败路径。

---

## 常见故障与处理

### A. 远端模型/上游抖动（503）
- 视为暂态故障，不要立刻改算法
- 让 watcher 在网络恢复后补跑
- 记录失败窗口与恢复时间

### B. watcher 调不到 `openclaw`（PATH 问题）
- 在脚本或 plist 中显式 PATH：`/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin`
- 再做一次手动运行验证

### C. `already-running`
- 这通常是正常并发保护，不应算致命错误
- 状态上应标记为跳过/已在运行

### D. 产物文件长期不更新
按顺序排查：
1. transcript 源是否仍在写
2. nightly 脚本是否执行成功
3. launchd 是否加载成功
4. watcher 是否有 cooldown / pending 条件阻塞

---

## 对用户的汇报格式（建议）

每次维护后用这个结构回复：

1. 当前状态（正常/降级/失败）
2. 本次动作（执行了哪些命令）
3. 关键证据（产物文件、日志、状态字段）
4. 下一步建议（是否需要人工介入）

---

## 非目标（不要做）

- 不要把这个仓库改造成“全自动云端转录服务”
- 不要上传用户语音文本样本到公开仓库
- 不要为了追求命中率降低防污染阈值到危险水平

---

#huanyuan
