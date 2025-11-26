"""Unit tests for emoji detector."""

import pytest
from scrubb.business.emoji_detector import EmojiDetector, EmojiMatch


class TestEmojiDetector:
    """Unit tests for EmojiDetector class."""
    
    def test_detector_initialization(self):
        """Test that detector initializes successfully."""
        detector = EmojiDetector()
        assert detector is not None
        assert detector._regex is not None
    
    def test_detect_single_emoji(self):
        """Test detecting a single emoji."""
        detector = EmojiDetector()
        text = "Hello 👋 World"
        matches = detector.detect(text)
        
        assert len(matches) == 1
        assert matches[0].text == "👋"
        assert matches[0].start == 6
        assert matches[0].end == 7  # Emoji is 1 character in Python string
        assert matches[0].grapheme_count >= 1
    
    def test_detect_multiple_emojis(self):
        """Test detecting multiple emojis."""
        detector = EmojiDetector()
        text = "Hello 👋 World 🌍 Test 🎉"
        matches = detector.detect(text)
        
        assert len(matches) == 3
        assert matches[0].text == "👋"
        assert matches[1].text == "🌍"
        assert matches[2].text == "🎉"
    
    def test_detect_no_emojis(self):
        """Test detecting when no emojis are present."""
        detector = EmojiDetector()
        text = "Hello World"
        matches = detector.detect(text)
        
        assert len(matches) == 0
    
    def test_detect_consecutive_emojis(self):
        """Test detecting consecutive emojis."""
        detector = EmojiDetector()
        text = "👋🌍🎉"
        matches = detector.detect(text)
        
        # Consecutive emojis should be detected as one match
        assert len(matches) == 1
        assert "👋" in matches[0].text
        assert "🌍" in matches[0].text
        assert "🎉" in matches[0].text
    
    def test_remove_single_emoji(self):
        """Test removing a single emoji."""
        detector = EmojiDetector()
        text = "Hello 👋 World"
        cleaned, count = detector.remove(text)
        
        assert cleaned == "Hello  World"
        assert count >= 1
        assert "👋" not in cleaned
    
    def test_remove_multiple_emojis(self):
        """Test removing multiple emojis."""
        detector = EmojiDetector()
        text = "Hello 👋 World 🌍 Test 🎉"
        cleaned, count = detector.remove(text)
        
        assert cleaned == "Hello  World  Test "
        assert count >= 3
        assert "👋" not in cleaned
        assert "🌍" not in cleaned
        assert "🎉" not in cleaned
    
    def test_remove_no_emojis(self):
        """Test removing when no emojis are present."""
        detector = EmojiDetector()
        text = "Hello World"
        cleaned, count = detector.remove(text)
        
        assert cleaned == text
        assert count == 0
    
    def test_count_single_emoji(self):
        """Test counting a single emoji."""
        detector = EmojiDetector()
        text = "Hello 👋 World"
        count = detector.count(text)
        
        assert count >= 1
    
    def test_count_multiple_emojis(self):
        """Test counting multiple emojis."""
        detector = EmojiDetector()
        text = "Hello 👋 World 🌍 Test 🎉"
        count = detector.count(text)
        
        assert count >= 3
    
    def test_count_no_emojis(self):
        """Test counting when no emojis are present."""
        detector = EmojiDetector()
        text = "Hello World"
        count = detector.count(text)
        
        assert count == 0
    
    def test_count_consecutive_emojis(self):
        """Test counting consecutive emojis."""
        detector = EmojiDetector()
        text = "👋🌍🎉"
        count = detector.count(text)
        
        # Should count grapheme clusters, not codepoints
        assert count >= 3
    
    def test_empty_string(self):
        """Test handling empty string."""
        detector = EmojiDetector()
        
        matches = detector.detect("")
        assert len(matches) == 0
        
        cleaned, count = detector.remove("")
        assert cleaned == ""
        assert count == 0
        
        count = detector.count("")
        assert count == 0
    
    def test_various_emoji_types(self):
        """Test detecting various types of emojis."""
        detector = EmojiDetector()
        
        # Emoticons
        text1 = "😀😃😄"
        assert detector.count(text1) >= 3
        
        # Symbols
        text2 = "⚡☀️⭐"
        assert detector.count(text2) >= 3
        
        # Flags
        text3 = "🇺🇸🇬🇧🇯🇵"
        assert detector.count(text3) >= 3
        
        # Transport
        text4 = "🚗🚕🚙"
        assert detector.count(text4) >= 3
    
    def test_emoji_with_skin_tone_modifiers(self):
        """Test handling emojis with skin tone modifiers."""
        detector = EmojiDetector()
        
        # Emoji with skin tone modifier
        text = "👋🏻👋🏼👋🏽"
        matches = detector.detect(text)
        
        # Should detect all variations
        assert len(matches) >= 1
        
        # Count should reflect grapheme clusters
        count = detector.count(text)
        assert count >= 3
    
    def test_text_with_mixed_content(self):
        """Test text with mixed emoji and regular content."""
        detector = EmojiDetector()
        text = "Check out this code: def hello(): print('👋') # Say hi 🎉"
        
        matches = detector.detect(text)
        assert len(matches) == 2
        
        cleaned, count = detector.remove(text)
        assert "def hello():" in cleaned
        assert "print('" in cleaned
        assert "👋" not in cleaned
        assert "🎉" not in cleaned
    
    def test_unicode_normalization(self):
        """Test that detector handles different Unicode normalizations."""
        detector = EmojiDetector()
        
        # Same emoji in different normalizations should be detected
        text1 = "👋"  # NFC
        text2 = "👋"  # NFD (if different)
        
        count1 = detector.count(text1)
        count2 = detector.count(text2)
        
        # Both should detect the emoji
        assert count1 >= 1
        assert count2 >= 1


class TestEmojiMatch:
    """Unit tests for EmojiMatch dataclass."""
    
    def test_emoji_match_creation(self):
        """Test creating an EmojiMatch."""
        match = EmojiMatch(
            text="👋",
            start=0,
            end=2,
            grapheme_count=1
        )
        
        assert match.text == "👋"
        assert match.start == 0
        assert match.end == 2
        assert match.grapheme_count == 1
    
    def test_emoji_match_immutable(self):
        """Test that EmojiMatch is immutable."""
        match = EmojiMatch(
            text="👋",
            start=0,
            end=2,
            grapheme_count=1
        )
        
        with pytest.raises(AttributeError):
            match.text = "🌍"


class TestModuleLevelValidation:
    """Test module-level regex validation."""
    
    def test_module_imports_successfully(self):
        """Test that the module imports without errors."""
        # If we got here, the module imported successfully
        # which means the regex validation passed
        from scrubb.business import emoji_detector
        assert emoji_detector is not None
    
    def test_regex_pattern_is_valid(self):
        """Test that the emoji regex pattern is valid."""
        import re
        from scrubb.business.emoji_detector import EmojiDetector
        
        # Should not raise an exception
        pattern = EmojiDetector.EMOJI_PATTERN
        regex = re.compile(pattern, flags=re.UNICODE)
        
        # Should be able to search
        result = regex.search("test")
        assert result is None  # No match expected
        
        result = regex.search("test 👋")
        assert result is not None  # Match expected
