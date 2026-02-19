"""
Tests for HonzikPersonality - prompt caching and generation.
"""

import pytest

from backend.services.honzik_personality import HonzikPersonality


class TestHonzikPromptGeneration:
    """Test prompt generation and caching."""

    def test_base_prompt_returns_string(self):
        """_get_base_prompt should return a non-empty string."""
        prompt = HonzikPersonality._get_base_prompt(
            level="beginner",
            corrections_level="balanced",
            native_language="ru",
            style="friendly",
        )
        assert isinstance(prompt, str)
        assert len(prompt) > 100  # Should be a substantial prompt

    def test_base_prompt_cached(self):
        """Same params should return same cached object (lru_cache)."""
        p1 = HonzikPersonality._get_base_prompt(
            level="intermediate",
            corrections_level="minimal",
            native_language="uk",
            style="tutor",
        )
        p2 = HonzikPersonality._get_base_prompt(
            level="intermediate",
            corrections_level="minimal",
            native_language="uk",
            style="tutor",
        )
        # lru_cache returns the exact same object
        assert p1 is p2

    def test_base_prompt_different_for_different_params(self):
        """Different params should produce different prompts."""
        p_beginner = HonzikPersonality._get_base_prompt(
            level="beginner",
            corrections_level="balanced",
            native_language="ru",
            style="friendly",
        )
        p_advanced = HonzikPersonality._get_base_prompt(
            level="advanced",
            corrections_level="detailed",
            native_language="ru",
            style="tutor",
        )
        assert p_beginner != p_advanced

    def test_base_prompt_contains_czech_context(self):
        """Prompt should mention Czech learning."""
        prompt = HonzikPersonality._get_base_prompt(
            level="beginner",
            corrections_level="balanced",
            native_language="ru",
            style="casual",
        )
        # Should contain Czech-related content
        assert any(
            word in prompt.lower()
            for word in ["česk", "čech", "czech", "honzík", "jazyk"]
        )

    def test_all_levels_produce_prompts(self):
        """All 4 levels should produce valid prompts."""
        for level in ("beginner", "intermediate", "advanced", "native"):
            prompt = HonzikPersonality._get_base_prompt(
                level=level,
                corrections_level="balanced",
                native_language="ru",
                style="friendly",
            )
            assert isinstance(prompt, str) and len(prompt) > 50, f"Failed for {level}"
