"""Unit tests for file classifier module."""

import pytest
from pathlib import Path
from scrubb.file_classifier import FileClassifier, FileCategory


class TestFileClassifier:
    """Test suite for FileClassifier."""
    
    @pytest.fixture
    def classifier(self):
        """Create a FileClassifier instance for testing."""
        return FileClassifier()
    
    def test_classify_image_files(self, classifier):
        """Test classification of image files with various extensions."""
        image_files = [
            "photo.jpg", "image.jpeg", "graphic.png", "animation.gif",
            "bitmap.bmp", "vector.svg", "modern.webp", "icon.ico", "scan.tiff"
        ]
        for filename in image_files:
            assert classifier.classify(Path(filename)) == FileCategory.IMAGE
    
    def test_classify_video_files(self, classifier):
        """Test classification of video files with various extensions."""
        video_files = [
            "movie.mp4", "clip.avi", "video.mov", "film.mkv",
            "stream.flv", "windows.wmv", "web.webm", "mobile.m4v", "old.mpeg"
        ]
        for filename in video_files:
            assert classifier.classify(Path(filename)) == FileCategory.VIDEO
    
    def test_classify_markdown_files(self, classifier):
        """Test classification of markdown files."""
        markdown_files = ["README.md", "notes.markdown"]
        for filename in markdown_files:
            assert classifier.classify(Path(filename)) == FileCategory.MARKDOWN
    
    def test_classify_document_files(self, classifier):
        """Test classification of document files with various extensions."""
        document_files = [
            "report.pdf", "letter.doc", "document.docx", "notes.txt",
            "formatted.rtf", "open.odt", "spreadsheet.xls", "data.xlsx",
            "presentation.ppt", "slides.pptx", "data.csv"
        ]
        for filename in document_files:
            assert classifier.classify(Path(filename)) == FileCategory.DOCUMENT
    
    def test_classify_development_files(self, classifier):
        """Test classification of code/development files."""
        dev_files = [
            "script.py", "app.js", "component.ts", "Main.java",
            "program.c", "code.cpp", "header.h", "lib.rs", "server.go",
            "script.rb", "web.php", "page.html", "style.css",
            "config.json", "data.xml", "settings.yaml", "config.yml",
            "pyproject.toml", "script.sh", "run.bash"
        ]
        for filename in dev_files:
            assert classifier.classify(Path(filename)) == FileCategory.DEVELOPMENT
    
    def test_classify_file_without_extension(self, classifier):
        """Test handling of files with no extension."""
        no_extension_files = ["README", "Makefile", "LICENSE"]
        for filename in no_extension_files:
            assert classifier.classify(Path(filename)) == FileCategory.OTHER
    
    def test_classify_unrecognized_extension(self, classifier):
        """Test handling of files with unrecognized extensions."""
        unknown_files = ["file.xyz", "data.unknown", "archive.rar"]
        for filename in unknown_files:
            assert classifier.classify(Path(filename)) == FileCategory.OTHER
    
    def test_case_insensitive_matching(self, classifier):
        """Test that extension matching is case-insensitive."""
        # Test uppercase extensions
        assert classifier.classify(Path("photo.JPG")) == FileCategory.IMAGE
        assert classifier.classify(Path("video.MP4")) == FileCategory.VIDEO
        assert classifier.classify(Path("README.MD")) == FileCategory.MARKDOWN
        assert classifier.classify(Path("document.PDF")) == FileCategory.DOCUMENT
        assert classifier.classify(Path("script.PY")) == FileCategory.DEVELOPMENT
        
        # Test mixed case extensions
        assert classifier.classify(Path("image.JpG")) == FileCategory.IMAGE
        assert classifier.classify(Path("clip.MoV")) == FileCategory.VIDEO
        assert classifier.classify(Path("notes.Markdown")) == FileCategory.MARKDOWN
