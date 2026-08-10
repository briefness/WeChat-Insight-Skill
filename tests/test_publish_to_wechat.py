import importlib.util
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch


MODULE_PATH = Path(__file__).parents[1] / "tools" / "publish_to_wechat.py"
SPEC = importlib.util.spec_from_file_location("publish_to_wechat", MODULE_PATH)
publish_to_wechat = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(publish_to_wechat)


class MarkdownToWechatHtmlTests(unittest.TestCase):
    def test_excludes_usage_assumptions_and_summary(self):
        markdown = """# 示例标题

> **使用假设**：项目复盘；目标读者为开发者。
>
> 这段也是使用假设的补充说明。

## 备选标题（3 个）

1. 不应出现在 HTML 中的备选标题

## 摘要

这段摘要不应出现在 HTML 中。

## 正文

这是需要保留的正文。

## 正文里的使用假设讨论

这里正常讨论使用假设，也应该保留。

## 转发文案

这段也不应出现。
"""

        html = publish_to_wechat.md_to_wechat_html(markdown)

        self.assertNotIn("项目复盘", html)
        self.assertNotIn("使用假设的补充说明", html)
        self.assertNotIn("不应出现在 HTML 中的备选标题", html)
        self.assertNotIn("备选标题（3 个）", html)
        self.assertNotIn("这段摘要不应出现在", html)
        self.assertNotIn(">摘要<", html)
        self.assertNotIn(">正文</h2>", html)
        self.assertIn("这是需要保留的正文", html)
        self.assertIn("正文里的使用假设讨论", html)
        self.assertIn("这里正常讨论使用假设", html)
        self.assertNotIn("这段也不应出现", html)

    def test_excludes_usage_assumptions_heading_section(self):
        markdown = """# 示例标题

## 使用假设

这段假设不应出现在 HTML 中。

## 正文

正文需要保留。
"""

        html = publish_to_wechat.md_to_wechat_html(markdown)

        self.assertNotIn("这段假设不应出现", html)
        self.assertIn("正文需要保留", html)


class DigestExtractionTests(unittest.TestCase):
    def test_prefers_explicit_summary_over_delivery_metadata(self):
        markdown = """# 示例标题

> **使用假设**：项目复盘。
>
> 使用假设的补充文字。

## 备选标题（3 个）

1. 第一个备选标题

## 摘要

这是应该进入公众号后台的摘要。

## 正文

这是正文第一段。
"""

        digest = publish_to_wechat.extract_digest(markdown)

        self.assertEqual("这是应该进入公众号后台的摘要。", digest)

    def test_falls_back_to_first_body_paragraph(self):
        markdown = """# 示例标题

> **使用假设**：项目复盘。

## 正文

这是正文第一段。

这是正文第二段。
"""

        digest = publish_to_wechat.extract_digest(markdown)

        self.assertEqual("这是正文第一段。", digest)

    def test_can_explicitly_use_first_body_paragraph(self):
        markdown = """# 示例标题

## 摘要

这是摘要区块。

## 正文

这是正文第一段。
"""

        digest = publish_to_wechat.extract_digest(
            markdown,
            source="first_paragraph"
        )

        self.assertEqual("这是正文第一段。", digest)


class PublishDefaultsTests(unittest.TestCase):
    def publish_and_get_article(self, config):
        with tempfile.TemporaryDirectory() as tmp_dir:
            article_path = Path(tmp_dir) / "article.md"
            article_path.write_text("# 示例标题\n\n## 正文\n\n正文内容。\n", encoding="utf-8")
            api = MagicMock()
            api.create_draft.return_value = "media-id"

            with patch.object(publish_to_wechat, "WechatAPI", return_value=api), \
                 patch.object(publish_to_wechat, "append_history"), \
                 patch.dict(os.environ, {"WECHAT_APP_ID": "app-id", "WECHAT_APP_SECRET": "secret"}):
                publish_to_wechat.publish_article(str(article_path), config=config)

            return api.create_draft.call_args.args[0][0]

    def test_comments_are_open_by_default(self):
        article = self.publish_and_get_article({})

        self.assertEqual(1, article["need_open_comment"])

    def test_explicit_comment_setting_is_respected(self):
        article = self.publish_and_get_article({"wechat": {"need_open_comment": False}})

        self.assertEqual(0, article["need_open_comment"])

    def test_manual_digest_source_requires_digest_argument(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            article_path = Path(tmp_dir) / "article.md"
            article_path.write_text("# 示例标题\n\n## 正文\n\n正文内容。\n", encoding="utf-8")
            api = MagicMock()

            with patch.object(publish_to_wechat, "WechatAPI", return_value=api), \
                 patch.dict(os.environ, {"WECHAT_APP_ID": "app-id", "WECHAT_APP_SECRET": "secret"}):
                with self.assertRaisesRegex(ValueError, "必须通过 --digest 提供摘要"):
                    publish_to_wechat.publish_article(
                        str(article_path),
                        config={"wechat": {"default_digest_source": "manual"}},
                    )

            api.create_draft.assert_not_called()


if __name__ == "__main__":
    unittest.main()
