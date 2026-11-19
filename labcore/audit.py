"""Cross-check raw measurements against inputs, frozen decisions and source snapshots."""
from collections import defaultdict
from datetime import datetime
import hashlib
import json
from pathlib import Path
from .datafiles import index_records,sha256
from .execution import ROOT
from .statistics import load_observations


def verify_phase(name):
    folder=ROOT/'measurements'/name
    configuration,rows,_=load_observations(folder)
    evidence=json.loads((folder/'evidence.json').read_text())
    if 'finish_utc' not in evidence: raise ValueError('Unfinished measurement phase')
    if evidence['protocol_sha256']!=sha256(ROOT/'study.json'): raise ValueError('Protocol changed')
    if evidence['configuration_sha256']!=sha256(folder/'configuration.json'): raise ValueError('Configuration changed')
    for relative,digest in evidence['source_hashes'].items():
        if sha256(ROOT/relative)!=digest or sha256(folder/'source-snapshot'/relative)!=digest:
            raise ValueError(f'Measured source does not match {relative}')
    index=ROOT/evidence['dataset_index']
    if sha256(index)!=evidence['index_sha256']: raise ValueError('Index changed')
    records=index_records(index)
    expected={(f,n,s) for f in configuration['families'] for n in configuration['lengths'] for s in configuration['seeds']}
    actual={(r['distribution'],int(r['length']),int(r['seed'])) for r in records}
    if expected!=actual or len(records)!=len(expected): raise ValueError('Dataset grid mismatch')
    digests={}
    for row in records:
        path=index.parent/row['path']
        if sha256(path)!=row['sha256']: raise ValueError(f'Dataset changed: {path.name}')
        lines=path.read_text().splitlines()
        if lines[0]!='value' or len(lines)-1!=int(row['length']): raise ValueError('Dataset format mismatch')
        checksum=1
        for value in sorted(map(int,lines[1:])): checksum=(31*checksum+value)&0xffffffff
        digests[row['id']]=checksum-(1<<32) if checksum>=1<<31 else checksum
    positions=defaultdict(set)
    for row in rows:
        identifier=f'{row["distribution"]}-{row["length"]}-{row["seed"]}'
        batch=max(1,min(8,(6000+row['length']-1)//row['length']))
        if row['dataset']!=identifier or row['batch_size']!=batch or row['digest']!=digests[identifier]*batch:
            raise ValueError('Input identity, batch or output checksum mismatch')
        positions[row['process'],row['dataset'],row['repetition']].add(row['order_position'])
    required=set(range(len(configuration['thresholds'])))
    if any(order!=required for order in positions.values()): raise ValueError('Candidate order does not form a permutation')
    if name!='screen':
        decision=json.loads((ROOT/'measurements'/f'{name}-frozen.json').read_text())
        if decision!=configuration['decision']: raise ValueError('Frozen decision differs from measured decision')
        source=ROOT/'measurements'/decision['source_phase']/'summary.json'
        prior=json.loads(source.read_text())
        if sha256(source)!=decision['source_summary_sha256']: raise ValueError('Selection evidence changed')
        if decision['shortlist']!=prior['shortlist']: raise ValueError('Shortlist changed')
        if name=='confirm' and decision['selected_cutoff']!=prior['selected_cutoff']: raise ValueError('Final choice changed')
        if datetime.fromisoformat(decision['frozen_utc'])>=datetime.fromisoformat(evidence['start_utc']):
            raise ValueError('Selection was not frozen before measurement')
    print(f'PASS {name}: {len(records)} datasets, {len(rows)} complete observations, source/input/configuration hashes, independent checksums and candidate-order permutations')
    return configuration


def verify_project():
    protocol=json.loads((ROOT/'study.json').read_text())
    for key in ['lengths','seeds']:
        phase_values=[set(plan[key]) for plan in protocol['phases'].values()]
        if any(phase_values[i]&phase_values[j] for i in range(3) for j in range(i+1,3)):
            raise ValueError(f'Overlap between experimental phases: {key}')
    origin=json.loads((ROOT/'docs/ORIGIN.json').read_text())
    if sha256(ROOT/origin['retained_source'])!=origin['source_sha256']:
        raise ValueError('Supplied MergeSort was modified')
    for name in ['screen','choose','confirm']: verify_phase(name)
    print('PASS: three disjoint phases and the single retained MergeSort source')
