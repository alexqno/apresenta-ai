import { cp, mkdir, readFile, rm } from 'node:fs/promises';
import { resolve } from 'node:path';

const root = process.cwd();
const config = JSON.parse(await readFile(resolve(root, 'deploy-config.json'), 'utf8'));
const manifest = JSON.parse(await readFile(resolve(root, 'assets-manifest.json'), 'utf8'));
const publicDirectory = resolve(root, 'public');

function safeSource(sourceRoot, relative) {
  if (typeof relative !== 'string' || relative.startsWith('/') || relative.split('/').includes('..')) throw new Error(`Caminho de asset inválido: ${relative}`);
  return resolve(sourceRoot, relative);
}
async function copyGroup(sourceRoot, outputRoot, files) {
  if (!Array.isArray(files)) throw new Error('Manifesto de assets inválido.');
  for (const relative of files) {
    const source = safeSource(sourceRoot, relative);
    const target = resolve(outputRoot, relative);
    await mkdir(resolve(target, '..'), { recursive: true });
    await cp(source, target);
  }
}

await rm(publicDirectory, { recursive: true, force: true });
await copyGroup(resolve(root, config.presentationRoot), resolve(publicDirectory, config.deck), manifest.deck);
await copyGroup(resolve(root, config.designRoot), resolve(publicDirectory, 'designs', config.design), manifest.design);
console.log(`Assets prontos em ${publicDirectory}`);
