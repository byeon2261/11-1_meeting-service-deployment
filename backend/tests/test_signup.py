"""실제 SDK의 오류 응답 처리와 공개 API의 정보 노출을 검증한다."""

import unittest

import httpx

from app.auth import SupabaseAuth
from app.main import create_app


class SignupTests(unittest.IsolatedAsyncioTestCase):
    async def signup_response(self, provider_status, provider_code):
        def provider(request):
            self.assertEqual(request.url.path, "/auth/v1/signup")
            return httpx.Response(provider_status, headers={"X-Supabase-Api-Version": "2024-01-01"}, json={
                "code": provider_code, "msg": "private-provider-detail",
                "weak_password": {"reasons": ["length"]}})

        async with httpx.AsyncClient(transport=httpx.MockTransport(provider)) as provider_http:
            auth = SupabaseAuth("https://project.supabase.co", "sb_publishable_test", http_client=provider_http)
            app = create_app(object(), object(), auth)
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url="http://test") as client:
                return await client.post("/api/auth/signup", json={
                    "email": "test@example.com", "password": "private-test-password"})

    async def test_provider_failures_have_actionable_public_codes(self):
        cases = [
            (400, "email_address_not_authorized", 403, "SIGNUP_EMAIL_NOT_AUTHORIZED"),
            (422, "email_address_invalid", 422, "INVALID_EMAIL"),
            (400, "validation_failed", 422, "INVALID_INPUT"),
            (400, "email_provider_disabled", 403, "SIGNUP_DISABLED"),
            (422, "signup_disabled", 403, "SIGNUP_DISABLED"),
            (429, "over_email_send_rate_limit", 429, "EMAIL_RATE_LIMIT"),
            (400, "captcha_failed", 400, "SIGNUP_VERIFICATION_FAILED"),
            (422, "weak_password", 422, "WEAK_PASSWORD"),
            (400, "email_exists", 409, "SIGNUP_REJECTED"),
            (429, "over_request_rate_limit", 429, "AUTH_RATE_LIMIT"),
            (503, "unexpected_failure", 502, "AUTH_UNAVAILABLE"),
            (400, "unknown_error", 400, "SIGNUP_REJECTED"),
        ]
        for provider_status, provider_code, status, code in cases:
            with self.subTest(provider_code=provider_code):
                response = await self.signup_response(provider_status, provider_code)
                self.assertEqual(response.status_code, status)
                self.assertEqual(response.json()["code"], code)
                self.assertEqual(response.headers["cache-control"], "no-store")
                self.assertIn("request_id", response.json())
                self.assertNotIn("private-provider-detail", response.text)
                self.assertNotIn("private-test-password", response.text)
                self.assertNotIn("test@example.com", response.text)


if __name__ == "__main__":
    unittest.main()
