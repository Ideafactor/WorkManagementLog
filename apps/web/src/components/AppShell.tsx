import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate } from "@tanstack/react-router";
import type { PropsWithChildren } from "react";
import { sessionQueryKey } from "../features/auth/RequireSession";
import { logout } from "../lib/api";
import type { Session } from "../lib/contracts";

export function AppShell({
  session,
  children,
}: PropsWithChildren<{ session: Session }>) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const logoutMutation = useMutation({
    mutationFn: logout,
    onSuccess: async () => {
      queryClient.removeQueries({ queryKey: sessionQueryKey });
      await navigate({ to: "/login", replace: true });
    },
  });

  return (
    <div className="app-shell">
      <aside className="side-nav">
        <Link className="brand" to="/">
          Company Web
        </Link>
        <nav aria-label="주 메뉴">
          <Link to="/">홈</Link>
          {session.user.role === "ADMIN" ? (
            <Link to="/admin">계정 관리</Link>
          ) : null}
        </nav>
        <div className="account">
          <strong>{session.user.name}</strong>
          <span>{session.user.role}</span>
          <button type="button" onClick={() => logoutMutation.mutate()}>
            로그아웃
          </button>
        </div>
      </aside>
      <main className="content">{children}</main>
    </div>
  );
}
