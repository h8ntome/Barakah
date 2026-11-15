import { useState } from "react";
import { Brand, Notice, SegmentedControl } from "../components/ui.jsx";
import { ActionForm, Field } from "../components/forms.jsx";
import {
  login,
  register,
  requestReset,
  confirmReset,
} from "../services/index.js";
export default function Auth() {
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [token, setToken] = useState("");
  const [notice, setNotice] = useState("");
  return (
    <div className="screen-content auth-screen">
      <Brand />
      <h2>
        {
          {
            login: "Welcome back.",
            register: "Make room for what matters.",
            request: "Reset your password",
            reset: "Choose a new password",
          }[mode]
        }
      </h2>
      <p>
        Your financial records, giving intentions and learning, together in one
        private workspace.
      </p>
      <SegmentedControl
        label="Account access"
        value={mode}
        onChange={(value) => {
          setMode(value);
          setNotice("");
        }}
        options={[
          { id: "login", label: "Existing account" },
          { id: "register", label: "New account" },
        ]}
      />
      <ActionForm
        key={mode}
        label={
          {
            login: "Sign in",
            register: "Create account",
            request: "Request reset",
            reset: "Reset password",
          }[mode]
        }
        success=""
        onSubmit={async () => {
          if (mode === "login") await login({ email, password });
          if (mode === "register")
            await register({ email, password, display_name: displayName });
          if (mode === "request") {
            const result = await requestReset({ email });
            setNotice(result.message);
          }
          if (mode === "reset") {
            await confirmReset({ token, new_password: password });
            setPassword("");
            setMode("login");
            setNotice("Password reset. Sign in with your new password.");
          }
        }}
      >
        {mode === "register" && (
          <Field
            label="Display name"
            value={displayName}
            onChange={setDisplayName}
            required
            maxLength={80}
            autoComplete="name"
          />
        )}
        {mode !== "reset" && (
          <Field
            label="Email address"
            type="email"
            value={email}
            onChange={setEmail}
            required
            autoComplete="email"
          />
        )}
        {mode === "reset" && (
          <Field
            label="Password reset token"
            value={token}
            onChange={setToken}
            required
            minLength={20}
            maxLength={200}
            autoComplete="off"
          />
        )}
        {mode !== "request" && (
          <Field
            label={mode === "login" ? "Password" : "New password"}
            type="password"
            value={password}
            onChange={setPassword}
            required
            minLength={mode === "login" ? 1 : 12}
            maxLength={128}
            autoComplete={
              mode === "login" ? "current-password" : "new-password"
            }
            help={mode !== "login" ? "Use 12–128 characters." : undefined}
          />
        )}
      </ActionForm>
      {notice && (
        <p className="save-status" role="status">
          {notice}
        </p>
      )}
      <div className="record-actions">
        <button
          className="text-button"
          onClick={() => {
            setMode("request");
            setNotice("");
          }}
        >
          Forgot password?
        </button>
        <button
          className="text-button"
          onClick={() => {
            setMode("reset");
            setNotice("");
          }}
        >
          Use reset token
        </button>
      </div>
      {(mode === "request" || mode === "reset") && (
        <Notice>
          Password delivery depends on the server configuration. In local
          development, the operator retrieves tokens from the private outbox; no
          email delivery is implied.
        </Notice>
      )}
      <Notice>
        No bank linking or payment processing. Zakat and investment guidance is
        educational, not a religious ruling.
      </Notice>
    </div>
  );
}
