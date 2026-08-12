import { workflow, node, trigger, ifElse, expr } from '@n8n/workflow-sdk';

const webhookTexto = trigger({
  type: 'n8n-nodes-base.webhook',
  version: 2.1,
  config: {
    name: 'Webhook Texto Hermes',
    position: [0, 0],
    parameters: {
      httpMethod: 'POST',
      path: 'hermes-linkedin-texto',
      authentication: 'none',
      responseMode: 'responseNode',
    },
  },
  output: [
    {
      headers: { 'x-hermes-secret': 'x'.repeat(20) },
      body: {
        postText:
          'Texto de teste validado no Telegram para o proximo post LinkedIn. #IA #AgentesDeIA #Automacao',
        tema: 'Post Telegram',
      },
    },
  ],
});

const parseAuthPayload = node({
  type: 'n8n-nodes-base.code',
  version: 2,
  config: {
    name: 'Parse Auth And Payload',
    position: [240, 0],
    parameters: {
      mode: 'runOnceForAllItems',
      language: 'javaScript',
      jsCode: `const raw = $input.first().json || {};
const body = raw.body || raw;
const headers = raw.headers || {};
const secret = String(headers['x-hermes-secret'] || headers['X-Hermes-Secret'] || body.secret || '').trim();
const authOk = secret.length >= 16;
let postText = String(
  body.postText || body.text || body.conteudo || body.content || body.message || ''
).trim();
postText = postText.replace(/\\r\\n/g, '\\n').replace(/\\n{3,}/g, '\\n\\n').trim();
const tema = String(body.tema || body.theme || body.caption || 'Post Telegram').trim().slice(0, 200) || 'Post Telegram';
const postDate = $now.setZone('America/Sao_Paulo').toFormat('yyyy-MM-dd');
const minLen = 50;
const maxLen = 3000;
let error = '';
if (!authOk) error = 'unauthorized';
else if (!postText) error = 'missing_postText';
else if (postText.length < minLen) error = 'text_too_short';
else if (postText.length > maxLen) error = 'text_too_long';
const ok = !error;
return [{
  json: {
    authOk,
    ok,
    error,
    postText,
    tema,
    postDate,
    charCount: postText.length,
    status: 'ready',
    source: 'hermes',
    notes: 'saved_via_hermes_telegram',
  },
}];`,
    },
  },
  output: [
    {
      ok: true,
      authOk: true,
      postText: 'Texto de teste validado no Telegram para o proximo post LinkedIn. #IA #AgentesDeIA #Automacao',
      tema: 'Post Telegram',
      postDate: '2026-08-11',
      charCount: 90,
      status: 'ready',
      source: 'hermes',
      notes: 'saved_via_hermes_telegram',
    },
  ],
});

const ifAuthOk = ifElse({
  version: 2.3,
  config: {
    name: 'IF Auth And Text Ok',
    position: [480, 0],
    parameters: {
      conditions: {
        combinator: 'and',
        options: { caseSensitive: true, leftValue: '', typeValidation: 'loose', version: 2 },
        conditions: [
          {
            id: 'ok',
            leftValue: expr('{{ $json.ok }}'),
            rightValue: true,
            operator: { type: 'boolean', operation: 'true', singleValue: true },
          },
        ],
      },
    },
  },
});

const supersedeOld = node({
  type: 'n8n-nodes-base.dataTable',
  version: 1.1,
  config: {
    name: 'Supersede Old Ready',
    position: [720, -80],
    parameters: {
      resource: 'row',
      operation: 'update',
      dataTableId: {
        __rl: true,
        mode: 'id',
        value: 'm1I5Y0xmJEGCsdIM',
        cachedResultName: 'LinkedIn Textos Agenda',
      },
      matchType: 'allConditions',
      filters: {
        conditions: [
          { keyName: 'status', keyValue: 'ready' },
          { keyName: 'source', keyValue: 'hermes' },
        ],
      },
      columns: {
        mappingMode: 'defineBelow',
        value: {
          status: 'superseded',
          notes: 'replaced_by_newer_hermes_text',
        },
        schema: [
          { id: 'status', displayName: 'status', required: false, defaultMatch: false, display: true, type: 'string' },
          { id: 'notes', displayName: 'notes', required: false, defaultMatch: false, display: true, type: 'string' },
        ],
      },
    },
  },
  output: [{ status: 'superseded' }],
});

const insertReady = node({
  type: 'n8n-nodes-base.dataTable',
  version: 1.1,
  config: {
    name: 'Insert Ready Text',
    position: [960, -80],
    parameters: {
      resource: 'row',
      operation: 'insert',
      dataTableId: {
        __rl: true,
        mode: 'id',
        value: 'm1I5Y0xmJEGCsdIM',
        cachedResultName: 'LinkedIn Textos Agenda',
      },
      columns: {
        mappingMode: 'defineBelow',
        value: {
          postDate: expr("{{ $('Parse Auth And Payload').item.json.postDate }}"),
          postText: expr("{{ $('Parse Auth And Payload').item.json.postText }}"),
          tema: expr("{{ $('Parse Auth And Payload').item.json.tema }}"),
          status: 'ready',
          source: 'hermes',
          notes: expr("{{ $('Parse Auth And Payload').item.json.notes }}"),
        },
        schema: [
          { id: 'postDate', displayName: 'postDate', required: false, defaultMatch: false, display: true, type: 'string' },
          { id: 'postText', displayName: 'postText', required: false, defaultMatch: false, display: true, type: 'string' },
          { id: 'tema', displayName: 'tema', required: false, defaultMatch: false, display: true, type: 'string' },
          { id: 'status', displayName: 'status', required: false, defaultMatch: false, display: true, type: 'string' },
          { id: 'source', displayName: 'source', required: false, defaultMatch: false, display: true, type: 'string' },
          { id: 'notes', displayName: 'notes', required: false, defaultMatch: false, display: true, type: 'string' },
        ],
      },
    },
  },
  output: [{ id: 1, status: 'ready' }],
});

const respondOk = node({
  type: 'n8n-nodes-base.respondToWebhook',
  version: 1.5,
  config: {
    name: 'Respond Ok',
    position: [1200, -80],
    parameters: {
      respondWith: 'json',
      responseBody: expr(
        '={{ ({ ok: true, status: "ready", charCount: $("Parse Auth And Payload").item.json.charCount, tema: $("Parse Auth And Payload").item.json.tema }) }}'
      ),
      options: { responseCode: 200 },
    },
  },
});

const respondError = node({
  type: 'n8n-nodes-base.respondToWebhook',
  version: 1.5,
  config: {
    name: 'Respond Error',
    position: [720, 120],
    parameters: {
      respondWith: 'json',
      responseBody: expr('={{ ({ ok: false, error: $json.error || "invalid_request" }) }}'),
      options: { responseCode: 400 },
    },
  },
});

export default workflow('linkedin-salvar-texto-hermes', 'LinkedIn Salvar Texto Hermes')
  .add(webhookTexto)
  .to(parseAuthPayload)
  .to(
    ifAuthOk
      .onTrue(supersedeOld.to(insertReady).to(respondOk))
      .onFalse(respondError)
  );
