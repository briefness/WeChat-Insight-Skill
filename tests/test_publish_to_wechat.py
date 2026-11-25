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

    def test_escapes_html_and_protects_inline_code_from_emphasis(self):
        markdown = """# 测试标题

正文含泛型 Array<string> 和条件 a < b && c > d，行内代码 `**kwargs` 和 `a * b * c`，链接 [`**cmd**`](https://example.com?a=1&b=2)。
"""

        html = publish_to_wechat.md_to_wechat_html(
            markdown, primary_color="#123456", external_link_footnotes=False
        )

        self.assertIn("Array&lt;string&gt;", html)
        self.assertIn("a &lt; b &amp;&amp; c &gt; d", html)
        self.assertIn(">**kwargs</code>", html)
        self.assertIn(">a * b * c</code>", html)
        self.assertNotIn("<em> b </em>", html)
        self.assertIn('href="https://example.com?a=1&amp;b=2"', html)
        self.assertIn(">**cmd**</code></a>", html)

    def test_external_links_convert_to_deduped_footnotes_while_wechat_links_stay_inline(self):
        markdown = """# 测试标题

参考 [官方文档](https://example.com/docs) 与 [重复引用](https://example.com/docs)，以及 [公众号历史文章](https://mp.weixin.qq.com/s/abc)。
"""

        html = publish_to_wechat.md_to_wechat_html(markdown)

        self.assertIn("参考链接", html)
        self.assertEqual(2, html.count(">[1]</sup>"))
        self.assertIn("官方文档：https://example.com/docs", html)
        self.assertNotIn('href="https://example.com/docs"', html)
        self.assertIn('href="https://mp.weixin.qq.com/s/abc"', html)

    def test_builtin_themes_apply_distinct_accents_and_quote_backgrounds(self):
        markdown = "# 主题测试\n\n> 一段引用\n"

        tech_html = publish_to_wechat.md_to_wechat_html(markdown, theme="tech")
        minimal_html = publish_to_wechat.md_to_wechat_html(markdown, theme="minimal")

        self.assertIn("#2563EB", tech_html)
        self.assertIn("#EFF6FF", tech_html)
        self.assertIn("#1a1a1a", minimal_html)
        self.assertIn("#f7f7f7", minimal_html)

    def test_strips_revision_notes_and_preserves_code_block_headings(self):
        markdown = """# 测试标题

```markdown
## 转发文案
代码块里的示例不应截断正文
```

正文继续保留。

---

## 本次修改说明

- 修改了标题
"""

        html = publish_to_wechat.md_to_wechat_html(markdown)

        self.assertIn("代码块里的示例不应截断正文", html)
        self.assertIn("正文继续保留", html)
        self.assertNotIn("本次修改说明", html)
        self.assertNotIn("修改了标题", html)

    def test_blockquote_handles_blank_quote_line_and_h3_uses_primary_color(self):
        markdown = """# 测试标题

### 小节标题

> 第一段引用
>
> 第二段引用

![](demo.png)
"""

        html = publish_to_wechat.md_to_wechat_html(markdown, primary_color="#2266AA")

        self.assertIn("border-left: 3px solid #2266AA;", html)
        self.assertEqual(1, html.count("<blockquote"))
        self.assertIn("第一段引用<br/><br/>第二段引用", html)
        self.assertNotIn("font-size: 12px;", html)

    def test_preview_html_escapes_title_and_script_closing_tag(self):
        article_html = publish_to_wechat.md_to_wechat_html(
            "# A <B> 标题\n\n```html\n<script>alert(1)</script>\n```\n"
        )
        page = publish_to_wechat.build_preview_html(
            "A <B> 标题",
            article_html,
            primary_color="#2266AA",
            digest="测试摘要内容",
            stats={"word_count": 420, "read_minutes": 1},
            theme="tech",
        )

        self.assertIn("<title>A &lt;B&gt; 标题 — 微信公众号预览</title>", page)
        self.assertIn("--primary: #2266AA;", page)
        self.assertNotIn('</script>"', page)
        self.assertIn("fallbackCopyHtml(ARTICLE_HTML);", page)
        self.assertIn("setView('mobile')", page)
        self.assertIn("约 420 字", page)
        self.assertIn("复制标题", page)
        self.assertIn("复制摘要", page)

    def test_upload_local_images_skips_code_blocks_and_trailing_metadata(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            img = Path(tmp_dir) / "real.png"
            img.write_bytes(b"\x89PNG\r\n\x1a\n")
            api = MagicMock()
            api.upload_inline_image.return_value = "https://mmbiz.qpic.cn/real"

            md = """# 标题

![真实图](real.png)

```markdown
![示例图](missing-in-code.png)
```

## 发布前检查

![元信息图](missing-in-meta.png)
"""
            updated = publish_to_wechat.upload_local_images(md, api, Path(tmp_dir))

            api.upload_inline_image.assert_called_once_with(str(img))
            self.assertIn("![真实图](https://mmbiz.qpic.cn/real)", updated)
            self.assertIn("![示例图](missing-in-code.png)", updated)
            self.assertIn("![元信息图](missing-in-meta.png)", updated)

    def test_upload_multipart_retries_once_on_40001(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            img = Path(tmp_dir) / "cover.png"
            img.write_bytes(b"\x89PNG\r\n\x1a\n")
            api = publish_to_wechat.WechatAPI("app-id", "secret")
            api._access_token = "expired-token"

            resp_expired = MagicMock()
            resp_expired.__enter__.return_value.read.return_value = b'{"errcode": 40001, "errmsg": "invalid credential"}'
            resp_ok = MagicMock()
            resp_ok.__enter__.return_value.read.return_value = b'{"media_id": "new-media-id"}'

            with patch.object(publish_to_wechat.urllib.request, "urlopen", side_effect=[resp_expired, resp_ok]), \
                 patch.object(api, "_fetch_access_token", side_effect=lambda: setattr(api, "_access_token", "fresh-token") or "fresh-token"):
                media_id = api.upload_cover_image(str(img))

            self.assertEqual("new-media-id", media_id)
            self.assertEqual("fresh-token", api._access_token)


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

    def test_dry_run_validates_without_credentials_or_api_calls(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            article_path = Path(tmp_dir) / "article.md"
            article_path.write_text(
                "# 正常标题\n\n## 摘要\n\n这是一段正常摘要。\n\n## 正文\n\n正文内容包含一些中文测试。\n\n![缺失图](missing.png)\n",
                encoding="utf-8",
            )

            with patch.object(publish_to_wechat, "WechatAPI") as api_cls, \
                 patch.dict(os.environ, {}, clear=True):
                result = publish_to_wechat.publish_article(
                    str(article_path),
                    author="独立开发者",
                    theme="tech",
                    dry_run=True,
                )

            api_cls.assert_not_called()
            self.assertTrue(result["dry_run"])
            self.assertEqual("tech", result["theme"])
            self.assertEqual([], result["validation"]["errors"])
            self.assertIn("missing.png", result["validation"]["missing_images"])
            self.assertGreater(result["stats"]["word_count"], 0)

    def test_publish_rejects_oversized_wechat_fields_before_api_call(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            article_path = Path(tmp_dir) / "article.md"
            long_title = "标" * 65
            article_path.write_text(f"# {long_title}\n\n## 正文\n\n正文内容。\n", encoding="utf-8")

            with patch.object(publish_to_wechat, "WechatAPI") as api_cls, \
                 patch.dict(os.environ, {"WECHAT_APP_ID": "app-id", "WECHAT_APP_SECRET": "secret"}):
                with self.assertRaisesRegex(ValueError, "标题超出微信上限"):
                    publish_to_wechat.publish_article(str(article_path), author="超过八个字的作者名称")

            api_cls.assert_not_called()


if __name__ == "__main__":
    unittest.main()
