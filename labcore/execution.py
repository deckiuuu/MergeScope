"""Compile, launch independent JVMs serially and preserve evidence for every phase."""
from datetime import datetime,timezone
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
from .datafiles import create_inputs,sha256

ROOT=Path(__file__).resolve().parent.parent


def now(): return datetime.now(timezone.utc).isoformat()


def machine_description():
    record={'system':platform.system(),'kernel':platform.release(),'architecture':platform.machine()}
    if sys.platform=='darwin':
        query=subprocess.run(['/usr/sbin/system_profiler','-json','SPHardwareDataType'],text=True,capture_output=True)
        if query.returncode==0:
            try:
                item=json.loads(query.stdout)['SPHardwareDataType'][0]
                for key in ['machine_name','chip_type','physical_memory','number_processors']:
                    if key in item: record[key]=item[key]
            except (ValueError,KeyError,IndexError): pass
    return record


def compile_sources(destination):
    destination=Path(destination); destination.mkdir(parents=True,exist_ok=True)
    sources=sorted((ROOT/'src').glob('*.java'))+sorted((ROOT/'tests').glob('*.java'))
    subprocess.run(['javac','-g','-encoding','UTF-8','-Xlint:all','-d',str(destination),*map(str,sources)],check=True)
    return sources


def contract_test():
    classes=ROOT/'scratch/test-classes'
    compile_sources(classes)
    done=subprocess.run(['java','-cp',str(classes),'SortContractTest'],check=True,text=True,capture_output=True)
    print(done.stdout,end='',flush=True)
    return done.stdout+done.stderr


def measure_phase(name,parameters,thresholds,decision=None):
    target=ROOT/'measurements'/name
    target.mkdir(parents=True,exist_ok=False)
    protocol_path=ROOT/'study.json'
    protocol=json.loads(protocol_path.read_text())
    configuration={**parameters,'thresholds':sorted(set(thresholds)),
        'families':protocol['families'],'warmup_seconds':protocol['warmup_seconds'],
        'practice_rounds':protocol['practice_rounds'],'jvm_options':protocol['jvm_options'],
        'order_seed':protocol['order_seed'],'phase':name}
    if decision is not None: configuration['decision']=decision
    (target/'configuration.json').write_text(json.dumps(configuration,indent=2)+'\n')
    sources=compile_sources(target/'compiled')
    checked=subprocess.run(['java','-cp',str(target/'compiled'),'SortContractTest'],check=True,text=True,capture_output=True)
    (target/'correctness.txt').write_text(checked.stdout+checked.stderr)
    index=create_inputs(ROOT/'datasets'/name,configuration['lengths'],configuration['seeds'],configuration['families'])
    plan='\n'.join([f'repetitions={configuration["repetitions"]}',f'practice={configuration["practice_rounds"]}',
        'thresholds='+','.join(map(str,configuration['thresholds'])),
        f'warmup.ms={int(configuration["warmup_seconds"]*1000)}',f'order.seed={configuration["order_seed"]}'])+'\n'
    (target/'jvm-plan.properties').write_text(plan)
    evidence={'start_utc':now(),'machine':machine_description(),'python':platform.python_version(),
        'protocol_sha256':sha256(protocol_path),'configuration_sha256':sha256(target/'configuration.json'),
        'dataset_index':str(index.relative_to(ROOT)),'index_sha256':sha256(index),
        'source_hashes':{str(p.relative_to(ROOT)):sha256(p) for p in sources},
        'timing_scope':'Only MergeSort.sort, including new auxiliary-array allocation; cloning, loading, boxing and oracle comparisons excluded',
        'processes_sequential':True}
    frozen=target/'source-snapshot'
    for source in sources:
        out=frozen/source.relative_to(ROOT)
        out.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,out)
    (target/'evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
    for process in range(configuration['processes']):
        prefix=target/f'process-{process:02d}'
        arguments=['java',*configuration['jvm_options'],'-cp',str(target/'compiled'),'MeasureTrial',str(index),str(target/'jvm-plan.properties'),str(process),str(prefix)]
        print(f'Starting {name} process {process+1}/{configuration["processes"]}',flush=True)
        with (target/f'process-{process:02d}.log').open('w') as log:
            worker=subprocess.Popen(arguments,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
            for line in worker.stdout:
                log.write(line);log.flush()
                if 'Finished dataset' in line and ('/60 ' not in line or ' 60/60 ' in line): print(line,end='',flush=True)
            if worker.wait()!=0: raise RuntimeError(f'Measurement failed: {prefix}')
    evidence['finish_utc']=now()
    (target/'evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
    print(f'Completed phase {name}',flush=True)
    return target
