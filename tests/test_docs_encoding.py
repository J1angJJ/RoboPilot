from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CHINESE_MARKDOWN_PATHS = [
    REPO_ROOT / "README.zh-CN.md",
    *sorted((REPO_ROOT / "docs" / "zh-CN").glob("**/*.md")),
]


def test_chinese_markdown_decodes_as_utf8_without_bom() -> None:
    assert CHINESE_MARKDOWN_PATHS

    for path in CHINESE_MARKDOWN_PATHS:
        data = path.read_bytes()
        assert data, f"{path} should not be empty"
        assert not data.startswith(b"\xef\xbb\xbf"), f"{path} must be UTF-8 without BOM"
        text = data.decode("utf-8")
        assert "\ufffd" not in text, f"{path} contains Unicode replacement characters"
