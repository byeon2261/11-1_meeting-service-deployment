import assert from "node:assert/strict";
import test from "node:test";
import { AuthRelayError, createAuthRelay } from "./authRelay.js";

test("signup failures explain provider restrictions without exposing provider details", async () => {
  const cases = [
    [403, "SIGNUP_EMAIL_NOT_AUTHORIZED", "인증 메일을 보낼 수 없습니다"],
    [422, "INVALID_EMAIL", "이메일 주소를 입력해주세요"],
    [403, "SIGNUP_DISABLED", "회원가입을 이용할 수 없습니다"],
    [429, "EMAIL_RATE_LIMIT", "인증 메일 발송 한도"],
    [400, "SIGNUP_VERIFICATION_FAILED", "가입 확인 절차"],
    [400, "SIGNUP_REJECTED", "회원가입을 완료하지 못했습니다"],
    [409, "SIGNUP_REJECTED", "이미 가입한 이메일"],
    [422, "INVALID_INPUT", "입력 형식과 길이"],
    [502, "AUTH_UNAVAILABLE", "인증 서버에 연결하지 못했습니다"],
  ];
  for (const [status, code, message] of cases) {
    const relay = createAuthRelay({ browser: null, fetchImpl: async (url, options) => {
      assert.equal(url, "/api/auth/signup");
      assert.equal(options.method, "POST");
      return { ok: false, status, json: async () => ({ code, detail: "private-provider-detail" }) };
    } });
    await relay.start();
    await assert.rejects(relay.signUp("test@example.com", "password"), (error) => {
      assert.ok(error instanceof AuthRelayError);
      assert.equal(error.status, status);
      assert.equal(error.code, code);
      assert.ok(error.message.includes(message), error.message);
      assert.ok(!error.message.includes("private-provider-detail"));
      return true;
    });
    assert.equal(relay.getSnapshot().session, null);
    relay.stop();
  }
});

test("signup preserves confirmation result and does not establish a session", async () => {
  for (const confirmation of [true, false]) {
    const relay = createAuthRelay({ browser: null, fetchImpl: async () => ({
      ok: true, status: 201, json: async () => ({ user_id: "test-user", email_confirmation_required: confirmation }),
    }) });
    await relay.start();
    assert.deepEqual(await relay.signUp("test@example.com", "password"), { confirmationRequired: confirmation });
    assert.equal(relay.getSnapshot().session, null);
    relay.stop();
  }
});
