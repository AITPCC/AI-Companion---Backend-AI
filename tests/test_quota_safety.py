import os
import unittest
from unittest.mock import AsyncMock, Mock, patch

os.environ.setdefault("GOOGLE_API_KEY", "test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")

from fastapi import HTTPException
from starlette.requests import Request

from app.api.dependencies import Actor
from app.api.routes import auth, chat
from app.schema.schemas import ChatConfig, ChatRequest, LoginRequest
from app.services import quota_service


def make_request(ip: str = "203.0.113.1") -> Request:
    return Request({"type": "http", "client": (ip, 1234), "headers": []})


class QuotaSafetyTests(unittest.IsolatedAsyncioTestCase):
    async def test_exhausted_login_does_not_check_password(self):
        with (
            patch.object(quota_service, "check_and_increment", return_value=False),
            patch.object(auth.user_service, "find_by_email") as find_user,
            patch.object(auth.auth_service, "verify_password") as verify_password,
        ):
            with self.assertRaises(HTTPException) as error:
                await auth.login(
                    LoginRequest(email="user@example.com", password="guess"),
                    make_request(),
                    Mock(),
                )

        self.assertEqual(error.exception.status_code, 429)
        find_user.assert_not_called()
        verify_password.assert_not_called()

    def test_login_key_has_fixed_length(self):
        key = quota_service.hash_key("a" * 254, "2001:db8::1")
        self.assertEqual(len(key), 64)

    async def test_guest_quota_uses_ip_instead_of_token_id(self):
        request = ChatRequest(message="hello", config=ChatConfig())
        session = Mock()

        with (
            patch.object(
                quota_service, "check_and_increment", return_value=True
            ) as check,
            patch.object(chat, "ai_service", new_callable=AsyncMock, return_value="hi"),
        ):
            await chat.chat(
                request, make_request(), session, Actor("guest", "token-one")
            )
            await chat.chat(
                request, make_request(), session, Actor("guest", "token-two")
            )

        self.assertEqual(check.call_args_list[0].args[2], "203.0.113.1")
        self.assertEqual(check.call_args_list[1].args[2], "203.0.113.1")

    def test_limit_is_part_of_atomic_upsert(self):
        session = Mock()
        session.exec.return_value.first.return_value = None

        from app.db.database import upsert_quota_and_increment

        allowed = upsert_quota_and_increment(
            session,
            "user",
            "1",
            "chat",
            quota_service.get_window_start(60),
            5,
        )

        self.assertFalse(allowed)
        session.commit.assert_called_once()


if __name__ == "__main__":
    unittest.main()
