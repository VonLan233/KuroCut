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

### 未测与下一步

- 缺少 A 场 60–90 秒日语小样和 10–20 分钟回放，故未声称 ASR、时间戳、字幕导出或粗剪通过。
- 系统 PATH 没有独立 FFmpeg；当前可先用环境内置二进制，真实素材测试时确认 FunClip 的调用路径。
- 未发现 Premiere Pro 版本，PR 工程验收保持未完成。
- 收到小样后先运行 FunClip 原生识别/字幕/粗剪，再补实际输出路径、时长、音轨、日语字体和失败原因。

官方依据：FunClip [v2.2.1 源码与安装说明](https://github.com/modelscope/FunClip)；PyTorch [Windows CUDA 安装说明](https://pytorch.org/get-started/locally/)。
