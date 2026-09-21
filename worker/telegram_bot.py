import os
import sys
import uuid
import json
import asyncio
import logging
import re
import requests
from typing import Optional, Dict, Tuple

logger = logging.getLogger("telegram_bot")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "SEU_TELEGRAM_BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "SEU_CHAT_ID")
OPENCODE_KEY = os.getenv("OPENCODE_API_KEY", "SUA_OPENCODE_API_KEY")
OPENCODE_URL = os.getenv("OPENCODE_API_BASE", "https://opencode.ai/zen/go/v1") + "/chat/completions"
SHARED_DIR = os.getenv("SHARED_DIR", "/app/shared")
DRAFTS_FILE = os.path.join(SHARED_DIR, "user_drafts.json")

def load_user_drafts() -> Dict[str, Dict]:
    if os.path.exists(DRAFTS_FILE):
        try:
            with open(DRAFTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_user_drafts(drafts: Dict[str, Dict]):
    try:
        with open(DRAFTS_FILE, "w", encoding="utf-8") as f:
            json.dump(drafts, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[!] Erro ao salvar rascunhos: {e}")

# State tracking
user_drafts: Dict[str, Dict] = load_user_drafts()
pending_engagements: Dict[str, Dict] = {}
pending_replies: Dict[str, Dict] = {}
pending_post_proposals: Dict[str, Dict] = {}

def send_telegram_message(text: str, reply_markup: Optional[dict] = None) -> Optional[int]:
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": ADMIN_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        r = requests.post(url, json=payload, timeout=15)
        if r.status_code == 200:
            return r.json().get("result", {}).get("message_id")
    except Exception as e:
        print(f"[!] Erro ao enviar mensagem Telegram: {e}")
    return None

def edit_telegram_message(message_id: int, text: str, reply_markup: Optional[dict] = None):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/editMessageText"
    payload = {
        "chat_id": ADMIN_CHAT_ID,
        "message_id": message_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    if reply_markup is not None:
        payload["reply_markup"] = reply_markup
    try:
        requests.post(url, json=payload, timeout=15)
    except Exception as e:
        print(f"[!] Erro ao editar mensagem Telegram: {e}")

def call_deepseek(prompt: str, mode: str = "engage") -> str:
    """
    mode:
      - 'reply': resposta a comentário em post próprio
      - 'engage': comentário em post de terceiros enviado via link
      - 'post': criação de nova publicação (fallback)
    """
    if mode == "reply":
        system = (
            "Você é o próprio Eduardo Cardoso no LinkedIn (especialista em Automação e IA).\n"
            "Escreva uma resposta curta, inteligente e conversacional ao comentário recebido no seu post.\n"
            "Regras estritas anti-IA:\n"
            "1. Proibido qualquer saudação vazia ('Com certeza!', 'Excelente ponto!', 'Concordo totalmente!').\n"
            "2. Proibido qualquer emoji corporativo (sem 🚀, sem 🔥, sem 💡, sem 👏, sem 👇).\n"
            "3. Proibido usar travessões (—) ou listas com marcadores.\n"
            "4. Responda em 1 a 3 frases, direto ao ponto, tom humano, profissional e autêntico."
        )
    elif mode == "engage":
        system = (
            "Você é o Eduardo Cardoso no LinkedIn (atua com Automação, IA Agêntica, n8n e Integrações).\n"
            "Crie um comentário perspicaz, construtivo e inteligente para enriquecer a discussão sobre a postagem.\n"
            "Regras estritas anti-IA:\n"
            "1. NUNCA comece bajulando ('Parabéns pelo post', 'Excelente reflexão', 'Muito bom', 'Concordo'). Comece direto pelo argumento.\n"
            "2. NUNCA use emojis corporativos (sem 🚀, sem 🔥, sem 💡, sem 👏, sem 👇).\n"
            "3. NUNCA use travessões (—) nem tópicos/listas numeradas.\n"
            "4. Seja conciso (no máximo 2 ou 3 frases). Traga um ponto prático, técnico ou questionamento inteligente.\n"
            "5. Soa 100% natural, como um colega sênior de mercado comentando."
        )
    else:
        system = (
            "Você é o próprio Eduardo Cardoso no LinkedIn (especialista em Automação e IA Agêntica).\n"
            "Crie um post de alto impacto e leitura agradável para o LinkedIn a partir da ideia fornecida.\n"
            "Regras estritas anti-IA:\n"
            "1. Proibido emojis corporativos (sem 🚀, 🔥, 💡, 👏, 📌, 👇, 🎯). No máximo 1 emoji muito sutil ou nenhum.\n"
            "2. Proibido travessões longos de IA ('—'). Use vírgulas, pontos ou parênteses.\n"
            "3. Proibido listas com marcadores ('•', '-', '1.'). Parágrafos curtos fluidos.\n"
            "4. Proibido CTAs apelativos ('Deixe nos comentários 👇'). Conclua com reflexão honesta.\n"
            "5. Tamanho entre 800 e 1.600 caracteres."
        )

    headers = {
        "Authorization": f"Bearer {OPENCODE_KEY}",
        "Content-Type": "application/json",
        "x-opencode-session": str(uuid.uuid4())
    }
    data = {
        "model": "deepseek-v4.1-flash",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    try:
        r = requests.post(OPENCODE_URL, headers=headers, json=data, timeout=35)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"].strip()
        else:
            return f"Erro na API DeepSeek (status {r.status_code})"
    except Exception as e:
        return f"Erro de conexão com DeepSeek: {e}"

def call_deepseek_dual_post(idea: str) -> Tuple[Dict, Dict]:
    """
    Gera duas propostas de posts para o LinkedIn com ângulos distintos,
    acompanhadas dos respectivos prompts de imagem técnica para o Meta AI:
    - Variação 1: Bastidores / Storytelling Real de Trincheira
    - Variação 2: Análise Técnica / Arquitetura
    """
    system_prompt = (
        "Você é o próprio Eduardo Cardoso no LinkedIn. Especialista sênior em Engenharia de Automação, IA Agêntica, n8n, Python e Integrações.\n"
        "Seu estilo é o de um 'pragmático de trincheira': você coloca a mão na massa, lida com produção real e compartilha aprendizados de colega sênior para colega sênior, com zero papo de palco.\n\n"
        "REGRAS ESTRITAS ANTI-IA (VIOLAÇÃO É INACEITÁVEL):\n"
        "1. PROIBIDO qualquer emoji corporativo (sem 🚀, sem 🔥, sem 💡, sem 👏, sem 📌, sem 👇, sem 🎯). Use no máximo 1 emoji muito sutil no texto inteiro ou nenhum.\n"
        "2. PROIBIDO travessões longos de IA ('—'). Use vírgulas, pontos ou parênteses naturais.\n"
        "3. PROIBIDO listas de marcadores artificiais (nada de '•', '-', '1.', '2.'). O texto deve fluir em parágrafos humanos bem espaçados.\n"
        "4. PROIBIDO aberturas clichês ('No mundo acelerado de hoje...', 'Você já parou para pensar...', 'Recentemente me deparei...'). Comece direto no fato, no problema ou na constatação forte.\n"
        "5. PROIBIDO apelos forçados de engajamento no final ('E você, o que acha? Deixe nos comentários! 👇', 'Compartilhe com a rede'). Conclua com uma reflexão técnica honesta e sóbria.\n"
        "6. PROIBIDO buzzwords vazias ('mindset', 'disruptivo', 'ecossistema', 'revolucionar', 'game changer', 'sinergia').\n"
        "7. TAMANHO: Cada post deve ter entre 800 e 1.600 caracteres, com parágrafos curtos (1 a 3 frases) separados por linha em branco para leitura confortável no celular.\n\n"
        "DIRETRIZES PARA O PROMPT DE IMAGEM (META AI):\n"
        "Para cada variação de post, gere um prompt de imagem técnico, profissional e direto para o Meta AI criar um asset visual de altíssimo impacto no LinkedIn.\n"
        "REGRAS VISUAIS MANDATÓRIAS (BASEADAS EM POSTS VIRAIS DE TECH NO LINKEDIN BRASIL):\n"
        "1. IDIOMA DO TEXTO NA IMAGEM: 100% PORTUGUÊS DO BRASIL. Qualquer título, cabeçalho, rótulo de etapa ou badge a ser exibido visualmente na imagem DEVE estar estritamente em português do Brasil e entre aspas (ex: 'ARQUITETURA DE PRODUÇÃO', '1. Triagem Automática', '2. Validação Humana'). NUNCA use termos em inglês na arte (nada de 'Text In', 'Text Out', 'human-in-the-loop').\n"
        "2. FORMATO & LAYOUT (ESCOLHA O ARQUÉTIPO ADEQUADO AO TEMA):\n"
        "   - Arquétipo A (Infográfico em Cards / Grid Dark Mode): Título marcante no topo em português, 3 a 4 cards conceituais organizados com bordas sutis e ícones funcionais.\n"
        "   - Arquétipo B (Diagrama de Fluxo Técnico de Engenharia): Estilo Miro/Excalidraw/n8n dark mode, com nós de processo conectados de ponta a ponta com rótulos em português.\n"
        "   - Arquétipo C (Comparativo Lado a Lado): 'Abordagem Frágil' vs 'Abordagem em Produção'.\n"
        "3. ESTILO TÉCNICO: Fundo escuro elegante (#0f172a / dark slate / obsidian), design flat vetorial moderno, linhas nítidas, tipografia limpa, proporção panorâmica 16:9 (Wide 16:9 aspect ratio).\n"
        "4. PROIBIDO TERMINANTEMENTE: Placas/camadas de vidro 3D flutuantes abstratas (render genérico falso), esferas brilhantes sem sentido, robôs humanoides metálicos, fotos de pessoas genéricas sorrindo, e flags do Midjourney (sem --ar ou --v).\n"
        "O prompt para o Meta AI deve ser escrito em inglês para direcionar o estilo gráfico, mas COM TODOS OS TÍTULOS E LABELS LITERAIS ENTRE ASPAS EM PORTUGUÊS DO BRASIL.\n\n"
        "INSTRUÇÃO DE SAÍDA:\n"
        "Gere EXATAMENTE a saída dividida pelas tags abaixo:\n\n"
        "===VARIAÇÃO 1===\n"
        "(Texto do post da Variação 1: Bastidores & Caso Real)\n\n"
        "===PROMPT IMAGEM 1===\n"
        "(Prompt otimizado para o Meta AI para a Variação 1 seguindo as regras acima)\n\n"
        "===VARIAÇÃO 2===\n"
        "(Texto do post da Variação 2: Arquitetura & Visão Crítica)\n\n"
        "===PROMPT IMAGEM 2===\n"
        "(Prompt otimizado para o Meta AI para a Variação 2 seguindo as regras acima)"
    )

    headers = {
        "Authorization": f"Bearer {OPENCODE_KEY}",
        "Content-Type": "application/json",
        "x-opencode-session": str(uuid.uuid4())
    }
    data = {
        "model": "deepseek-v4.1-flash",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": idea}
        ],
        "temperature": 0.7
    }
    try:
        r = requests.post(OPENCODE_URL, headers=headers, json=data, timeout=50)
        if r.status_code == 200:
            content = r.json()["choices"][0]["message"]["content"].strip()
            v1_text, img1_prompt, v2_text, img2_prompt = "", "", "", ""
            
            if "===PROMPT IMAGEM 1===" in content and "===VARIAÇÃO 2===" in content and "===PROMPT IMAGEM 2===" in content:
                p1 = content.split("===PROMPT IMAGEM 1===")
                v1_text = p1[0].replace("===VARIAÇÃO 1===", "").strip()
                p2 = p1[1].split("===VARIAÇÃO 2===")
                img1_prompt = p2[0].strip()
                p3 = p2[1].split("===PROMPT IMAGEM 2===")
                v2_text = p3[0].strip()
                img2_prompt = p3[1].strip()
            elif "===VARIAÇÃO 2===" in content:
                parts = content.split("===VARIAÇÃO 2===")
                v1_text = parts[0].replace("===VARIAÇÃO 1===", "").strip()
                v2_text = parts[1].strip()
                img1_prompt = "Wide 16:9 aspect ratio, dark mode minimalist technical architecture diagram, clean glowing data lines, sleek modern aesthetic, 4k render."
                img2_prompt = "Wide 16:9 aspect ratio, dark mode clean vector tech workflow diagram, minimalist node connections, high contrast, 4k render."
            else:
                v1_text = content
                v2_text = content
                img1_prompt = "Wide 16:9 aspect ratio, dark mode minimalist technical illustration, 4k render."
                img2_prompt = img1_prompt

            return (
                {"text": v1_text, "image_prompt": img1_prompt},
                {"text": v2_text, "image_prompt": img2_prompt}
            )
        else:
            err = f"Erro na API DeepSeek (status {r.status_code})"
            return ({"text": err, "image_prompt": ""}, {"text": err, "image_prompt": ""})
    except Exception as e:
        err = f"Erro de conexão com DeepSeek: {e}"
        return ({"text": err, "image_prompt": ""}, {"text": err, "image_prompt": ""})

LINKEDIN_URL_REGEX = re.compile(r"https?://(?:[a-zA-Z0-9-]+\.)?(?:linkedin\.com|lnkd\.in)/[^\s]+")

HELP_TEXT = (
    "💡 *Guia do Assistente LinkedIn — Eduardo Cardoso*\n\n"
    "Seu assistente conta exclusivamente com as funções essenciais para o seu dia a dia:\n\n"
    "1️⃣ *Curtir e Comentar Posts de Terceiros:*\n"
    "• Cole o link de qualquer post do LinkedIn aqui no chat (ex: `https://www.linkedin.com/posts/...` ou `lnkd.in/...`).\n"
    "• O assistente extrai o autor e o texto, e o DeepSeek v4.1 redige um comentário perspicaz e sem clichês.\n"
    "• Você aprova com 1 clique no botão `[✅ Curtir e Comentar Post]`!\n\n"
    "2️⃣ *Criar Nova Publicação:*\n"
    "• Envie `/post sua ideia ou tema` (ex: `/post Agentes autônomos integrados ao n8n`).\n"
    "• O DeepSeek v4.1 gera a cópia completa otimizada para leitura no celular.\n"
    "• Se desejar imagem, basta enviar a foto logo em seguida e confirmar!\n\n"
    "3️⃣ *Comandos Rápidos:*\n"
    "• `/menu` — Abre o painel com botões interativos de ação rápida\n"
    "• `/visitantes` — Lista quem visitou seu perfil recentemente no LinkedIn Premium\n"
    "• `/status` — Checa a saúde da sessão do LinkedIn, IA e servidor\n"
    "• `/ajuda` — Mostra este guia de instruções"
)

async def handle_profile_views(msg_id: Optional[int] = None):
    initial_text = "🔍 *Consultando visitantes recentes no LinkedIn Premium...*"
    if msg_id:
        edit_telegram_message(msg_id, initial_text)
    else:
        send_telegram_message(initial_text)

    from app import get_profile_views
    try:
        data = await get_profile_views()
        viewers = data.get("viewers", [])
        count = data.get("count", 0)

        if count == 0:
            msg = "👀 *Nenhum visitante recente identificado no momento.*"
            if msg_id:
                edit_telegram_message(msg_id, msg)
            else:
                send_telegram_message(msg)
            return

        lines = [f"👀 *Quem Viu Seu Perfil ({count} recentes — LinkedIn Premium):*\n"]
        for v in viewers[:8]:
            tag = ""
            if v.get("isRecruiter"):
                tag = " 🎯 *[Recrutador/RH]*"
            elif v.get("isDecisionMaker"):
                tag = " 💼 *[Tomador de Decisão]*"

            time_str = f" • _{v.get('timeAgo')}_" if v.get('timeAgo') else ""
            lines.append(
                f"👤 *{v['name']}*{tag}{time_str}\n"
                f"📌 {v['headline']}\n"
                f"🔗 [Acessar Perfil]({v['profileUrl']})\n"
            )

        lines.append("💡 *Dica:* Para recrutadores e líderes, envie uma mensagem sutil e elegante pelo chat ou InMail agradecendo a visita!")
        final_text = "\n".join(lines)
        if msg_id:
            edit_telegram_message(msg_id, final_text)
        else:
            send_telegram_message(final_text)
    except Exception as e:
        err = f"❌ *Erro ao consultar visitantes:* {e}"
        if msg_id:
            edit_telegram_message(msg_id, err)
        else:
            send_telegram_message(err)

def send_main_menu(message_id: Optional[int] = None):
    text = (
        "⚡ *Painel de Controle — Assistente LinkedIn*\n\n"
        "Selecione uma ação rápida abaixo ou envie diretamente um comando/link:"
    )
    keyboard = {
        "inline_keyboard": [
            [{"text": "✍️ Criar Novo Post", "callback_data": "menu_action:post"}],
            [{"text": "👀 Quem Viu Meu Perfil (Premium)", "callback_data": "menu_action:views"}],
            [{"text": "📊 Checar Status da Conexão", "callback_data": "menu_action:status"}],
            [{"text": "💡 Guia de Utilização", "callback_data": "menu_action:help"}]
        ]
    }
    if message_id:
        edit_telegram_message(message_id, text, reply_markup=keyboard)
    else:
        send_telegram_message(text, reply_markup=keyboard)

async def run_telegram_loop(pw_manager):
    print("[*] Iniciando Telegram Bot Daemon para o usuario:", ADMIN_CHAT_ID)
    offset = 0

    # Mensagem de boas-vindas com todas as capacidades ativas
    send_telegram_message(
        "🤖 *Assistente LinkedIn Conectado e Operacional!*\n\n"
        "Menu limpo e configurado com os recursos essenciais:\n"
        "• ✍️ `/post <ideia>` — Criar publicação com ou sem foto\n"
        "• 📊 `/status` — Verificar saúde da conexão e serviços\n"
        "• 💡 `/ajuda` — Guia prático de utilização\n"
        "• ⚡ `/menu` — Painel interativo com botões rápidos\n\n"
        "🔗 _Dica: Você também pode colar qualquer link do LinkedIn aqui para curtir e comentar._"
    )

    while True:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates?offset={offset}&timeout=20"
            r = await asyncio.to_thread(requests.get, url, timeout=25)
            if r.status_code != 200:
                await asyncio.sleep(5)
                continue

            data = r.json()
            if not data.get("ok"):
                await asyncio.sleep(5)
                continue

            for update in data.get("result", []):
                offset = update["update_id"] + 1

                # ==========================================
                # 1. TRATA CALLBACK QUERIES (BOTÕES INLINE)
                # ==========================================
                if "callback_query" in update:
                    cb = update["callback_query"]
                    cb_id = cb["id"]
                    cb_data = cb.get("data", "")
                    msg_id = cb["message"]["message_id"]

                    # Confirma recebimento do clique
                    await asyncio.to_thread(
                        requests.post,
                        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/answerCallbackQuery",
                        json={"callback_query_id": cb_id}
                    )

                    # --- APROVAR ENGAJAMENTO EM POST DE TERCEIROS ---
                    if cb_data.startswith("approve_engage:"):
                        engage_id = cb_data.split(":", 1)[1]
                        item = pending_engagements.get(engage_id)
                        if item:
                            edit_telegram_message(msg_id, "⏳ *Acessando LinkedIn... Curtindo post e digitando comentário com delay humano...*")
                            from app import engage_post, PostEngageRequest
                            try:
                                req = PostEngageRequest(
                                    post_url=item["post_url"],
                                    comment_text=item["comment_text"],
                                    like_first=True
                                )
                                res = await engage_post(req)
                                edit_telegram_message(
                                    msg_id,
                                    f"✅ *Sucesso absoluto!*\n\n"
                                    f"• *Post curtido:* Sim (Reação Gostei)\n"
                                    f"• *Comentário publicado no perfil de:* {item['author']}\n"
                                    f"• *Texto enviado:* _{item['comment_text']}_"
                                )
                                pending_engagements.pop(engage_id, None)
                            except Exception as e:
                                edit_telegram_message(msg_id, f"❌ *Erro ao publicar no LinkedIn:* {e}")
                        else:
                            edit_telegram_message(msg_id, "⚠️ *Essa solicitação expirou ou já foi processada.*")

                    # --- REGENERAR COMENTÁRIO PARA POST ---
                    elif cb_data.startswith("regen_engage:"):
                        engage_id = cb_data.split(":", 1)[1]
                        item = pending_engagements.get(engage_id)
                        if item:
                            edit_telegram_message(msg_id, "🔄 *Gerando outra opção de comentário com o DeepSeek v4.1...*")
                            prompt = f"Post de {item['author']}: '{item['text']}'"
                            new_comment = await asyncio.to_thread(call_deepseek, prompt, "engage")
                            item["comment_text"] = new_comment

                            keyboard = {
                                "inline_keyboard": [
                                    [{"text": "✅ Curtir e Comentar Post", "callback_data": f"approve_engage:{engage_id}"}],
                                    [{"text": "🔄 Gerar Outra Opção", "callback_data": f"regen_engage:{engage_id}"}],
                                    [{"text": "❌ Cancelar", "callback_data": f"cancel_engage:{engage_id}"}]
                                ]
                            }
                            edit_telegram_message(
                                msg_id,
                                f"🎯 *Post do LinkedIn Identificado:*\n\n"
                                f"👤 *Autor:* {item['author']}\n"
                                f"📝 *Trecho do Post:* _{item['text'][:140]}..._\n\n"
                                f"💬 *Nova Sugestão de Comentário:*\n"
                                f"_{new_comment}_\n\n"
                                f"👉 *Deseja curtir a postagem e publicar este comentário?*",
                                reply_markup=keyboard
                            )

                    # --- CANCELAR ENGAJAMENTO ---
                    elif cb_data.startswith("cancel_engage:"):
                        engage_id = cb_data.split(":", 1)[1]
                        pending_engagements.pop(engage_id, None)
                        edit_telegram_message(msg_id, "❌ *Ação cancelada. O post não foi curtido nem comentado.*")

                    # --- APROVAR RESPOSTA A COMENTÁRIO EM POST PRÓPRIO ---
                    elif cb_data.startswith("approve_reply:"):
                        comment_id = cb_data.split(":", 1)[1]
                        item = pending_replies.get(comment_id)
                        edit_telegram_message(msg_id, "⏳ *Curtindo comentário e postando resposta com delay humano...*")
                        from app import reply_comment, ReplyRequest
                        try:
                            if item:
                                req = ReplyRequest(
                                    post_url=item["post_url"],
                                    comment_text=item.get("comment_text"),
                                    reply_text=item["reply_text"],
                                    like_first=True
                                )
                                await reply_comment(req)
                                pending_replies.pop(comment_id, None)
                            edit_telegram_message(msg_id, "✅ *Resposta publicada e comentário do seguidor curtido com sucesso no LinkedIn!*")
                        except Exception as e:
                            edit_telegram_message(msg_id, f"❌ *Erro ao responder comentário:* {e}")

                    # --- REJEITAR RESPOSTA A COMENTÁRIO ---
                    elif cb_data.startswith("reject_reply:"):
                        comment_id = cb_data.split(":", 1)[1]
                        pending_replies.pop(comment_id, None)
                        edit_telegram_message(msg_id, "❌ *Comentário descartado sem resposta.*")

                    # --- PUBLICAR POST PRÓPRIO (/post) ---
                    elif cb_data == "publish_post_now":
                        draft = user_drafts.get(ADMIN_CHAT_ID, {})
                        if draft and draft.get("text"):
                            edit_telegram_message(msg_id, "⏳ *Publicando post no seu feed do LinkedIn...*")
                            from app import publish_post, PublishPostRequest
                            req = PublishPostRequest(text=draft["text"], image_filename=draft.get("image"))
                            try:
                                res = await publish_post(req)
                                edit_telegram_message(msg_id, "🚀 *Post publicado com sucesso no seu perfil do LinkedIn!*")
                                user_drafts.pop(ADMIN_CHAT_ID, None)
                                save_user_drafts(user_drafts)
                            except Exception as e:
                                edit_telegram_message(msg_id, f"❌ *Erro ao publicar no LinkedIn:* {e}")
                        else:
                            edit_telegram_message(msg_id, "⚠️ *Nenhum rascunho de post pendente.*")

                    # --- ESCOLHER VARIAÇÃO DE POST (/post) ---
                    elif cb_data.startswith("choose_post:"):
                        _, prop_id, opt_num = cb_data.split(":")
                        prop = pending_post_proposals.get(prop_id)
                        if prop:
                            chosen = prop["opt1"] if opt_num == "1" else prop["opt2"]
                            chosen_text = chosen["text"]
                            img_prompt = chosen.get("image_prompt", "")
                            user_drafts[ADMIN_CHAT_ID] = {"text": chosen_text, "image": None}
                            save_user_drafts(user_drafts)
                            
                            keyboard = {
                                "inline_keyboard": [
                                    [{"text": "🚀 Publicar Sem Foto", "callback_data": "publish_post_now"}],
                                    [{"text": "❌ Descartar", "callback_data": "cancel_draft"}]
                                ]
                            }
                            
                            msg_content = (
                                f"✅ *Opção {opt_num} Selecionada!*\n\n"
                                f"📝 *Texto para Publicação:*\n\n"
                                f"{chosen_text}\n\n"
                                f"──────────────\n"
                                f"🎨 *Prompt para o Meta AI* _(toque para copiar):_\n"
                                f"```\n{img_prompt}\n```\n\n"
                                f"👉 *Como gerar a imagem:*\n"
                                f"1. Toque no bloco de código acima para copiar o prompt em inglês.\n"
                                f"2. Cole no **Meta AI** (WhatsApp ou Web) para gerar a arte 16:9.\n"
                                f"3. Se quiser postar com ela, **envie a foto aqui no chat**.\n"
                                f"4. Ou clique abaixo para publicar apenas o texto agora:"
                            )
                            edit_telegram_message(msg_id, msg_content, reply_markup=keyboard)
                        else:
                            edit_telegram_message(msg_id, "⚠️ *Essa proposta expirou ou já foi utilizada.*")

                    # --- REGENERAR PROPOSTAS DE POST ---
                    elif cb_data.startswith("regen_post:"):
                        prop_id = cb_data.split(":", 1)[1]
                        prop = pending_post_proposals.get(prop_id)
                        if prop:
                            edit_telegram_message(msg_id, "🔄 *Gerando 2 novas opções humanizadas com o DeepSeek v4.1...*")
                            opt1, opt2 = await asyncio.to_thread(call_deepseek_dual_post, prop["idea"])
                            prop["opt1"] = opt1
                            prop["opt2"] = opt2
                            
                            keyboard = {
                                "inline_keyboard": [
                                    [
                                        {"text": "1️⃣ Escolher Opção 1", "callback_data": f"choose_post:{prop_id}:1"},
                                        {"text": "2️⃣ Escolher Opção 2", "callback_data": f"choose_post:{prop_id}:2"}
                                    ],
                                    [{"text": "🔄 Gerar Novas Opções", "callback_data": f"regen_post:{prop_id}"}],
                                    [{"text": "❌ Cancelar", "callback_data": f"cancel_post:{prop_id}"}]
                                ]
                            }
                            
                            opt1_text = opt1["text"]
                            opt2_text = opt2["text"]
                            msg_text = (
                                f"🎯 *Novas Opções Geradas para o seu LinkedIn:*\n\n"
                                f"──────────────\n"
                                f"📌 *OPÇÃO 1 — Bastidores & Caso Real:*\n\n"
                                f"{opt1_text}\n\n"
                                f"──────────────\n"
                                f"📌 *OPÇÃO 2 — Arquitetura & Visão Crítica:*\n\n"
                                f"{opt2_text}\n\n"
                                f"👉 *Qual das duas você prefere publicar?*"
                            )
                            if len(msg_text) <= 4000:
                                edit_telegram_message(msg_id, msg_text, reply_markup=keyboard)
                            else:
                                edit_telegram_message(msg_id, f"📌 *OPÇÃO 1 — Bastidores & Caso Real:*\n\n{opt1_text}")
                                send_telegram_message(
                                    f"📌 *OPÇÃO 2 — Arquitetura & Visão Crítica:*\n\n{opt2_text}\n\n👉 *Qual das duas você prefere publicar?*",
                                    reply_markup=keyboard
                                )
                        else:
                            edit_telegram_message(msg_id, "⚠️ *Essa proposta expirou.*")

                    # --- CANCELAR PROPOSTA DE POST ---
                    elif cb_data.startswith("cancel_post:"):
                        prop_id = cb_data.split(":", 1)[1]
                        pending_post_proposals.pop(prop_id, None)
                        edit_telegram_message(msg_id, "❌ *Criação de post cancelada.*")

                    elif cb_data == "cancel_draft":
                        user_drafts.pop(ADMIN_CHAT_ID, None)
                        save_user_drafts(user_drafts)
                        edit_telegram_message(msg_id, "❌ *Rascunho de post descartado.*")

                    # --- AÇÕES DO MENU PRINCIPAL ---
                    elif cb_data.startswith("menu_action:"):
                        action = cb_data.split(":", 1)[1]
                        if action == "post":
                            edit_telegram_message(
                                msg_id,
                                "✍️ *Como criar uma nova publicação:*\n\n"
                                "Envie uma mensagem começando com `/post` seguido da sua ideia ou tema.\n\n"
                                "📌 *Exemplo:*\n"
                                "`/post Como estruturamos agentes de IA autônomos no n8n`\n\n"
                                "_O DeepSeek v4.1 irá redigir o texto e você poderá revisar ou anexar foto antes de publicar._"
                            )
                        elif action == "views":
                            await handle_profile_views(msg_id)
                        elif action == "status":
                            from app import status
                            st = await status()
                            edit_telegram_message(
                                msg_id,
                                f"📊 *Status do Sistema:*\n\n"
                                f"• *LinkedIn Logado:* {'✅ Sim' if st.get('logged_in') else '❌ Não'}\n"
                                f"• *URL:* `{st.get('current_url')}`\n"
                                f"• *DeepSeek:* ✅ Ativo (OpenCode Go v4.1)\n"
                                f"• *n8n:* ✅ Online na porta 5678\n\n"
                                f"_Sessão ativa e operacional._"
                            )
                        elif action == "help":
                            edit_telegram_message(msg_id, HELP_TEXT)

                # ==========================================
                # 2. TRATA MENSAGENS DE TEXTO E MÍDIA
                # ==========================================
                if "message" in update:
                    msg = update["message"]
                    chat_id = str(msg["chat"]["id"])
                    if chat_id != ADMIN_CHAT_ID:
                        continue  # Ignora mensagens de outros chats

                    text = msg.get("text", "")

                    if text.startswith("/start"):
                        send_telegram_message(
                            "👋 *Olá Eduardo!*\n"
                            "Seu assistente LinkedIn com DeepSeek v4.1 está 100% conectado e operacional.\n\n"
                            "• Digite `/menu` para abrir as opções rápidas\n"
                            "• Cole qualquer link do LinkedIn para curtir e comentar\n"
                            "• Use `/post <ideia>` para criar um novo post\n"
                            "• Digite `/ajuda` para ver o guia completo"
                        )

                    elif text.startswith("/menu"):
                        send_main_menu()

                    elif text.startswith("/ajuda") or text.startswith("/help"):
                        send_telegram_message(HELP_TEXT)

                    elif text.startswith("/status"):
                        from app import status
                        st = await status()
                        send_telegram_message(
                            f"📊 *Status do Sistema:*\n\n"
                            f"• *LinkedIn Logado:* {'✅ Sim' if st.get('logged_in') else '❌ Não'}\n"
                            f"• *URL:* `{st.get('current_url')}`\n"
                            f"• *DeepSeek:* ✅ Ativo (OpenCode Go v4.1)\n"
                            f"• *n8n:* ✅ Online na porta 5678"
                        )

                    elif text.startswith("/visitantes") or text.startswith("/quemviu"):
                        await handle_profile_views()

                    elif text.startswith("/postar"):
                        send_telegram_message("💡 *Dica:* Para criar um novo post, use o comando `/post <sua ideia>`!")

                    elif text.startswith("/engajar"):
                        send_telegram_message("💡 *Dica:* Para engajar em uma postagem, basta colar o link do post do LinkedIn diretamente aqui no chat!")

                    # --- DETECÇÃO DE LINK DO LINKEDIN (ENGAJAMENTO EM POST DE TERCEIROS) ---
                    elif LINKEDIN_URL_REGEX.search(text):
                        match = LINKEDIN_URL_REGEX.search(text)
                        target_url = match.group(0).split("?")[0]

                        send_telegram_message(f"🔍 *Link do LinkedIn detectado!*\n`{target_url}`\n\nAcessando post para analisar o autor e o conteúdo...")

                        from app import analyze_post, PostAnalyzeRequest
                        try:
                            analysis = await analyze_post(PostAnalyzeRequest(post_url=target_url))
                            author = analysis.get("author", "Autor")
                            post_snippet = analysis.get("text", "")

                            send_telegram_message(f"🧠 *Post lido com sucesso!*\n👤 *Autor:* {author}\n✍️ Gerando comentário inteligente e personalizado com o DeepSeek v4.1...")

                            prompt = f"Post de {author}:\n'{post_snippet}'"
                            generated_comment = await asyncio.to_thread(call_deepseek, prompt, "engage")

                            engage_id = uuid.uuid4().hex[:8]
                            pending_engagements[engage_id] = {
                                "post_url": target_url,
                                "author": author,
                                "text": post_snippet,
                                "comment_text": generated_comment
                            }

                            keyboard = {
                                "inline_keyboard": [
                                    [{"text": "✅ Curtir e Comentar Post", "callback_data": f"approve_engage:{engage_id}"}],
                                    [{"text": "🔄 Gerar Outra Opção", "callback_data": f"regen_engage:{engage_id}"}],
                                    [{"text": "❌ Cancelar", "callback_data": f"cancel_engage:{engage_id}"}]
                                ]
                            }

                            send_telegram_message(
                                f"🎯 *Post Identificado:*\n"
                                f"👤 *Autor:* {author}\n"
                                f"📝 *Resumo do Post:* _{post_snippet[:150]}..._\n\n"
                                f"💬 *Sugestão de Comentário:*\n"
                                f"_{generated_comment}_\n\n"
                                f"👉 *Deseja curtir a postagem e publicar este comentário?*",
                                reply_markup=keyboard
                            )
                        except Exception as e:
                            send_telegram_message(f"❌ *Erro ao analisar a postagem do LinkedIn:* {e}")

                    # --- CRIAÇÃO DE NOVO POST (DUPLA PROPOSTA ANTI-IA) ---
                    elif text.startswith("/post"):
                        idea = text.replace("/post", "").strip()
                        if not idea:
                            send_telegram_message(
                                "💡 *Envie a ideia do post após o comando:*\n"
                                "Exemplo: `/post Como estruturamos agentes de IA autônomos no n8n para suporte técnico`"
                            )
                            continue

                        send_telegram_message(
                            "✍️ *Analisando sua ideia e redigindo 2 opções humanizadas com o DeepSeek v4.1...*\n"
                            "_(Voz: pragmático de trincheira • Sem emojis corporativos • Sem clichês de IA)_"
                        )
                        opt1, opt2 = await asyncio.to_thread(call_deepseek_dual_post, idea)

                        prop_id = uuid.uuid4().hex[:8]
                        pending_post_proposals[prop_id] = {
                            "idea": idea,
                            "opt1": opt1,
                            "opt2": opt2
                        }

                        keyboard = {
                            "inline_keyboard": [
                                [
                                    {"text": "1️⃣ Escolher Opção 1", "callback_data": f"choose_post:{prop_id}:1"},
                                    {"text": "2️⃣ Escolher Opção 2", "callback_data": f"choose_post:{prop_id}:2"}
                                ],
                                [{"text": "🔄 Gerar Novas Opções", "callback_data": f"regen_post:{prop_id}"}],
                                [{"text": "❌ Cancelar", "callback_data": f"cancel_post:{prop_id}"}]
                            ]
                        }

                        opt1_text = opt1["text"]
                        opt2_text = opt2["text"]
                        msg_text = (
                            f"🎯 *2 Opções de Posts Geradas para o seu LinkedIn:*\n\n"
                            f"──────────────\n"
                            f"📌 *OPÇÃO 1 — Bastidores & Caso Real:*\n\n"
                            f"{opt1_text}\n\n"
                            f"──────────────\n"
                            f"📌 *OPÇÃO 2 — Arquitetura & Visão Crítica:*\n\n"
                            f"{opt2_text}\n\n"
                            f"👉 *Qual das duas você prefere publicar?*"
                        )
                        if len(msg_text) <= 4000:
                            send_telegram_message(msg_text, reply_markup=keyboard)
                        else:
                            send_telegram_message(f"📌 *OPÇÃO 1 — Bastidores & Caso Real:*\n\n{opt1_text}")
                            send_telegram_message(
                                f"📌 *OPÇÃO 2 — Arquitetura & Visão Crítica:*\n\n{opt2_text}\n\n👉 *Qual das duas você prefere publicar?*",
                                reply_markup=keyboard
                            )

                    # --- TRATA ENVIO DE FOTO PARA ANEXAR AO POST ---
                    elif "photo" in msg:
                        draft = user_drafts.get(ADMIN_CHAT_ID)
                        if not draft or not draft.get("text"):
                            send_telegram_message(
                                "⚠️ *Envie primeiro a ideia usando `/post <ideia>` e selecione a opção desejada antes de enviar a foto.*"
                            )
                            continue

                        photo = msg["photo"][-1]
                        file_id = photo["file_id"]
                        send_telegram_message("📥 *Baixando e processando imagem...*")

                        f_info = await asyncio.to_thread(requests.get, f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile?file_id={file_id}")
                        f_path = f_info.json()["result"]["file_path"]
                        f_content = await asyncio.to_thread(requests.get, f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{f_path}")

                        img_name = f"post_{uuid.uuid4().hex[:8]}.jpg"
                        dest = os.path.join(SHARED_DIR, img_name)
                        with open(dest, "wb") as f:
                            f.write(f_content.content)

                        draft["image"] = img_name
                        save_user_drafts(user_drafts)

                        keyboard = {
                            "inline_keyboard": [
                                [{"text": "🚀 Confirmar e Publicar com Foto", "callback_data": "publish_post_now"}]
                            ]
                        }

                        send_telegram_message(
                            f"🖼️ *Imagem anexada com sucesso!*\n\n"
                            f"📝 *Texto:* {draft['text'][:150]}...\n\n"
                            f"Clique no botão abaixo para postar:",
                            reply_markup=keyboard
                        )

        except Exception as e:
            print(f"[!] Erro no loop do Telegram: {e}")
            await asyncio.sleep(5)
