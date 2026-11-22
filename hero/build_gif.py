"""
Build the animated README hero from the separate Setup.png at repository root.
Run from repository root:
  python -m pip install -r hero/requirements.txt
  python hero/build_gif.py
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import math

ROOT = Path(__file__).resolve().parents[1]
PHOTO = ROOT / "Setup.png"
OUT = Path(__file__).resolve().parent / "hero.gif"
if not PHOTO.exists():
    raise FileNotFoundError("Keep Setup.png in the repository root.")

W, H = 1200, 900
src = Image.open(PHOTO).convert("RGB")
sw, sh = src.size
src = src.resize((W,H), Image.Resampling.LANCZOS)
src = ImageEnhance.Contrast(src).enhance(1.04)
src = ImageEnhance.Color(src).enhance(.90)
src = ImageEnhance.Brightness(src).enhance(1.035)

def font(paths, size):
    for path in paths:
        try: return ImageFont.truetype(path, size)
        except OSError: pass
    return ImageFont.load_default()
REG = ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
BOLD = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
MONO = ["/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"]
eyebrow, namefont, rolefont, focusfont = font(MONO,17), font(BOLD,64), font(BOLD,27), font(MONO,16)

def ease(t):
    t=max(0,min(1,t)); return 1-(1-t)**3
def shadow(d, xy, txt, ft, color, anchor="mm"):
    x,y=xy
    d.text((x+2,y+3),txt,font=ft,fill=(0,0,0,210),anchor=anchor,stroke_width=3,stroke_fill=(0,0,0,170))
    d.text((x,y),txt,font=ft,fill=color,anchor=anchor,stroke_width=1,stroke_fill=(0,0,0,120))

frames=[]
for i in range(48):
    frame=src.convert("RGBA")
    # Subtle edge vignette only; never place a panel over the photograph.
    vignette=Image.new("L",(W,H),0); pix=vignette.load()
    cx,cy=W/2,H/2; maxd=math.sqrt(cx*cx+cy*cy)
    for y in range(H):
        for x in range(W):
            dist=math.sqrt((x-cx)**2+(y-cy)**2)/maxd
            pix[x,y]=int(min(24,(dist**1.8)*24))
    shade=Image.new("RGBA",(W,H),(0,0,0,0)); shade.putalpha(vignette)
    frame=Image.alpha_composite(frame,shade); d=ImageDraw.Draw(frame)
    fade=ease(i/6) if i<7 else 1.0
    if i>=43: fade*=1-ease((i-43)/4)
    shift=int(8*(1-fade))
    shadow(d,(W//2,66+shift),"HELLO, I'M",eyebrow,(248,248,248,int(250*fade)))
    full="JOE PAUL K"; chars=max(0,min(len(full),int((i-5)/2)+1))
    alpha=int(255*ease((i-5)/4)*fade) if i>=5 else 0
    if chars:
        if chars>=len(full):
            w=d.textbbox((0,0),"JOE PAUL",font=namefont)[2]
            kw=d.textbbox((0,0),"K",font=namefont)[2]
            start=(W-(w+20+kw))//2
            shadow(d,(start+w//2,132+shift),"JOE PAUL",namefont,(250,250,250,alpha))
            shadow(d,(start+w+20+kw//2,132+shift),"K",namefont,(255,145,35,alpha))
        else: shadow(d,(W//2,132+shift),full[:chars],namefont,(250,250,250,alpha))
    line=ease((i-13)/8) if i>=13 else 0; lw=int(480*line)
    if lw: d.rounded_rectangle((W//2-lw//2,188+shift,W//2+lw//2,192+shift),radius=2,fill=(255,145,35,int(245*fade)))
    rp=ease((i-18)/7) if i>=18 else 0; ra=int(255*rp*fade)
    shadow(d,(W//2,226+shift),"AI/ML ENGINEER",rolefont,(250,250,250,ra))
    if ra:
        shadow(d,(W//2-205,226+shift),"[",rolefont,(255,145,35,ra))
        shadow(d,(W//2+205,226+shift),"]",rolefont,(255,145,35,ra))
    fp=ease((i-25)/7) if i>=25 else 0
    shadow(d,(W//2,272+shift),"GENERATIVE AI  /  RAG  /  AI AGENTS  /  LLM SYSTEMS",focusfont,(255,190,125,int(248*fp*fade)))
    if i>=32 and (i//3)%2==0:
        d.rounded_rectangle((W//2+355,263+shift,W//2+358,281+shift),radius=1,fill=(255,145,35,int(255*fade)))
    sx=100+(i*24)%1000
    d.ellipse((sx-3,40,sx+3,46),fill=(255,145,35,int(190*fade)))
    frames.append(frame.convert("RGB"))
small=[f.resize((800,600),Image.Resampling.LANCZOS) for f in frames]
palette=small[len(small)//2].quantize(colors=80,method=Image.Quantize.MEDIANCUT)
small=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in small]
small[0].save(OUT,save_all=True,append_images=small[1:],duration=115,loop=0,optimize=True,disposal=2)
print("Built:",OUT)
