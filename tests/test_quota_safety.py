import asyncio
import os
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

os.environ.setdefault("GOOGLE_API_KEY", "test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-at-least-thirty-two-characters")

from fastapi import HTTPException
from starlette.requests import Request

from app.api.client_ip import client_ip
from app.api.routes import auth
from app.schema.schemas import LoginRequest
from app.services import quota_service as quotas


def request(peer="203.0.113.1", forwarded=""):
    return Request(
        {
            "type": "http",
            "client": (peer, 123),
            "headers": [(b"x-forwarded-for", forwarded.encode())],
        }
    )


class QuotaSafetyTests(unittest.TestCase):
    def test_exhausted_login_does_not_verify_password(self):
        with (
            patch.object(quotas, "reserve", side_effect=HTTPException(429)),
            patch.object(auth.user_service, "find_by_email") as lookup,
            patch.object(auth.auth_service, "verify_password") as verify,
        ):
            with self.assertRaises(HTTPException):
                auth.login(
                    LoginRequest(email="a@example.com", password="correct"),
                    request(),
                    Mock(),
                )
            lookup.assert_not_called()
            verify.assert_not_called()

    def test_success_refunds_original_reservation(self):
        reservation = object()
        with (
            patch.object(quotas, "reserve", return_value=reservation),
            patch.object(quotas, "refund") as refund,
            patch.object(
                auth.user_service,
                "find_by_email",
                return_value=SimpleNamespace(user_id=1, password_hash="x"),
            ),
            patch.object(auth.auth_service, "verify_password", return_value=True),
        ):
            auth.login(
                LoginRequest(email="a@example.com", password="correct"),
                request(),
                Mock(),
            )
            refund.assert_called_once_with(reservation)

    def test_composite_identity_is_bounded_and_unambiguous(self):
        email = "a" * 64 + "@" + "b" * 63 + "." + "c" * 63 + "." + "d" * 57 + ".com"
        validated = LoginRequest(email=email, password="x")
        self.assertEqual(len(quotas.identity_key(validated.email, "2001:db8::1")), 64)
        self.assertNotEqual(
            quotas.identity_key("a:b", "c"), quotas.identity_key("a", "b:c")
        )

    def test_proxy_chain_ignores_forged_leftmost_address(self):
        with patch(
            "app.api.client_ip.get_settings",
            return_value=SimpleNamespace(trusted_proxy_cidrs="10.0.0.0/8"),
        ):
            self.assertEqual(
                client_ip(request("10.0.0.1", "192.0.2.99, 203.0.113.1")), "203.0.113.1"
            )
            self.assertEqual(
                client_ip(request("203.0.113.2", "192.0.2.99")), "203.0.113.2"
            )
            with self.assertRaises(HTTPException):
                client_ip(request("10.0.0.1"))

    def test_database_failure_is_closed(self):
        from sqlalchemy.exc import OperationalError

        with patch(
            "app.services.quota_service.database.reserve_quota",
            side_effect=OperationalError("test", {}, Exception()),
        ):
            with self.assertRaises(HTTPException) as error:
                quotas.reserve(quotas.Budget("user", "1", "chat", 1, 60))
            self.assertEqual(error.exception.status_code, 503)

    def test_slow_quota_does_not_block_event_loop(self):
        import threading

        entered, release = threading.Event(), threading.Event()

        def slow(_):
            entered.set()
            release.wait(2)

        async def run():
            with patch.object(quotas, "reserve", side_effect=slow):
                task = asyncio.create_task(quotas.reserve_async(None))
                try:
                    for _ in range(100):
                        if entered.is_set():
                            break
                        await asyncio.sleep(0.01)
                    self.assertTrue(entered.is_set())
                    self.assertFalse(task.done())
                finally:
                    release.set()
                    await task

        asyncio.run(run())


class GuestChatTests(unittest.TestCase):
    def test_new_guest_token_cannot_reset_source_budget(self):
        from collections import Counter
        from unittest.mock import AsyncMock

        from app.api.dependencies import Actor
        from app.api.routes import chat
        from app.schema.schemas import ChatConfig, ChatRequest

        counts = Counter()

        async def reserve(budget):
            key = (budget.kind, budget.identity)
            counts[key] += 1
            if counts[key] > budget.limit:
                raise HTTPException(429)

        async def run():
            with (
                patch.object(chat.quota_service, "reserve_async", side_effect=reserve),
                patch.object(
                    chat, "ai_service", new_callable=AsyncMock, return_value="hello"
                ) as model,
                patch.object(
                    chat,
                    "settings",
                    SimpleNamespace(
                        guest_source_limit=2,
                        chat_guest_limit=10,
                        chat_window_seconds=60,
                    ),
                ),
            ):
                message = ChatRequest(message="Hello", config=ChatConfig())
                for token in ("one", "two"):
                    await chat.chat(message, request(), Actor("guest", token))
                with self.assertRaises(HTTPException) as error:
                    await chat.chat(message, request(), Actor("guest", "three"))
                self.assertEqual(error.exception.status_code, 429)
                self.assertEqual(model.await_count, 2)

        asyncio.run(run())

    def test_quota_outage_never_calls_model(self):
        from unittest.mock import AsyncMock

        from app.api.dependencies import Actor
        from app.api.routes import chat
        from app.schema.schemas import ChatConfig, ChatRequest

        async def run():
            with (
                patch.object(
                    chat.quota_service, "reserve_async", side_effect=HTTPException(503)
                ),
                patch.object(chat, "ai_service", new_callable=AsyncMock) as model,
            ):
                with self.assertRaises(HTTPException) as error:
                    await chat.chat(
                        ChatRequest(message="Hello", config=ChatConfig()),
                        request(),
                        Actor("user", "1"),
                    )
                self.assertEqual(error.exception.status_code, 503)
                model.assert_not_called()

        asyncio.run(run())
