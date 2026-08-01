// Cole no node Code: Generate Post Text Free
// Entrada: item de Build Theme Context

const ctx = $input.first().json || {};
const tema = String(ctx.tema || 'Agentes de IA');
const themeIndex = Number(ctx.themeIndex || 1);
const dayOfMonth = Number(ctx.dayOfMonth || 1);
const today = String(ctx.today || '');

const hooks = [
  'IA sem criterio vira teatro. Com criterio, vira vantagem.',
  'O problema quase nunca e o modelo. E o processo ao redor.',
  'Automacao burra escala erro. Automacao com IA precisa de regra.',
  'Se nao da para medir, nao da para melhorar — nem com IA.',
  'Agente de IA nao e magica. E orquestracao com responsabilidade.',
  'Hype vende slide. Operacao boa vende resultado.',
  'O melhor prompt do mundo nao salva dado ruim.',
  'Antes de pedir inteligencia, organize a rotina.',
];
const hook = hooks[(themeIndex - 1) % hooks.length];

const develop =
  'Quando o tema e "' +
  tema +
  '", o erro comum e comecar pela ferramenta e esquecer a regra: entrada clara, decisao explicita e saida util.';
const develop2 =
  'Na pratica, isso vira checklist: o que entra, o que a IA decide, o que um humano valida e o que e registrado.';

const bulletSets = [
  [
    'Defina o resultado mensuravel antes de escolher modelo',
    'Separe geracao de decisao (e de publicacao)',
    'Coloque humano no ponto de risco, nao em tudo',
    'Registre falha com causa, nao so com desculpa',
  ],
  [
    'Comece por um fluxo estreito e observavel',
    'Evite catalogo de ferramentas sem criterio',
    'Padronize prompt, entrada e saida',
    'Meca retrabalho, nao so posts gerados',
  ],
  [
    'Trate custo e latencia como requisito',
    'Use memoria so quando reduzir erro real',
    'Teste com casos feios, nao so o feliz',
    'Desligue o que nao justifica manutencao',
  ],
];
const bullets = bulletSets[(themeIndex - 1) % bulletSets.length];

const questions = [
  'Voce ja tem criterio escrito para isso — sim ou nao?',
  'No seu time, IA acelera processo ou so gera mais texto?',
  'Comenta A (processo) ou B (modelo) o que mais trava hoje.',
  'Voce mediria sucesso por velocidade ou por erro evitado?',
];
const question = questions[(themeIndex - 1) % questions.length];

const tagSets = [
  '#IA #InteligenciaArtificial #AgentesIA',
  '#IA #Automacao #AgentesIA',
  '#InteligenciaArtificial #LLM #n8n',
  '#IA #FuturoDoTrabalho #AgentesIA',
];
const tags = tagSets[(themeIndex - 1) % tagSets.length];

const postText = [
  hook,
  '',
  develop,
  '',
  develop2,
  '',
  ...bullets.map((b) => '• ' + b),
  '',
  question,
  '',
  tags,
].join('\n');

if (postText.length < 200) {
  throw new Error('Template curto demais (' + postText.length + ')');
}

return [
  {
    json: {
      text: postText,
      content: postText,
      postText,
      tema,
      themeIndex,
      dayOfMonth,
      today,
      textSource: 'template_free',
    },
  },
];
