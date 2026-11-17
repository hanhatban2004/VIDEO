import asyncio
import subprocess
from pathlib import Path

import edge_tts
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)
WORK = ROOT / "build"
WORK.mkdir(exist_ok=True)

W, H = 1080, 1920          # Đổi thành 1920, 1080 nếu muốn video ngang 16:9
FPS = 25
FONT_DIR = "/usr/share/fonts/truetype/dejavu/"

SCENES = [
    {"id": 1, "duration": 25, "title": "Chào hỏi tự tin",
     "lines": [
        ("Em", "Con chào bố mẹ ạ! Hôm nay bố mẹ có khỏe không ạ?"),
        ("Bố mẹ", "Bố mẹ khỏe. Con chuẩn bị đi học chưa?"),
        ("Em", "Dạ, con chuẩn bị xong rồi ạ!"),
     ],
     "message": "Luôn chủ động chào hỏi với thái độ vui vẻ, tự tin và lễ phép."},
    {"id": 2, "duration": 30, "title": "Chủ động giúp đỡ gia đình",
     "lines": [
        ("Em", "Mẹ ơi, để con phụ mẹ chuẩn bị bữa ăn nhé!"),
        ("Mẹ", "Ừ, con giúp mẹ lấy bát đũa nhé!"),
        ("Em", "Dạ, để con làm ngay ạ!"),
     ],
     "message": "Chủ động quan tâm, giúp đỡ mọi người bằng những hành động nhỏ."},
    {"id": 3, "duration": 35, "title": "Tự tin bày tỏ ý kiến",
     "lines": [
        ("Bố", "Cuối tuần này gia đình mình nên làm gì nhỉ?"),
        ("Em", "Con nghĩ cả nhà mình có thể cùng đi dã ngoại hoặc nấu một bữa ăn thật ngon ở nhà ạ!"),
        ("Mẹ", "Ý kiến hay đấy!"),
        ("Em", "Con cũng muốn nghe ý kiến của bố mẹ nữa ạ!"),
     ],
     "message": "Mạnh dạn chia sẻ suy nghĩ, biết lắng nghe và tôn trọng ý kiến của người khác."},
    {"id": 4, "duration": 35, "title": "Giao tiếp thân thiện, biết lắng nghe",
     "lines": [
        ("Em", "Hôm nay ở trường của em có chuyện gì vui không?"),
        ("Người thân", "Hôm nay em được cô giáo khen vì làm bài tốt!"),
        ("Em", "Thật tuyệt! Chúc mừng em nhé!"),
        ("Người thân", "Cảm ơn anh/chị!"),
     ],
     "message": "Biết quan tâm, lắng nghe, chia sẻ và động viên người thân."},
    {"id": 5, "duration": 25, "title": "Kết thúc – Thông điệp",
     "lines": [
        ("Em", "Qua những việc làm hằng ngày, em hiểu rằng sự tự tin, thân thiện và chủ động trong giao tiếp bắt đầu từ chính gia đình mình. Chỉ cần biết chào hỏi, lắng nghe, chia sẻ và quan tâm đến mọi người, chúng ta sẽ giúp gia đình thêm vui vẻ, yêu thương và gắn kết. Hãy bắt đầu giao tiếp bằng sự tự tin và chân thành ngay từ hôm nay!"),
     ],
     "message": "TỰ TIN – THÂN THIỆN – CHỦ ĐỘNG GIAO TIẾP"},
]

VOICE_MAP = {
    "Em": "vi-VN-HoaiMyNeural",
    "Bố": "vi-VN-NamMinhNeural",
    "Mẹ": "vi-VN-HoaiMyNeural",
    "Bố mẹ": "vi-VN-NamMinhNeural",
    "Người thân": "vi-VN-HoaiMyNeural",
}

def make_slide(scene, out_path):
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        draw.line([(0, y), (W, y)], fill=(int(255 - 25 * t), int(240 - 20 * t), int(225 - 15 * t)))

    try:
        title_font = ImageFont.truetype(FONT_DIR + "DejaVuSans-Bold.ttf", 78)
        body_font = ImageFont.truetype(FONT_DIR + "DejaVuSans.ttf", 46)
        small_font = ImageFont.truetype(FONT_DIR + "DejaVuSans-Oblique.ttf", 40)
    except Exception:
        title_font = body_font = small_font = ImageFont.load_default()

    def wrap(text, font, maxw):
        words, lines, cur = text.split(), [], ""
        for w in words:
            test = (cur + " " + w).strip()
            if draw.textlength(test, font=font) <= maxw:
                cur = test
            else:
                if cur: lines.append(cur)
                cur = w
        if cur: lines.append(cur)
        return lines

    draw.text((W // 2, 120), f"CẢNH {scene['id']}", font=small_font, fill="#95A5A6", anchor="mm")
    draw.text((W // 2, 220), scene["title"], font=title_font, fill="#2C3E50", anchor="mm")

    y = 480
    for speaker, text in scene["lines"]:
        color = "#2980B9" if speaker == "Em" else "#8E44AD"
        draw.text((100, y), f"{speaker}:", font=body_font, fill=color)
        y += 70
        for ln in wrap(text, body_font, W - 200):
            draw.text((100, y), ln, font=body_font, fill="#2C3E50")
            y += 62
        y += 30

    msg_y = H - 400
    draw.line([(100, msg_y), (W - 100, msg_y)], fill="#E67E22", width=3)
    draw.text((W // 2, msg_y + 60), "THÔNG ĐIỆP", font=small_font, fill="#E67E22", anchor="mm")
    y = msg_y + 140
    for ln in wrap(scene["message"], body_font, W - 200):
        draw.text((W // 2, y), ln, font=body_font, fill="#D35400", anchor="mm")
        y += 62

    img.save(out_path)

async def tts(text, voice, path):
    await edge_tts.Communicate(text, voice, rate="-5%").save(str(path))

async def build_scene_audio(scene, d):
    parts = []
    for i, (spk, text) in enumerate(scene["lines"]):
        p = d / f"l{i}.mp3"
        await tts(text, VOICE_MAP.get(spk, "vi-VN-HoaiMyNeural"), p)
        parts.append(p)
    with open(d / "concat.txt", "w", encoding="utf-8") as f:
        for p in parts:
            f.write(f"file '{p.name}'\n")
    out = d / "audio.mp3"
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0",
                    "-i", "concat.txt", "-c", "copy", "audio.mp3"],
                   check=True, cwd=str(d), capture_output=True)
    return out

def build_scene_video(scene, slide, audio, out):
    dur = scene["duration"]
    vf = (f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
          f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=white,"
          f"format=yuv420p,fade=t=in:st=0:d=0.5,"
          f"fade=t=out:st={dur - 0.5}:d=0.5")
    subprocess.run([
        "ffmpeg", "-y", "-loop", "1", "-t", str(dur), "-i", str(slide),
        "-i", str(audio), "-vf", vf, "-af", f"apad=whole_dur={dur}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k", "-t", str(dur),
        "-pix_fmt", "yuv420p", str(out),
    ], check=True, capture_output=True)

def concat_videos(videos, out):
    lst = WORK / "videos.txt"
    with open(lst, "w", encoding="utf-8") as f:
        for v in videos:
            f.write(f"file '{v.resolve()}'\n")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0",
                    "-i", str(lst), "-c", "copy", str(out)],
                   check=True, capture_output=True)

async def main():
    clips = []
    for scene in SCENES:
        d = WORK / f"scene_{scene['id']}"
        d.mkdir(exist_ok=True)
        slide = d / "slide.png"
        print(f"[{scene['id']}] slide", flush=True); make_slide(scene, slide)
        print(f"[{scene['id']}] tts", flush=True);   audio = await build_scene_audio(scene, d)
        print(f"[{scene['id']}] video", flush=True)
        clip = d / "clip.mp4"
        build_scene_video(scene, slide, audio, clip)
        clips.append(clip)

    final = OUT / "video.mp4"
    print("[*] concat", flush=True)
    concat_videos(clips, final)
    print(f"DONE {final}", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
