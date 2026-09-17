"""Read-only sample ASR; fixed windows are navigation aids, not subtitle timing."""
import json
import re
import subprocess
import time
from pathlib import Path


def windows(count, rate=16000):
    # ponytail: fixed windows can split phrases; overlap helps review, not alignment.
    start = 0
    while start < count:
        end = min(start + 30 * rate, count)
        yield start, end
        if end == count:
            break
        start += 27 * rate


def main():
    import imageio_ffmpeg
    import numpy as np
    from funasr import AutoModel

    root = Path(r'D:\KuroCut\media')
    out = root / 'work' / 'sample-review-2026-09-17'
    out.mkdir(exist_ok=True)
    model = AutoModel(model='iic/SenseVoiceSmall', device='cuda:0',
                      disable_update=True, disable_pbar=True)
    for source in sorted((root / 'samples').glob('*.mkv')):
        target = out / (source.stem + '.json')
        if target.exists():
            print('EXISTS ' + target.name, flush=True)
            continue
        began = time.monotonic()
        audio = subprocess.run([
            imageio_ffmpeg.get_ffmpeg_exe(), '-v', 'error', '-i', str(source),
            '-map', '0:a:0', '-ac', '1', '-ar', '16000', '-f', 'f32le', '-'
        ], check=True, capture_output=True).stdout
        samples = np.frombuffer(audio, dtype='<f4').copy()
        records = []
        for start, end in windows(len(samples)):
            result = model.generate(input=samples[start:end], language='ja',
                                    use_itn=True, cache={}, fs=16000,
                                    disable_pbar=True)
            raw = '\n'.join(row.get('text', '') for row in result)
            records.append(dict(start=start / 16000, end=end / 16000,
                                text=re.sub(r'<\|.*?\|>', '', raw), raw=raw))
            print(f'{source.stem} {end / 16000:.1f}s', flush=True)
        payload = dict(source=str(source), audio_duration=len(samples) / 16000,
                       model='iic/SenseVoiceSmall', language='ja', use_itn=True,
                       window_seconds=30, overlap_seconds=3, vad=False,
                       timestamp_kind='audio window boundaries, NOT speech alignment',
                       elapsed_seconds=round(time.monotonic() - began, 2),
                       windows=records)
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
        print('SAVED ' + target.name, flush=True)


if __name__ == '__main__':
    assert list(windows(0)) == []
    assert list(windows(31, rate=1)) == [(0, 30), (27, 31)]
    assert list(windows(57, rate=1)) == [(0, 30), (27, 57)]
    assert list(windows(30, rate=1)) == [(0, 30)]
    main()
