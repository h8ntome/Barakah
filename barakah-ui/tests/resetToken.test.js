import test from "node:test";
import assert from "node:assert/strict";
import { consumeResetToken } from "../src/utils/resetToken.js";
test("emailed reset link token is captured once and removed without changing other URL state", () => {
  const location = {
    href: "https://barakah.example/reset-password?token=private%2Btoken&lang=en#form",
  };
  const state = { navigation: "existing" };
  const calls = [];
  const history = {
    state,
    replaceState(value, title, path) {
      calls.push([value, title, path]);
      location.href = new URL(path, location.href).href;
    },
  };
  assert.equal(consumeResetToken(location, history), "private+token");
  assert.deepEqual(calls, [[state, "", "/reset-password?lang=en#form"]]);
  assert.equal(consumeResetToken(location, history), "");
  assert.equal(calls.length, 1);
});
test("all duplicate and blank token parameters are removed; absent token leaves URL untouched", () => {
  const calls = [];
  const history = { state: null, replaceState: (...args) => calls.push(args) };
  assert.equal(
    consumeResetToken(
      { href: "https://barakah.example/?token=&token=secret" },
      history,
    ),
    "",
  );
  assert.equal(calls[0][2], "/");
  assert.equal(
    consumeResetToken(
      { href: "https://barakah.example/?other=value" },
      history,
    ),
    "",
  );
  assert.equal(calls.length, 1);
});
