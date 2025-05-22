import os
import redis
from flask import Flask, request, render_template, redirect, url_for
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

@app.route('/')
def index():
    return redirect('/create')
@app.route('/create', methods=['GET', 'POST'])
def create():
    short_url = None
    if request.method == 'POST':
        original_url = request.form.get('originalUrl')
        if not original_url:
            return render_template('create.html', error='URL이 필요합니다.')

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
    return render_template('create.html', short_url=short_url)


@app.route('/<code>')
def preview(code):
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
    original = r.get(f"short:{code}")
    if not original:
        return 'URL not found', 404
    return redirect(original)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
