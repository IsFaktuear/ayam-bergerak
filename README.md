# Ayam Bergerak - Proyek Sistem Multimedia

Ayam jantan interaktif "Si Jago Bangun Pagi" dengan alur wajib tugas:
**Gambar (Visual) - Suara (Audio) - Gerak (Animasi)**. Tampilan halamannya memakai
layout kandang interaktif: panggung di kiri, panel aksi, pengaturan, catatan aktivitas,
dan fakta ayam di kanan.

- Nama: Ahmad Muqarrobin (Robin)
- NIM: 242502040003
- Kelas: 3TI01
- Karakter: Ayam (ayam jantan)

## Isi folder
- `index.html` - halaman web interaktifnya (HTML + CSS + JavaScript, tanpa library luar)
- `kokok.mp3` - rekaman kokok ayam asli (domain publik, Wikimedia Commons, direkam alys via PDSounds)
- `kotek.mp3` - rekaman kotek ayam asli (domain publik, Wikimedia Commons, direkam alys via PDSounds)
- `ayam_bergerak.mp4` - versi video, 10 detik, 854x480, ada suara kotek dan kokoknya
- `buat_ayam_bergerak.py` - program Python pembuat video itu (Pillow + NumPy + FFmpeg, memakai kedua MP3 di atas)

## Cara menjalankan webnya
Buka saja `index.html` di browser. Klik ayamnya (atau tekan Spasi) untuk berkokok,
ada juga tombol Berkotek dan Mematuk, slider Kecepatan, dan slider Volume.

## Cara membuat ulang videonya
```
pip install pillow numpy
python buat_ayam_bergerak.py
```
Butuh FFmpeg terpasang. Hasilnya menimpa `ayam_bergerak.mp4`.

## Cara publish ke GitHub Pages
1. Buat repository baru di GitHub, nama: `ayam-bergerak`
2. Upload file-file ini ke repository itu: `index.html`, `kokok.mp3`, `kotek.mp3`, `ayam_bergerak.mp4`, `buat_ayam_bergerak.py`
3. Di repository: Settings - Pages - Source pilih "Deploy from a branch", Branch: `main`, folder `/ (root)`, Save
4. Tunggu 1-2 menit, webnya online di: `https://<username-github>.github.io/ayam-bergerak/`
