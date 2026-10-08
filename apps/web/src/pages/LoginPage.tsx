import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "@tanstack/react-router";
import { LoginForm } from "../features/auth/LoginForm";
import { sessionQueryKey } from "../features/auth/RequireSession";
import { login } from "../lib/api";

export function LoginPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const mutation = useMutation({
    mutationFn: ({ email, password }: { email: string; password: string }) =>
      login(email, password),
    onSuccess: async (session) => {
      queryClient.setQueryData(sessionQueryKey, session);
      await navigate({
        to: session.user.mustChangePassword ? "/change-password" : "/",
        replace: true,
      });
    },
  });

  return (
    <main className="auth-page">
      <section className="auth-card">
        <p className="eyebrow">Internal Service</p>
        <h1>Company Web</h1>
        <p>관리자가 발급한 계정으로 로그인하세요.</p>
        <LoginForm
          busy={mutation.isPending}
          error={
            mutation.isError ? "이메일 또는 비밀번호를 확인해 주세요." : null
          }
          onSubmit={(email, password) => mutation.mutate({ email, password })}
        />
      </section>
    </main>
  );
}
