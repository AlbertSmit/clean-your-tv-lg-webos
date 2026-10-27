const assert = require('node:assert/strict');
const {test} = require('node:test');
const {create} = require('../../launcher/app-library');
const inventory = [{id:'a',title:'Alpha'}, {id:'b',title:'Beta'}, {id:'c',title:'Gamma'}];
function setup() {
 const values = new Map();
 const storage = {getItem:k=>values.get(k)||null,setItem:(k,v)=>values.set(k,v)};
 return {storage, model:create(storage, inventory, {dockApps:['a','b','c']})};
}
test('hidden app remains available after an incomplete TV inventory response', () => {
 const {model,storage} = setup();
 model.save(['b','c'], ['a']);
 model.refresh([{id:'b',title:'Beta updated'}, {id:'d',title:'Delta'}]);
 assert.deepEqual(model.available().map(a=>a.id), ['a','d']);
 model.add('a');
 assert.deepEqual(model.visible().map(a=>a.id), ['b','c','a']);
 assert.equal(model.visible()[0].title, 'Beta updated');
 assert.deepEqual(create(storage, [], {}).visible().map(a=>a.id), ['b','c','a']);
});
test('Undo restores the whole layout after a partial or empty refresh', () => {
 for (const response of [[{id:'a',title:'Alpha'}], []]) {
  const {model} = setup();
  model.refresh(response);
  model.save(['b','c'], ['a']);
  model.save(['a','b','c'], []);
  assert.deepEqual(model.visible().map(a=>a.id), ['a','b','c']);
 }
});
test('dominant colors are validated, copied and preserved by partial inventories', () => {
 const {storage} = setup();
 const color = [12, 80, 255];
 const model = create(storage, [{id:'a',title:'Alpha',icon:'a.png',iconColor:'#123456',dominantColor:color}], {dockApps:['a']});
 color[0] = 200;
 assert.deepEqual(model.visible()[0].dominantColor, [12,80,255]);
 model.refresh([{id:'a',title:'Updated'}]);
 assert.deepEqual(model.visible()[0].dominantColor, [12,80,255]);
 assert.equal(model.visible()[0].icon, 'a.png');
 assert.equal(model.visible()[0].iconColor, '#123456');
 model.save(['a'], []);
 assert.equal(JSON.parse(storage.getItem('tvhome.layout')).catalog[0].dominantColor, undefined, 'persistent catalog retains the existing rollback-compatible schema');
 model.refresh([{id:'a',title:'Updated icon',icon:'b.png'}]);
 assert.equal(model.visible()[0].icon, 'b.png');
 assert.equal(model.visible()[0].dominantColor, undefined, 'changed artwork must not retain its previous color');
 assert.equal(model.visible()[0].iconColor, '');
});
test('invalid dominant colors fall through to other color sources', () => {
 for (const dominantColor of [null, [], [1,2], [1,2,3,4], ['1',2,3], [NaN,2,3], [Infinity,2,3], [-1,2,3], [256,2,3]]) {
  const {storage} = setup();
  const model = create(storage, [{id:'a',title:'Alpha',dominantColor,iconColor:'#123456'}], {dockApps:['a']});
  assert.equal(model.visible()[0].dominantColor, undefined);
  assert.equal(model.visible()[0].iconColor, '#123456');
 }
});
test('an icon refresh invalidates cached colors even when the app is hidden', () => {
 const values = new Map([['tvhome.color.a', '[1,2,3]']]);
 const storage = {getItem:k=>values.get(k)||null,setItem:(k,v)=>values.set(k,v),removeItem:k=>values.delete(k)};
 const model = create(storage, [{id:'a',title:'Alpha',icon:'old.png'}], {hiddenApps:['a']});
 model.refresh([{id:'a',title:'Alpha',icon:'new.png'}]);
 assert.equal(values.has('tvhome.color.a'), false);
 assert.equal(model.available()[0].icon, 'new.png');
});
