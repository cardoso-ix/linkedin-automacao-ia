import os
import sys
import json
import time
import random
import asyncio
import re
from typing import Optional, List, Dict
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from playwright.async_api import async_playwright, Playwright, BrowserContext, Page

SESSION_DIR = os.getenv("SESSION_DIR", "/app/session")
PROFILE_DIR = os.path.join(SESSION_DIR, "profile")
SHARED_DIR = os.getenv("SHARED_DIR", "/app/shared")
EMAIL = os.getenv("LINKEDIN_EMAIL", "")
PASSWORD = os.getenv("LINKEDIN_PASSWORD", "")
LI_AT_COOKIE = os.getenv("LINKEDIN_LI_AT", "")

os.makedirs(PROFILE_DIR, exist_ok=True)
os.makedirs(SHARED_DIR, exist_ok=True)

class PlaywrightManager:
    def __init__(self):
        self.playwright: Optional[Playwright] = None
        self.context: Optional[BrowserContext] = None
        self._lock = asyncio.Lock()

    async def start(self):
        self.playwright = await async_playwright().start()
        self.context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=False,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
                "--window-size=1920,1080",
                "--lang=pt-BR,pt,en-US,en"
            ],
            viewport={"width": 1920, "height": 1080},
            locale="pt-BR",
            timezone_id="America/Sao_Paulo",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        )
        print("[*] Playwright persistent context iniciado.")
        # Verifica se já está logado
        await self.ensure_logged_in()

    async def ensure_logged_in(self) -> bool:
        async with self._lock:
            page = await self.get_page()
            try:
                print("[*] Verificando autenticação no LinkedIn...")
                await page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded", timeout=45000)
                await page.wait_for_timeout(3000)
                
                if "feed" in page.url and "login" not in page.url:
                    print(f"[+] Sessão ativa confirmada: {page.url}")
                    return True

                print("[*] Sessão não ativa. Tentando login com credenciais...")
                await page.goto("https://www.linkedin.com/login", wait_until="domcontentloaded", timeout=45000)
                await page.wait_for_timeout(2000)

                u_input = page.locator("input[type='email']:visible").first
                p_input = page.locator("input[type='password']:visible").first

                if await u_input.count() > 0 and await p_input.count() > 0:
                    await u_input.fill(EMAIL)
                    await page.wait_for_timeout(600)
                    await p_input.fill(PASSWORD)
                    await page.wait_for_timeout(600)
                    await p_input.press("Enter")
                    print("[*] Credenciais enviadas. Aguardando feed...")
                    await page.wait_for_timeout(10000)

                is_logged = "feed" in page.url and "login" not in page.url
                print(f"[+] Resultado do login: {is_logged} (URL: {page.url})")
                return is_logged
            except Exception as e:
                print(f"[!] Erro ao verificar login: {e}")
                return False

    async def stop(self):
        if self.context:
            await self.context.close()
        if self.playwright:
            await self.playwright.stop()
        print("[*] Playwright finalizado.")

    async def get_page(self) -> Page:
        if not self.context:
            await self.start()
        pages = self.context.pages
        return pages[0] if pages else await self.context.new_page()

pw_manager = PlaywrightManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await pw_manager.start()
    from telegram_bot import run_telegram_loop
    tg_task = asyncio.create_task(run_telegram_loop(pw_manager))
    yield
    tg_task.cancel()
    await pw_manager.stop()

app = FastAPI(title="LinkedIn Automation Bridge", lifespan=lifespan)

class ReplyRequest(BaseModel):
    post_url: str
    comment_text: Optional[str] = None
    reply_text: str
    like_first: bool = True

class PublishPostRequest(BaseModel):
    text: str
    image_filename: Optional[str] = None

class PostAnalyzeRequest(BaseModel):
    post_url: str

class PostEngageRequest(BaseModel):
    post_url: str
    comment_text: str
    like_first: bool = True

@app.get("/health")
async def health():
    return {"status": "ok", "service": "linkedin-bridge"}

@app.get("/status")
async def status():
    page = await pw_manager.get_page()
    await page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded", timeout=45000)
    await page.wait_for_timeout(2000)
    current_url = page.url
    is_logged = "feed" in current_url and "login" not in current_url
    return {
        "logged_in": is_logged,
        "current_url": current_url,
        "title": await page.title()
    }

@app.get("/comments/recent")
async def get_recent_comments():
    """Busca publicações e comentários recentes no perfil do usuário"""
    page = await pw_manager.get_page()
    try:
        activity_url = "https://www.linkedin.com/in/eduardo-cardoso-213a02267/recent-activity/all/"
        await page.goto(activity_url, wait_until="domcontentloaded", timeout=45000)
        await page.wait_for_timeout(4000)

        # Procura posts
        posts = page.locator("div.feed-shared-update-v2, div[data-urn*='activity']")
        count = await posts.count()
        if count == 0:
            return {"post_url": None, "comments": []}

        first_post = posts.first
        post_urn = await first_post.get_attribute("data-urn") or ""
        post_url = f"https://www.linkedin.com/feed/update/{post_urn}/" if post_urn else page.url

        # Abre a seção de comentários se não estiver visível
        comment_btn = first_post.locator("button[aria-label*='comentário'], button[aria-label*='comment']")
        if await comment_btn.count() > 0:
            await comment_btn.first.click()
            await page.wait_for_timeout(2000)

        # Coleta os comentários
        comments_elements = first_post.locator("article.comments-comment-item, .comments-comment-item")
        total_comments = await comments_elements.count()

        extracted = []
        for i in range(min(total_comments, 10)):
            item = comments_elements.nth(i)
            author = await item.locator(".comments-post-meta__name-text, .comments-comment-item__main-content h3").first.text_content() or "Conexão"
            content = await item.locator(".comments-comment-item__main-content, .update-components-text").first.text_content() or ""
            
            clean_author = author.strip()
            clean_content = content.strip()

            if clean_content:
                extracted.append({
                    "id": f"comment_{i}",
                    "author": clean_author,
                    "text": clean_content,
                    "post_url": post_url
                })

        return {
            "post_url": post_url,
            "total_found": len(extracted),
            "comments": extracted
        }
    except Exception as e:
        return {"error": str(e), "comments": []}

@app.post("/comments/reply")
async def reply_comment(req: ReplyRequest):
    """Curte o comentário e responde com delay humanizado"""
    page = await pw_manager.get_page()
    try:
        await page.goto(req.post_url, wait_until="domcontentloaded", timeout=45000)
        await page.wait_for_timeout(3000)

        # Se like_first, clica em Gostei no comentário
        if req.like_first:
            try:
                like_btn = page.locator("button.reactions-react-button, button:has-text('Gostei'), button[aria-label*='Gostei'], button[aria-label*='Like']").first
                if await like_btn.is_visible():
                    aria_pressed = await like_btn.get_attribute("aria-pressed")
                    if aria_pressed != "true":
                        await like_btn.click()
                        await asyncio.sleep(random.uniform(1.2, 2.5))
            except Exception as ex:
                print(f"[!] Erro ao curtir comentário: {ex}")

        # Caixa de resposta
        reply_box = page.locator("div.ql-editor, div[contenteditable='true'], textarea[placeholder*='comentário']").first
        if not await reply_box.is_visible():
            reply_btn = page.locator("button:has-text('Responder'), button[aria-label*='Responder']").first
            if await reply_btn.is_visible():
                await reply_btn.click()
                await page.wait_for_timeout(1500)
                reply_box = page.locator("div.ql-editor, div[contenteditable='true']").first

        if await reply_box.is_visible():
            await reply_box.click()
            for word in req.reply_text.split(" "):
                await reply_box.type(word + " ", delay=random.randint(35, 75))
                await asyncio.sleep(random.uniform(0.03, 0.08))

            await page.wait_for_timeout(1500)
            submit_btn = page.locator("button.comments-comment-box__submit-button, button:has-text('Comentar'), button:has-text('Publicar'), button:has-text('Responder')").first
            await submit_btn.click()
            await page.wait_for_timeout(3000)

        return {"success": True, "message": "Comentário respondido e curtido com sucesso no LinkedIn!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/posts/analyze")
async def analyze_post(req: PostAnalyzeRequest):
    """Acessa a URL do post ou artigo do LinkedIn e extrai o autor e o texto para a IA"""
    page = await pw_manager.get_page()
    try:
        clean_url = req.post_url.split("?")[0].strip()
        print(f"[*] Analisando post do LinkedIn: {clean_url}")
        await page.goto(clean_url, wait_until="domcontentloaded", timeout=45000)
        await page.wait_for_timeout(4000)

        final_url = page.url.split("?")[0]
        page_title = await page.title()

        # Extrai autor
        author = await page.evaluate('''() => {
            // Tenta seletor de autor de post
            const a1 = document.querySelector('.update-components-actor__name, .feed-shared-actor__name, span.update-components-actor__title');
            if (a1 && a1.innerText.trim()) return a1.innerText.trim();
            // Tenta seletor de autor de artigo
            const a2 = document.querySelector('.reader-author-info__link, h3.reader-author-info__name');
            if (a2 && a2.innerText.trim()) return a2.innerText.trim();
            // Tenta extrair pelo aria-label do botão de Like
            const btn = document.querySelector('button[aria-label*="publicação de"]');
            if (btn) {
                const match = btn.getAttribute('aria-label').match(/publicação de (.+)/);
                if (match) return match[1].trim();
            }
            return 'Autor no LinkedIn';
        }''')

        # Extrai texto do post
        text_content = await page.evaluate('''() => {
            const el = document.querySelector('.update-components-text, .feed-shared-update-v2__description, article, .reader-article-content, main');
            if (el && el.innerText.trim()) {
                return el.innerText.trim().substring(0, 1500).replace(/\\n+/g, ' ');
            }
            return document.body.innerText.substring(0, 1000).replace(/\\n+/g, ' ');
        }''')

        return {
            "success": True,
            "post_url": final_url,
            "title": page_title,
            "author": author,
            "text": text_content
        }
    except Exception as e:
        print(f"[!] Erro ao analisar post: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/posts/engage")
async def engage_post(req: PostEngageRequest):
    """Curte a postagem e publica o comentário gerado na postagem da pessoa"""
    page = await pw_manager.get_page()
    try:
        clean_url = req.post_url.split("?")[0].strip()
        print(f"[*] Engajando no post: {clean_url}")
        await page.goto(clean_url, wait_until="domcontentloaded", timeout=45000)
        await page.wait_for_timeout(3500)

        # 1. Curtir a postagem (Like)
        liked = False
        if req.like_first:
            try:
                await page.evaluate("window.scrollBy(0, 250)")
                await page.wait_for_timeout(1000)

                like_selectors = [
                    "button.react-button__trigger",
                    "button.reactions-react-button",
                    "button[aria-label*='Reagir com gostar']",
                    "button[aria-label*='Gostei']",
                    "button[aria-label*='Like']",
                    "button:has-text('Gostei')",
                    "button:has-text('Like')"
                ]
                for sel in like_selectors:
                    btn = page.locator(sel).first
                    if await btn.count() > 0:
                        aria_pressed = await btn.get_attribute("aria-pressed")
                        if aria_pressed != "true":
                            print(f"[*] Clicando no botão Gostei com seletor: {sel}")
                            await btn.scroll_into_view_if_needed()
                            await btn.click()
                            liked = True
                            await asyncio.sleep(random.uniform(1.5, 2.5))
                            break
                        else:
                            print("[*] Post já estava curtido.")
                            liked = True
                            break
            except Exception as ex:
                print(f"[!] Erro ao clicar no Like: {ex}")

        # 2. Se comment_text foi fornecido, digita e envia
        if req.comment_text and req.comment_text.strip():
            comment_box = page.locator("div.ql-editor, div[contenteditable='true'], textarea[placeholder*='coment']").first
            if not await comment_box.is_visible():
                comment_trigger = page.locator("button.comment-button, button:has-text('Comentar'), button[aria-label*='Comentar'], button[aria-label*='Comment']").first
                if await comment_trigger.is_visible():
                    print("[*] Clicando no botão para abrir caixa de comentário...")
                    await comment_trigger.click()
                    await page.wait_for_timeout(2000)
                    comment_box = page.locator("div.ql-editor, div[contenteditable='true']").first

            if not await comment_box.is_visible():
                raise Exception("Caixa de comentário não encontrada na página da postagem.")

            # 3. Digitação humanizada do comentário
            print("[*] Digitando comentário com cadência humana...")
            await comment_box.click()
            for word in req.comment_text.strip().split(" "):
                await comment_box.type(word + " ", delay=random.randint(35, 75))
                await asyncio.sleep(random.uniform(0.03, 0.08))

            await page.wait_for_timeout(1500)

            # 4. Clicar no botão Comentar / Publicar
            submit_btn = page.locator("button.comments-comment-box__submit-button, button:has-text('Comentar'), button:has-text('Publicar')").first
            await submit_btn.click()
            print("[*] Comentário enviado! Aguardando confirmação...")
            await page.wait_for_timeout(3500)

        return {
            "success": True,
            "liked": liked,
            "message": "Post curtido e comentário publicado com sucesso!"
        }
    except Exception as e:
        print(f"[!] Erro ao engajar no post: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/posts/publish")
async def publish_post(req: PublishPostRequest):
    """Publica um novo post no perfil do LinkedIn"""
    page = await pw_manager.get_page()
    try:
        await page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded", timeout=45000)
        await page.wait_for_timeout(3000)

        # 1. Botão 'Começar publicação' (pode ser div[role="button"] ou button)
        start_btn = page.locator(
            "div[role='button']:has-text('Começar publicação'), "
            "button:has-text('Começar publicação'), "
            "[aria-label*='Começar publicação'], "
            "[aria-label*='Start a post'], "
            "button:has-text('Start a post')"
        ).first
        await start_btn.wait_for(state="visible", timeout=20000)
        await start_btn.click()
        await page.wait_for_timeout(2000)

        # 2. Anexo de imagem (se houver)
        if req.image_filename:
            image_path = os.path.join(SHARED_DIR, req.image_filename)
            if os.path.exists(image_path):
                media_btn = page.locator(
                    "button[aria-label*='Mídia'], "
                    "button[aria-label*='Media'], "
                    "button[aria-label*='Adicionar mídia']"
                ).first
                if await media_btn.count() > 0 and await media_btn.is_visible():
                    async with page.expect_file_chooser(timeout=10000) as fc_info:
                        await media_btn.click()
                    file_chooser = await fc_info.value
                    await file_chooser.set_files(image_path)
                else:
                    file_input = page.locator("input[type='file']").first
                    if await file_input.count() > 0:
                        await file_input.set_input_files(image_path)

                await page.wait_for_timeout(3000)

                # Confirmação no modal do editor de imagem ("Avançar" / "Next")
                next_btn = page.locator(
                    "button:has-text('Avançar'), "
                    "button:has-text('Next'), "
                    "button:has-text('Concluído'), "
                    "button:has-text('Done')"
                ).first
                if await next_btn.count() > 0 and await next_btn.is_visible():
                    await next_btn.click()
                    await page.wait_for_timeout(2000)

        # 3. Digitação do texto do post com cadência humana
        editor = page.locator("div.ql-editor, div[contenteditable='true']").first
        await editor.wait_for(state="visible", timeout=15000)
        await editor.click()
        for chunk in req.text.split(" "):
            await editor.type(chunk + " ", delay=random.randint(25, 60))
            await asyncio.sleep(random.uniform(0.02, 0.05))

        await page.wait_for_timeout(2000)

        # 4. Botão Publicar
        post_btn = page.locator(
            "button:has-text('Publicar'), "
            "button:has-text('Post'), "
            "button.share-actions__primary-action"
        ).first
        await post_btn.wait_for(state="visible", timeout=10000)
        
        if await post_btn.is_disabled():
            await editor.press("Space")
            await page.wait_for_timeout(1000)

        await post_btn.click()
        await page.wait_for_timeout(6000)

        return {"success": True, "message": "Post publicado com sucesso no LinkedIn!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/posts/scrape-viral")
async def scrape_viral_posts(keyword: str = "feed"):
    """Raspa postagens do LinkedIn para analisar engajamento e tipos de mídia"""
    page = await pw_manager.get_page()
    try:
        import urllib.parse
        if keyword.lower() == "feed":
            url = "https://www.linkedin.com/feed/"
        else:
            encoded_kw = urllib.parse.quote(keyword)
            url = f"https://www.linkedin.com/search/results/content/?keywords={encoded_kw}&origin=SWITCH_SEARCH_VERTICAL"
        print(f"[*] Raspando posts virais para: {keyword} (URL: {url})")
        await page.goto(url, wait_until="domcontentloaded", timeout=45000)
        await page.wait_for_timeout(5000)

        # Captura screenshot de depuração
        await page.screenshot(path="/app/shared/scrape_debug.png")
        page_title = await page.title()
        current_url = page.url
        body_text = await page.evaluate("() => document.body.innerText.slice(0, 1000)")

        # Scroll to load multiple posts
        for _ in range(4):
            await page.evaluate("window.scrollBy(0, 1200)")
            await page.wait_for_timeout(2000)

        posts_data = await page.evaluate('''() => {
            const links = Array.from(document.querySelectorAll('a'))
                .filter(a => a.href && (a.href.includes('/feed/update/urn:li:activity:') || a.href.includes('/posts/')));
            
            const results = [];
            const seen = new Set();

            links.forEach(a => {
                const url = a.href.split('?')[0];
                if (seen.has(url)) return;
                seen.add(url);

                const card = a.closest('.feed-shared-update-v2, div[data-urn*="activity"], div[data-id*="activity"]') || a.closest('div.artdeco-card') || a.parentElement.parentElement;
                if (!card) return;

                const textEl = card.querySelector('.update-components-text, .feed-shared-update-v2__description, span.break-words');
                const text = textEl ? textEl.innerText.trim() : '';

                const authorEl = card.querySelector('.update-components-actor__name, .feed-shared-actor__name, span.update-components-actor__title');
                const author = authorEl ? authorEl.innerText.trim() : 'Autor';

                const reactionsEl = card.querySelector('.social-details-social-counts__reactions-count, [aria-label*="reações"], [aria-label*="reactions"]');
                const reactions = reactionsEl ? reactionsEl.innerText.trim() : '';

                const commentsEl = card.querySelector('.social-details-social-counts__comments, [aria-label*="comentários"], [aria-label*="comments"]');
                const comments = commentsEl ? commentsEl.innerText.trim() : '';

                const imgEl = card.querySelector('img.feed-shared-image__image, .update-components-image__image, img[alt]:not([alt=""])');
                const hasImage = !!imgEl;
                const imgAlt = imgEl ? (imgEl.alt || '') : '';
                const imgSrc = imgEl ? (imgEl.src || '') : '';

                const hasDoc = !!card.querySelector('.feed-shared-document, .document-container, [data-test-document-player]');

                results.push({
                    url,
                    author,
                    reactions,
                    comments,
                    hasImage,
                    imgAlt,
                    hasDoc,
                    textSnippet: text.slice(0, 300)
                });
            });
            return results;
        }''')
        return {
            "count": len(posts_data),
            "debug": {"title": page_title, "url": current_url, "snippet": body_text[:300]},
            "posts": posts_data
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/posts/search-analysis")
async def search_analysis(query: str = "n8n automação"):
    """Pesquisa posts e analisa imagens e engajamento no LinkedIn"""
    page = await pw_manager.get_page()
    try:
        import urllib.parse
        encoded_kw = urllib.parse.quote(query)
        url = f"https://www.linkedin.com/search/results/content/?keywords={encoded_kw}&origin=SWITCH_SEARCH_VERTICAL"
        print(f"[*] Navegando para busca do LinkedIn: {url}")
        await page.goto(url, wait_until="domcontentloaded", timeout=45000)
        await page.wait_for_timeout(6000)

        for _ in range(3):
            await page.evaluate("window.scrollBy(0, 1000)")
            await page.wait_for_timeout(2000)

        await page.screenshot(path="/app/shared/search_results.png")

        posts = await page.evaluate('''() => {
            const results = [];
            const cards = document.querySelectorAll('.feed-shared-update-v2, .search-results-container [data-chameleon-result-urn], div.artdeco-card');
            cards.forEach(card => {
                const author = card.querySelector('.update-components-actor__name, .feed-shared-actor__name')?.innerText?.trim() || '';
                const text = card.querySelector('.update-components-text, .feed-shared-update-v2__description, span.break-words')?.innerText?.trim() || '';
                const reactions = card.querySelector('.social-details-social-counts__reactions-count, [aria-label*="reações"], [aria-label*="reactions"]')?.innerText?.trim() || '';
                const comments = card.querySelector('.social-details-social-counts__comments, [aria-label*="comentários"], [aria-label*="comments"]')?.innerText?.trim() || '';
                const img = card.querySelector('img.feed-shared-image__image, .update-components-image__image, img[alt]:not([alt=""])');
                const hasDoc = !!card.querySelector('.feed-shared-document, .document-container, [data-test-document-player]');
                if (text) {
                    results.push({
                        author,
                        text: text.slice(0, 300),
                        reactions,
                        comments,
                        hasImage: !!img,
                        imgAlt: img ? (img.alt || '') : '',
                        hasDoc
                    });
                }
            });
            return results;
        }''')
        return {"count": len(posts), "posts": posts}
    except Exception as e:
        return {"error": str(e)}

@app.get("/profile/views")
async def get_profile_views():
    """Coleta visitantes recentes do perfil (Quem viu meu perfil - LinkedIn Premium)"""
    page = await pw_manager.get_page()
    try:
        url = "https://www.linkedin.com/analytics/profile-views/"
        print(f"[*] Acessando estatísticas de visitantes: {url}")
        await page.goto(url, wait_until="domcontentloaded", timeout=45000)
        # Scroll para carregar mais visitantes
        for _ in range(3):
            await page.evaluate("window.scrollBy(0, 800)")
            await page.wait_for_timeout(1500)

        page_title = await page.title()
        current_url = page.url

        viewers = await page.evaluate('''() => {
            const results = [];
            const seenUrls = new Set();
            
            const profileLinks = Array.from(document.querySelectorAll('a[href*="/in/"]'))
                .filter(a => {
                    const href = a.href || '';
                    return href.includes('/in/') && !href.includes('/in/me') && !href.includes('/in/eduardo');
                });

            profileLinks.forEach(link => {
                const cleanUrl = link.href.split('?')[0];
                if (seenUrls.has(cleanUrl)) return;

                const card = link.closest('li, div.artdeco-entity-lockup, div[data-view-name], div.artdeco-card') || link.parentElement?.parentElement;
                if (!card) return;

                const fullCardText = card.innerText ? card.innerText.trim() : '';
                const lines = fullCardText.split('\\n').map(l => l.trim()).filter(l => l.length > 0);

                let name = '';
                let headline = '';
                let timeAgo = '';

                for (let i = 0; i < lines.length; i++) {
                    const l = lines[i].trim();
                    const low = l.toLowerCase();
                    if (low.includes('visto há') || low.includes('visualizado há') || low.includes('viewed')) {
                        timeAgo = l;
                    }
                }

                const candidateLines = lines.filter(l => {
                    const low = l.toLowerCase();
                    return !low.includes('1º') && !low.includes('2º') && !low.includes('3º') &&
                           !low.includes('conexão em comum') && !low.includes('conexões em comum') &&
                           low !== 'mensagem' && low !== 'conectar' && low !== 'seguir' &&
                           low !== 'pendente' && low !== 'remover' && low !== '--' &&
                           l !== timeAgo;
                });

                if (candidateLines.length > 0) {
                    name = candidateLines[0].replace(/•.*/, '').replace(/\s+/g, ' ').trim();
                }

                if (candidateLines.length > 1) {
                    headline = candidateLines[1].replace(/\s+/g, ' ').trim();
                }

                if (name && name.length > 2 && !name.toLowerCase().includes('premium') && !name.toLowerCase().includes('vagas')) {
                    seenUrls.add(cleanUrl);
                    
                    const lowerHeadline = headline.toLowerCase();
                    const isRecruiter = lowerHeadline.includes('recruiter') || 
                                        lowerHeadline.includes('talent') || 
                                        lowerHeadline.includes('rh') || 
                                        lowerHeadline.includes('people') || 
                                        lowerHeadline.includes('hunting') ||
                                        lowerHeadline.includes('headhunter') ||
                                        lowerHeadline.includes('seleção') ||
                                        lowerHeadline.includes('recrutador');

                    const isDecisionMaker = lowerHeadline.includes('cto') || 
                                            lowerHeadline.includes('ceo') || 
                                            lowerHeadline.includes('founder') || 
                                            lowerHeadline.includes('head') || 
                                            lowerHeadline.includes('diretor') || 
                                            lowerHeadline.includes('gerente') || 
                                            lowerHeadline.includes('lead') ||
                                            lowerHeadline.includes('co-founder') ||
                                            lowerHeadline.includes('tech lead');

                    results.push({
                        name,
                        headline,
                        timeAgo,
                        profileUrl: cleanUrl,
                        isRecruiter,
                        isDecisionMaker
                    });
                }
            });

            return results;
        }''')

        return {
            "count": len(viewers),
            "debug": {"title": page_title, "url": current_url},
            "viewers": viewers
        }
    except Exception as e:
        return {"error": str(e)}






