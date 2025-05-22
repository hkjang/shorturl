# Flask Redis Short URL 서비스

Python + Flask + Redis + Docker를 활용한 Short URL 생성 및 리디렉션 서비스입니다.

## 주요 기능

| 기능 | 설명 |
|------|------|
| Short URL 생성 | 사용자가 입력한 URL을 짧은 코드로 압축 |
| 리디렉션 | `/r/<short_code>` 요청 시 원본 URL로 이동 |
| 프리뷰 페이지 | 생성된 단축 URL을 예쁘게 출력 |
| 웹 UI 제공 | Bootstrap 기반의 URL 생성 웹 페이지 |
| Docker 지원 | 컨테이너 기반 배포 환경 지원 |

---

## 폴더 구조

```

short-url-app/
├── app.py                  # Flask 메인 애플리케이션
├── Dockerfile              # Docker 빌드 파일
├── requirements.txt        # Python 의존성
├── templates/
│   ├── create.html         # URL 생성 페이지
│   └── preview\.html        # Short URL 미리보기 페이지
├── static/
│   └── css/
│       └── bootstrap.min.css  # Bootstrap CSS

```

---

## API 명세

| 경로 | 메서드 | 설명 |
|------|--------|------|
| `/` 또는 `/create` | GET | Short URL 생성 페이지 표시 |
| `/shorten` | POST | 입력한 URL을 단축 처리 |
| `/<short_code>` | GET | Short URL 미리보기 표시 |
| `/r/<short_code>` | GET | 원본 URL로 리디렉션 |

---

## 설치 및 실행

### 1. Docker로 실행

```bash
docker build -t short-url-app .
docker run -d -p 5000:5000 --name short-url --env REDIS_HOST=your-redis-host short-url-app
````

### 2. 로컬에서 실행

```bash
pip install -r requirements.txt
export REDIS_HOST=localhost  # 또는 실제 호스트
python app.py
```

---

## 환경변수

| 변수명          | 설명                 | 기본값                     |
| ------------ | ------------------ | ----------------------- |
| `REDIS_HOST` | Redis 서버 호스트       | `localhost`             |
| `REDIS_PORT` | Redis 포트           | `6379`                  |
| `BASE_URL`   | 단축 URL 생성 시 기본 도메인 | `http://localhost:5000` |

---

## 기타 정보

* 단축 URL은 **대소문자 구분**됩니다.
* Redis 키 패턴은 `short:<code>`입니다.
* Bootstrap은 정적 파일로 포함되어 있어 외부 CDN 불필요합니다.

---

## 라이선스

MIT
