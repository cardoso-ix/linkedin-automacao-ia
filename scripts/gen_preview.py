"""Gera PNG de preview da automacao LinkedIn para o portfolio."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parents[1] / "assets" / "preview.png"
W, H = 640, 360

img = Image.new("RGB", (W, H), "#0b1220")
d = ImageDraw.Draw(img)

try:
    fxs = ImageFont.truetype("segoeui.ttf", 10)
    fsm = ImageFont.truetype("segoeui.ttf", 12)
    fmd = ImageFont.truetype("segoeuib.ttf", 15)
    flg = ImageFont.truetype("segoeuib.ttf", 20)
    fmono = ImageFont.truetype("consola.ttf", 11)
except OSError:
    fxs = fsm = fmd = flg = fmono = ImageFont.load_default()

# Background gradient-ish blocks
d.rectangle((0, 0, W, H), fill="#0b1220")
d.ellipse((-80, -60, 220, 200), fill="#12203a")
d.ellipse((420, 180, 720, 420), fill="#1a1430")

# Window card
d.rounded_rectangle((24, 24, 616, 336), radius=14, fill="#111827", outline="#243044")
d.rounded_rectangle((24, 24, 616, 58), radius=14, fill="#162033")
d.rectangle((24, 44, 616, 58), fill="#162033")
d.ellipse((40, 34, 52, 46), fill="#ef4444")
d.ellipse((60, 34, 72, 46), fill="#f59e0b")
d.ellipse((80, 34, 92, 46), fill="#22c55e")
d.text((110, 34), "Make · LinkedIn Automacao IA", fill="#94a3b8", font=fsm)

# Left flow column
d.rounded_rectangle((40, 76, 250, 312), radius=10, fill="#0f172a", outline="#1e293b")
d.text((56, 88), "FLUXO 8h", fill="#38bdf8", font=fxs)

steps = [
    ("1", "Schedule", "#38bdf8"),
    ("2", "GPT-4o texto", "#818cf8"),
    ("3", "Router", "#a78bfa"),
    ("4", "Charge / Texto", "#f472b6"),
    ("5", "LinkedIn", "#0a66c2"),
]
y = 112
for num, label, color in steps:
    d.rounded_rectangle((56, y, 234, y + 28), radius=6, fill="#1e293b")
    d.ellipse((66, y + 6, 86, y + 26), fill=color)
    d.text((70, y + 8), num, fill="#0b1220", font=fxs)
    d.text((96, y + 8), label, fill="#e2e8f0", font=fsm)
    y += 36

# Right post preview
d.rounded_rectangle((268, 76, 600, 312), radius=10, fill="#0f172a", outline="#1e293b")
d.ellipse((284, 92, 316, 124), fill="#0a66c2")
d.text((292, 100), "EC", fill="#ffffff", font=fsm)
d.text((328, 94), "Eduardo Cardoso", fill="#f8fafc", font=fmd)
d.text((328, 114), "Agentes de IA · Automacao", fill="#64748b", font=fxs)

d.text((284, 140), "90% confundem chatbot com agente.", fill="#e2e8f0", font=fsm)
d.text((284, 160), "Na pratica, agente EXECUTA.", fill="#e2e8f0", font=fsm)

bullets = [
    "LLM + tools + memoria",
    "Function calling real",
    "Testar antes do deploy",
]
by = 190
for b in bullets:
    d.text((284, by), ">", fill="#38bdf8", font=fmono)
    d.text((300, by), b, fill="#cbd5e1", font=fsm)
    by += 22

d.text((284, 262), "Qual ferramenta voce testaria primeiro?", fill="#94a3b8", font=fxs)
d.text((284, 286), "#AgentesIA  #Automacao  #Make", fill="#38bdf8", font=fxs)

# Badge
d.rounded_rectangle((470, 84, 586, 108), radius=6, fill="#052e1a", outline="#166534")
d.text((482, 88), "1 post / dia", fill="#4ade80", font=fxs)

OUT.parent.mkdir(parents=True, exist_ok=True)
img.save(OUT, "PNG", optimize=True)
print(f"OK: {OUT}")
