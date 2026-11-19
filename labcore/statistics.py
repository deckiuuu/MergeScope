"""Block-paired analysis and a predeclared three-phase selection process."""
from collections import Counter,defaultdict
import csv
from functools import lru_cache
import itertools
import json
import math
from pathlib import Path
import random
import statistics
from .datafiles import sha256
from .execution import ROOT,measure_phase,now


def emit_csv(path,records):
    if records:
        with Path(path).open('w',newline='',encoding='utf-8') as output:
            writer=csv.DictWriter(output,fieldnames=list(records[0]))
            writer.writeheader();writer.writerows(records)


def quantile(values,fraction):
    ordered=sorted(values)
    coordinate=(len(ordered)-1)*fraction
    lower=int(coordinate)
    upper=min(lower+1,len(ordered)-1)
    return ordered[lower]+(coordinate-lower)*(ordered[upper]-ordered[lower])


@lru_cache(maxsize=None)
def leaf_profile(n,cutoff):
    if n<=cutoff: return ((n,1),)
    counts=Counter(dict(leaf_profile((n+1)//2,cutoff)))
    counts.update(dict(leaf_profile(n//2,cutoff)))
    return tuple(sorted(counts.items()))


def structural_groups(lengths,thresholds):
    groups=defaultdict(list)
    for cutoff in sorted(thresholds):
        groups[tuple(leaf_profile(n,cutoff) for n in lengths)].append(cutoff)
    return sorted(groups.values(),key=lambda g:g[0])


def load_observations(folder):
    folder=Path(folder)
    configuration=json.loads((folder/'configuration.json').read_text())
    blocks=defaultdict(list)
    all_rows=[]
    identities=set()
    expected_checksums=defaultdict(set)
    for source in sorted(folder.glob('process-*.csv')):
        with source.open(encoding='utf-8') as stream:
            for row in csv.DictReader(stream):
                for name in ['process','length','seed','cutoff','repetition','order_position','batch_size','elapsed_ns','digest']:
                    row[name]=int(row[name])
                row['nanos_per_sort']=float(row['nanos_per_sort'])
                identity=(row['process'],row['distribution'],row['length'],row['seed'],row['cutoff'],row['repetition'])
                if identity in identities: raise ValueError(f'Duplicate observation {identity}')
                identities.add(identity)
                if row['elapsed_ns']<=0 or row['batch_size']<1 or not math.isfinite(row['nanos_per_sort']):
                    raise ValueError('Invalid timing value')
                if abs(row['elapsed_ns']/row['batch_size']-row['nanos_per_sort'])>0.000001:
                    raise ValueError('Batch division disagrees with raw elapsed time')
                key=(row['distribution'],row['length'],row['seed'],row['process'],row['cutoff'])
                blocks[key].append(row['nanos_per_sort'])
                expected_checksums[(row['dataset'],row['batch_size'])].add(row['digest'])
                all_rows.append(row)
    expected=set(itertools.product(range(configuration['processes']),configuration['families'],
        configuration['lengths'],configuration['seeds'],configuration['thresholds'],range(configuration['repetitions'])))
    if expected!=identities:
        raise ValueError(f'Incomplete grid: {len(expected-identities)} missing, {len(identities-expected)} unexpected')
    if any(len(values)!=1 for values in expected_checksums.values()):
        raise ValueError('Output digests differ for the same input')
    medians={key:statistics.median(values) for key,values in blocks.items()}
    return configuration,all_rows,medians


def bootstrap_ratio(block_medians,configuration,baseline,selected,repeats,seed):
    # Every cluster keeps the complete distribution x length design together.
    cluster={}
    for process in range(configuration['processes']):
        for data_seed in configuration['seeds']:
            logs=[math.log(block_medians[(family,n,data_seed,process,baseline)]/
                block_medians[(family,n,data_seed,process,selected)])
                for family in configuration['families'] for n in configuration['lengths']]
            cluster[process,data_seed]=statistics.fmean(logs)
    point=math.exp(statistics.fmean(cluster.values()))
    generator=random.Random(seed)
    estimates=[]
    for _ in range(repeats):
        drawn=[]
        for _ in range(configuration['processes']):
            process=generator.randrange(configuration['processes'])
            for _ in configuration['seeds']:
                data_seed=generator.choice(configuration['seeds'])
                drawn.append(cluster[process,data_seed])
        estimates.append(math.exp(statistics.fmean(drawn)))
    return point,quantile(estimates,.025),quantile(estimates,.975)


def analyze(folder):
    folder=Path(folder)
    protocol=json.loads((ROOT/'study.json').read_text())
    configuration=json.loads((folder/'configuration.json').read_text())
    allowed=configuration.get('decision',{}).get('shortlist',configuration['thresholds'])
    groups=structural_groups(configuration['lengths'],allowed) if configuration['phase']=='screen' else [[c] for c in sorted(allowed)]
    configuration,rows,medians=load_observations(folder)
    base_blocks=list(itertools.product(configuration['families'],configuration['lengths'],configuration['seeds'],range(configuration['processes'])))
    def score(cutoff):
        return math.exp(statistics.fmean(math.log(medians[(*key,cutoff)]/medians[(*key,1)]) for key in base_blocks))
    rankings=[{'representative':group[0],'same_tree':group,'score':score(group[0])} for group in groups]
    rankings.sort(key=lambda row:(row['score'],row['representative']))
    if configuration['phase']=='confirm':
        selected=configuration['decision']['selected_cutoff']
    else: selected=rankings[0]['representative']
    shortlist=[row['representative'] for row in rankings[:3]] if configuration['phase']=='screen' else list(allowed)
    pairwise=[]
    controls=sorted(set(protocol['mandatory_controls']+shortlist+[selected])&set(configuration['thresholds']))
    for baseline in controls:
        point,low,high=bootstrap_ratio(medians,configuration,baseline,selected,protocol['bootstrap_resamples'],protocol['bootstrap_seed']+baseline)
        pairwise.append({'baseline':baseline,'selected':selected,'speedup':point,'ci_low':low,'ci_high':high,'time_saved_fraction':1-1/point})
    emit_csv(folder/'paired-effects.csv',pairwise)
    emit_csv(folder/'candidate-ranking.csv',[{'rank':i+1,'representative':r['representative'],
        'same_tree':';'.join(map(str,r['same_tree'])),'relative_time':r['score']} for i,r in enumerate(rankings)])
    emit_csv(folder/'every-threshold.csv',[{'cutoff':c,'relative_time':score(c)} for c in configuration['thresholds']])
    distribution=[]
    for family in configuration['families']:
        keys=[key for key in base_blocks if key[0]==family]
        for cutoff in configuration['thresholds']:
            ratio=math.exp(statistics.fmean(math.log(medians[(*key,cutoff)]/medians[(*key,1)]) for key in keys))
            distribution.append({'distribution':family,'cutoff':cutoff,'relative_time':ratio})
    emit_csv(folder/'distribution-effects.csv',distribution)
    pooled=defaultdict(list)
    for row in rows: pooled[row['distribution'],row['length'],row['cutoff']].append(row['nanos_per_sort'])
    descriptions=[]
    for (family,n,cutoff),values in sorted(pooled.items()):
        center=statistics.median(values)
        descriptions.append({'distribution':family,'length':n,'cutoff':cutoff,'samples':len(values),
            'median_ms':center/1e6,'mean_ms':statistics.fmean(values)/1e6,'sd_ms':statistics.stdev(values)/1e6,
            'q1_ms':quantile(values,.25)/1e6,'q3_ms':quantile(values,.75)/1e6,
            'minimum_ms':min(values)/1e6,'maximum_ms':max(values)/1e6,
            'mad_ms':statistics.median(abs(v-center) for v in values)/1e6})
    emit_csv(folder/'descriptive-times.csv',descriptions)
    result={'phase':configuration['phase'],'selected_cutoff':selected,'shortlist':shortlist,
        'rankings':rankings,'observed_fastest':rankings[0]['representative'],
        'near_optimal_representatives':[r['representative'] for r in rankings if r['score']<=rankings[0]['score']*(1+protocol['practical_tolerance'])],
        'observations':len(rows),'timed_sort_calls':sum(row['batch_size'] for row in rows),
        'paired_effects':pairwise,'configuration':configuration,
        'analysis_notes':{'weighting':'Equal weight to distribution x length x data seed x JVM; median over repetitions in each paired block',
            'equivalent_thresholds':'Screen only smallest representatives of identical recursion signatures; retain the fixed shortlist in later phases; never pool observations across cutoff aliases',
            'interval':f'{protocol["bootstrap_resamples"]} hierarchical percentile bootstrap replicates: JVM process, then data-seed cluster; fixed distribution x length design',
            'limitations':'Pairwise intervals, limited JVM processes, one machine session; no claim of universal optimum or simultaneous coverage'}}
    (folder/'summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({key:result[key] for key in ['phase','selected_cutoff','shortlist','observed_fastest','observations','timed_sort_calls']},ensure_ascii=False,indent=2),flush=True)
    return result


def prepare_next_phase(name,execute=False):
    if name not in ['choose','confirm']: raise ValueError('Expected choose or confirm')
    previous='screen' if name=='choose' else 'choose'
    source=ROOT/'measurements'/previous/'summary.json'
    summary=json.loads(source.read_text())
    protocol=json.loads((ROOT/'study.json').read_text())
    record={'frozen_utc':now(),'source_phase':previous,'source_summary_sha256':sha256(source),
        'shortlist':summary['shortlist'],'protocol_sha256':sha256(ROOT/'study.json')}
    if name=='confirm': record['selected_cutoff']=summary['selected_cutoff']
    frozen=ROOT/'measurements'/f'{name}-frozen.json'
    with frozen.open('x',encoding='utf-8') as output:
        output.write(json.dumps(record,indent=2)+'\n')
    thresholds=sorted(set(protocol['mandatory_controls']+record['shortlist']))
    print(f'Frozen {name}: candidates={record["shortlist"]}, selected={record.get("selected_cutoff","chosen only after phase choose")}',flush=True)
    if execute: return measure_phase(name,protocol['phases'][name],thresholds,record)
    return record
