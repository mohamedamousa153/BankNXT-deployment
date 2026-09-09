const fs = require('fs');
const content = fs.readFileSync('frontend/app.jsx', 'utf8');

let stack = [];
for(let i=0; i<content.length; i++) {
  if (content[i] === '{') stack.push('{');
  if (content[i] === '}') {
    if (stack.length === 0) { console.log('Unbalanced } at index', i); break; }
    stack.pop();
  }
}
console.log('Final brace stack length:', stack.length);

stack = [];
for(let i=0; i<content.length; i++) {
  if (content[i] === '(') stack.push('(');
  if (content[i] === ')') {
    if (stack.length === 0) { console.log('Unbalanced ) at index', i); break; }
    stack.pop();
  }
}
console.log('Final paren stack length:', stack.length);
