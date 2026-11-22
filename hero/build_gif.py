"""
Regenerate hero/hero.gif from the separate Setup.png in the repository root.

From repository root:
    python -m pip install -r hero/requirements.txt
    python hero/build_gif.py
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

ROOT = Path(__file__).resolve().parents[1]
PHOTO = ROOT / "Setup.png"
OUT = Path(__file__).resolve().parent / "hero.gif"
if not PHOTO.exists():
    raise FileNotFoundError("Keep Setup.png in the repository root.")

W, H = 1280, 520
src = Image.open(PHOTO).convert("RGB")
ratio = W / H
sw, sh = src.size
crop_h = int(sw / ratio)
top = max(0, min(sh-crop_h, int(sh*.16)))
src = src.crop((0, top, sw, top+crop_h)).resize((W,H), Image.Resampling.LANCZOS)
src = ImageEnhance.Contrast(src).enhance(1.05)
src = ImageEnhance.Color(src).enhance(.82)

def ft(paths, size):
    for p in paths:
        try: return ImageFont.truetype(p, size)
        except OSError: pass
    return ImageFont.load_default()
REG = ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
BOLD = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
MONO = ["/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"]
eyebrow, namefont, rolefont, descfont, stackfont = (
    ft(MONO,18), ft(BOLD,66), ft(BOLD,30), ft(REG,21), ft(MONO,15)
)
def ease(x):
    x=max(0,min(1,x)); return 1-(1-x)**3
def centered(d,y,t,f,c,a):
    d.text((W//2,y),t,font=f,fill=(*c,int(max(0,min(255,a)))),anchor="mm")

frames=[]
for i in range(54):
    frame=src.convert("RGBA")
    frame=Image.alpha_composite(frame,Image.new("RGBA",(W,H),(0,0,0,105)))
    panel=Image.new("RGBA",(W,H),(0,0,0,0)); p=ImageDraw.Draw(panel)
    p.rounded_rectangle((115,52,1165,468),radius=24,fill=(5,8,12,205),outline=(255,138,0,150),width=2)
    p.line((175,73,1105,73),fill=(255,255,255,35),width=1)
    frame=Image.alpha_composite(frame,panel); d=ImageDraw.Draw(frame)
    master=ease(i/4) if i<5 else (1-ease((i-47)/6) if i>=47 else 1)
    ep=ease((i-1)/6) if i>=1 else 0
    centered(d,112,"HELLO, I'M",eyebrow,(245,245,245),255*ep*master)
    full="JOE PAUL K"; box=d.textbbox((0,0),full,font=namefont); tw=box[2]-box[0]; nx=(W-tw)//2
    chars=max(0,min(len(full),int((i-6)/2)+1)); na=255*ease((i-6)/4)*master if i>=6 else 0
    if chars:
        if chars==len(full):
            ww=d.textbbox((0,0),"JOE PAUL ",font=namefont)[2]
            d.text((nx,151),"JOE PAUL ",font=namefont,fill=(250,250,250,int(na)))
            d.text((nx+ww,151),"K",font=namefont,fill=(255,138,0,int(na)))
        else: d.text((nx,151),full[:chars],font=namefont,fill=(250,250,250,int(na)))
    lp=ease((i-17)/9) if i>=17 else 0; lw=int(520*lp)
    if lw: d.rounded_rectangle((W//2-lw//2,245,W//2+lw//2,249),radius=2,fill=(255,138,0,int(255*master)))
    rp=ease((i-21)/7) if i>=21 else 0; ra=255*rp*master
    centered(d,292,"AI/ML ENGINEER",rolefont,(250,250,250),ra)
    if rp:
        d.text((W//2-270,292),"[",font=rolefont,fill=(255,138,0,int(ra)),anchor="mm")
        d.text((W//2+270,292),"]",font=rolefont,fill=(255,138,0,int(ra)),anchor="mm")
    dp=ease((i-28)/7) if i>=28 else 0
    centered(d,354,"Building practical AI solutions through machine learning,",descfont,(245,245,245),250*dp*master)
    centered(d,386,"computer vision and intelligent systems.",descfont,(245,245,245),250*dp*master)
    sp=ease((i-35)/6) if i>=35 else 0
    centered(d,438,"PYTHON  /  COMPUTER VISION  /  LLMs  /  MLOps",stackfont,(255,177,92),245*sp*master)
    sx=155+(i*24)%970; d.ellipse((sx-3,84,sx+3,90),fill=(255,138,0,int(170*master)))
    frames.append(frame.convert("RGB"))
small=[f.resize((1000,406),Image.Resampling.LANCZOS) for f in frames]
palette=small[len(small)//2].quantize(colors=160,method=Image.Quantize.MEDIANCUT)
small=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in small]
small[0].save(OUT,save_all=True,append_images=small[1:],duration=110,loop=0,optimize=True,disposal=2)
print(f"Built: {OUT}")
