#!/usr/bin/env python3
"""Check repository integrity while preserving the recorded scientific baseline."""
import argparse
import csv
import hashlib
from pathlib import Path
import re
from urllib.parse import unquote,urlsplit

ROOT=Path(__file__).resolve().parents[1]
EXCLUDED_DIRECTORIES={'.git','scratch','reruns','compiled','__pycache__','dist','.venv','venv',
    '.idea','.vscode','.pytest_cache','.mypy_cache','.ruff_cache'}
EXCLUDED_FILES={'.DS_Store','Thumbs.db'}
NAVIGATION_FILES=['README.md','SUBMISSION.md','docs/GITHUB_GUIDE.md']


def digest(path):
    with Path(path).open('rb') as source:
        result=hashlib.sha256()
        for block in iter(lambda:source.read(1024*1024),b''): result.update(block)
    return result.hexdigest()


def product_files(root=ROOT):
    root=Path(root)
    result=[]
    for path in root.rglob('*'):
        relative=path.relative_to(root)
        if set(relative.parts)&EXCLUDED_DIRECTORIES or path.name in EXCLUDED_FILES:
            continue
        if path.suffix in {'.pyc','.class','.tmp','.iml'}: continue
        if path.is_symlink(): raise ValueError(f'Symlink not supported in submission: {relative}')
        if path.is_file(): result.append(path)
    return sorted(result)


def manifest_entries(path):
    records={}
    for number,line in enumerate(Path(path).read_text(encoding='utf-8').splitlines(),1):
        if not line.strip(): continue
        if '  ' not in line: raise ValueError(f'Invalid checksum record at line {number}')
        expected,name=line.split('  ',1)
        if not re.fullmatch('[0-9a-f]{64}',expected): raise ValueError('Invalid SHA-256')
        candidate=Path(name)
        if not name or candidate.is_absolute() or '..' in candidate.parts or '\\' in name:
            raise ValueError(f'Unsafe checksum path: {name}')
        if name in records: raise ValueError(f'Duplicate checksum path: {name}')
        records[name]=expected
    return records


def verify_manifest(manifest,root=ROOT):
    records=manifest_entries(manifest)
    for name,expected in records.items():
        path=Path(root)/name
        if not path.is_file(): raise ValueError(f'Missing preserved file: {name}')
        if digest(path)!=expected: raise ValueError(f'Checksum mismatch: {name}')
    return records


def check_navigation(root=ROOT):
    count=0
    for name in NAVIGATION_FILES:
        source=Path(root)/name
        for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',source.read_text(encoding='utf-8')):
            target=target.strip().split(' ',1)[0].strip('<>')
            url=urlsplit(target)
            if url.scheme or url.netloc or not url.path: continue
            resolved=(source.parent/unquote(url.path)).resolve()
            try: resolved.relative_to(Path(root).resolve())
            except ValueError: raise ValueError(f'Navigation escapes repository: {name} -> {target}')
            if not resolved.exists(): raise ValueError(f'Broken local link: {name} -> {target}')
            count+=1
    return count


def check(root=ROOT):
    root=Path(root)
    preserved=verify_manifest(root/'docs/BASELINE_SHA256.txt',root)
    recorded=verify_manifest(root/'CHECKSUMS.txt',root)
    actual={str(path.relative_to(root)) for path in product_files(root) if path.name!='CHECKSUMS.txt'}
    if actual!=set(recorded):
        raise ValueError(f'Inventory mismatch: unlisted={sorted(actual-set(recorded))}, missing={sorted(set(recorded)-actual)}')
    links=check_navigation(root)
    largest=max(product_files(root),key=lambda path:path.stat().st_size)
    if largest.stat().st_size>100*1024*1024:
        raise ValueError('A file exceeds the regular GitHub repository upload limit')
    print(f'PASS repository: {len(preserved)} baseline files, {len(recorded)} current checksums, {links} local navigation links')
    print(f'Largest product: {largest.relative_to(root)} ({largest.stat().st_size:,} bytes)')
    return recorded


def refresh(root=ROOT):
    root=Path(root)
    # Metadata maintenance cannot silently bless changed experimental evidence.
    verify_manifest(root/'docs/BASELINE_SHA256.txt',root)
    previous={}
    ledger=root/'CREATION_LEDGER.csv'
    if ledger.exists():
        with ledger.open(encoding='utf-8',newline='') as source:
            previous={row['path']:row for row in csv.DictReader(source)}
    temporary=ledger.with_suffix('.csv.tmp')
    with temporary.open('w',encoding='utf-8',newline='') as output:
        fields=['path','origin','derived_from','sha256']
        writer=csv.DictWriter(output,fieldnames=fields,lineterminator='\n');writer.writeheader()
        for path in product_files(root):
            relative=str(path.relative_to(root))
            if relative in {'CREATION_LEDGER.csv','CHECKSUMS.txt'}: continue
            current=digest(path)
            if relative in previous and previous[relative]['sha256']==current:
                record=previous[relative]
            else:
                record={'path':relative,'origin':'GitHub repository preparation or metadata maintenance',
                    'derived_from':'Fresh rebuilt project; recorded scientific baseline preserved','sha256':current}
            writer.writerow({field:record[field] for field in fields})
    temporary.replace(ledger)
    checksum=root/'CHECKSUMS.txt'
    rows=[f'{digest(path)}  {path.relative_to(root)}\n' for path in product_files(root) if path!=checksum]
    temporary=checksum.with_suffix('.txt.tmp')
    temporary.write_text(''.join(rows),encoding='utf-8');temporary.replace(checksum)
    return check(root)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['check','refresh'])
    arguments=parser.parse_args()
    try: (check if arguments.command=='check' else refresh)()
    except (ValueError,OSError) as error: raise SystemExit(str(error))
