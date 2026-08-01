// Cole no node Code: Check Infographic Ready (versão catálogo)

const input = $input.first();
const sanitize = $('Sanitize Post Text').item.json;
let pick = {};
try {
  pick = $('Pick Catalog Image').item.json || {};
} catch (e) {
  pick = {};
}

const binary = input.binary || {};
const keys = Object.keys(binary);
const hasBinary = keys.length > 0 && !!(binary.data || binary[keys[0]]);
const err = input.json && (input.json.error || input.json.errorMessage);
const hasInfographic = hasBinary && !err;

const out = {
  json: {
    ...sanitize,
    hasInfographic,
    imageSource: hasInfographic ? pick.imageSource || 'catalog' : 'fallback',
    imageUrl: pick.imageUrl || '',
  },
};
if (hasBinary) out.binary = binary;
return [out];
