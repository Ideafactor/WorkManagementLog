import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "@tanstack/react-router";
import type { PropsWithChildren } from "react";
import { useEffect } from "react";
import { AppShell } from "../../components/AppShell";
import { getSession, HTTPError } from "../../lib/api";

export const sessionQueryKey = ["session"] as const;

export function RequireSession({ children }: PropsWithChildren) {
  const navigate = useNavigate();
  const query = useQuery({
    queryKey: sessionQueryKey,
    queryFn: getSession,
    retry: false,
  });

  useEffect(() => {
    if (
      query.error instanceof HTTPError &&
      query.error.response.status === 401
    ) {
      void navigate({ to: "/login", replace: true });
    }
  }, [navigate, query.error]);

  useEffect(() => {
    if (query.data?.user.mustChangePassword) {
      void navigate({ to: "/change-password", replace: true });
    }
  }, [navigate, query.data]);

  if (query.isPending)
    return (
      <main className="center-card">로그인 상태를 확인하고 있습니다.</main>
    );
  if (query.isError || !query.data) {
    return <main className="center-card">세션을 확인할 수 없습니다.</main>;
  }
  return <AppShell session={query.data}>{children}</AppShell>;
}
