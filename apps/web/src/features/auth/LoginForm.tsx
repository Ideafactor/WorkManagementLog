import type { FormEvent } from "react";
import { useState } from "react";

interface LoginFormProps {
  busy: boolean;
  error: string | null;
  onSubmit: (email: string, password: string) => void;
}

export function LoginForm({ busy, error, onSubmit }: LoginFormProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSubmit(email.trim(), password);
  }

  return (
    <form className="auth-form" onSubmit={submit}>
      <label>
        이메일
        <input
          autoComplete="username"
          type="email"
          required
          value={email}
          onChange={(event) => setEmail(event.target.value)}
        />
      </label>
      <label>
        비밀번호
        <input
          autoComplete="current-password"
          type="password"
          required
          value={password}
          onChange={(event) => setPassword(event.target.value)}
        />
      </label>
      {error ? (
        <p className="error" role="alert">
          {error}
        </p>
      ) : null}
      <button type="submit" disabled={busy}>
        {busy ? "로그인 중…" : "로그인"}
      </button>
    </form>
  );
}
