import os
import re
import redis
from urllib.parse import urlparse
from flask import Flask, request, render_template, redirect, jsonify
from dotenv import load_dotenv
from nanoid import generate

load_dotenv()

app = Flask(__name__)
r = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    decode_responses=True
)

BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')
TTL_SECONDS = int(os.getenv('TTL_SECONDS', 60 * 60 * 24))
MAX_URL_LENGTH = 2048

URL_REGEX = re.compile(r'^(https?://)?[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,}(:\d+)?(/.*)?$')


def is_valid_url(url: str) -> bool:
    if not url or len(url) > MAX_URL_LENGTH:
        return False
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ('http', 'https'):
            return False
        if not parsed.netloc or not URL_REGEX.match(url):
            return False
        hostname = parsed.hostname
        # SSRF 방지
        if hostname in ('localhost', '127.0.0.1') or hostname.startswith('169.254') or hostname.endswith('.local'):
            return False
    except Exception:
        return False
    return True


@app.route('/')
def index():
    return redirect('/create')


@app.route('/create', methods=['GET', 'POST'])
def create():
    short_url = None
    error = None
    if request.method == 'POST':
        original_url = request.form.get('originalUrl', '').strip()

        if not is_valid_url(original_url):
            return render_template('create.html', error='유효하지 않은 URL입니다.')

        existing_code = r.get(f"url:{original_url}")
        if existing_code:
            short_url = f"{BASE_URL}/{existing_code}"
        else:
            while True:
                code = generate(size=6)
                if not r.exists(f"short:{code}"):
                    break
            r.set(f"short:{code}", original_url, ex=TTL_SECONDS)
            r.set(f"url:{original_url}", code, ex=TTL_SECONDS)
            short_url = f"{BASE_URL}/{code}"

    return render_template('create.html', short_url=short_url, error=error)


@app.route('/<code>')
def preview(code):
    if not code.isalnum():
        return render_template('preview.html', error='코드 형식이 잘못되었습니다.')

    original = r.get(f"short:{code}")
    if not original:
        return render_template('preview.html', error='단축 URL을 찾을 수 없습니다.')

    return render_template(
        'preview.html',
        original_url=original,
        short_code=code,
        short_url=f"{BASE_URL}/{code}"
    )


@app.route('/r/<code>')
def redirect_to(code):
    if not code.isalnum():
        return 'Invalid code format', 400

    original = r.get(f"short:{code}")
    if not original:
        return 'URL not found', 404
    return redirect(original)


@app.route('/api/create', methods=['GET', 'POST'])
def api_create():
    if request.method == 'POST':
        data = request.get_json()
        original_url = data.get('originalUrl')
    else:
        original_url = request.args.get('originalUrl')

    if not original_url:
        return jsonify({'error': 'originalUrl is required'}), 400

    # 정규식 URL 유효성 검사
    import re
    url_regex = re.compile(r'^(http|https)://[^\s]+$')
    if not url_regex.match(original_url) or len(original_url) > 2048:
        return jsonify({'error': '잘못된 URL 형식입니다.'}), 400

    existing_code = r.get(f"url:{original_url}")
    if existing_code:
        short_url = f"{BASE_URL}/{existing_code}"
        code = existing_code
    else:
        while True:
            code = generate(size=6)
            if not r.exists(f"short:{code}"):
                break
        r.set(f"short:{code}", original_url, ex=TTL_SECONDS)
        r.set(f"url:{original_url}", code, ex=TTL_SECONDS)
        short_url = f"{BASE_URL}/{code}"

    return jsonify({
        'original_url': original_url,
        'short_code': code,
        'short_url': short_url,
        'message': '단축 URL이 생성되었습니다.'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
