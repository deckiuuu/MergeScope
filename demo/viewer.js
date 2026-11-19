(function (environment) {
  'use strict';
  function createViewer(document, corpus, clock) {
    const ids = ['size','family','threshold','threshold-label','comparison-count','current-depth',
      'phase-name','step-label','comparison-detail','numbers','alias-note','recursion-tree',
      'restart','previous','autoplay','next','finish','preset-one','preset-seven','preset-ten','preset-result'];
    const ui = Object.fromEntries(ids.map(id => {
      const element = document.getElementById(id);
      if (!element) throw new Error('Missing control: '+id);
      return [id,element];
    }));
    let sample, recording, position=0, interval=null;
    ui.size.value='33'; ui.family.value='mixed';
    ui.threshold.value=String(corpus.summary.selected_cutoff);

    function pause() {
      if (interval!==null) clock.clearInterval(interval);
      interval=null; ui.autoplay.textContent='Tự chạy';
    }
    function element(tag,text,className) {
      const node=document.createElement(tag);
      if (text!==undefined) node.textContent=String(text);
      if (className) node.className=className;
      return node;
    }
    function drawTree(depth) {
      const rows=[];
      const cutoff=Number(ui.threshold.value);
      function branch(first,last,level) {
        if (!rows[level]) rows[level]=[];
        const leaf=last-first+1<=cutoff;
        rows[level].push({first,last,leaf});
        if (!leaf) {
          const middle=first+Math.floor((last-first)/2);
          branch(first,middle,level+1); branch(middle+1,last,level+1);
        }
      }
      branch(0,sample.size-1,0);
      ui['recursion-tree'].replaceChildren();
      rows.forEach((nodes,level)=>{
        const row=element('div',undefined,'tree-row');
        nodes.forEach(node=>row.append(element('span',node.first===node.last?node.first:`${node.first}..${node.last}`,
          'branch'+(node.leaf?' leaf':'')+(level===depth?' current-depth':''))));
        ui['recursion-tree'].append(row);
      });
    }
    function render() {
      const event=recording[position];
      ui['threshold-label'].textContent=ui.threshold.value;
      ui['comparison-count'].textContent=String(event.count);
      ui['current-depth'].textContent=String(event.depth);
      ui['step-label'].textContent=`Bước ${position+1} / ${recording.length}`;
      const stage={start:'Mảng ban đầu',insert:'Trong Insertion sort',merge:'Trong phép trộn',done:'Hoàn tất sắp xếp'};
      ui['phase-name'].textContent=stage[event.phase];
      if (event.type==='comparison') {
        const relation=event.outcome<0?'<':event.outcome>0?'>':'=';
        ui['comparison-detail'].textContent=`${event.left[0]} (#${event.left[1]}) ${relation} ${event.right[0]} (#${event.right[1]})`;
      } else ui['comparison-detail'].textContent=event.type==='initial'?'Mỗi # đánh dấu vị trí trước khi sắp xếp.':'Kết quả khớp oracle và giữ thứ tự ban đầu của các khóa bằng nhau.';
      ui.numbers.replaceChildren();
      ui.numbers.style.setProperty('--columns',sample.size<=16?'16':'11');
      const maximum=Math.max(...recording[0].array.map(pair=>pair[0]));
      event.array.forEach(([key,id])=>{
        const flags=(event.left&&id===event.left[1]?' is-a':'')+(event.right&&id===event.right[1]?' is-b':'')+(event.type==='complete'?' finished':'');
        const node=element('div',undefined,'number'+flags);
        const track=element('div',undefined,'column-track');
        const bar=element('div',undefined,'column');
        bar.style.setProperty('--bar',`${Math.max(6,Math.round(key/maximum*100))}%`);
        track.append(bar);node.append(track,element('strong',key),element('small','#'+id));
        node.setAttribute('aria-label',`Khóa ${key}, vị trí ban đầu ${id}`);
        ui.numbers.append(node);
      });
      ui.numbers.setAttribute('aria-label',event.array.map(([key,id])=>`${key} (#${id})`).join(', '));
      const alias=sample.aliases[String(ui.threshold.value)];
      const same=Object.keys(sample.aliases).filter(c=>sample.aliases[c]===alias).map(Number).sort((a,b)=>a-b);
      ui['alias-note'].textContent=`Trên ví dụ N = ${sample.size}, các CUTOFF ${same[0]}${same.length>1?' đến '+same[same.length-1]:''} tạo bản ghi so sánh giống nhau, đã đối chiếu bằng Java.`;
      ui.previous.disabled=position===0;ui.restart.disabled=position===0;
      ui.next.disabled=position===recording.length-1;ui.finish.disabled=position===recording.length-1;
      drawTree(event.depth);
      if (position===recording.length-1) pause();
    }
    function reset() {
      pause();position=0;
      const cutoff=Math.max(1,Math.min(128,Math.round(Number(ui.threshold.value)||1)));
      ui.threshold.value=String(cutoff);
      sample=corpus.cases.find(item=>item.size===Number(ui.size.value)&&item.family===ui.family.value);
      if (!sample) throw new Error('Unknown example');
      recording=sample.recordings[sample.aliases[String(cutoff)]];
      if (!recording) throw new Error('Missing recording');
      render();
    }
    ui.size.addEventListener('change',reset);ui.family.addEventListener('change',reset);
    ui.threshold.addEventListener('input',reset);
    ui.restart.addEventListener('click',()=>{pause();position=0;render();});
    ui.finish.addEventListener('click',()=>{pause();position=recording.length-1;render();});
    ui.previous.addEventListener('click',()=>{pause();position=Math.max(0,position-1);render();});
    ui.next.addEventListener('click',()=>{pause();position=Math.min(recording.length-1,position+1);render();});
    ui.autoplay.addEventListener('click',()=>{
      if (interval!==null) {pause();return;}
      if (position===recording.length-1) {position=0;render();}
      ui.autoplay.textContent='Tạm dừng';
      interval=clock.setInterval(()=>{position=Math.min(position+1,recording.length-1);render();},220);
    });
    for (const [name,value] of [['one',1],['seven',7],['ten',10],['result',corpus.summary.selected_cutoff]])
      ui['preset-'+name].addEventListener('click',()=>{ui.threshold.value=String(value);reset();});
    reset();
    return {snapshot:()=>({position,total:recording.length,cutoff:Number(ui.threshold.value),size:sample.size,family:sample.family,running:interval!==null})};
  }
  if (typeof module==='object'&&module.exports) module.exports={createViewer};
  if (typeof document!=='undefined') {
    const corpus=JSON.parse(document.getElementById('comparison-corpus').textContent);
    createViewer(document,corpus,{setInterval:environment.setInterval.bind(environment),clearInterval:environment.clearInterval.bind(environment)});
  }
})(globalThis);
