import os
from flask import Flask, request, send_file, render_template
import yt_dlp
import uuid

app = Flask(__name__)
DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), 'downloads')
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.get('/')
def home():
    return render_template('index.html')

@app.post('/download')
def download():
    url = request.form.get('url', '').strip()
    if 'instagram.com' not in url:
        return render_template('index.html', error='Please enter a valid Instagram URL.'), 400
    job = uuid.uuid4().hex
    outtmpl = os.path.join(DOWNLOAD_DIR, job + '.%(ext)s')
    try:
        opts = {'outtmpl': outtmpl, 'format': 'best[ext=mp4]/best', 'noplaylist': True, 'quiet': True, 'no_warnings': True}
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            path = ydl.prepare_filename(info)
        return send_file(path, as_attachment=True, download_name=os.path.basename(path))
    except Exception:
        return render_template('index.html', error='Could not download this link. Make sure it is a public Instagram post or reel.'), 400

@app.get('/health')
def health():
    return {'status': 'ok', 'service': 'PW Vision Instagram Downloader'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
