#!/usr/bin/env node
/**
 * Dry-run OpenRouter: gera texto (DeepSeek) + capa (FLUX.2 Pro).
 * NÃO publica no LinkedIn. NÃO chama n8n.
 *
 * Uso:
 *   OPENROUTER_API_KEY=sk-or-... node scripts/dry-run-openrouter.mjs
 *
 * Saídas em /tmp/linkedin-dry-run/ (texto .md + capa .png se a API retornar).
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..');
const outDir = '/tmp/linkedin-dry-run';
const key = process.env.OPENROUTER_API_KEY;

if (!key) {
  console.error('Falta OPENROUTER_API_KEY. Defina no ambiente e rode de novo.');
  console.error('Este script NÃO posta no LinkedIn.');
  process.exit(1);
}

const textPrompt = JSON.parse(
  fs.readFileSync(path.join(root, 'prompts/post-texto.json'), 'utf8'),
);
const coverPrompt = JSON.parse(
  fs.readFileSync(path.join(root, 'prompts/post-imagem-capa.json'), 'utf8'),
);
const replyPrompt = JSON.parse(
  fs.readFileSync(path.join(root, 'prompts/resposta-comentario.json'), 'utf8'),
);

const tema =
  process.env.DRY_RUN_TEMA ||
  'Por que agentes de IA falham sem observabilidade e limites claros';
const estilo =
  coverPrompt.style_rotation[
    (new Date().getUTCDate() - 1) % coverPrompt.style_rotation.length
  ];

function fill(template, map) {
  return template.replace(/\{\{\s*([^}]+)\s*\}\}/g, (_, k) => map[k.trim()] ?? '');
}

async function chat(model, messages, maxTokens = 1200) {
  const res = await fetch('https://openrouter.ai/api/v1/chat/completions', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${key}`,
      'Content-Type': 'application/json',
      'HTTP-Referer': 'https://github.com/cardoso-ix/linkedin-automacao-ia',
      'X-Title': 'linkedin-automacao-ia-dry-run',
    },
    body: JSON.stringify({ model, messages, max_tokens: maxTokens }),
  });
  const body = await res.json();
  if (!res.ok) {
    throw new Error(`chat ${res.status}: ${JSON.stringify(body).slice(0, 500)}`);
  }
  return body.choices?.[0]?.message?.content ?? '';
}

async function image(prompt) {
  const res = await fetch(coverPrompt.endpoint, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${key}`,
      'Content-Type': 'application/json',
      'HTTP-Referer': 'https://github.com/cardoso-ix/linkedin-automacao-ia',
      'X-Title': 'linkedin-automacao-ia-dry-run',
    },
    body: JSON.stringify({
      model: coverPrompt.model,
      prompt,
      aspect_ratio: coverPrompt.aspect_ratio,
      output_format: coverPrompt.output_format,
    }),
  });
  const body = await res.json();
  if (!res.ok) {
    throw new Error(`image ${res.status}: ${JSON.stringify(body).slice(0, 800)}`);
  }
  return body;
}

fs.mkdirSync(outDir, { recursive: true });
console.log('DRY-RUN OpenRouter — sem LinkedIn, sem n8n publish');
console.log('tema:', tema);
console.log('estilo capa:', estilo);

const postMessages = textPrompt.messages.map((m) => ({
  role: m.role,
  content: fill(m.content, {
    '$json.tema': tema,
    '$json.themeIndex': '1',
    '$json.today': new Date().toISOString().slice(0, 10),
    '$json.memoryContext': '(dry-run: sem memória)',
  })
    .replace(/\{\{\s*\$json\.tema\s*\}\}/g, tema)
    .replace(/\{\{\s*\$json\.themeIndex\s*\}\}/g, '1')
    .replace(/\{\{\s*\$json\.today\s*\}\}/g, new Date().toISOString().slice(0, 10))
    .replace(/\{\{\s*\$json\.memoryContext\s*\}\}/g, '(dry-run: sem memória)'),
}));

const postText = await chat(textPrompt.model, postMessages, 1400);
fs.writeFileSync(path.join(outDir, 'post.txt'), postText);
console.log('texto chars:', postText.length);
console.log('texto preview:', postText.slice(0, 180).replace(/\n/g, ' '), '...');

const replyMessages = replyPrompt.messages.map((m) => ({
  role: m.role,
  content: m.content
    .replace(/\{\{\s*\$json\.authorName\s*\}\}/g, 'Ana')
    .replace(/\{\{\s*\$json\.commentText\s*\}\}/g, 'Concordo, observabilidade muda o jogo.')
    .replace(/\{\{\s*\$json\.postText\s*\}\}/g, postText.slice(0, 400)),
}));
const replyText = await chat(replyPrompt.model, replyMessages, 200);
fs.writeFileSync(path.join(outDir, 'reply.txt'), replyText);
console.log('reply:', replyText);

const imagePrompt = fill(coverPrompt.prompt_template, {
  estilo_da_rodada: estilo,
  tema_do_post: tema,
});
const neg = coverPrompt.negative_prompt || coverPrompt.negative_cues.join(', ');
const fullImagePrompt = `${imagePrompt}\n\nNegative: ${neg}`;
fs.writeFileSync(path.join(outDir, 'cover-prompt.txt'), fullImagePrompt);

const imgBody = await image(fullImagePrompt);
fs.writeFileSync(path.join(outDir, 'cover-response.json'), JSON.stringify(imgBody, null, 2));

const b64 =
  imgBody?.data?.[0]?.b64_json ||
  imgBody?.images?.[0]?.b64_json ||
  imgBody?.data?.[0]?.image_base64;
const url = imgBody?.data?.[0]?.url || imgBody?.images?.[0]?.url;

if (b64) {
  fs.writeFileSync(path.join(outDir, 'cover.png'), Buffer.from(b64, 'base64'));
  console.log('capa salva:', path.join(outDir, 'cover.png'));
} else if (url) {
  const r = await fetch(url);
  const buf = Buffer.from(await r.arrayBuffer());
  fs.writeFileSync(path.join(outDir, 'cover.png'), buf);
  console.log('capa baixada:', path.join(outDir, 'cover.png'), 'bytes', buf.length);
} else {
  console.log('capa: resposta sem b64/url óbvios — veja cover-response.json');
}

console.log('OK dry-run. Arquivos em', outDir);
console.log('Nada foi publicado no LinkedIn.');
