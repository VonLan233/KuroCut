"""Small local ASR check with sentence timestamps for the PV review range."""
import json
import subprocess
from pathlib import Path


FFMPEG = r"D:\KuroCut\experiments\FunClip\.venv\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
PYTHON = r"D:\KuroCut\experiments\FunClip\.venv\Scripts\python.exe"
ROOT = Path(r"D:\KuroCut\media\work\sample-review-2026-09-17")
SOURCE = Path(r"D:\KuroCut\media\samples\stage0-002-trailer-pv.mkv")
START, END = 27.0, 138.0


def main():
    from faster_whisper import WhisperModel

    wav = ROOT / "pv-review-27-138.wav"
    subprocess.run([
        FFMPEG, "-y", "-v", "error", "-i", str(SOURCE), "-ss", str(START),
        "-t", str(END - START), "-map", "0:a:0", "-ac", "1", "-ar", "16000",
        "-c:a", "pcm_s16le", str(wav)
    ], check=True)
    model = WhisperModel("small", device="cuda", compute_type="float16")
    segments, info = model.transcribe(
        str(wav), language="ja", beam_size=5, vad_filter=False,
        condition_on_previous_text=False, temperature=0.0
    )
    rows = []
    for segment in segments:
        text = segment.text.strip()
        if text:
            rows.append({"start": round(START + segment.start, 3),
                         "end": round(START + segment.end, 3), "text": text})
    zh = {
        "こっち!": "这边！（待核）",
        "落ち着いて!大丈夫!": "冷静，没事！",
        "ついね!": "终于！（原词疑似ついに，待核）",
        "大丈夫大丈夫大丈夫!": "没事没事没事！",
        "え、なんで汗かいてんの?": "诶，怎么出汗了？",
        "何も!": "没什么！",
        "何?": "什么？",
        "え、何?": "诶，什么？",
        "かっこいい!かっこいい!": "好帅！好帅！",
        "顔やばいな!": "这张脸不得了……（语气待核）",
        "あ、大丈夫かな?この動きはね、見てるから大丈夫大丈夫": "啊，没事吗？这个动作……我正在看，所以没事没事。（待核）",
        "動きを見て": "看这个动作。（待核）",
        "あ、やばい、なんか気絶しちゃいそう": "啊，不妙，好像要昏过去了。（待核）",
        "ダメ!落ちて!": "不行！掉下去！（待核）",
        "いやマジで!白髪ヤバい!": "不是，真的！白发太不得了了！（语气待核）",
        "え?待って!": "诶？等等！",
        "ちょっと待って": "等一下。",
        "wwwww": "哈哈哈哈（网络笑声）",
        "ああ!もういい!": "啊！够了！",
        "もういいよ!": "已经够了！",
        "死んでもいい!": "死而无憾了！（夸张表达，待核）",
    }
    for row in rows:
        row["zh_draft"] = zh.get(row["text"], "（待翻译／待核）")
    def stamp(seconds):
        ms = round(seconds * 1000)
        h, ms = divmod(ms, 3600000)
        m, ms = divmod(ms, 60000)
        s, ms = divmod(ms, 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
    srt = []
    for i, row in enumerate(rows, 1):
        srt.extend([str(i), f"{stamp(row['start'])} --> {stamp(row['end'])}",
                    row["text"] + "\n" + row["zh_draft"], ""])
    (ROOT / "pv-review-27-138.review.srt").write_text("\n".join(srt), encoding="utf-8")
    (ROOT / "pv-review-27-138.faster-whisper.json").write_text(
        json.dumps({"source": str(SOURCE), "range": [START, END],
                    "model": "small", "language": info.language,
                    "language_probability": info.language_probability,
                    "segments": rows}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"segments": len(rows), "language": info.language,
                      "probability": info.language_probability}, ensure_ascii=False))


if __name__ == "__main__":
    main()
