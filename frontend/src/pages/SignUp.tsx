import { type FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { AuthShell, Field } from "./SignIn";

export function SignUp() {
  const { signUp } = useAuth();
  const nav = useNavigate();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    await signUp(name, email, password);
    setLoading(false);
    nav("/");
  }

  return (
    <AuthShell
      title="Create your account"
      subtitle="A reflective dashboard of your week."
      footer={
        <>
          Already have an account?{" "}
          <Link to="/signin" className="text-primary hover:underline">
            Sign in
          </Link>
        </>
      }
    >
      <form onSubmit={onSubmit} className="flex flex-col gap-4">
        <Field
          label="Name"
          type="text"
          value={name}
          onChange={setName}
          placeholder="Julia"
          required
        />
        <Field
          label="Email"
          type="email"
          value={email}
          onChange={setEmail}
          placeholder="you@example.com"
          required
        />
        <Field
          label="Password"
          type="password"
          value={password}
          onChange={setPassword}
          placeholder="At least 8 characters"
          required
        />
        <button
          type="submit"
          disabled={loading}
          className="mt-2 bg-primary text-white text-sm font-medium rounded-md py-2.5 hover:opacity-90 disabled:opacity-50 transition-opacity"
        >
          {loading ? "Creating account…" : "Create account"}
        </button>
      </form>
    </AuthShell>
  );
}
