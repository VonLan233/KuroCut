# KuroCut 执行日志

## 2026-09-16：阶段 0 环境与底座准备

状态：部分完成。仅完成环境检查、仓库准备和 FunClip 独立环境安装；未运行真实日语样片。

### 仓库

- GitHub：`https://github.com/VonLan233/KuroCut.git`
- 初始提交：`3314a6e`（计划、既有分析和参考图）
- 远端 Windows 工作目录：`D:\KuroCut`

### Windows 实测

| 项目 | 结果 |
| --- | --- |
| OS | Microsoft Windows 11（远端 `ver` 为 `10.0.22000.376`） |
| CPU | AMD Ryzen 7 9800X3D 8-Core Processor |
| 内存 | 31.1 GiB |
| GPU | NVIDIA GeForce RTX 5080，16303 MiB，驱动 610.88 |
| Python | 3.12.5 |
| Git | `C:\Program Files\Git\cmd\git.exe` |
| FFmpeg | 系统 PATH 无；FunClip 环境内置 `imageio_ffmpeg` 7.1 可执行文件 |
| 磁盘 | C: 748.76/182.09 GiB；D: 1362.81/544.66 GiB（总量/可用） |

### FunClip

- 路径：`D:\KuroCut\experiments\FunClip`
- 版本：`v2.2.1`，commit `2a954d4fbad6a57a5271390be4eb43f80d201b60`
- 环境：`D:\KuroCut\experiments\FunClip\.venv`
- 依赖：`python -m pip install -r requirements.txt` 完成；`pip check` 通过
- PyTorch：`2.11.0+cu128`
- Torchaudio：`2.11.0+cu128`
- GPU 验证：`torch.cuda.is_available() = True`，识别 RTX 5080
- 本地 FFmpeg：`...\.venv\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe`
- yt-dlp：`2026.08.19`，安装在同一独立环境
- 素材目录：`D:\KuroCut\media\incoming`、`source`、`samples`、`work`；这些目录已加入 Git 忽略范围

### 源视频工作流准备

下载和简单裁切均在 Windows 远端执行；源文件不覆盖，裁切只写入 `media\samples`。链接到位后可使用：

```bat
set "KURO_FFMPEG=D:\KuroCut\experiments\FunClip\.venv\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
D:\KuroCut\experiments\FunClip\.venv\Scripts\python -m yt_dlp --ffmpeg-location "%KURO_FFMPEG%" -o "D:\KuroCut\media\source\%%(upload_date)s_%%(id)s.%%(ext)s" "<URL>"
"%KURO_FFMPEG%" -ss 00:10:00 -to 00:11:30 -i "D:\KuroCut\media\source\<file>" -map 0 -c copy "D:\KuroCut\media\samples\sample-90s.mkv"
```

### 未测与下一步

- 已有 A 场源和 90 秒/14 分钟样片；SenseVoice 识别与 SRT 输出已通过首次冒烟，但日语断句、完整 10–20 分钟 FunClip 粗剪和字幕对齐仍待核。
- 系统 PATH 没有独立 FFmpeg；已用环境内置二进制完成下载合并和本地裁切。
- 未发现 Premiere Pro 版本，PR 工程验收保持未完成。
- 下一步：核对 SRT 与原声、运行 14 分钟样片的 FunClip 流程，再决定是否补 punc 模型或提高源分辨率。

官方依据：FunClip [v2.2.1 源码与安装说明](https://github.com/modelscope/FunClip)；PyTorch [Windows CUDA 安装说明](https://pytorch.org/get-started/locally/)。

## 2026-09-16：A 场源抓取与阶段 0 冒烟

- 源 URL：`https://www.youtube.com/watch?v=_IDj48tRiXc`
- yt-dlp 配置：`--ignore-config`（绕过远端失效的 `127.0.0.1:7890` 代理配置）、视频 `135`（854×480 H.264/30fps）+ 音频 `251`（Opus）
- 源文件：`D:\KuroCut\media\source\20260911_IDj48tRiXc.mkv`，5:05:08.05，1,716,312,183 bytes
- 源 SHA256：`41b4fce5795c210c104ee820aa8f28581e2f65e18f3b67182654f8f4f9c1bf0b`
- 阶段 0 样片：`stage0-000-90s.mkv`、`stage0-001-hajimari.mkv`、`stage0-002-trailer-pv.mkv`，均含视频和原声
- 已按明确起止时间生成 20 条素材：`D:\KuroCut\media\work\clips\001-*.mkv` 至 `020-*.mkv`；无损流复制，未重编码
- SenseVoiceSmall：对 `stage0-001-hajimari.mkv` 识别成功，输出 `D:\KuroCut\media\work\stage0-001\transcript.txt` 与 `transcript.srt`；文本 717 字符、SRT 751 字符，推理日志显示 rtf 约 0.053
- 发现：SenseVoice 路径未配置 punc model 时跳过句级分段，当前 SRT 可用但字幕断句质量待核；另有一次直接调用缺少 `VideoClipper.lang`，已通过调用侧设置修复，未改第三方源码

未自动裁切的待补结束时间：`お金ない`、`実際に使ってみる`、`待機モーション`、`脅かす系彼氏`、`待機モーション2`、`おまけ`。`待機モーション2` 的 `4:04:14 4:05:00 4:05:50` 也需要确认哪个是结束点。

## 2026-09-16：基础理解字幕样片

- 原因：阶段 0 只验证源抓取、裁切和 ASR；FunClip 不会自动复现参考图中的动效，参考图也没有被实现为模板。
- 日语 ASR 当前缺少可靠句级时间戳，原始 SRT 几乎是一整段，不能直接烧录成可读字幕。
- 已生成基于 ASR 草稿的中文理解字幕：`D:\KuroCut\media\work\stage0-001\transcript.zh.srt`
- 已生成硬字幕样片：`D:\KuroCut\media\work\stage0-001\stage0-001-hajimari-zh-hard.mkv`
- 字幕样式：白字、黑描边、底部居中；视频使用 RTX 5080 的 NVENC 编码，原声保留。
- 该中文版本是“理解草稿”，按语义段落铺时，不把未经人工核对的 ASR 当成最终翻译。下一步先由用户检查是否能读懂，再决定是否为 20 条片段逐条翻译/烧录。

## 2026-09-17：PV 片段句级时间戳对照

- 远端在同一 FunClip venv 补装 `faster-whisper`，使用本地 `small` 日语模型和 RTX 5080。
- 受控范围：`stage0-002-trailer-pv.mkv` 原片 00:27–02:18；输入先解码为 16 kHz 单声道音频，模型时间加回 27 秒源偏移。
- 输出：`D:\KuroCut\media\work\sample-review-2026-09-17\pv-review-27-138.faster-whisper.json`、`pv-review-27-138.review.srt`。
- 结果：42 个句段，语言识别为 `ja`，概率 1.0；前段出现“冷静→惊叹→好帅→观察动作”，后段出现白发、父亲等候选语义。
- 约一半中文只保留“待翻译／待核”，专名、PV 台词来源和含混句不自动定稿；这证明本地小模型适合生成带时间的初稿，不足以取消人工验收。
- 审稿硬字幕：`D:\KuroCut\media\work\sample-review-2026-09-17\pv-review-27-138-zh-hard.mkv`，已抽帧确认字幕显示、原声保留。
- 脚本：`outputs/sample-review-2026-09-17/timestamp_transcribe.py`。本轮未覆盖原有 SenseVoice 结果或源视频。

## 2026-09-17：OpenCode Contributor Free 与 Muse 重做

- 远端 OpenCode：`1.18.31`；`opencode/muse-spark-1.3-contributor-free` 出现在模型列表，环境变量认证可用，连通性测试返回 `MUSE_CONNECTED`。
- Muse 读取 PV JSON、旧报告、音频能量和抽帧证据，修订 `pv-review-27-138.faster-whisper.json`：42 段变为 44 段，补回两处高能量喊声，所有不确定语义保留待核说明；JSON 单调性验证通过。
- 基于修订 JSON 重新生成 `pv-review-27-138.muse-zh.srt` 与 `pv-review-27-138-muse-zh-hard.mkv`；远端抽帧确认双语字幕显示。
- 项目根新增 `opencode.json`，默认模型固定为 `opencode/muse-spark-1.3-contributor-free`；不保存 API Key。
- 高级“一步成片”路线见 `docs/2026-09-17-advanced-one-step-video-workflow.md`：一步触发、分层执行、可恢复、可生成审稿 MP4 和 PR 交换时间线。
