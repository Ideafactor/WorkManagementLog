# WorkManagementLog

사내 웹 서비스를 위한 재사용 가능한 기반 프로젝트입니다. MaruLog에서 제품별 도메인을 분리한 템플릿으로, 로그인·권한·사용자 관리와 SPA/API 배포 구조를 제공합니다. 업무 기록, 연차, 출퇴근 등의 제품 기능은 아직 포함하지 않습니다.

## 주요 기능과 기술

- **웹:** React 19, TypeScript, Vite, TanStack Router/Query, Zod
- **API:** Python 3.13, FastAPI, Pydantic v2, SQLAlchemy async, Alembic
- **데이터베이스:** PostgreSQL 16, 실행용 pooled URL과 migration용 direct URL 분리
- **인증:** Argon2id 비밀번호 해시, HttpOnly 세션 쿠키, CSRF 검증, MEMBER/ADMIN 권한
- **관리:** 최초 관리자 생성, 사용자 목록·생성, 역할·상태 변경 API
- **운영:** 단일 origin의 SPA/API Docker 이미지, JSON 로그, 상태 확인 엔드포인트
- **검증:** Ruff, basedpyright, pytest, Biome, TypeScript, Vitest, Playwright

## 빠른 시작: Docker Compose

Git과 Docker Compose가 필요합니다. 저장소를 받은 뒤 루트에서 실행합니다.

```bash
git clone https://github.com/Ideafactor/WorkManagementLog.git
cd WorkManagementLog
cp .env.example .env.local
```

`.env.example`은 변수 목록이며 빈 값 그대로 실행할 수 없습니다. `.env.local`을 다음과 같이 작성하고, 설명용 값을 실제 로컬 비밀값으로 바꿉니다.

```dotenv
APP_ENV=development
APP_TIMEZONE=Asia/Seoul
PORT=8000
SESSION_SECRET=<32자 이상의 임의 비밀값>
CSRF_SECRET=<SESSION_SECRET과 다른 32자 이상의 임의 비밀값>
BOOTSTRAP_ADMIN_EMAIL=admin@example.com
BOOTSTRAP_ADMIN_NAME=Administrator
BOOTSTRAP_ADMIN_PASSWORD=<12자 이상의 초기 비밀번호>
FORWARDED_ALLOW_IPS=127.0.0.1
```

비밀값은 `openssl rand -hex 32`를 각각 실행해 생성할 수 있습니다. Compose가 두 데이터베이스 URL을 내부 `db` 서비스 주소로 주입하므로 위 설정에는 생략합니다.

```bash
docker compose up --build -d
docker compose logs -f app
```

앱 컨테이너는 Alembic migration과 관리자 bootstrap을 실행한 뒤 서버를 시작합니다. [http://localhost:8000](http://localhost:8000)에서 설정한 관리자 계정으로 로그인합니다. 같은 이메일이 이미 있으면 bootstrap은 기존 계정이나 비밀번호를 변경하지 않습니다.

```bash
# 상태 확인
curl --fail http://localhost:8000/health
curl --fail http://localhost:8000/ready

# 중지: 데이터베이스 볼륨은 유지됩니다.
docker compose down
```

Compose의 데이터베이스 계정은 로컬 개발 전용입니다. 기본 포트는 8000이며, 변경할 때는 `PORT`와 `compose.yaml`의 컨테이너 포트 매핑을 함께 수정해야 합니다.

## 환경변수

| 변수 | 용도 / 조건 |
| --- | --- |
| `APP_ENV` | `development`, `test`, `production`; 기본값 `development` |
| `APP_TIMEZONE` | `Asia/Seoul` |
| `DATABASE_URL_POOLED` | API 실행용 PostgreSQL URL, 필수 |
| `DATABASE_URL_DIRECT` | Alembic migration용 PostgreSQL URL, 필수 |
| `SESSION_SECRET` | 세션 토큰 digest용 비밀값, 32자 이상 |
| `CSRF_SECRET` | CSRF 토큰 digest용 비밀값, 32자 이상이며 세션 비밀값과 달라야 함 |
| `BOOTSTRAP_ADMIN_EMAIL` | 최초 관리자 이메일, 선택 |
| `BOOTSTRAP_ADMIN_NAME` | 최초 관리자 이름, 1–100자 |
| `BOOTSTRAP_ADMIN_PASSWORD` | 최초 관리자 비밀번호, 12자 이상 |
| `PORT` | 컨테이너 서버 포트, 기본값 `8000` |
| `FORWARDED_ALLOW_IPS` | 신뢰할 프록시 IP, 기본값 `127.0.0.1` |
| `APP_STATIC_DIR` | 빌드된 SPA 디렉터리, 기본값 `/app/static` |

관리자 설정 3개는 모두 지정하거나 모두 생략합니다. 생략하려면 빈 문자열 대신 해당 줄을 제거합니다. 운영에서는 pooled/direct URL이 서로 달라야 하며, Secure 쿠키를 사용하므로 HTTPS가 필요합니다. 비밀번호는 해시로, 세션 및 CSRF 토큰은 digest로 저장합니다. 실제 비밀값은 Git에 넣지 않고 실행 환경으로 주입합니다.

## 로컬 개발

Python 3.13, uv, Bun과 실행 중인 PostgreSQL이 필요합니다. 웹 패키지의 Node.js 요구 버전은 24.x입니다. CI/Docker의 도구 버전은 uv `0.12.3`, Bun `1.3.14`입니다.

API 설정 파일은 실행 디렉터리 기준으로 읽습니다. 직접 개발할 때는 `apps/api/.env.local`을 만들고 위 환경변수와 다음 두 URL을 설정합니다. 로컬 DB 사용자·비밀번호·포트·DB 이름으로 교체하세요. Compose 기본 DB는 호스트에 포트를 공개하지 않으므로 별도의 로컬 PostgreSQL 또는 개발용 포트 매핑이 필요합니다.

```dotenv
DATABASE_URL_POOLED=postgresql+asyncpg://USER:PASSWORD@127.0.0.1:5432/DATABASE
DATABASE_URL_DIRECT=postgresql+asyncpg://USER:PASSWORD@127.0.0.1:5432/DATABASE
```

첫 번째 터미널에서 API를 실행합니다.

```bash
cd apps/api
uv sync --locked
uv run alembic upgrade head
uv run python -m app.bootstrap
uv run uvicorn app.main:app --reload --port 8000
```

두 번째 터미널에서 웹을 실행합니다.

```bash
cd apps/web
bun install --frozen-lockfile
bun run dev
```

[http://localhost:5173](http://localhost:5173)으로 접속합니다. Vite는 `/api`, `/health`, `/ready` 요청을 로컬 API의 8000 포트로 전달합니다.

## 프로젝트 구조

```text
apps/
  api/
    app/              # 인증, 설정, 데이터베이스, 관리 API
    alembic/          # 스키마 migration
    tests/            # API 테스트
  web/
    src/
      app/            # 라우터 구성
      components/     # 공통 UI
      features/       # 기능별 UI와 상태
      lib/            # API 클라이언트와 응답 검증
      pages/          # 페이지 진입점
    e2e/              # Playwright 테스트
scripts/              # 검증 및 컨테이너 실행 명령
docs/                 # 아키텍처와 API 계약
.github/workflows/    # CI 및 수동 AWS 배포 예제
```

## 검증

의존성을 설치한 다음 저장소 루트에서 실행합니다.

```bash
./scripts/check.sh
```

API lint·format·typecheck·pytest와 웹 lint·typecheck·Vitest·프로덕션 빌드를 순서대로 수행합니다. 현재 API 테스트는 DB 연결이 필요 없는 상태 확인과 보안 기본 함수에 집중되어 있습니다. 전체 인증·관리 흐름의 통합 테스트는 기능 확장 시 보강해야 합니다.

Playwright 로그인 화면 smoke test는 실행 중인 앱이 필요하며 별도로 실행합니다.

```bash
cd apps/web
bunx playwright install chromium
E2E_BASE_URL=http://127.0.0.1:8000 bun run e2e
```

CI는 `main` push 및 PR에서 API/웹 검증을 실행하고, 성공하면 `linux/amd64` Docker 이미지를 빌드합니다. Playwright는 현재 CI에 포함되어 있지 않습니다.

## 배포

Docker 이미지는 빌드된 웹과 API를 함께 포함하고 비루트 사용자로 실행됩니다.

```bash
docker build -t workmanagementlog:local .
```

컨테이너 진입점 `appctl`은 다음 명령을 지원합니다.

| 명령 | 동작 |
| --- | --- |
| `serve` | 서버 실행, 기본 명령 |
| `migrate` | Alembic을 최신 revision으로 적용 |
| `bootstrap` | 최초 관리자 생성 |
| `release` | migration, 최신 revision 확인, 관리자 생성 |
| `release-and-serve` | release 처리 후 서버 실행, 로컬 Compose에서 사용 |

운영에서는 배포 단계에서 `release`를 실행하고 앱을 `serve`로 시작할 수 있습니다. `/health`는 DB와 무관한 liveness, `/ready`는 DB 연결을 검사하는 readiness입니다. 기본 Docker healthcheck는 8000 포트의 `/health`를 사용하므로 포트를 변경하면 healthcheck도 조정해야 합니다.

[배포 예제](.github/workflows/deploy-example.yml)는 수동 실행(`workflow_dispatch`)이며 GitHub OIDC → ECR 이미지 업로드 → EC2 SSM 명령 전달 순서입니다. 사용하려면 다음을 준비합니다.

- Repository Variables: `AWS_DEPLOY_ROLE_ARN`, `AWS_REGION`, `ECR_REPOSITORY`, `SERVICE_NAME`
- GitHub `production` environment 및 AWS OIDC 신뢰 정책/권한
- ECR 저장소와 SSM으로 관리되는 EC2 인스턴스의 `Service` 태그
- EC2의 `/opt/app/deploy.sh`: 전달받은 커밋 SHA 이미지 배포, 환경변수 주입, migration 및 상태 확인 구현

예제에는 실제 AWS 리소스나 서버 배포 스크립트가 포함되어 있지 않습니다.

## 기능 확장 규칙

변경 전에 [아키텍처](docs/architecture.md), [API 계약](docs/api-contract.md), [개발 지침](AGENTS.md)을 확인하세요.

1. 새 도메인은 독립 패키지로 구성하고 router·service·schema·model·test·migration을 소유하도록 합니다.
2. 공유 인증·설정·API 클라이언트에 제품별 로직을 추가하지 않습니다.
3. API 계약을 바꾸면 `docs/api-contract.md`를 함께 수정합니다.
4. 스키마 변경에는 Alembic을 사용하며 서버 시작 코드에서 운영 테이블을 생성하지 않습니다.
5. 기존 변경 가능 리소스는 `version`과 따옴표가 있는 `If-Match: "<version>"`을 사용합니다.
6. 기능마다 성공·검증·권한·미존재·동시성 경로를 테스트합니다.
7. `.env` 파일, 인증 토큰, 운영 비밀값을 커밋하거나 Docker 이미지에 포함하지 않습니다.

새 서비스로 재사용할 때는 패키지명, 화면의 서비스명, Docker OCI label도 함께 변경하세요.
