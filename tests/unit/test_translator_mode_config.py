"""Tests for P1.6 — translator_mode config option in Config + _make_translating_collector."""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock, call
from pathlib import Path

from core.utils.config import Config, MeetingConfig, LLMConfig


# ── Config model ──────────────────────────────────────────────────────────


class TestTranslatorModeConfig:
    def test_default_is_final_only(self):
        cfg = Config()
        assert cfg.translator_mode == "final_only"

    def test_accepts_off(self):
        cfg = Config(translator_mode="off")
        assert cfg.translator_mode == "off"

    def test_accepts_all_intermediate(self):
        cfg = Config(translator_mode="all_intermediate")
        assert cfg.translator_mode == "all_intermediate"

    def test_rejects_invalid_value(self):
        with pytest.raises(Exception):
            Config(translator_mode="invalid_value")

    def test_loads_from_dict(self):
        """Config(**yaml_data) works when translator_mode present."""
        data = {"translator_mode": "all_intermediate", "vault_path": "/tmp/vault"}
        cfg = Config(**data)
        assert cfg.translator_mode == "all_intermediate"

    def test_loads_from_dict_missing_field_defaults(self):
        """translator_mode defaults when not in yaml."""
        cfg = Config(**{"vault_path": "/tmp/vault"})
        assert cfg.translator_mode == "final_only"

    def test_other_config_fields_unaffected(self):
        cfg = Config(translator_mode="off")
        assert cfg.meeting.max_debate_rounds == 2
        assert cfg.llm.primary == "claude-sonnet-4-6"


# ── _make_translating_collector ───────────────────────────────────────────


class TestMakeTranslatingCollector:
    """_make_translating_collector wraps collect_fn to translate each perspective."""

    def _make_translator(self, suffix: str = " [translated]") -> MagicMock:
        t = MagicMock()
        t.apply = MagicMock(side_effect=lambda text: text + suffix)
        return t

    def _mock_collect(self, perspectives: dict) -> "Callable":
        def _inner(state):
            return {"perspectives": perspectives}
        return _inner

    def test_translates_each_perspective(self):
        from core.orchestrator.flow_controller import _make_translating_collector

        translator = self._make_translator(" [T]")
        collect_fn = self._mock_collect({"01-dept": "text A", "02-dept": "text B"})
        wrapped = _make_translating_collector(collect_fn, translator)

        result = wrapped(state={})
        assert result["perspectives"]["01-dept"] == "text A [T]"
        assert result["perspectives"]["02-dept"] == "text B [T]"
        assert translator.apply.call_count == 2

    def test_skips_error_placeholders(self):
        from core.orchestrator.flow_controller import _make_translating_collector

        translator = self._make_translator(" [T]")
        collect_fn = self._mock_collect({
            "01-dept": "[ERROR] something went wrong",
            "02-dept": "[Phong 02-dept chua ton tai]",
            "03-dept": "valid text",
        })
        wrapped = _make_translating_collector(collect_fn, translator)
        result = wrapped(state={})

        # Error/placeholder strings passed through unchanged
        assert result["perspectives"]["01-dept"] == "[ERROR] something went wrong"
        assert result["perspectives"]["02-dept"] == "[Phong 02-dept chua ton tai]"
        # Valid text translated
        assert result["perspectives"]["03-dept"] == "valid text [T]"
        assert translator.apply.call_count == 1

    def test_fallback_when_translator_raises(self):
        from core.orchestrator.flow_controller import _make_translating_collector

        translator = MagicMock()
        translator.apply = MagicMock(side_effect=RuntimeError("LLM failed"))
        collect_fn = self._mock_collect({"01-dept": "some text"})
        wrapped = _make_translating_collector(collect_fn, translator)

        # Must NOT raise — fallback to raw text
        result = wrapped(state={})
        assert result["perspectives"]["01-dept"] == "some text"

    def test_empty_perspectives_ok(self):
        from core.orchestrator.flow_controller import _make_translating_collector

        translator = self._make_translator()
        collect_fn = self._mock_collect({})
        wrapped = _make_translating_collector(collect_fn, translator)
        result = wrapped(state={})
        assert result["perspectives"] == {}
        translator.apply.assert_not_called()

    def test_original_collect_fn_called_with_state(self):
        from core.orchestrator.flow_controller import _make_translating_collector

        sentinel_state = {"brief": "check state passed"}
        captured = []

        def _capture(state):
            captured.append(state)
            return {"perspectives": {}}

        translator = self._make_translator()
        wrapped = _make_translating_collector(_capture, translator)
        wrapped(sentinel_state)
        assert captured == [sentinel_state]
