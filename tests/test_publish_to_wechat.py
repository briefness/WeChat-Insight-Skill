import importlib.util
import unittest
from pathlib import Path


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

## 备选标题

1. 示例标题

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
        self.assertNotIn("这段摘要不应出现在", html)
        self.assertNotIn(">摘要<", html)
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


if __name__ == "__main__":
    unittest.main()
