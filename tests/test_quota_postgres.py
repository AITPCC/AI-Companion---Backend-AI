"""Integration checks against a disposable PostgreSQL database, isolated by schema."""

import os
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from uuid import uuid4

os.environ.setdefault("GOOGLE_API_KEY", "test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-at-least-thirty-two-characters")

from sqlalchemy import text
from sqlmodel import Session, create_engine, select

from app.db.database import reserve_quota
from app.jobs.cleanup_quotas import cleanup_batch
from app.models.quota import Quota
from app.services import quota_service as quotas


@unittest.skipUnless(
    os.environ.get("QUOTA_TEST_DATABASE_URL"), "Needs disposable PostgreSQL"
)
class PostgresQuotaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.admin = create_engine(os.environ["QUOTA_TEST_DATABASE_URL"])
        cls.schema = "quota_test_" + uuid4().hex
        with cls.admin.begin() as connection:
            connection.execute(text(f'CREATE SCHEMA "{cls.schema}"'))
        cls.engine = create_engine(
            os.environ["QUOTA_TEST_DATABASE_URL"],
            connect_args={
                "options": f"-c search_path={cls.schema} -c statement_timeout=5000"
            },
        )
        Quota.__table__.create(cls.engine)

    @classmethod
    def tearDownClass(cls):
        cls.engine.dispose()
        with cls.admin.begin() as connection:
            connection.execute(text(f'DROP SCHEMA "{cls.schema}" CASCADE'))
        cls.admin.dispose()

    def setUp(self):
        with self.engine.begin() as connection:
            connection.execute(text("TRUNCATE quotas"))
        self.window = datetime(2026, 9, 12, tzinfo=timezone.utc)

    def reserve(self, identity="same", window=None, zone="UTC"):
        with Session(self.engine) as session:
            session.execute(
                text("SELECT set_config('TimeZone', :zone, true)"), {"zone": zone}
            )
            return reserve_quota(
                session, "user", identity, "chat", window or self.window, 5
            )

    def test_parallel_requests_admit_exactly_limit(self):
        with ThreadPoolExecutor(max_workers=12) as executor:
            admitted = list(executor.map(lambda _: self.reserve(), range(40)))
        self.assertEqual(sum(admitted), 5)
        with Session(self.engine) as session:
            self.assertEqual(session.exec(select(Quota)).one().request_count, 5)

    def test_time_zones_share_counter_and_new_window_resets(self):
        for _ in range(3):
            self.assertTrue(self.reserve(zone="UTC"))
        for _ in range(2):
            self.assertTrue(self.reserve(zone="Asia/Singapore"))
        self.assertFalse(self.reserve(zone="America/New_York"))
        self.assertTrue(self.reserve(window=self.window + timedelta(days=1)))

    def test_cleanup_preserves_active_windows(self):
        self.reserve("old", self.window - timedelta(days=3))
        self.reserve("active", self.window)
        with Session(self.engine) as session:
            self.assertEqual(cleanup_batch(session, self.window - timedelta(days=2)), 1)
            self.assertEqual(session.exec(select(Quota)).one().actor_id, "active")

    def test_refund_targets_original_window(self):
        budget = quotas.Budget("user", "same", "chat", 5, 86400)
        self.reserve()
        self.reserve(window=self.window + timedelta(days=1))
        with patch.object(quotas, "engine", self.engine):
            quotas.refund(quotas.Reservation(budget, self.window))
        with Session(self.engine) as session:
            rows = session.exec(select(Quota).order_by(Quota.window_start)).all()
            self.assertEqual([row.request_count for row in rows], [0, 1])
