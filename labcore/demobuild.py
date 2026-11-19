"""Build the offline viewer from direct recordings of the supplied Java class."""
import html
import json
import subprocess
from .datafiles import sha256
from .execution import ROOT


def build_demo():
    classes=ROOT/'scratch/recording-classes';classes.mkdir(parents=True,exist_ok=True)
    subprocess.run(['javac','-g','-encoding','UTF-8','-Xlint:all','-d',str(classes),
        str(ROOT/'src/MergeSort.java'),str(ROOT/'tools/TraceCapture.java')],check=True)
    raw=ROOT/'scratch/comparison-recordings.json'
    capture=subprocess.run(['java','-cp',str(classes),'TraceCapture',str(raw)],text=True,capture_output=True,check=True)
    (ROOT/'docs/TRACE_CHECKS.txt').write_text(capture.stdout+capture.stderr)
    corpus=json.loads(raw.read_text())
    final=json.loads((ROOT/'measurements/confirm/summary.json').read_text())
    selected=final['selected_cutoff']
    corpus['summary']={'selected_cutoff':selected,'source_sha256':sha256(ROOT/'src/MergeSort.java')}
    effects=[r for r in final['paired_effects'] if r['baseline']!=selected]
    rows=''.join(f'<tr><td>{r["baseline"]}</td><td>{r["speedup"]:.4f}×</td><td>{r["ci_low"]:.4f} đến {r["ci_high"]:.4f}</td></tr>' for r in effects)
    replacements={'__RUNS__':str(corpus['verified_runs']),'__SOURCE_HASH__':corpus['summary']['source_sha256'][:16],
        '__SELECTED__':str(selected),'__EFFECT_ROWS__':rows,
        '__CONCLUSION__':html.escape(f'CUTOFF {selected} được chọn trên pha chọn riêng rồi giữ nguyên khi xác nhận. Kết luận chỉ áp dụng cho cài đặt Integer[], máy và thiết kế dữ liệu trong báo cáo.'),
        '__CORPUS__':json.dumps(corpus,separators=(',',':'),ensure_ascii=False)}
    page=(ROOT/'demo/page.html').read_text()
    for key,value in replacements.items(): page=page.replace(key,value)
    if any(key in page for key in replacements): raise ValueError('Unresolved demo placeholder')
    (ROOT/'demo/index.html').write_text(page,encoding='utf-8')
    print(capture.stdout,end='')
    print(f'Offline viewer built with selected cutoff {selected}.')
