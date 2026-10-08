import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "@tanstack/react-router";
import type { FormEvent } from "react";
import { useState } from "react";
import { sessionQueryKey } from "../features/auth/RequireSession";
import { changePassword } from "../lib/api";

export function ChangePasswordPage() {
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const mutation = useMutation({
    mutationFn: () => changePassword(currentPassword, newPassword),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: sessionQueryKey });
      await navigate({ to: "/", replace: true });
    },
  });

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    mutation.mutate();
  }

  return (
    <main className="auth-page">
      <section className="auth-card">
        <p className="eyebrow">Security</p>
        <h1>비밀번호 변경</h1>
        <form className="auth-form" onSubmit={submit}>
          <label>
            현재 비밀번호
            <input
              type="password"
              autoComplete="current-password"
              required
              value={currentPassword}
              onChange={(event) => setCurrentPassword(event.target.value)}
            />
          </label>
          <label>
            새 비밀번호
            <input
              type="password"
              autoComplete="new-password"
              required
              minLength={12}
              value={newPassword}
              onChange={(event) => setNewPassword(event.target.value)}
            />
          </label>
          {mutation.isError ? (
            <p className="error" role="alert">
              변경하지 못했습니다.
            </p>
          ) : null}
          <button type="submit" disabled={mutation.isPending}>
            비밀번호 변경
          </button>
        </form>
      </section>
    </main>
  );
}
