"""Headless Streamlit UI smoke test.

Run:
    python scripts/ui_smoke_test.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

EXPECTED_TABS = [
    "💬 Chat",
    "📚 RAG",
    "📖 Open Wiki",
    "🤖 Agent",
    "🎯 Fine-Tune",
    "📖 Concepts",
]


def _assert_no_uncaught_exceptions(app: AppTest) -> None:
    exceptions = [str(item.value) for item in app.exception]
    assert not exceptions, f"Streamlit raised exceptions: {exceptions}"


def main() -> int:
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=120)
    app.run()
    _assert_no_uncaught_exceptions(app)

    # AppTest flattens nested Fine-Tune tabs into this collection, so verify
    # that the six top-level labels appear in the expected order.
    labels = [tab.label for tab in app.tabs]
    expected_positions = [labels.index(label) for label in EXPECTED_TABS]
    assert expected_positions == sorted(expected_positions), f"Unexpected tabs: {labels}"

    app.text_input(key="wiki_q").set_value("What is Open Wiki vs RAG?")
    app.button(key="wiki_btn").click()
    app.run()
    _assert_no_uncaught_exceptions(app)

    assert any("Matched Wiki Pages" in item.value for item in app.subheader)

    medical_app = AppTest.from_file(
        str(ROOT / "medical_assistant" / "app.py"),
        default_timeout=120,
    ).run()
    _assert_no_uncaught_exceptions(medical_app)

    fine_tuning_app = AppTest.from_file(
        str(ROOT / "fine_tuning" / "app.py"),
        default_timeout=120,
    ).run()
    _assert_no_uncaught_exceptions(fine_tuning_app)

    print(
        "UI smoke test passed: main Wiki query plus medical and fine-tuning "
        "application startup."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
