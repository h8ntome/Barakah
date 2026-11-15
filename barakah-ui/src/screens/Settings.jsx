import { useState } from "react";
import AIModelSettings from "../components/AIModelSettings.jsx";
import { CurrencyField } from "../components/FinancialForms.jsx";
import { ActionForm, Field } from "../components/forms.jsx";
import { Notice, SectionHeader } from "../components/ui.jsx";
import {
  updateProfile,
  changePassword,
  deleteUser,
  logout,
  resetDemo,
} from "../services/index.js";
export default function Settings({ user, active }) {
  const [preferences, setPreferences] = useState({
    country: user.country || "",
    timezone: user.timezone || "UTC",
    language: user.language || "en",
    currency: user.currency || "USD",
  });
  const [name, setName] = useState(user.display_name);
  const [password, setPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [deletePassword, setDeletePassword] = useState("");
  const [confirmed, setConfirmed] = useState(false);
  return (
    <section>
      <SectionHeader title="Your settings" />
      <p className="section-description">{user.email}</p>
      <AIModelSettings user={user} active={active} />
      <SectionHeader title="Profile and preferences" />
      <ActionForm
        label="Save settings"
        onSubmit={() =>
          updateProfile({
            display_name: name,
            ...preferences,
          })
        }
      >
        <Field
          label="Display name"
          value={name}
          onChange={setName}
          required
          maxLength={80}
        />
        <Field
          label="Country code"
          value={preferences.country}
          onChange={(country) =>
            setPreferences({ ...preferences, country: country.toUpperCase() })
          }
          pattern="[A-Z]{2}"
          required
          maxLength={2}
          help="Two-letter country code, such as PK or US."
        />
        <Field
          label="Time zone"
          value={preferences.timezone}
          onChange={(timezone) => setPreferences({ ...preferences, timezone })}
          required
          maxLength={64}
          help="IANA time zone, such as Asia/Karachi or Europe/London."
        />
        <Field
          label="Preferred language"
          value={preferences.language}
          onChange={(language) => setPreferences({ ...preferences, language })}
          required
          pattern="[a-z]{2,3}(-[A-Z]{2})?"
          help="Preference only; this interface is currently in English."
        />
        <CurrencyField
          label="Preferred currency"
          value={preferences.currency}
          onChange={(currency) => setPreferences({ ...preferences, currency })}
        />
        <p className="formula-note">
          Preferences do not convert financial records. Record dates remain
          exactly as entered.
        </p>
      </ActionForm>
      {user.is_demo && <>
        <Notice>Private demo · fictional data only. Expires after 24 hours. Reset replaces only this demo workspace and its changes.</Notice>
        <ActionForm label="Reset demo data" success="" onSubmit={resetDemo} />
      </>}
      <ActionForm label="Sign out" success="" onSubmit={logout} />
      {!user.is_demo && <><details className="details-section">
        <summary>Change password</summary>
        <ActionForm
          label="Change password and sign out"
          success=""
          onSubmit={() =>
            changePassword({
              current_password: password,
              new_password: newPassword,
            })
          }
        >
          <Field
            label="Current password"
            type="password"
            value={password}
            onChange={setPassword}
            required
            autoComplete="current-password"
          />
          <Field
            label="New password"
            type="password"
            value={newPassword}
            onChange={setNewPassword}
            required
            minLength={12}
            maxLength={128}
            autoComplete="new-password"
          />
        </ActionForm>
      </details>
      <details className="details-section">
        <summary>Delete account and personal data</summary>
        <Notice>
          This permanently deletes your account and its records, including
          conversations. This cannot be undone.
        </Notice>
        <ActionForm
          label="Permanently delete account"
          success=""
          onSubmit={async () => {
            if (!confirmed)
              throw new Error(
                "Confirm that you want to permanently delete your account.",
              );
            await deleteUser({ password: deletePassword });
          }}
        >
          <Field
            label="Password to confirm deletion"
            type="password"
            value={deletePassword}
            onChange={setDeletePassword}
            required
            autoComplete="current-password"
          />
          <label className="check-field">
            <input
              type="checkbox"
              checked={confirmed}
              onChange={(event) => setConfirmed(event.target.checked)}
              required
            />
            <span>I understand that all my records will be deleted.</span>
          </label>
        </ActionForm>
      </details></>}
    </section>
  );
}
