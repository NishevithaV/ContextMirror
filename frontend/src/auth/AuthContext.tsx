import { createContext, useContext, useEffect, useState } from "react";

// Real auth when VITE_API_BASE is set — POSTs to /auth/login + /auth/register,
// stores the JWT in localStorage. Falls back to mock auth (no backend) if
// VITE_API_BASE is empty, so the Vercel demo still works standalone.

export type AuthUser = {
  id: string;
  name: string;
  email: string;
};

type AuthContextValue = {
  user: AuthUser | null;
  token: string | null;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (name: string, email: string, password: string) => Promise<void>;
  signOut: () => void;
};

const USER_KEY = "contextmirror.auth.user";
const TOKEN_KEY = "contextmirror.auth.token";
const API_BASE = import.meta.env.VITE_API_BASE ?? "";

const AuthContext = createContext<AuthContextValue | null>(null);

async function callAuth(
  path: "/auth/login" | "/auth/register",
  body: { email: string; password: string }
): Promise<{ access_token: string; user_id: string; email: string }> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(detail?.detail ?? `HTTP ${res.status}`);
  }
  return res.json();
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(() => {
    try {
      const raw = localStorage.getItem(USER_KEY);
      return raw ? (JSON.parse(raw) as AuthUser) : null;
    } catch {
      return null;
    }
  });
  const [token, setToken] = useState<string | null>(() =>
    localStorage.getItem(TOKEN_KEY)
  );

  useEffect(() => {
    if (user) localStorage.setItem(USER_KEY, JSON.stringify(user));
    else localStorage.removeItem(USER_KEY);
  }, [user]);

  useEffect(() => {
    if (token) localStorage.setItem(TOKEN_KEY, token);
    else localStorage.removeItem(TOKEN_KEY);
  }, [token]);

  async function signIn(email: string, password: string) {
    if (API_BASE) {
      const res = await callAuth("/auth/login", { email, password });
      setToken(res.access_token);
      setUser({
        id: res.user_id,
        email: res.email,
        name: nameFromEmail(res.email),
      });
      return;
    }
    // Mock fallback
    setUser({ id: `user-${email}`, name: nameFromEmail(email), email });
    setToken(null);
  }

  async function signUp(name: string, email: string, password: string) {
    if (API_BASE) {
      const res = await callAuth("/auth/register", { email, password });
      setToken(res.access_token);
      setUser({ id: res.user_id, email: res.email, name });
      return;
    }
    // Mock fallback
    setUser({ id: `user-${email}`, name, email });
    setToken(null);
  }

  function signOut() {
    setUser(null);
    setToken(null);
  }

  return (
    <AuthContext.Provider value={{ user, token, signIn, signUp, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}

function nameFromEmail(email: string): string {
  const local = email.split("@")[0] || "User";
  return local.charAt(0).toUpperCase() + local.slice(1);
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}

// For non-React callers (like api.ts) to read/clear the token directly.
export function getStoredToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}
export function clearStoredAuth(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}
