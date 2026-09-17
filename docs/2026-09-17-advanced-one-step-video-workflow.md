# KuroCut 高级“一步成片”工作流调研

日期：2026-09-17

## 结论

“一步成片”应该理解为一个入口触发的可恢复流水线，不是让一个模型直接凭视频输出最终 MP4。模型负责理解和决策，确定性工具负责时间轴、渲染和校验；这样才能保留字幕、切点和 PR 工程的可修改性。

## 推荐架构

```text
yt-dlp / ffprobe
  → 场景与音频索引
  → WhisperX 或 faster-whisper 句/词级时间戳
  → Qwen3-VL 4B/8B 分段看画面与事件
  → Muse Spark 1.3 Contributor Free 融合文本和视觉证据
  → JSON 编辑决策表
  → FFmpeg 审稿 MP4 + SRT/ASS
  → OTIO/FCP7 XML 交换时间线
  → PR 中保存原生工程
  → 自动 QA + 人工最终验收
```

## 各层职责

| 层 | 首选 | 产物 | 不能假设的能力 |
| --- | --- | --- | --- |
| 取源与索引 | yt-dlp、ffprobe、PySceneDetect | 源文件 manifest、场景边界、音轨信息 | 场景切换不等于精彩点 |
| 语音 | faster-whisper；需要更细时间时 WhisperX | 日语句/词时间戳、SRT、语言和置信线索 | 专名、PV台词归属和语气仍会错 |
| 画面 | Qwen3-VL 4B 起步，8B 作对照 | 带源时间的事件、人物区域、画面证据 | 低帧率采样会漏掉短暂表情；不能只看文本 |
| 编排 | Muse Spark 1.3 Contributor Free | 结构化 edit JSON：shots、字幕、构图、效果、疑点 | 模型信心不是事实真值 |
| 渲染 | FFmpeg + ASS；PR 内用图形/MOGRT | 审稿 MP4、可编辑字幕、预览图 | ASS 烧录不是 PR 可编辑工程 |
| 工程交付 | OTIO/FCP7 XML 交换，目标 PR 内保存 `.prproj` | 工程、媒体包、版本 manifest | XML 合法不代表 PR 动效完整兼容 |
| QA | ffprobe、黑帧/缺音/越界/重叠检查 | QA 报告、失败列表 | 技术通过不等于内容好笑或翻译正确 |

## 对当前机器的落地顺序

1. 保留当前 `faster-whisper small` 作为快速时间轴初稿；必要时单独测试 WhisperX 词级对齐，不重跑整场。
2. 安装并测试 Qwen3-VL 4B/8B 量化版本，只抽取候选窗口的关键帧，不把 5 小时视频一次送入显存。Qwen3-VL 官方实现支持视频理解、时间定位和可调视频像素预算，但 Windows 后端需先验证。
3. 让 Muse 只输出严格的编辑决策 JSON，并要求每个候选绑定源时间、转录证据和画面证据；不能直接覆盖字幕或最终工程。
4. 由同一份 edit JSON 生成中文审稿版、日语字幕版和 XML/OTIO 交换时间线。
5. 先在 PR 中手动保存一个可重开的原生工程，再自动化重复导入；不能把 XML 文件本身称为 PR 工程。

## 这次调研后的取舍

- 不增加“万能一键剪辑模型”；当前收益最大的缺口是句级/词级时间戳和视觉证据融合。
- 不让 Muse 直接处理音频或视频；它用于文本决策和代码/流程编排。
- 不把低置信尾段自动剪掉；疑似 PV 混音、主播反应和剧情台词必须保留疑点，交给审稿流程。
- 第一版高级流程仍输出可读中文硬字幕审稿视频；特效和 PR 工程在候选通过后再生成，避免把错误字幕包装成成片。

## 参考实现依据

- [Qwen3-VL 官方仓库](https://github.com/QwenLM/Qwen3-VL)：视频理解、时间定位、视频像素预算和视频后端说明。
- [WhisperX 官方仓库](https://github.com/m-bain/whisperX)：词级时间戳、强制对齐、VAD 和说话人分离。
- [OpenTimelineIO 官方仓库](https://github.com/AcademySoftwareFoundation/OpenTimelineIO)：编辑时间线交换格式与适配器机制。
- [PySceneDetect 文档](https://www.scenedetect.com/docs/head/)：场景检测基础能力。
