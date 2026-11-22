"""Rebuild the animated GitHub profile banner from the compact background.
Run from repository root:
  python -m pip install -r hero/requirements.txt
  python hero/build_gif.py
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math

HERE = Path(__file__).resolve().parent
PHOTO = HERE / "background.jpg"
OUT = HERE / "hero.gif"
W, H = 1200, 420

if not PHOTO.exists():
    raise FileNotFoundError("hero/background.jpg is missing.")

src = Image.open(PHOTO).convert("RGB").resize((W, H), Image.Resampling.LANCZOS)

def font(paths, size):
    for path in paths:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default()

BOLD = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
MONO = ["/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"]
f_small = font(MONO, 16)
f_name = font(BOLD, 58)
f_role = font(BOLD, 26)
f_skills = font(MONO, 13)

def ease(t):
    t = max(0, min(1, t))
    return 1 - (1-t)**3

def centered(draw, y, text, face, fill):
    draw.text((W//2, y), text, font=face, fill=fill, anchor="mm")

frames = []
for i in range(36):
    frame = src.convert("RGBA")
    shade = Image.new("RGBA", (W, H), (0,0,0,0))
    sd = ImageDraw.Draw(shade)
    for y in range(190):
        sd.line((0,y,W,y), fill=(0,0,0,int(76*(1-y/190))))
    frame = Image.alpha_composite(frame, shade)
    d = ImageDraw.Draw(frame)

    p = ease((i-1)/5) if i >= 1 else 0
    centered(d, 24, "HELLO, I'M", f_small, (250,250,250,int(245*p)))

    p = ease((i-4)/6) if i >= 4 else 0
    name = "JOE PAUL "
    nw = d.textbbox((0,0), name, font=f_name)[2]
    kw = d.textbbox((0,0), "K", font=f_name)[2]
    x = (W-nw-kw)//2
    if p:
        d.text((x,48), name, font=f_name, fill=(255,255,255,int(255*p)))
        d.text((x+nw,48), "K", font=f_name, fill=(255,145,35,int(255*p)))

    p = ease((i-10)/7) if i >= 10 else 0
    line_w = int(330*p)
    if line_w:
        d.rounded_rectangle((W//2-line_w//2,119,W//2+line_w//2,122),
                            radius=2, fill=(255,145,35,235))

    p = ease((i-14)/6) if i >= 14 else 0
    centered(d, 151, "AI/ML ENGINEER", f_role, (255,255,255,int(250*p)))

    p = ease((i-20)/6) if i >= 20 else 0
    centered(d, 184, "GENERATIVE AI  /  RAG  /  AI AGENTS  /  LLM SYSTEMS",
             f_skills, (255,196,145,int(245*p)))

    if i >= 25:
        pulse = 145 + int(105*(.5+.5*math.sin(i*.65)))
        d.rounded_rectangle((W//2+300,177,W//2+303,192),
                            radius=1, fill=(255,145,35,pulse))
    frames.append(frame.convert("RGB"))

small = [f.resize((1000,350), Image.Resampling.LANCZOS) for f in frames]
palette = small[len(small)//2].quantize(colors=128, method=Image.Quantize.MEDIANCUT)
small = [f.quantize(palette=palette, dither=Image.Dither.NONE) for f in small]
small[0].save(OUT, save_all=True, append_images=small[1:], duration=115,
              loop=0, optimize=True, disposal=2)
print("Generated", OUT)
