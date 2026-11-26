#!/usr/bin/env python3
"""오늘의 1위 — 매일 올릴 세로 영상(틱톡·쇼츠·릴스용, 1080×1920) 만들기.

data/rankings.js 의 순위로 '오늘 가장 많이 본 영상 TOP 3' 카운트다운 영상을 만듭니다.
다른 사람의 영상 화면은 쓰지 않고 제목·채널·조회수만 그래픽으로 보여 줍니다(저작권 안전).
소리는 넣지 않습니다. 올릴 때 각 앱의 음악 고르기에서 인기 음원을 붙이세요.

사용법:  python3 scripts/make-video.py [global|kr] [출력폴더]
결과:    출력폴더/today1-YYYY-MM-DD-global.mp4
"""
import json, os, re, subprocess, sys, tempfile, datetime
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGION = sys.argv[1] if len(sys.argv) > 1 else "global"
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "video")
W, H, FPS = 1080, 1920, 30
RED, RED2, GOLD, INK = (255, 31, 61), (255, 104, 124), (255, 200, 61), (58, 38, 0)

def font(weight, size):
    path = {"black": "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc",
            "bold": "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
            "reg": "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"}[weight]
    if not os.path.exists(path):
        path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
    return ImageFont.truetype(path, size, index=1)  # 1 = KR

# ---------- 데이터 ----------
src = open(os.path.join(ROOT, "data/rankings.js"), encoding="utf-8").read()
meta = json.loads(re.search(r"window\.META=(\{.*?\});", src).group(1))
i = src.index("window.RANKINGS=") + len("window.RANKINGS=")
R = json.loads(src[i:src.rindex(";")])

def is_channel(it):
    return str(it[3]).startswith("u:") or "채널 전체" in it[0]

def top(region, kind="daily", n=3):
    m = {}
    for k, v in R.items():
        if not k.endswith("-" + region) or k.startswith("ad-"):
            continue
        b = v[kind]
        for bb in (b, b.get("extra")):
            if not bb:
                continue
            for it in bb["items"]:
                if is_channel(it):
                    continue
                key = it[0] if str(it[3]).startswith("s:") else it[3]
                m.setdefault(key, it)
    return sorted(m.values(), key=lambda x: -x[2])[:n]

EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿️‍]")
def clean(s):
    return re.sub(r"\s+", " ", EMOJI.sub("", s)).strip()

def channel(desc):
    parts = [p for p in desc.split(" · ") if not re.match(r"차트 \d+위", p)]
    return clean(parts[0]) if parts else ""

def views(n):
    if n >= 1e8:
        return f"{n/1e8:.1f}억".replace(".0억", "억")
    return f"{round(n/1e4):,}만"

items = top(REGION)
day = datetime.date.fromisoformat(meta["updated"])
WD = "월화수목금토일"[day.weekday()]
DATE = f"{day.month}월 {day.day}일 ({WD})"
WHERE = "전세계" if REGION == "global" else "대한민국"

# 영어 제목(번역 파일)과 내레이션·자막
_s = open(os.path.join(ROOT, "i18n/source.js"), encoding="utf-8").read()
_e = open(os.path.join(ROOT, "i18n/en.js"), encoding="utf-8").read()
SRC_DATA = json.loads(_s[_s.index("=") + 1:_s.rindex(";")])["data"]
EN_DATA = json.loads(_e[_e.index(").en=") + 5:_e.rindex(";")])["data"]
HANGUL = re.compile("[가-힣]")
def en(s):
    if not HANGUL.search(s):
        return s
    try:
        v = EN_DATA[SRC_DATA.index(s)]
        return v or s
    except ValueError:
        return s

def millions(n):
    m = n / 1e6
    return (f"{m:.0f}" if m >= 10 else f"{m:.1f}".rstrip("0").rstrip(".")) + " million"

def short(s, n=30):
    s = clean(s)
    if len(s) <= n:
        return s
    cut = s[:n - 1]
    if " " in cut[n // 2:]:
        cut = cut[:cut.rindex(" ")]
    return cut.rstrip(" ,:-") + "…"

WORD = {1: "one", 2: "two", 3: "three"}
def narration():
    where_en = "in the world" if REGION == "global" else "in South Korea"
    out = [(f"What was the most-watched video {where_en} today? Here's the top three!",
            f"오늘 {WHERE}에서 가장 많이 본 영상은?\nTOP 3를 공개합니다!")]
    for r in (3, 2, 1):
        if len(items) < r:
            continue
        it = items[r - 1]; ch = channel(it[1]); ti = clean(en(it[0]))
        lead = "And number one" if r == 1 else f"Number {WORD[r]}"
        if ti.isupper():
            ti = ti.capitalize().replace(" i ", " I ")
        frm = f", from {clean(en(ch))}" if ch and ch.lower() not in ti.lower() else ""
        tail = f"with {millions(it[2])} views in just one day!" if r == 1 else f"{millions(it[2])} views in a day."
        ko_head = (f"그리고 1위는" if r == 1 else f"{r}위는") + (f" {short(ch, 14)}의" if ch else "")
        out.append((f"{lead}{frm}: {ti.rstrip('.!')}! {tail[0].upper() + tail[1:]}",
                    f"{ko_head}\n'{short(it[0])}'\n하루 {views(it[2])} 회!"))
    out.append(("For the full top ten, search Today's Number One. Follow for tomorrow's ranking!",
                "4~10위, 음악·스포츠·키즈 순위는\n'오늘의 1위'에서!\n내일 순위도 팔로우하세요"))
    return out

MODE = os.environ.get("VOICE", "en")  # en: 영어 목소리+한글 자막 / ko: 한국어 목소리+영어 자막

def views_say(n):  # 읽기 좋은 숫자(쉼표 없이)
    return f"{n/1e8:.1f}억".replace(".0억", "억") if n >= 1e8 else f"{round(n/1e4)}만"

def m_short(n):
    return f"{n/1e6:.1f}M".replace(".0M", "M")

def narration_ko():
    """(한국어 목소리, 영어 자막) 목록"""
    where_en = "in the world" if REGION == "global" else "in South Korea"
    out = [(f"오늘 {'전 세계' if REGION == 'global' else '대한민국'}에서 가장 많이 본 영상은 무엇일까요? TOP 3를 공개합니다!",
            f"What was the most-watched video {where_en} today?\nHere's the TOP 3!")]
    for r in (3, 2, 1):
        if len(items) < r:
            continue
        it = items[r - 1]; ch = channel(it[1])
        tags = [clean(x) for x in it[1].split(" · ")[1:] if not re.match(r"차트 \d+위", x)]
        if HANGUL.search(it[0]):
            what = f"{clean(it[0])}"
        elif tags:
            what = f"{' '.join(tags)} 영상"
        else:
            what = f"{ch} 채널 영상" if ch else "이 영상"
        head = "그리고 대망의 1위!" if r == 1 else f"{r}위!"
        tail = f"하루 무려 {views_say(it[2])} 회입니다!" if r == 1 else f"하루 {views_say(it[2])} 회를 기록했습니다."
        ti = clean(en(it[0]))
        sub_head = ("And No.1" if r == 1 else f"No.{r}") + (f" — {clean(en(ch))}" if ch else "")
        out.append((f"{head} {what}. {tail}",
                    f"{sub_head}\n'{short(ti, 32)}'\n{m_short(it[2])} views in {'just ' if r == 1 else ''}one day!"))
    out.append(("4위부터 10위, 음악과 스포츠 순위는 검색창에 오늘의 1위! 내일 순위도 팔로우하세요.",
                "Ranks 4–10, music, sports & kids:\nsearch 'Today's No.1'\nFollow for tomorrow's ranking!"))
    return out

def seconds(line):  # 말하기 속도에 맞춘 장면 길이
    if HANGUL.search(line):
        return round(max(3.5, len(re.sub(r"[^가-힣0-9A-Za-z]", "", line)) / 6.0 + 0.9), 1)
    return round(max(3.5, len(line.split()) / 3.0 + 0.8), 1)

# ---------- 그리기 도구 ----------
def bg():
    im = Image.new("RGB", (W, H), RED)
    d = ImageDraw.Draw(im)
    for y in range(H):  # 위→아래 그라데이션
        t = y / H
        c = tuple(int(RED[k] * (1 - t) + RED2[k] * t * 0.55 + RED[k] * t * 0.45) for k in range(3))
        d.line([(0, y), (W, y)], fill=c)
    st = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(st)
    for x in range(-H, W, 46):  # 사선 무늬(사이트와 같은 느낌)
        sd.line([(x, H), (x + H, 0)], fill=(255, 255, 255, 18), width=3)
    im.paste(st, (0, 0), st)
    return im

ICON = Image.open(os.path.join(ROOT, "icons/icon-512.png")).convert("RGBA")

def brand(im, y=150):
    ic = ICON.resize((96, 96), Image.LANCZOS)
    f = font("black", 58)
    d = ImageDraw.Draw(im)
    w1 = d.textlength("오늘의 ", font=f); w2 = d.textlength("1위", font=f)
    x = (W - (96 + 22 + w1 + w2)) // 2
    im.paste(ic, (int(x), y), ic)
    tx = x + 96 + 22
    d.text((tx, y + 48), "오늘의 ", font=f, fill="white", anchor="lm")
    d.text((tx + w1, y + 48), "1위", font=f, fill=GOLD, anchor="lm")

def wrap(d, text, f, maxw, maxlines):
    words, lines, cur = text.split(" "), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw:
            cur = t; continue
        if cur:
            lines.append(cur)
        cur = w
        while d.textlength(cur, font=f) > maxw:  # 띄어쓰기 없는 긴 낱말
            k = len(cur)
            while k > 1 and d.textlength(cur[:k], font=f) > maxw:
                k -= 1
            lines.append(cur[:k]); cur = cur[k:]
    if cur:
        lines.append(cur)
    if len(lines) > maxlines:
        lines = lines[:maxlines]
        while d.textlength(lines[-1] + "…", font=f) > maxw and lines[-1]:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1].rstrip() + "…"
    return lines

def center(d, y, text, f, fill):
    d.text((W // 2, y), text, font=f, fill=fill, anchor="mm")

def pill(im, y, text, f, fg, bgc):
    d = ImageDraw.Draw(im)
    tw = d.textlength(text, font=f)
    x0, x1 = (W - tw) / 2 - 40, (W + tw) / 2 + 40
    d.rounded_rectangle([x0, y - 44, x1, y + 44], radius=44, fill=bgc)
    d.text((W // 2, y), text, font=f, fill=fg, anchor="mm")

def card(im, box, radius=56, fill=(255, 255, 255)):
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([box[0], box[1] + 24, box[2], box[3] + 24], radius, fill=(80, 0, 15, 110))
    sh = sh.filter(ImageFilter.GaussianBlur(28))
    im.paste(sh, (0, 0), sh)
    ImageDraw.Draw(im).rounded_rectangle(box, radius, fill=fill)

# ---------- 장면 ----------
# 틱톡 화면은 아래쪽(약 380px)과 오른쪽(약 140px)을 버튼·글이 가리므로 내용은 가운데 위쪽에 둡니다.
def scene_intro():
    im = bg(); brand(im); d = ImageDraw.Draw(im)
    pill(im, 470, DATE, font("bold", 46), INK, GOLD)
    center(d, 690, f"오늘 {WHERE}에서", font("black", 92), "white")
    center(d, 815, "가장 많이 본 영상은?", font("black", 92), "white")
    center(d, 1010, "TOP 3", font("black", 230), GOLD)
    center(d, 1215, "유튜브 · 쇼츠 · 인스타 릴스 조회수 합산", font("bold", 42), (255, 235, 238))
    return im

def scene_rank(rank, it):
    im = bg(); brand(im); d = ImageDraw.Draw(im)
    gold = rank == 1
    center(d, 420, f"{rank}위", font("black", 260 if gold else 210), GOLD if gold else "white")
    ft = font("black", 74)
    lines = wrap(d, clean(it[0]), ft, W - 140 - 110, 3)
    ch = channel(it[1])
    tags = [p for p in it[1].split(" · ")[1:] if not re.match(r"차트 \d+위", p)]
    # 카드 높이를 글 줄 수에 맞춥니다.
    top_y = 600
    h = 70 + len(lines) * 96 + (70 if ch else 0) + (80 if tags else 0) + 60 + 250
    box = (70, top_y, W - 70, top_y + h)
    card(im, box, fill=(255, 250, 235) if gold else (255, 255, 255))
    d = ImageDraw.Draw(im)
    y = top_y + 70 + 40
    for ln in lines:
        d.text((W // 2, y), ln, font=ft, fill=(30, 20, 25), anchor="mm"); y += 96
    if ch:
        d.text((W // 2, y + 6), ch, font=font("bold", 46), fill=(140, 110, 120), anchor="mm"); y += 70
    if tags:
        tf = font("bold", 38); txt = "  ·  ".join(clean(x) for x in tags)
        tw = d.textlength(txt, font=tf)
        d.rounded_rectangle([(W - tw) / 2 - 28, y - 4, (W + tw) / 2 + 28, y + 60], radius=32, fill=(255, 232, 236))
        d.text((W // 2, y + 28), txt, font=tf, fill=RED, anchor="mm"); y += 80
    y += 20
    d.line([(box[0] + 80, y), (box[2] - 80, y)], fill=(240, 225, 228), width=3)
    d.text((W // 2, y + 60), "하루 조회수", font=font("bold", 40), fill=(150, 120, 128), anchor="mm")
    d.text((W // 2, y + 140), views(it[2]) + " 회", font=font("black", 92), fill=RED, anchor="mm")
    if gold:
        pill(im, box[3] + 120, "오늘의 1위", font("black", 50), INK, GOLD)
    return im

def scene_outro():
    im = bg(); brand(im, 300); d = ImageDraw.Draw(im)
    center(d, 590, "4위부터 10위,", font("black", 84), "white")
    center(d, 700, "음악 · 스포츠 · 키즈 순위는", font("black", 76), "white")
    box = (90, 830, W - 90, 1130)
    card(im, box)
    d = ImageDraw.Draw(im)
    d.text((W // 2, 925), "검색창에", font=font("bold", 46), fill=(140, 110, 120), anchor="mm")
    f = font("black", 104); w1 = d.textlength("오늘의 ", font=f); w2 = d.textlength("1위", font=f)
    x = (W - w1 - w2) / 2
    d.text((x, 1040), "오늘의 ", font=f, fill=(30, 20, 25), anchor="lm")
    d.text((x + w1, 1040), "1위", font=f, fill=RED, anchor="lm")
    center(d, 1235, "sally1963.github.io/today1", font("bold", 46), "white")
    center(d, 1320, "매일 밤 12시 새 순위 · 프로필 링크", font("bold", 40), (255, 225, 230))
    return im

def subtitle(im, text):
    """아래쪽 버튼 영역(약 380px) 바로 위에 한글 자막을 그립니다."""
    d = ImageDraw.Draw(im); f = font("bold", 50)
    lines = []
    for part in text.split("\n"):
        lines += wrap(d, part, f, W - 200, 2)
    lines = lines[:3]
    lh = 68; hgt = lh * len(lines) + 44; cy = 1560
    y0 = cy - hgt / 2
    wmax = max(d.textlength(l, font=f) for l in lines)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(ov).rounded_rectangle([(W - wmax) / 2 - 36, y0, (W + wmax) / 2 + 36, y0 + hgt], 28, fill=(20, 8, 12, 190))
    im.paste(ov, (0, 0), ov)
    d = ImageDraw.Draw(im)
    for k, l in enumerate(lines):
        d.text((W // 2, y0 + 22 + lh * k + lh / 2), l, font=f, fill="white", anchor="mm")
    return im

# ---------- 영상으로 묶기 ----------
def encode(png, sec, out):
    tmp = out[:-4] + ".part.mp4"
    vf = (f"format=yuv420p,loop=-1:1,trim=duration={sec},setpts=N/{FPS}/TB,"
          f"fade=t=in:st=0:d=0.35:color=0xff1f3d")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", png, "-vf", vf,
                    "-r", str(FPS), "-c:v", "libx264", "-crf", "18", "-preset", "veryfast",
                    "-pix_fmt", "yuv420p", tmp], check=True)
    os.replace(tmp, out)

def main(preview=False):
    nar = narration_ko() if MODE == "ko" else narration()
    pics = [scene_intro()] + [scene_rank(r, items[r - 1]) for r in (3, 2, 1) if len(items) >= r] + [scene_outro()]
    subs = os.environ.get("SUB", "1") == "1"
    scenes = []
    vdir = os.environ.get("VOICE_DIR")  # voice1.wav ~ voiceN.wav 가 있으면 목소리를 합칩니다
    wavs = []
    for k, (im, (say, sub)) in enumerate(zip(pics, nar)):
        sec = seconds(say)
        w = os.path.join(vdir, f"voice{k+1}.wav") if vdir else None
        if w and os.path.exists(w):
            d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", w],
                                     capture_output=True, text=True).stdout.strip())
            sec = round(max(3.0, d + 0.7), 2)
            wavs.append((w, sec))
        scenes.append((subtitle(im, sub) if subs else im, sec))
    os.makedirs(OUTDIR, exist_ok=True)
    base = os.path.join(OUTDIR, f"today1-{meta['updated']}-{REGION}" + ("-ko" if MODE == "ko" else ""))
    # 내레이션 대본(영어)·자막 시간표
    tsec, rows, srt = 0.0, [], []
    def ts(x):
        return f"{int(x//3600):02}:{int(x%3600//60):02}:{int(x%60):02},{int(round(x%1*1000)):03}"
    for k, ((eng, ko), (_, sec)) in enumerate(zip(nar, scenes)):
        vl, sl = ("한국어 목소리", "영어 자막") if MODE == "ko" else ("영어 목소리", "한글 자막")
        rows.append(f"[{tsec:4.1f}초 ~ {tsec+sec:4.1f}초]\n{vl}: {eng}\n{sl}: {ko.replace(chr(10), ' ')}\n")
        srt.append(f"{k+1}\n{ts(tsec+0.2)} --> {ts(tsec+sec-0.1)}\n{ko}\n")
        tsec += sec
    open(base + "-narration.txt", "w", encoding="utf-8").write("\n".join(rows))
    open(base + "-subtitles.srt", "w", encoding="utf-8").write("\n".join(srt))
    work = tempfile.mkdtemp()
    if preview:
        for k, (im, _) in enumerate(scenes):
            im.save(os.path.join(OUTDIR, f"frame{k}.png"))
        return
    parts = []
    for k, (im, sec) in enumerate(scenes):
        p = os.path.join(work, f"s{k}.png"); im.save(p)
        o = os.path.join(work, f"s{k}.mp4"); encode(p, sec, o); parts.append(o)
    lst = os.path.join(work, "list.txt")
    open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    out = base + ".mp4"
    tmp = out[:-4] + ".part.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c", "copy", "-movflags", "+faststart", tmp], check=True)
    os.replace(tmp, out)
    if wavs and len(wavs) == len(scenes):  # 장면마다 목소리를 0.3초 뒤에 시작해 이어 붙입니다
        args, flt = [], []
        for k, (w, sec) in enumerate(wavs):
            args += ["-i", w]
            flt.append(f"[{k+1}:a]aresample=48000,aformat=channel_layouts=stereo,adelay=300:all=1,apad,atrim=0:{sec}[a{k}]")
        flt.append("".join(f"[a{k}]" for k in range(len(wavs))) + f"concat=n={len(wavs)}:v=0:a=1[aout]")
        tmp2 = out[:-4] + ".part.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", out, *args, "-filter_complex", ";".join(flt),
                        "-map", "0:v", "-map", "[aout]", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                        "-shortest", "-movflags", "+faststart", tmp2], check=True)
        os.replace(tmp2, out)
    print(out)

if __name__ == "__main__":
    main(preview=os.environ.get("PREVIEW") == "1")
