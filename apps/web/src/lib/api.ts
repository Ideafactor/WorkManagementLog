import ky, { HTTPError } from "ky";
import { sessionSchema, userListSchema, userSchema } from "./contracts";

const client = ky.create({
  prefixUrl: "/api/v1",
  credentials: "include",
  retry: 0,
});

function cookie(name: string): string | undefined {
  const prefix = `${encodeURIComponent(name)}=`;
  return document.cookie
    .split(";")
    .map((part) => part.trim())
    .find((part) => part.startsWith(prefix))
    ?.slice(prefix.length);
}

function mutationHeaders(extra?: HeadersInit): Headers {
  const headers = new Headers(extra);
  const csrfToken = cookie("app_csrf");
  if (csrfToken) headers.set("X-CSRF-Token", decodeURIComponent(csrfToken));
  return headers;
}

export { HTTPError };

export async function getSession() {
  return sessionSchema.parse(await client.get("auth/me").json());
}

export async function login(email: string, password: string) {
  return sessionSchema.parse(
    await client.post("auth/login", { json: { email, password } }).json(),
  );
}

export async function logout(): Promise<void> {
  await client.post("auth/logout", { headers: mutationHeaders() });
}

export async function changePassword(
  currentPassword: string,
  newPassword: string,
) {
  return userSchema.parse(
    await client
      .post("auth/password", {
        headers: mutationHeaders(),
        json: { currentPassword, newPassword },
      })
      .json(),
  );
}

export async function listUsers() {
  return userListSchema.parse(await client.get("admin/users").json());
}

export async function createUser(input: {
  email: string;
  name: string;
  initialPassword: string;
  role: "MEMBER" | "ADMIN";
}) {
  return userSchema.parse(
    await client
      .post("admin/users", { headers: mutationHeaders(), json: input })
      .json(),
  );
}
