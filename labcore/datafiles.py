"""Plain-text experimental inputs with deterministic seeds and content hashes."""
import csv
import hashlib
import json
from pathlib import Path
import random


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def create_inputs(destination, lengths, seeds, families):
    destination=Path(destination)
    destination.mkdir(parents=True,exist_ok=False)
    records=[]
    for n in lengths:
        for seed in seeds:
            stream=random.Random((seed*6364136223846793005+n*1442695040888963407)&((1<<64)-1))
            base=[stream.randint(-2_000_000,2_000_000) for _ in range(n)]
            increasing=sorted(base)
            for family in families:
                values=base.copy()
                if family=='ascending': values=increasing.copy()
                elif family=='descending': values=increasing[::-1]
                elif family=='almost_sorted':
                    values=increasing.copy()
                    disturbance=random.Random(seed*31+n*17)
                    for _ in range(max(1,n//200)):
                        left,right=disturbance.randrange(n),disturbance.randrange(n)
                        values[left],values[right]=values[right],values[left]
                elif family=='repeated_keys':
                    duplicate=random.Random(seed*103+n)
                    values=[1_000_000+257*duplicate.randrange(16) for _ in range(n)]
                elif family!='uniform': raise ValueError(f'Unknown input family: {family}')
                identifier=f'{family}-{n}-{seed}'
                filename=identifier+'.csv'
                (destination/filename).write_text('value\n'+''.join(f'{v}\n' for v in values),encoding='utf-8')
                records.append(dict(id=identifier,distribution=family,length=n,seed=seed,path=filename,sha256=sha256(destination/filename)))
    with (destination/'index.csv').open('w',newline='',encoding='utf-8') as output:
        writer=csv.DictWriter(output,fieldnames=list(records[0]))
        writer.writeheader(); writer.writerows(records)
    (destination/'generation.json').write_text(json.dumps({
        'format':'UTF-8 CSV with one signed int32 value per row; header value',
        'rng':'Python random.Random with explicit integer mixing, as implemented in labcore/datafiles.py',
        'almost_sorted_swaps':'max(1,length//200) random transpositions',
        'repeated_keys':'16 keys 1000000+257*k for k=0..15',
        'lengths':lengths,'seeds':seeds,'families':families},indent=2)+'\n')
    return destination/'index.csv'


def index_records(path):
    with Path(path).open(encoding='utf-8',newline='') as source:
        return list(csv.DictReader(source))
