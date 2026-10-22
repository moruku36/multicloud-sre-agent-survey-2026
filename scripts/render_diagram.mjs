import { readFileSync, writeFileSync } from 'node:fs';
import { render } from 'pele';

const source = readFileSync('docs/agent-architecture.mmd', 'utf8');
const { svg } = render(source);
if (!svg?.includes('<svg')) throw new Error('Pele did not return SVG');
writeFileSync('docs/agent-architecture.svg', svg + '\n');
