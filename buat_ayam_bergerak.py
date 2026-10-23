# buat_ayam_bergerak.py
# Versi video (MP4) dari proyek "Ayam Bergerak - Si Jago Bangun Pagi".
# Frame digambar satu per satu dengan Pillow, suara memakai rekaman ayam asli
# (file MP3) yang dicampur ke trek audio dengan NumPy, lalu digabung jadi MP4 oleh FFmpeg.
#
# Cara pakai:
#   pip install pillow numpy
#   python buat_ayam_bergerak.py
# Hasil: ayam_bergerak.mp4 (10 detik, 854x480, 24 fps = 240 frame)
#
# Alur adegan:
#   0,0 - 5,0 dtk : ayam berjalan (walk cycle, kepala maju-mundur)
#   5,0 - 7,0 dtk : ayam berhenti dan mematuk biji sambil berkotek
#   7,0 - 10,0 dtk: ayam mendongak dan berkokok "KUKURUYUK!"

import math
import os
import shutil
import subprocess
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS, DUR = 854, 480, 24, 10
N = FPS * DUR
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
FRAMES = os.path.join(OUT_DIR, "_frames")
WAV = os.path.join(OUT_DIR, "_suara.wav")
MP4 = os.path.join(OUT_DIR, "ayam_bergerak.mp4")
GROUND_Y = 392  # garis tanah tempat kaki ayam berpijak

try:
    F_BIG = ImageFont.truetype("DejaVuSans-Bold.ttf", 34)
    F_MED = ImageFont.truetype("DejaVuSans-Bold.ttf", 22)
except Exception:
    F_BIG = ImageFont.load_default()
    F_MED = ImageFont.load_default()


# --------------------------------------------------------------- latar
def buat_latar():
    """Langit gradasi pagi + matahari, digambar sekali lalu dipakai ulang."""
    img = Image.new("RGB", (W, H), (142, 212, 247))
    d = ImageDraw.Draw(img)
    for y in range(300):  # gradasi langit ke krem di dekat tanah
        t = y / 300
        r = int(142 + (254 - 142) * t)
        g = int(212 + (243 - 212) * t)
        b = int(247 + (199 - 247) * t)
        d.line([(0, y), (W, y)], fill=(r, g, b))
    d.ellipse([W - 190, 30, W - 80, 140], fill=(255, 217, 59))  # matahari
    d.ellipse([W - 178, 42, W - 92, 128], fill=(255, 245, 157))
    d.rectangle([0, GROUND_Y - 92, W, GROUND_Y - 22], fill=(222, 184, 110))  # ladang jauh di balik pagar
    d.rectangle([0, GROUND_Y - 22, W, H], fill=(238, 194, 94))  # tanah
    d.rectangle([0, GROUND_Y - 22, W, GROUND_Y - 12], fill=(223, 165, 63))
    return img


def gambar_awal(img, geser):
    d = ImageDraw.Draw(img)
    for cx, cy, s in [(120, 70, 1.0), (480, 46, 0.7), (700, 96, 0.85)]:
        x = ((cx - geser * 6) % (W + 240)) - 120
        d.ellipse([x, cy, x + 110 * s, cy + 30 * s], fill=(255, 255, 255))
        d.ellipse([x + 18 * s, cy - 22 * s, x + 66 * s, cy + 16 * s], fill=(255, 255, 255))
        d.ellipse([x + 48 * s, cy - 14 * s, x + 88 * s, cy + 18 * s], fill=(255, 255, 255))


def gambar_pagar_tanah(img, geser):
    d = ImageDraw.Draw(img)
    # pagar kayu bergeser (parallax, lebih lambat dari tanah)
    off = -(geser % 118)
    for x in range(off - 118, W + 118, 118):
        d.rectangle([x + 54, GROUND_Y - 92, x + 64, GROUND_Y - 22], fill=(169, 116, 63))
    d.rectangle([0, GROUND_Y - 76, W, GROUND_Y - 66], fill=(185, 131, 74))
    # bintik tanah + biji bergeser penuh
    off = -(geser % 140)
    for x in range(off - 140, W + 140, 140):
        for dx, dy in [(20, 30), (70, 60), (110, 22)]:
            d.ellipse([x + dx - 3, GROUND_Y + dy - 3, x + dx + 3, GROUND_Y + dy + 3],
                      fill=(180, 122, 46))
    for x in range(off - 140, W + 140, 280):  # biji pucat
        d.ellipse([x + 40, GROUND_Y + 38, x + 49, GROUND_Y + 44], fill=(255, 243, 176))


# --------------------------------------------------------------- ayam
def gambar_ayam(img, f):
    """Gambar ayam di tengah panggung sesuai detik adegan."""
    d = ImageDraw.Draw(img)
    t = f / FPS
    cx, base = W // 2 - 30, GROUND_Y  # pangkal gambar ayam
    sedang_matuk = 5.0 <= t < 7.0
    sedang_kokok = t >= 7.0

    if sedang_kokok:
        fase, bob, kepala = 0.0, 0, "kokok"
    elif sedang_matuk:
        fase, bob, kepala = 0.0, 0, "matuk"
    else:
        fase = t * 2 * math.pi * 1.6  # 1,6 langkah per detik
        bob = -abs(math.sin(fase)) * 6
        kepala = "jalan"

    hip_y = base - 78 + bob
    # ---- kaki (walk cycle: ayun bergantian) ----
    for hip_x, lawan in [(cx - 22, 0.0), (cx + 22, math.pi)]:
        ayun = math.sin(fase + lawan) * 24 if kepala == "jalan" else 0
        angkat = max(0.0, -math.cos(fase + lawan)) * 10 if kepala == "jalan" else 0
        fx = hip_x + ayun
        fy = base - angkat
        d.line([hip_x, hip_y, fx, fy], fill=(230, 126, 34), width=7)
        for jx in (-12, 0, 12):  # jari kaki
            d.line([fx, fy, fx + jx, fy + 4], fill=(230, 126, 34), width=4)

    # ---- ekor ----
    for warna, naik, geser in [((30, 111, 92), 96, 0), ((20, 83, 45), 76, 14), ((46, 134, 171), 112, -12)]:
        titik = []
        for k in range(21):
            s = k / 20
            x = (cx - 78 + geser) - 52 * math.sin(s * math.pi * 0.9)
            y = (hip_y - 42) - naik * math.sin(s * math.pi * 0.75)
            titik.append((x, y))
        d.line(titik, fill=warna, width=13)

    # ---- badan ----
    d.ellipse([cx - 88, hip_y - 108, cx + 88, hip_y + 8], fill=(211, 84, 0))
    d.ellipse([cx - 72, hip_y - 96, cx + 76, hip_y - 2], fill=(230, 126, 34))
    # sayap (mengepak saat berkokok)
    kepak = -18 * abs(math.sin(t * 18)) if sedang_kokok else 0
    d.ellipse([cx - 62, hip_y - 88 + kepak, cx + 38, hip_y - 18 + kepak], fill=(166, 62, 0))

    # ---- leher + kepala: 3 pose ----
    if kepala == "kokok":
        hx, hy = cx + 88, hip_y - 148  # mendongak
    elif kepala == "matuk":
        turun = abs(math.sin((t - 5.0) * math.pi * 2.8))  # turun-naik mematuk
        hx, hy = cx + 108, hip_y - 118 + turun * 96
    else:
        hx = cx + 84 + math.sin(fase) * 7  # kepala maju-mundur khas ayam
        hy = hip_y - 132
    d.line([cx + 56, hip_y - 62, hx, hy + 18], fill=(230, 126, 34), width=30)
    d.ellipse([hx - 27, hy - 27, hx + 27, hy + 27], fill=(211, 84, 0))
    # jengger
    for jx, jy, r in [(-14, -30, 11), (0, -38, 13), (14, -30, 11)]:
        d.ellipse([hx + jx - r, hy + jy - r, hx + jx + r, hy + jy + r], fill=(231, 76, 60))
    # pial
    d.ellipse([hx + 12, hy + 18, hx + 26, hy + 44], fill=(231, 76, 60))
    # paruh (bawah membuka saat berkokok)
    d.polygon([(hx + 22, hy - 8), (hx + 52, hy), (hx + 22, hy + 8)], fill=(241, 196, 15))
    if sedang_kokok:
        d.polygon([(hx + 22, hy + 8), (hx + 48, hy + 20), (hx + 20, hy + 16)], fill=(212, 172, 13))
    d.ellipse([hx + 2, hy - 10, hx + 13, hy + 1], fill=(20, 20, 20))  # mata

    # ---- gelembung teks ----
    if sedang_kokok:
        d.rounded_rectangle([hx + 36, hy - 92, hx + 330, hy - 38], 14,
                            fill=(255, 255, 255), outline=(231, 76, 60), width=4)
        d.text((hx + 56, hy - 79), "KUKURUYUK!", fill=(192, 57, 43), font=F_BIG)
    elif sedang_matuk:
        d.rounded_rectangle([hx + 24, hy - 84, hx + 268, hy - 36], 14,
                            fill=(255, 255, 255), outline=(243, 156, 18), width=4)
        d.text((hx + 40, hy - 72), "kotok... kotok...", fill=(125, 76, 0), font=F_MED)


# --------------------------------------------------------------- suara
# Rekaman ayam asli, domain publik dari Wikimedia Commons (direkam alys, PDSounds):
#   kokok.mp3 - potongan "Medium rooster crowing"
#   kotek.mp3 - potongan "Hen announcing shes lain an egg"
SR = 44100


def _muat_mp3(nama):
    """Dekode MP3 di folder ini jadi array float mono 44100 Hz lewat FFmpeg."""
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", os.path.join(OUT_DIR, nama),
         "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
        check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def _tambah(buf, t0, suara, vol=1.0, potong=None):
    if potong:
        suara = suara[:int(potong * SR)]
    mulai = int(t0 * SR)
    n = min(len(suara), len(buf) - mulai)
    if n > 0:
        buf[mulai:mulai + n] += suara[:n] * vol


def buat_suara():
    buf = np.zeros(DUR * SR)
    _tambah(buf, 5.2, _muat_mp3("kotek.mp3"), 0.9, potong=1.8)  # kotek saat mematuk
    _tambah(buf, 7.0, _muat_mp3("kokok.mp3"), 1.0)              # kokok penutup
    buf = np.clip(buf, -1, 1)
    with wave.open(WAV, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((buf * 32767).astype(np.int16).tobytes())


# --------------------------------------------------------------- utama
def main():
    os.makedirs(FRAMES, exist_ok=True)
    latar = buat_latar()
    for f in range(N):
        img = latar.copy()
        geser = 0 if f >= 5 * FPS else int(f * 3.2)  # berhenti bergeser saat ayam berhenti
        gambar_awal(img, f // 6)
        gambar_pagar_tanah(img, geser)
        gambar_ayam(img, f)
        img.save(os.path.join(FRAMES, f"frame_{f:04d}.png"))
        if f % 48 == 0:
            print(f"frame {f}/{N}")
    buat_suara()
    subprocess.run(
        ["ffmpeg", "-y", "-framerate", str(FPS), "-i", os.path.join(FRAMES, "frame_%04d.png"),
         "-i", WAV, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
         "-shortest", MP4],
        check=True)
    shutil.rmtree(FRAMES)
    os.remove(WAV)
    print("Selesai:", MP4)


if __name__ == "__main__":
    main()
