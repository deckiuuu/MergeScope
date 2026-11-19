'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {createViewer}=require('../demo/viewer.js');
const root=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(root,'demo/index.html'),'utf8');
const corpus=JSON.parse(html.match(/<script id="comparison-corpus" type="application\/json">([\s\S]*?)<\/script>/)[1]);

class FakeElement {
  constructor(){this.children=[];this.handlers=new Map();this.value='';this._text='';this.disabled=false;this.attributes={};this.style={setProperty:(key,value)=>{this.style[key]=value;}};}
  set textContent(text){this._text=String(text);this.children=[];}
  get textContent(){return this._text+this.children.map(child=>child.textContent).join('');}
  append(...nodes){this.children.push(...nodes);}
  replaceChildren(...nodes){this.children=[...nodes];this._text='';}
  addEventListener(event,action){this.handlers.set(event,action);}
  setAttribute(key,value){this.attributes[key]=value;}
  fire(event){assert(this.handlers.has(event),'Missing UI event '+event);this.handlers.get(event)();}
}

test('recordings and viewer controls remain consistent across every offered cutoff',()=>{
  const controls=new Map();
  for(const match of html.matchAll(/\bid="([^"]+)"/g)) controls.set(match[1],new FakeElement());
  const document={getElementById:id=>controls.get(id),createElement:()=>new FakeElement()};
  let counter=0;
  const ticks=new Map();
  const clock={setInterval:fn=>{ticks.set(++counter,fn);return counter;},clearInterval:id=>ticks.delete(id)};
  const viewer=createViewer(document,corpus,clock);
  const get=id=>controls.get(id);
  let combinations=0,transitions=0;
  for(const sample of corpus.cases){
    get('size').value=String(sample.size);get('family').value=sample.family;get('family').fire('change');
    const traversed=new Set();
    for(let cutoff=1;cutoff<=128;cutoff++){
      get('threshold').value=String(cutoff);get('threshold').fire('input');
      const index=sample.aliases[cutoff];
      const events=sample.recordings[index];
      assert(events.length>=2);
      assert.equal(viewer.snapshot().position,0);
      assert.equal(viewer.snapshot().cutoff,cutoff);
      assert.equal(get('numbers').children.length,sample.size);
      assert.equal(get('comparison-count').textContent,'0');
      assert.equal(get('previous').disabled,true);
      let comparison=0;
      for(const event of events){
        assert.equal(event.array.length,sample.size);
        if(event.type==='comparison'){
          assert.equal(Math.sign(event.left[0]-event.right[0]),event.outcome);
          comparison++;
          assert.equal(event.count,comparison);
          if(cutoff===1)assert.equal(event.phase,'merge');
          if(cutoff>=sample.size)assert.equal(event.phase,'insert');
        }
      }
      if(!traversed.has(index)){
        traversed.add(index);
        for(let step=1;step<events.length;step++){
          get('next').fire('click');transitions++;
          assert.equal(viewer.snapshot().position,step);
          assert.equal(get('comparison-count').textContent,String(events[step].count));
          assert.equal(get('step-label').textContent,`Bước ${step+1} / ${events.length}`);
        }
      }else get('finish').fire('click');
      assert.equal(viewer.snapshot().position,events.length-1);
      assert.equal(get('next').disabled,true);
      const actual=get('numbers').children.map(node=>Number(node.children[1].textContent));
      assert.deepEqual(actual,events.at(-1).array.map(pair=>pair[0]));
      const end=events.at(-1).array;
      assert.equal(new Set(end.map(pair=>pair[1])).size,sample.size);
      for(let j=1;j<end.length;j++){
        assert(end[j-1][0]<=end[j][0]);
        if(end[j-1][0]===end[j][0])assert(end[j-1][1]<end[j][1]);
      }
      get('previous').fire('click');assert.equal(viewer.snapshot().position,events.length-2);
      get('restart').fire('click');assert.equal(viewer.snapshot().position,0);
      get('finish').fire('click');assert.equal(viewer.snapshot().position,events.length-1);
      combinations++;
    }
    assert.equal(traversed.size,sample.recordings.length);
  }
  get('autoplay').fire('click');assert.equal(ticks.size,1);
  assert.equal(viewer.snapshot().position,0);
  [...ticks.values()][0]();assert.equal(viewer.snapshot().position,1);
  get('autoplay').fire('click');assert.equal(ticks.size,0);
  get('autoplay').fire('click');get('threshold').value='7';get('threshold').fire('input');
  assert.equal(ticks.size,0);assert.equal(viewer.snapshot().position,0);
  for(const [id,value] of [['preset-one',1],['preset-seven',7],['preset-ten',10],['preset-result',corpus.summary.selected_cutoff]]){
    get(id).fire('click');assert.equal(viewer.snapshot().cutoff,value);
  }
  get('autoplay').fire('click');
  let safety=0;
  while(ticks.size&&safety++<10000)[...ticks.values()][0]();
  assert(safety<10000);assert.equal(viewer.snapshot().position,viewer.snapshot().total-1);
  for(const match of html.matchAll(/(?:href|src)="([^"]+)"/g)){
    assert(!/^https?:/i.test(match[1]),'Offline page requested external resource');
    assert(fs.existsSync(path.resolve(root,'demo',match[1])),'Missing local resource '+match[1]);
  }
  assert.equal(combinations,corpus.verified_runs);
  const result={combinations,full_recordings:corpus.distinct_recordings,step_transitions:transitions,
    checks:['comparison outcomes','sorted values and stable identities','next/previous','restart/finish','autoplay/pause/end','cutoff/size/distribution changes','presets','offline links'],
    scope:'Real Java recordings and viewer logic in a minimal DOM; no browser rendering claim'};
  fs.writeFileSync(path.join(root,'docs/VIEWER_CHECKS.json'),JSON.stringify(result,null,2)+'\n');
  process.stdout.write(JSON.stringify(result)+'\n');
});
