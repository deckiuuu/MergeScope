#!/usr/bin/env python3
"""Single entry point for the fresh MergeSort cutoff laboratory."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
from labcore.execution import ROOT,contract_test,measure_phase


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('test')
    phase=sub.add_parser('phase')
    phase.add_argument('name',choices=['screen','choose','confirm'])
    study=sub.add_parser('study')
    study.add_argument('--new-run',help='Create a clean experiment workspace under reruns/NAME')
    summarize=sub.add_parser('analyze');summarize.add_argument('phase',type=Path)
    sub.add_parser('verify')
    sub.add_parser('demo')
    sub.add_parser('report')
    args=parser.parse_args()
    if args.command=='test': contract_test()
    elif args.command=='phase':
        protocol=json.loads((ROOT/'study.json').read_text())
        if args.name=='screen': measure_phase('screen',protocol['phases']['screen'],protocol['thresholds'])
        else:
            from labcore.statistics import prepare_next_phase
            prepare_next_phase(args.name,execute=True)
    elif args.command=='study':
        if args.new_run:
            if Path(args.new_run).name!=args.new_run or args.new_run in ['.','..']:
                raise ValueError('new-run must be a simple directory name')
            destination=ROOT/'reruns'/args.new_run
            destination.mkdir(parents=True,exist_ok=False)
            for directory in ['src','tests','labcore','tools','demo']:
                if (ROOT/directory).exists():
                    shutil.copytree(ROOT/directory,destination/directory,
                        ignore=shutil.ignore_patterns('__pycache__','*.class','index.html'))
            for name in ['cutofflab.py','study.json']:
                shutil.copyfile(ROOT/name,destination/name)
            for directory in ['datasets','measurements','report/charts','docs']:
                (destination/directory).mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT/'docs/ORIGIN.json',destination/'docs/ORIGIN.json')
            (destination/'README.md').write_text('Lượt đo mới được tạo bằng --new-run.\n\n'
                'Xem measurements/confirm/summary.json cho lựa chọn và kết quả của lượt này.\n'
                'Chạy python3 cutofflab.py verify để kiểm tra dữ liệu và nguồn.\n'
                'Báo cáo và demo có thể dựng bằng các lệnh report và demo.\n')
            subprocess.run([sys.executable,str(destination/'cutofflab.py'),'study'],cwd=destination,check=True)
            print(f'New measurements saved in {destination}')
            return
        from labcore.statistics import analyze,prepare_next_phase
        protocol=json.loads((ROOT/'study.json').read_text())
        measure_phase('screen',protocol['phases']['screen'],protocol['thresholds'])
        analyze(ROOT/'measurements/screen')
        prepare_next_phase('choose',execute=True)
        analyze(ROOT/'measurements/choose')
        prepare_next_phase('confirm',execute=True)
        analyze(ROOT/'measurements/confirm')
        from labcore.audit import verify_project
        verify_project()
    elif args.command=='analyze':
        from labcore.statistics import analyze
        analyze(args.phase.resolve())
    elif args.command=='verify':
        from labcore.audit import verify_project
        verify_project()
    elif args.command=='demo':
        from labcore.demobuild import build_demo
        build_demo()
    elif args.command=='report':
        from labcore.writeup import build_report
        build_report()


if __name__=='__main__': main()
