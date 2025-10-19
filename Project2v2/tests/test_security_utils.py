import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from security_utils import (  # noqa: E402
    ValidationError,
    escape_html,
    sanitize_prompt,
    validate_repo_url,
)


class SecurityUtilsTestCase(unittest.TestCase):
    def test_validate_repo_url_allows_standard_repo(self):
        url = "https://github.com/openai/gpt"
        self.assertEqual(validate_repo_url(url), url)

    def test_validate_repo_url_normalizes_scheme_and_host(self):
        url = "http://www.github.com/openai/gpt"
        self.assertEqual(validate_repo_url(url), "https://github.com/openai/gpt")

    def test_validate_repo_url_rejects_non_github(self):
        with self.assertRaises(ValidationError):
            validate_repo_url("https://gitlab.com/openai/gpt")

    def test_validate_repo_url_rejects_missing_owner(self):
        with self.assertRaises(ValidationError):
            validate_repo_url("https://github.com/")

    def test_sanitize_prompt_removes_control_chars_and_truncates(self):
        dirty = "hello\x00world\x1fsomething"
        cleaned = sanitize_prompt(dirty, max_length=5)
        self.assertEqual(cleaned, "hello")

    def test_escape_html_encodes_entities(self):
        self.assertEqual(escape_html('<script>'), "&lt;script&gt;")


if __name__ == "__main__":
    unittest.main()
