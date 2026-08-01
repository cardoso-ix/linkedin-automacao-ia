// Cole no node Code: Pick Catalog Image
// Entrada: linhas de Get Catalog Images (LinkedIn Imagens Agenda)

const sanitize = $('Sanitize Post Text').item.json || {};
const today = String(($('Build Theme Context').item.json || {}).today || '');
const themeIndex = Number(sanitize.themeIndex || 0);
const rows = $input
  .all()
  .map((i) => i.json)
  .filter((r) => r && String(r.imageUrl || '').trim());

let chosen = rows.find((r) => String(r.postDate || '') === today);
if (!chosen) chosen = rows.find((r) => Number(r.themeIndex) === themeIndex);
if (!chosen && rows.length) {
  chosen = rows[(Math.max(themeIndex, 1) - 1) % rows.length];
}

const imageUrl = chosen ? String(chosen.imageUrl || '').trim() : '';

return [
  {
    json: {
      ...sanitize,
      hasCatalogUrl: Boolean(imageUrl),
      imageUrl,
      catalogPostDate: chosen ? String(chosen.postDate || '') : '',
      catalogTema: chosen ? String(chosen.tema || '') : '',
      imageSource: imageUrl ? 'catalog' : 'none',
      catalogCount: rows.length,
    },
  },
];
