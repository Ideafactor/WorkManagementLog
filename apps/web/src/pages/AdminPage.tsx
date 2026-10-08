import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { FormEvent } from "react";
import { useState } from "react";
import { createUser, listUsers } from "../lib/api";

const usersQueryKey = ["admin", "users"] as const;

export function AdminPage() {
  const queryClient = useQueryClient();
  const users = useQuery({ queryKey: usersQueryKey, queryFn: listUsers });
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<"MEMBER" | "ADMIN">("MEMBER");
  const mutation = useMutation({
    mutationFn: createUser,
    onSuccess: async () => {
      setName("");
      setEmail("");
      setPassword("");
      setRole("MEMBER");
      await queryClient.invalidateQueries({ queryKey: usersQueryKey });
    },
  });

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    mutation.mutate({
      name: name.trim(),
      email: email.trim(),
      initialPassword: password,
      role,
    });
  }

  return (
    <section>
      <p className="eyebrow">Administration</p>
      <h1>계정 관리</h1>
      <div className="admin-layout">
        <article className="card">
          <h2>새 계정</h2>
          <form className="auth-form" onSubmit={submit}>
            <label>
              이름
              <input
                required
                value={name}
                onChange={(event) => setName(event.target.value)}
              />
            </label>
            <label>
              이메일
              <input
                required
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
              />
            </label>
            <label>
              초기 비밀번호
              <input
                required
                minLength={12}
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
              />
            </label>
            <label>
              역할
              <select
                value={role}
                onChange={(event) => setRole(event.target.value as typeof role)}
              >
                <option value="MEMBER">직원</option>
                <option value="ADMIN">관리자</option>
              </select>
            </label>
            {mutation.isError ? (
              <p className="error" role="alert">
                계정을 만들지 못했습니다.
              </p>
            ) : null}
            <button type="submit" disabled={mutation.isPending}>
              계정 생성
            </button>
          </form>
        </article>
        <article className="card">
          <h2>등록 계정</h2>
          {users.isPending ? <p>불러오는 중…</p> : null}
          {users.isError ? (
            <p className="error">계정을 불러오지 못했습니다.</p>
          ) : null}
          {users.data ? (
            <ul className="user-list">
              {users.data.map((user) => (
                <li key={user.id}>
                  <span>
                    <strong>{user.name}</strong>
                    <br />
                    {user.email}
                  </span>
                  <span className="badge">{user.role}</span>
                </li>
              ))}
            </ul>
          ) : null}
        </article>
      </div>
    </section>
  );
}
