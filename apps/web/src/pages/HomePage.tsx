export function HomePage() {
  return (
    <section>
      <p className="eyebrow">Starter dashboard</p>
      <h1>새 서비스의 핵심 기능을 시작하세요.</h1>
      <div className="card-grid">
        <article className="card">
          <h2>인증 기반</h2>
          <p>
            7일 절대 세션, CSRF 검증, Argon2id 비밀번호 처리가 준비되어
            있습니다.
          </p>
        </article>
        <article className="card">
          <h2>API 기반</h2>
          <p>
            FastAPI, SQLAlchemy async, Alembic과 공통 오류 형식을 사용합니다.
          </p>
        </article>
        <article className="card">
          <h2>배포 기반</h2>
          <p>
            같은 origin의 SPA/API 이미지와 health/readiness 경계를 제공합니다.
          </p>
        </article>
      </div>
    </section>
  );
}
