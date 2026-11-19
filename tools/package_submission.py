#!/usr/bin/env python3
"""Create and verify a source/data/report ZIP without Git history or temporary files."""
import argparse
from pathlib import Path
import zipfile
from repository_check import ROOT,check,digest,product_files


def package(output_name):
    if Path(output_name).name!=output_name or not output_name.endswith('.zip'):
        raise ValueError('Archive name must be a simple .zip filename')
    check()
    destination=ROOT/'dist';destination.mkdir(exist_ok=True)
    archive=destination/output_name
    temporary=archive.with_suffix('.zip.tmp')
    files=product_files()
    prefix='mergescope'
    expected={f'{prefix}/{path.relative_to(ROOT)}':digest(path) for path in files}
    try:
        with zipfile.ZipFile(temporary,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as output:
            for path in files: output.write(path,Path(prefix)/path.relative_to(ROOT))
        with zipfile.ZipFile(temporary) as output:
            if output.testzip() is not None: raise ValueError('Archive CRC check failed')
            if set(output.namelist())!=set(expected): raise ValueError('Archive inventory mismatch')
            import hashlib
            for name,expected_hash in expected.items():
                if hashlib.sha256(output.read(name)).hexdigest()!=expected_hash:
                    raise ValueError(f'Archive hash mismatch: {name}')
        temporary.replace(archive)
    finally:
        temporary.unlink(missing_ok=True)
    print(f'PASS ZIP: {len(files)} files, CRC and member SHA-256 checked')
    print(archive)
    return archive


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--name',default='mergescope-submission.zip')
    arguments=parser.parse_args()
    try: package(arguments.name)
    except (ValueError,OSError) as error: raise SystemExit(str(error))
