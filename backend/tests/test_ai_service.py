"""Tests for ai_service: JSON extraction logic."""

import json
import pytest

from ai_service import _extract_json


class TestExtractJson:
    def test_clean_json(self):
        data = {"ats_score": 85, "summary": "Good resume"}
        result = _extract_json(json.dumps(data))
        assert result == data

    def test_markdown_fenced_json(self):
        raw = '```json\n{"ats_score": 75}\n```'
        result = _extract_json(raw)
        assert result == {"ats_score": 75}

    def test_markdown_fenced_no_language(self):
        raw = '```\n{"score": 90}\n```'
        result = _extract_json(raw)
        assert result == {"score": 90}

    def test_json_with_surrounding_text(self):
        raw = 'Here is the analysis:\n{"ats_score": 60}\nEnd of analysis.'
        result = _extract_json(raw)
        assert result is not None
        assert result["ats_score"] == 60

    def test_nested_json(self):
        data = {
            "ats_score": 80,
            "skill_categories": [
                {"category": "Python", "score": 90}
            ]
        }
        result = _extract_json(json.dumps(data))
        assert result == data

    def test_empty_string_returns_none(self):
        assert _extract_json("") is None

    def test_invalid_json_returns_none(self):
        assert _extract_json("this is not json at all") is None

    def test_partial_json_returns_none(self):
        assert _extract_json('{"incomplete": ') is None

    def test_json_with_whitespace(self):
        raw = '  \n  {"key": "value"}  \n  '
        result = _extract_json(raw)
        assert result == {"key": "value"}

    def test_json_array_parsed(self):
        # json.loads handles arrays too — _extract_json passes them through
        raw = '[1, 2, 3]'
        result = _extract_json(raw)
        assert result == [1, 2, 3]

    def test_multiple_json_objects_greedy(self):
        # Greedy regex matches from first { to last } which is invalid JSON
        raw = '{"first": 1} {"second": 2}'
        result = _extract_json(raw)
        # The merged span is invalid JSON, so extraction fails
        assert result is None

    def test_json_with_special_characters(self):
        data = {"summary": "Use C++ & Java <8> for 'best' results"}
        result = _extract_json(json.dumps(data))
        assert result["summary"] == "Use C++ & Java <8> for 'best' results"
