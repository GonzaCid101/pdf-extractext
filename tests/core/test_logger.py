"""Tests para la configuración de logging."""

import logging
from datetime import datetime, timezone

from app.core.logger import BuenosAiresFormatter


class TestBuenosAiresFormatter:
    def test_format_time_uses_buenos_aires_timezone(self):
        created = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc).timestamp()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname=__file__,
            lineno=1,
            msg="mensaje",
            args=(),
            exc_info=None,
        )
        record.created = created

        formatted = BuenosAiresFormatter().formatTime(record)

        assert formatted == "2026-01-15 09:00:00"
