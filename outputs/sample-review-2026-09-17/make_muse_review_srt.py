import json
from pathlib import Path


root = Path(__file__).parent
data = json.loads((root / "pv-review-27-138.faster-whisper.json").read_text(encoding="utf-8"))


def stamp(seconds):
    ms = round(seconds * 1000)
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1_000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


lines = []
for i, row in enumerate(data["segments"], 1):
    lines += [str(i), f"{stamp(row['start'])} --> {stamp(row['end'])}",
              row["text"], row["zh_draft"], ""]
(root / "pv-review-27-138.muse-zh.srt").write_text("\n".join(lines), encoding="utf-8")
print(f"wrote {len(data['segments'])} subtitles")
