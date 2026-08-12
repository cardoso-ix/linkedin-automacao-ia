import { workflow, node, trigger, ifElse, expr } from '@n8n/workflow-sdk';

const webhookFoto = trigger({
  type: 'n8n-nodes-base.webhook',
  version: 2.1,
  config: {
    name: 'Webhook Foto Hermes',
    position: [0, 0],
    parameters: {
      httpMethod: 'POST',
      path: 'hermes-linkedin-foto',
      authentication: 'none',
      responseMode: 'responseNode',
    },
  },
  output: [
    {
      headers: { 'x-hermes-secret': 'x'.repeat(20) },
      body: {
        imageBase64: 'iVBORw0KGgo=',
        mimeType: 'image/png',
        fileName: 'foto.png',
        tema: 'Foto Hermes',
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
let imageBase64 = String(body.imageBase64 || body.base64 || body.data || '').trim();
if (imageBase64.includes(',')) imageBase64 = imageBase64.split(',').pop();
imageBase64 = imageBase64.replace(/\\s+/g, '');
const mimeType = String(body.mimeType || body.contentType || 'image/jpeg').trim() || 'image/jpeg';
let fileName = String(body.fileName || body.filename || 'foto-linkedin.jpg').trim();
fileName = fileName.replace(/[^a-zA-Z0-9._-]/g, '_');
const tema = String(body.tema || body.theme || 'Foto Hermes').slice(0, 200);
const postDate = $now.setZone('America/Sao_Paulo').toFormat('yyyy-MM-dd');
const stamp = $now.setZone('America/Sao_Paulo').toFormat('yyyyMMdd-HHmmss');
const ext = mimeType.includes('png') ? 'png' : (mimeType.includes('webp') ? 'webp' : 'jpg');
const safeName = fileName.includes('.') ? fileName : (fileName + '.' + ext);
const filePath = '/home/node/.n8n/linkedin-photos/' + stamp + '-' + safeName;
const ok = Boolean(authOk && imageBase64.length > 100);
return [{
  json: {
    authOk,
    ok,
    error: !authOk ? 'unauthorized' : (!imageBase64 ? 'missing_imageBase64' : (imageBase64.length <= 100 ? 'image_too_small' : '')),
    imageBase64,
    mimeType,
    fileName: safeName,
    filePath,
    tema,
    postDate,
    status: 'ready',
    source: 'hermes',
    notes: 'saved_via_hermes_telegram',
    themeIndex: 0,
  },
}];`,
    },
  },
  output: [
    {
      ok: true,
      authOk: true,
      imageBase64: 'iVBORw0KGgo=',
      mimeType: 'image/png',
      fileName: 'foto.png',
      filePath: '/home/node/.n8n/linkedin-photos/x.png',
      tema: 'Foto Hermes',
      postDate: '2026-08-11',
      status: 'ready',
      source: 'hermes',
      notes: 'saved_via_hermes_telegram',
      themeIndex: 0,
    },
  ],
});

const ifAuthOk = ifElse({
  version: 2.3,
  config: {
    name: 'IF Auth And Image Ok',
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

const convertBase64 = node({
  type: 'n8n-nodes-base.convertToFile',
  version: 1.1,
  config: {
    name: 'Convert Base64 To Binary',
    position: [720, -80],
    parameters: {
      operation: 'toBinary',
      sourceProperty: 'imageBase64',
      options: {
        fileName: expr('{{ $json.fileName }}'),
        mimeType: expr('{{ $json.mimeType }}'),
        dataIsBase64: true,
      },
    },
  },
  output: [{ fileName: 'foto.png' }],
});

const writePhoto = node({
  type: 'n8n-nodes-base.readWriteFile',
  version: 1.1,
  config: {
    name: 'Write Photo Disk',
    position: [960, -80],
    parameters: {
      operation: 'write',
      fileName: expr('{{ $json.filePath }}'),
      dataPropertyName: 'data',
    },
  },
  output: [{ filePath: '/home/node/.n8n/linkedin-photos/x.png' }],
});

const supersedeOld = node({
  type: 'n8n-nodes-base.dataTable',
  version: 1.1,
  config: {
    name: 'Supersede Old Ready',
    position: [1200, -80],
    parameters: {
      resource: 'row',
      operation: 'update',
      dataTableId: {
        __rl: true,
        mode: 'id',
        value: 'iuKvPfKaSd77gl4H',
        cachedResultName: 'LinkedIn Imagens Agenda',
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
          notes: 'replaced_by_newer_hermes_photo',
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
    name: 'Insert Ready Photo',
    position: [1440, -80],
    parameters: {
      resource: 'row',
      operation: 'insert',
      dataTableId: {
        __rl: true,
        mode: 'id',
        value: 'iuKvPfKaSd77gl4H',
        cachedResultName: 'LinkedIn Imagens Agenda',
      },
      columns: {
        mappingMode: 'defineBelow',
        value: {
          postDate: expr("{{ $('Parse Auth And Payload').item.json.postDate }}"),
          imageUrl: expr("{{ $('Parse Auth And Payload').item.json.filePath }}"),
          themeIndex: 0,
          tema: expr("{{ $('Parse Auth And Payload').item.json.tema }}"),
          status: 'ready',
          notes: expr("{{ $('Parse Auth And Payload').item.json.notes }}"),
          filePath: expr("{{ $('Parse Auth And Payload').item.json.filePath }}"),
          source: 'hermes',
        },
        schema: [
          { id: 'postDate', displayName: 'postDate', required: false, defaultMatch: false, display: true, type: 'string' },
          { id: 'imageUrl', displayName: 'imageUrl', required: false, defaultMatch: false, display: true, type: 'string' },
          { id: 'themeIndex', displayName: 'themeIndex', required: false, defaultMatch: false, display: true, type: 'number' },
          { id: 'tema', displayName: 'tema', required: false, defaultMatch: false, display: true, type: 'string' },
          { id: 'status', displayName: 'status', required: false, defaultMatch: false, display: true, type: 'string' },
          { id: 'notes', displayName: 'notes', required: false, defaultMatch: false, display: true, type: 'string' },
          { id: 'filePath', displayName: 'filePath', required: false, defaultMatch: false, display: true, type: 'string' },
          { id: 'source', displayName: 'source', required: false, defaultMatch: false, display: true, type: 'string' },
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
    position: [1680, -80],
    parameters: {
      respondWith: 'json',
      responseBody: expr(
        '={{ ({ ok: true, status: "ready", filePath: $("Parse Auth And Payload").item.json.filePath, tema: $("Parse Auth And Payload").item.json.tema }) }}'
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

export default workflow('linkedin-salvar-foto-hermes', 'LinkedIn Salvar Foto Hermes')
  .add(webhookFoto)
  .to(parseAuthPayload)
  .to(
    ifAuthOk
      .onTrue(
        convertBase64
          .to(writePhoto)
          .to(supersedeOld)
          .to(insertReady)
          .to(respondOk)
      )
      .onFalse(respondError)
  );
