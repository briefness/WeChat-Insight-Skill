#!/usr/bin/env python3
"""
微信公众号草稿发布工具
将 Markdown 文章转换为公众号兼容 HTML 并上传到草稿箱

用法:
    python3 publish_to_wechat.py <markdown_file> [--cover <cover_image>] [--config <config_file>]
                                 [--author <author_name>] [--digest <digest_text>]
                                 [--theme warm|minimal|tech] [--no-link-footnotes]
                                 [--html-only | --dry-run]

环境变量:
    WECHAT_APP_ID      公众号 AppID（优先于配置文件）
    WECHAT_APP_SECRET  公众号 AppSecret（优先于配置文件）
"""

import argparse
import json
import os
import re
import sys
import urllib.request
import urllib.error
import urllib.parse
import mimetypes
import uuid
from pathlib import Path


# ─── Markdown → 公众号 HTML ───────────────────────────────────────────

HTML_THEMES = {
    'warm': {
        'accent': '#F4845F',
        'quote_bg': '#FFF7F3',
        'quote_bg_end': '#FFFAF8',
        'inline_code_color': '#d6336c',
    },
    'minimal': {
        'accent': '#1a1a1a',
        'quote_bg': '#f7f7f7',
        'quote_bg_end': '#fafafa',
        'inline_code_color': '#333333',
    },
    'tech': {
        'accent': '#2563EB',
        'quote_bg': '#EFF6FF',
        'quote_bg_end': '#F8FAFC',
        'inline_code_color': '#1D4ED8',
    },
}


def resolve_theme(theme: str = 'warm', primary_color: str = None) -> dict:
    """解析内置 HTML 主题，并允许显式 primary_color 覆盖主色。"""
    key = (theme or 'warm').strip().lower()
    if key not in HTML_THEMES:
        print(f"[WARN] 未知主题 {theme!r}，回退到 'warm'", file=sys.stderr)
        key = 'warm'
    resolved = dict(HTML_THEMES[key])
    resolved['name'] = key
    if primary_color:
        resolved['accent'] = primary_color
    return resolved


def _is_external_wechat_link(href: str) -> bool:
    """判断链接是否为非微信公众号域名的外部 HTTP(S) 链接。"""
    if not (href.startswith('http://') or href.startswith('https://')):
        return False
    host = (urllib.parse.urlparse(href).hostname or '').lower()
    return host != 'mp.weixin.qq.com' and not host.endswith('.mp.weixin.qq.com')


def compute_article_stats(md_text: str) -> dict:
    """统计可发布正文的中英文字数与预计阅读分钟数（约 350 字/分钟）。"""
    _, body = extract_title_and_body(md_text)
    body = strip_delivery_metadata(body)
    plain = re.sub(r'```[\s\S]*?```', ' ', body)
    plain = re.sub(r'!\[[^\]]*\]\([^)]+\)', ' ', plain)
    plain = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', plain)
    cjk_count = len(re.findall(r'[\u4e00-\u9fff]', plain))
    word_count = len(re.findall(r'[A-Za-z0-9_]+', plain))
    total = cjk_count + word_count
    read_minutes = max(1, round(total / 350)) if total else 1
    return {'word_count': total, 'read_minutes': read_minutes}


def extract_title_and_body(md_text: str):
    """从 Markdown 中提取标题和正文。首行 # 开头的是标题，其余为正文。"""
    lines = md_text.strip().split('\n')
    title = ""
    body_start = 0

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('# '):
            title = stripped[2:].strip()
            body_start = i + 1
            break
        elif stripped:
            break

    body = '\n'.join(lines[body_start:]).strip()
    return title, body


def _normalize_h2_heading(line: str) -> str:
    """提取二级标题的归一化文本，非二级标题返回空字符串。"""
    heading_match = re.fullmatch(r'##\s+(.+?)\s*', line.strip())
    if not heading_match:
        return ''
    return heading_match.group(1).strip('*` ').rstrip('：:')


_TRAILING_METADATA_HEADINGS = ('转发文案', '发布前检查', '本次修改说明')


def strip_delivery_metadata(body: str) -> str:
    """移除 Skill 交付信息，仅保留可发布正文所需的 Markdown。"""
    lines = body.split('\n')
    filtered = []
    in_code_block = False
    i = 0

    while i < len(lines):
        stripped = lines[i].strip()

        if stripped.startswith('```'):
            in_code_block = not in_code_block
            filtered.append(lines[i])
            i += 1
            continue

        if in_code_block:
            filtered.append(lines[i])
            i += 1
            continue

        heading = _normalize_h2_heading(lines[i])

        # 截掉尾部交付区块及其前的空行和分隔线
        if heading in _TRAILING_METADATA_HEADINGS:
            while filtered and filtered[-1].strip() in ('---', '***', '___', ''):
                filtered.pop()
            break

        is_delivery_section = (
            heading in ('使用假设', '摘要')
            or heading.startswith('备选标题')
        )
        if is_delivery_section:
            i += 1
            while i < len(lines) and not re.match(r'^##\s+', lines[i].strip()):
                i += 1
            continue

        # “正文”只是交付包的包装标题，不应出现在公众号正文中。
        if heading == '正文':
            i += 1
            continue

        if re.match(r'^>\s*(?:\*\*)?使用假设(?:\*\*)?\s*[：:]?', stripped):
            while i < len(lines) and lines[i].strip().startswith('>'):
                i += 1
            continue

        if re.match(r'^(?:\*\*)?使用假设(?:\*\*)?\s*[：:]', stripped):
            i += 1
            continue

        filtered.append(lines[i])
        i += 1

    return '\n'.join(filtered).strip()


def md_to_wechat_html(
    md_text: str,
    primary_color: str = None,
    theme: str = 'warm',
    external_link_footnotes: bool = True,
) -> str:
    """
    将 Markdown 转换为公众号编辑器兼容的 HTML。
    使用 inline 样式，不依赖外部 CSS，确保粘贴后样式不丢失。

    Args:
        md_text: Markdown 文本内容
        primary_color: 品牌主色（可选，传入时覆盖主题主色）
        theme: 内置主题名称（warm / minimal / tech），默认 warm
        external_link_footnotes: 是否将非微信域名外链转为文末编号脚注，默认 True
    """
    theme_cfg = resolve_theme(theme, primary_color)
    accent = theme_cfg['accent']
    quote_bg = theme_cfg['quote_bg']
    quote_bg_end = theme_cfg['quote_bg_end']
    inline_code_color = theme_cfg['inline_code_color']

    _, body = extract_title_and_body(md_text)
    body = strip_delivery_metadata(body)
    lines = body.split('\n')
    html_parts = []
    ol_counter = [0]  # 用列表包装，方便嵌套函数修改
    footnotes = []  # [(plain_label, escaped_href), ...]
    footnote_index = {}  # escaped_href -> 1-based index

    def _format_emphasis(segment: str) -> str:
        """对已转义的文本处理加粗和斜体。"""
        segment = re.sub(
            r'\*\*([^*]+)\*\*',
            lambda m: f'<strong style="font-weight: bold; color: {accent};">{m.group(1)}</strong>',
            segment
        )
        segment = re.sub(
            r'(?<!\*)\*([^*]+)\*(?!\*)',
            lambda m: f'<em>{m.group(1)}</em>',
            segment
        )
        return segment

    def inline_format(text: str) -> str:
        """处理行内格式：先保护行内代码并转义 HTML，再处理链接、加粗、斜体。"""
        code_tokens = []
        code_plain_texts = []

        def _stash_code(m: re.Match) -> str:
            idx = len(code_tokens)
            escaped_code = escape_html(m.group(1))
            code_plain_texts.append(escaped_code)
            code_tokens.append(
                f'<code style="background: #f6f8fa; padding: 2px 6px; '
                f'border-radius: 3px; font-size: 13px; '
                f'font-family: Consolas, Monaco, monospace; '
                f'color: {inline_code_color};">{escaped_code}</code>'
            )
            return f'\x00CODE{idx}\x00'

        # 1. 先提取行内代码，避免内部符号被后续正则误改
        text = re.sub(r'`([^`]+)`', _stash_code, text)
        # 2. 转义正文中的原生 HTML 字符（如 Array<string>、a < b）
        text = escape_html(text)

        # 3. 提取链接，防止 URL 中的星号等被强调语法破坏
        link_tokens = []

        def _stash_link(m: re.Match) -> str:
            idx = len(link_tokens)
            raw_label = m.group(1)
            label = _format_emphasis(raw_label)
            href = m.group(2).strip()
            if href.lower().startswith('javascript:'):
                href = '#'

            if external_link_footnotes and _is_external_wechat_link(href):
                if href not in footnote_index:
                    plain_label = re.sub(r'\*+', '', raw_label)
                    for c_idx, c_plain in enumerate(code_plain_texts):
                        plain_label = plain_label.replace(f'\x00CODE{c_idx}\x00', c_plain)
                    footnote_index[href] = len(footnotes) + 1
                    footnotes.append((plain_label.strip() or href, href))
                num = footnote_index[href]
                link_tokens.append(
                    f'<span style="color: {accent}; border-bottom: 1px solid {accent};">'
                    f'{label}</span>'
                    f'<sup style="color: {accent}; font-size: 11px; margin-left: 2px;">[{num}]</sup>'
                )
            else:
                link_tokens.append(
                    f'<a href="{href}" '
                    f'style="color: {accent}; text-decoration: none;">{label}</a>'
                )
            return f'\x00LINK{idx}\x00'

        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', _stash_link, text)
        # 4. 加粗与斜体
        text = _format_emphasis(text)

        # 5. 先还原链接，再还原行内代码（支持链接文本内嵌套行内代码）
        for idx, html in enumerate(link_tokens):
            text = text.replace(f'\x00LINK{idx}\x00', html)
        for idx, html in enumerate(code_tokens):
            text = text.replace(f'\x00CODE{idx}\x00', html)
        return text

    i = 0
    while i < len(lines):
        line = lines[i].rstrip()

        # 空行
        if not line.strip():
            i += 1
            continue

        # 二级标题
        if line.startswith('## '):
            ol_counter[0] = 0
            text = line[3:].strip()
            html_parts.append(
                f'<h2 style="font-size: 19px; font-weight: bold; '
                f'margin: 32px 0 14px 0; color: #1a1a1a; '
                f'line-height: 1.5; padding-left: 14px; '
                f'border-left: 4px solid {accent}; '
                f'letter-spacing: 0.02em;">{inline_format(text)}</h2>'
            )
            i += 1
            continue

        # 三级标题
        if line.startswith('### '):
            ol_counter[0] = 0
            text = line[4:].strip()
            html_parts.append(
                f'<h3 style="font-size: 16px; font-weight: bold; '
                f'margin: 24px 0 10px 0; color: #3a3a3a; '
                f'line-height: 1.6; padding-left: 10px; '
                f'border-left: 3px solid {accent}; '
                f'letter-spacing: 0.01em;">{inline_format(text)}</h3>'
            )
            i += 1
            continue

        # 引用块（兼容空引用行 `>`）
        if line.startswith('> ') or line.strip() == '>':
            ol_counter[0] = 0
            quote_lines = []
            while i < len(lines) and (lines[i].startswith('> ') or lines[i].strip() == '>'):
                raw = lines[i][2:].strip() if lines[i].startswith('> ') else ''
                quote_lines.append(inline_format(raw) if raw else '')
                i += 1
            # 保留引用块内的换行，不压成一行
            quote_inner = '<br/>'.join(quote_lines)
            html_parts.append(
                f'<blockquote style="border-left: 5px solid {accent}; '
                f'padding: 14px 18px; margin: 20px 0; '
                f'background-color: {quote_bg}; '
                f'background: linear-gradient(135deg, {quote_bg} 0%, {quote_bg_end} 100%); '
                f'color: #555; border-radius: 0 8px 8px 0; '
                f'font-size: 14.5px; line-height: 1.9;">'
                f'{quote_inner}</blockquote>'
            )
            continue

        # 无序列表 — 用 p 标签模拟，bullet 用 Unicode ● 字符，避开微信对 ul/li 的默认样式覆盖
        if re.match(r'^[-*+] ', line):
            ol_counter[0] = 0  # 切换到无序时重置有序计数
            text = re.sub(r'^[-*+] ', '', line).strip()
            html_parts.append(
                f'<p style="font-size: 15px; line-height: 1.9; margin: 0 0 8px 0; '
                f'color: #333; padding-left: 1.2em; text-indent: -1.2em;">'
                f'<span style="color: {accent}; font-size: 13px; '
                f'margin-right: 6px;">●</span>'
                f'{inline_format(text)}</p>'
            )
            i += 1
            continue

        # 有序列表 — 用 p 标签模拟，手动拼序号，避开微信对 ol/li 的默认样式覆盖
        ol_match = re.match(r'^(\d+)\. ', line)
        if ol_match:
            ol_counter[0] += 1
            text = re.sub(r'^\d+\. ', '', line).strip()
            html_parts.append(
                f'<p style="font-size: 15px; line-height: 1.9; margin: 0 0 10px 0; '
                f'color: #333; padding-left: 1.8em; text-indent: -1.8em;">'
                f'<span style="color: {accent}; font-weight: bold; '
                f'margin-right: 6px;">{ol_counter[0]}.</span>'
                f'{inline_format(text)}</p>'
            )
            i += 1
            continue
        else:
            ol_counter[0] = 0  # 非列表行重置有序计数

        # 代码块
        if line.strip().startswith('```'):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            if i < len(lines):
                i += 1  # 跳过结束 ```
            code_text = '\n'.join(code_lines)
            html_parts.append(
                f'<pre style="background: #1e1e2e; border-radius: 10px; '
                f'padding: 16px 20px; margin: 20px 0; '
                f'font-size: 13px; font-family: Consolas, Monaco, \'Courier New\', monospace; '
                f'line-height: 1.7; overflow-x: auto; '
                f'color: #cdd6f4; border: 1px solid #313244; '
                f'box-shadow: 0 4px 12px rgba(0,0,0,0.15);">'
                f'<code style="background: none; padding: 0; color: inherit; font-size: inherit;">{escape_html(code_text)}</code></pre>'
            )
            continue

        # 图片
        img_match = re.match(r'!\[([^\]]*)\]\(([^)]+)\)', line.strip())
        if img_match:
            alt = img_match.group(1).strip()
            src = img_match.group(2).strip()
            img_block = (
                f'<p style="margin: 24px 0 {"8px" if alt else "24px"} 0; text-align: center;">'
                f'<img src="{escape_html(src)}" alt="{escape_html(alt)}" '
                f'style="max-width: 100%; height: auto; '
                f'border-radius: 10px; display: block; margin: 0 auto; '
                f'box-shadow: 0 4px 16px rgba(0,0,0,0.10);" />'
                f'</p>'
            )
            if alt:
                img_block += (
                    f'<p style="margin: 4px 0 20px; text-align: center; font-size: 12px; '
                    f'color: #999; line-height: 1.6;">{escape_html(alt)}</p>'
                )
            html_parts.append(img_block)
            i += 1
            continue

        # 分隔线 — Unicode 字符装饰，微信完全兼容，有设计感
        if line.strip() in ('---', '***', '___'):
            html_parts.append(
                f'<p style="text-align: center; margin: 36px 0; '
                f'font-size: 16px; letter-spacing: 4px; '
                f'color: {accent}; line-height: 1; '
                f'font-weight: normal;">────◆────</p>'
            )
            i += 1
            continue

        # 普通段落
        para_lines = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not is_block_start(lines[i]):
            para_lines.append(lines[i].rstrip())
            i += 1

        para_text = ' '.join(para_lines).strip()
        html_parts.append(
            f'<p style="font-size: 15.5px; line-height: 2.1; '
            f'margin: 0 0 20px 0; color: #333; '
            f'text-align: justify; letter-spacing: 0.01em;">{inline_format(para_text)}</p>'
        )

    # 微信公众号正文禁止外部超链接，外链自动汇总为文末编号脚注方便复制
    if footnotes:
        html_parts.append(
            '<p style="font-size: 14px; font-weight: bold; color: #666; '
            'margin: 28px 0 10px 0; padding-top: 14px; '
            'border-top: 1px solid #eaeaea;">参考链接</p>'
        )
        for num, (fn_label, fn_url) in enumerate(footnotes, 1):
            html_parts.append(
                f'<p style="font-size: 12.5px; line-height: 1.7; margin: 0 0 6px 0; '
                f'color: #666; word-break: break-all;">'
                f'<span style="color: {accent}; font-weight: bold; margin-right: 4px;">[{num}]</span>'
                f'{fn_label}：{fn_url}</p>'
            )

    return '\n'.join(html_parts)


def is_block_start(line: str) -> bool:
    """判断一行是否是块级元素的开始。"""
    stripped = line.strip()
    if stripped.startswith('## '): return True
    if stripped.startswith('### '): return True
    if stripped.startswith('> ') or stripped == '>': return True
    if re.match(r'^[-*+] ', stripped): return True
    if re.match(r'^\d+\. ', stripped): return True
    if stripped.startswith('```'): return True
    if stripped.startswith('!['): return True
    if stripped in ('---', '***', '___'): return True
    return False





def escape_html(text: str) -> str:
    """HTML 转义。"""
    return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;'))


# ─── 微信公众号 API ────────────────────────────────────────────────────

class WechatAPI:
    """微信公众号 API 封装，只实现草稿箱相关接口。"""

    BASE_URL = 'https://api.weixin.qq.com'

    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self._access_token = None

    def _fetch_access_token(self) -> str:
        """从微信服务器获取新的 access_token。"""
        url = (
            f'{self.BASE_URL}/cgi-bin/token?'
            f'grant_type=client_credential'
            f'&appid={urllib.parse.quote(self.app_id)}'
            f'&secret={urllib.parse.quote(self.app_secret)}'
        )
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                data = json.loads(resp.read().decode('utf-8'))
        except urllib.error.URLError as e:
            raise RuntimeError(f"获取 access_token 失败：网络错误 {e}")

        if 'access_token' not in data:
            err_code = data.get('errcode', 'unknown')
            err_msg = data.get('errmsg', 'unknown error')
            if err_code == 40164:
                raise RuntimeError(
                    "获取 access_token 失败：IP 不在白名单。\n"
                    "请登录微信公众平台 → 设置与开发 → 基本配置 → "
                    "IP 白名单，将当前服务器 IP 加入白名单。"
                )
            raise RuntimeError(f"获取 access_token 失败：errcode={err_code}, errmsg={err_msg}")

        self._access_token = data['access_token']
        return self._access_token

    def get_access_token(self) -> str:
        """获取 access_token，带缓存。token 过期（40001）时自动重新获取一次。"""
        if not self._access_token:
            self._fetch_access_token()
        return self._access_token

    def invalidate_token(self):
        """P3: 清除缓存 token，下次调用时重新获取（用于处理 40001 过期）。"""
        self._access_token = None

    def _post_json(self, path: str, payload: dict, _retry: bool = True) -> dict:
        """发送 POST JSON 请求。P3: token 过期（40001）时自动刷新重试一次。"""
        token = self.get_access_token()
        url = f'{self.BASE_URL}{path}?access_token={urllib.parse.quote(token)}'
        data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        req = urllib.request.Request(
            url, data=data,
            headers={'Content-Type': 'application/json; charset=utf-8'},
            method='POST'
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                result = json.loads(resp.read().decode('utf-8'))
        except urllib.error.URLError as e:
            raise RuntimeError(f"请求 {path} 失败：{e}")

        # P3: token 过期自动刷新重试一次
        if result.get('errcode') == 40001 and _retry:
            print("[INFO] access_token 已过期，正在重新获取...")
            self.invalidate_token()
            return self._post_json(path, payload, _retry=False)

        return result

    def _upload_multipart(
        self,
        path: str,
        file_path: str,
        extra_query: str = '',
        label: str = '图片',
        _retry: bool = True,
    ) -> dict:
        """发送 multipart/form-data 图片上传请求，token 过期（40001）时自动刷新重试一次。"""
        img_path = Path(file_path)
        if not img_path.exists():
            raise FileNotFoundError(f"{label}不存在：{file_path}")

        file_size = img_path.stat().st_size
        if file_size > 10 * 1024 * 1024:
            raise ValueError(f"{label}不能超过 10MB")

        mime_type = mimetypes.guess_type(file_path)[0] or 'image/jpeg'
        if not mime_type.startswith('image/'):
            raise ValueError(f"{label}必须是图片文件，当前文件类型：{mime_type}")

        token = self.get_access_token()
        url = f'{self.BASE_URL}{path}?access_token={urllib.parse.quote(token)}{extra_query}'
        boundary = f'----WebKitFormBoundary{uuid.uuid4().hex}'

        body = [
            f'--{boundary}',
            f'Content-Disposition: form-data; name="media"; filename="{img_path.name}"',
            f'Content-Type: {mime_type}',
            '',
            img_path.read_bytes(),
            f'--{boundary}--',
            '',
        ]
        body_bytes = b'\r\n'.join(
            b if isinstance(b, bytes) else b.encode('utf-8') for b in body
        )

        req = urllib.request.Request(
            url, data=body_bytes,
            headers={'Content-Type': f'multipart/form-data; boundary={boundary}'},
            method='POST'
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode('utf-8'))
        except urllib.error.URLError as e:
            raise RuntimeError(f"上传{label}失败：{e}")

        if result.get('errcode') == 40001 and _retry:
            print("[INFO] access_token 已过期，正在重新获取...")
            self.invalidate_token()
            return self._upload_multipart(
                path, file_path, extra_query=extra_query, label=label, _retry=False
            )

        return result

    def _upload_media(self, file_path: str, media_type: str = 'image') -> dict:
        """上传永久素材，返回接口响应。"""
        return self._upload_multipart(
            '/cgi-bin/material/add_material',
            file_path,
            extra_query=f'&type={urllib.parse.quote(media_type)}',
            label='封面图',
        )

    def upload_cover_image(self, image_path: str) -> str:
        """上传封面图为永久素材，返回 media_id（用作草稿 thumb_media_id）。"""
        # 微信永久素材接口返回 media_id，草稿接口的 thumb_media_id 字段使用同一 ID
        result = self._upload_media(image_path, 'image')
        if 'media_id' not in result:
            err_code = result.get('errcode', 'unknown')
            err_msg = result.get('errmsg', 'unknown error')
            raise RuntimeError(f"上传封面图失败：errcode={err_code}, errmsg={err_msg}")
        return result['media_id']

    def create_draft(self, articles: list) -> str:
        """创建草稿，返回 media_id。"""
        result = self._post_json('/cgi-bin/draft/add', {'articles': articles})
        if 'media_id' not in result:
            err_code = result.get('errcode', 'unknown')
            err_msg = result.get('errmsg', 'unknown error')
            raise RuntimeError(f"创建草稿失败：errcode={err_code}, errmsg={err_msg}")
        return result['media_id']

    def get_draft_count(self) -> int:
        """获取草稿总数（用于验证）。"""
        result = self._post_json('/cgi-bin/draft/count', {})
        return result.get('total_count', 0)

    def upload_inline_image(self, image_path: str) -> str:
        """上传正文图片，返回微信 CDN URL。
        使用 /cgi-bin/media/uploadimg 接口，专用于图文正文中的图片。
        注意：此接口要求已认证的服务号或订阅号，未认证账号会返回 48001。
        """
        result = self._upload_multipart(
            '/cgi-bin/media/uploadimg',
            image_path,
            label='正文图片',
        )

        if 'url' not in result:
            err_code = result.get('errcode', 'unknown')
            if err_code == 48001:
                raise RuntimeError(
                    "上传正文图片失败：账号未认证（errcode=48001）。"
                    "正文本地图片上传需要已认证的公众号，"
                    "请在公众号后台手动替换图片，或改用外部图片链接。"
                )
            raise RuntimeError(
                f"上传正文图片失败：errcode={err_code}, "
                f"errmsg={result.get('errmsg', 'unknown')}"
            )
        return result['url']


# ─── 主流程 ────────────────────────────────────────────────────────────

def upload_local_images(md_text: str, api: 'WechatAPI', md_dir: Path) -> str:
    """扫描 Markdown 正文中的本地图片路径，上传到微信素材库并替换为 CDN URL。

    跳过代码块与尾部交付元信息（转发文案/发布前检查/本次修改说明）；远程 URL 原样保留。
    上传失败时打印 WARN 并保留原路径（不中断发布流程）。
    """
    def replace_img(m: re.Match) -> str:
        alt = m.group(1)
        src = m.group(2).strip()
        # 远程图片原样保留
        if src.startswith('http://') or src.startswith('https://'):
            return m.group(0)
        # 解析本地路径（相对路径相对于 Markdown 文件所在目录）
        img_path = Path(src) if Path(src).is_absolute() else md_dir / src
        if not img_path.exists():
            print(f"[WARN] 正文图片不存在，跳过上传：{src}", file=sys.stderr)
            return m.group(0)
        try:
            cdn_url = api.upload_inline_image(str(img_path))
            print(f"[INFO] 正文图片已上传：{img_path.name} → {cdn_url[:60]}...")
            return f'![{alt}]({cdn_url})'
        except Exception as e:
            print(f"[WARN] 正文图片上传失败，保留原路径（{src}）：{e}", file=sys.stderr)
            return m.group(0)

    out_lines = []
    in_code_block = False
    in_trailing_meta = False

    for line in md_text.split('\n'):
        stripped = line.strip()
        if stripped.startswith('```'):
            in_code_block = not in_code_block
            out_lines.append(line)
            continue

        if not in_code_block and _normalize_h2_heading(line) in _TRAILING_METADATA_HEADINGS:
            in_trailing_meta = True

        if in_code_block or in_trailing_meta:
            out_lines.append(line)
        else:
            out_lines.append(re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_img, line))

    return '\n'.join(out_lines)


def validate_config(config: dict) -> None:
    """校验配置文件结构和必填字段类型，发现问题时打印具体提示。

    只做警告，不抛异常——凭证缺失由 publish_article 负责报错。
    """
    wechat = config.get('wechat', {})
    if not isinstance(wechat, dict):
        print("[WARN] 配置文件 wechat 节必须是对象（{}），当前格式有误", file=sys.stderr)
        return

    str_fields = ['app_id', 'app_secret', 'default_author', 'default_digest_source']
    for field in str_fields:
        val = wechat.get(field)
        if val is not None and not isinstance(val, str):
            print(f"[WARN] 配置文件 wechat.{field} 应为字符串，当前值：{val!r}", file=sys.stderr)

    int_fields = ['need_open_comment', 'only_fans_can_comment']
    for field in int_fields:
        val = wechat.get(field)
        if val is not None and val not in (0, 1, True, False):
            print(f"[WARN] 配置文件 wechat.{field} 应为 0 或 1，当前值：{val!r}", file=sys.stderr)

    brand = config.get('brand', {})
    if not isinstance(brand, dict):
        print("[WARN] 配置文件 brand 节必须是对象（{}），当前格式有误", file=sys.stderr)


def append_history(title: str, media_id: str, md_file: str) -> None:
    """将发布记录追加到 ~/.local/share/wechat-writer/history.jsonl。"""
    import datetime
    history_dir = Path.home() / '.local' / 'share' / 'wechat-writer'
    history_dir.mkdir(parents=True, exist_ok=True)
    history_file = history_dir / 'history.jsonl'
    record = {
        'time': datetime.datetime.now().isoformat(timespec='seconds'),
        'title': title,
        'media_id': media_id,
        'file': str(Path(md_file).resolve()),
    }
    with open(history_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(record, ensure_ascii=False) + '\n')
    print(f"[INFO] 发布记录已保存：{history_file}")


def load_config(config_path: str = None) -> dict:
    """加载配置文件并校验字段类型。"""
    config = {}

    search_paths = []
    if config_path:
        search_paths.append(Path(config_path))
    search_paths.append(Path.cwd() / '.wechat-writer-config.json')
    search_paths.append(Path.home() / '.config' / 'wechat-writer' / 'config.json')

    for path in search_paths:
        if path and path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                print(f"[INFO] 读取配置：{path}")
                validate_config(config)  # 加载后立即校验字段类型
                break
            except json.JSONDecodeError as e:
                print(f"[WARN] 配置文件格式错误：{path} ({e})")
                continue

    return config


def mask_secret(secret: str) -> str:
    """脱敏显示密钥。"""
    if len(secret) <= 8:
        return '****'
    return secret[:4] + '****' + secret[-4:]


def extract_digest(
    md_text: str,
    max_len: int = 120,
    source: str = 'summary_section'
) -> str:
    """优先读取“摘要”交付区块，缺失时回退到正文第一段。"""
    lines = md_text.strip().split('\n')

    if source == 'summary_section':
        for index, line in enumerate(lines):
            heading_match = re.fullmatch(r'##\s+(.+?)\s*', line.strip())
            heading = heading_match.group(1).strip('*` ').rstrip('：:') if heading_match else ''
            if heading != '摘要':
                continue

            summary_lines = []
            for summary_line in lines[index + 1:]:
                if re.match(r'^##\s+', summary_line.strip()):
                    break
                stripped = summary_line.strip()
                if stripped:
                    summary_lines.append(stripped)
            summary = ''.join(summary_lines)
            if summary:
                return summary[:max_len]

    _, body = extract_title_and_body(md_text)
    lines = strip_delivery_metadata(body).split('\n')
    content_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if content_lines:
                break
            continue
        if stripped.startswith('#'):
            continue
        if stripped in ('---', '***', '___'):
            continue
        if re.match(r'^!\[[^]]*\]\([^)]+\)$', stripped):
            continue
        if stripped.startswith('> '):
            inner = stripped[2:].strip()
            if inner.startswith('【配图建议'):
                continue
            stripped = inner
        if not stripped:
            continue
        content_lines.append(stripped)
        if sum(len(l) for l in content_lines) >= max_len:
            break

    digest = ''.join(content_lines)[:max_len]
    return digest



def _collect_body_local_images(md_text: str, md_dir: Path) -> tuple:
    """扫描正文中引用的本地图片（跳过代码块与尾部交付元信息），返回 (存在列表, 缺失列表)。"""
    found = []
    missing = []
    in_code_block = False

    for line in md_text.split('\n'):
        stripped = line.strip()
        if stripped.startswith('```'):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        if _normalize_h2_heading(line) in _TRAILING_METADATA_HEADINGS:
            break
        for m in re.finditer(r'!\[[^\]]*\]\(([^)]+)\)', line):
            src = m.group(1).strip()
            if src.startswith(('http://', 'https://')):
                continue
            img_path = Path(src) if Path(src).is_absolute() else md_dir / src
            if img_path.exists():
                found.append(str(img_path))
            else:
                missing.append(src)
    return found, missing


def validate_draft_payload(
    title: str,
    author: str,
    digest: str,
    html_content: str,
    md_text: str,
    md_dir: Path,
    cover_image: str = None,
) -> dict:
    """按微信公众号草稿接口限制执行发布前预检，返回 errors / warnings / local_images / missing_images。"""
    errors = []
    warnings = []

    if not title:
        errors.append("缺少一级标题（# 开头的行）")
    elif len(title) > 64:
        errors.append(f"标题超出微信上限：{len(title)} 字（上限 64 字）")

    if author and len(author) > 8:
        errors.append(f"作者名超出微信上限：{len(author)} 字（上限 8 字）")

    if digest and len(digest) > 120:
        errors.append(f"摘要超出微信上限：{len(digest)} 字（上限 120 字）")

    if cover_image:
        cover_path = Path(cover_image)
        if not cover_path.exists():
            errors.append(f"封面图不存在：{cover_image}")
        else:
            if cover_path.stat().st_size > 10 * 1024 * 1024:
                errors.append(f"封面图超过 10MB 限制：{cover_image}")
            mime_type = mimetypes.guess_type(cover_image)[0] or 'image/jpeg'
            if not mime_type.startswith('image/'):
                errors.append(f"封面图不是有效图片格式：{mime_type}")
    else:
        warnings.append("未提供封面图，草稿将使用空白封面（可在公众号后台替换）")

    local_images, missing_images = _collect_body_local_images(md_text, md_dir)
    for src in missing_images:
        warnings.append(f"正文引用的本地图片不存在：{src}")

    html_bytes = len(html_content.encode('utf-8'))
    if html_bytes > 1024 * 1024:
        warnings.append(f"正文 HTML 体积较大（{html_bytes // 1024} KB），可能接近微信接口上限")

    return {
        'errors': errors,
        'warnings': warnings,
        'local_images': local_images,
        'missing_images': missing_images,
        'html_bytes': html_bytes,
    }


def _resolve_brand_theme_and_color(brand_cfg: dict, cli_theme: str = None) -> tuple:
    """根据 CLI --theme 与配置文件决定最终主题名与可选主色覆盖。"""
    theme_name = (cli_theme or brand_cfg.get('html_theme') or 'warm').strip().lower()
    cfg_color = brand_cfg.get('primary_color')
    # 当切换非 warm 主题且配置中的 primary_color 仍为默认暖橙时，采用目标主题自带主色
    if theme_name != 'warm' and cfg_color in (None, '', '#F4845F'):
        override_color = None
    else:
        override_color = cfg_color or None
    return theme_name, override_color


def _resolve_digest(md_text: str, wechat_cfg: dict, output_cfg: dict, digest: str = None) -> str:
    """解析文章摘要（优先 CLI 传入，其次按配置自动提取）。"""
    if digest:
        return digest
    digest_source = wechat_cfg.get('default_digest_source', 'summary_section')
    if digest_source == 'manual':
        raise ValueError(
            "配置 wechat.default_digest_source 为 manual 时，必须通过 --digest 提供摘要"
        )
    if digest_source not in ('summary_section', 'first_paragraph'):
        print(
            f"[WARN] 未知的摘要来源 {digest_source!r}，回退到 summary_section",
            file=sys.stderr
        )
        digest_source = 'summary_section'
    digest_max_length = output_cfg.get('digest_max_length', 80)
    if not isinstance(digest_max_length, int) or digest_max_length <= 0:
        print("[WARN] output.digest_max_length 必须是正整数，回退到 80", file=sys.stderr)
        digest_max_length = 80
    return extract_digest(md_text, digest_max_length, digest_source)


def publish_article(
    md_file: str,
    cover_image: str = None,
    config: dict = None,
    author: str = None,
    digest: str = None,
    theme: str = None,
    external_link_footnotes: bool = True,
    dry_run: bool = False,
) -> dict:
    """
    将 Markdown 文章发布到微信公众号草稿箱；dry_run=True 时仅执行本地预检不调网络 API。

    返回包含 media_id（dry_run 为 None）和文章信息的字典。
    """
    config = config or {}
    wechat_cfg = config.get('wechat', {})
    brand_cfg = config.get('brand', {})
    output_cfg = config.get('output', {})

    # 读取 Markdown 文件
    md_path = Path(md_file)
    if not md_path.exists():
        raise FileNotFoundError(f"Markdown 文件不存在：{md_file}")

    md_text = md_path.read_text(encoding='utf-8')
    title, _ = extract_title_and_body(md_text)

    if not title:
        raise ValueError("Markdown 文件中未找到一级标题（# 开头的行）")

    theme_name, override_color = _resolve_brand_theme_and_color(brand_cfg, theme)
    resolved_digest = _resolve_digest(md_text, wechat_cfg, output_cfg, digest)
    resolved_author = author if author is not None else wechat_cfg.get('default_author', '')

    # 预渲染 HTML 并执行字段硬限制预检（上传图片前尽早暴露错误）
    preview_html = md_to_wechat_html(
        md_text,
        primary_color=override_color,
        theme=theme_name,
        external_link_footnotes=external_link_footnotes,
    )
    validation = validate_draft_payload(
        title=title,
        author=resolved_author,
        digest=resolved_digest,
        html_content=preview_html,
        md_text=md_text,
        md_dir=md_path.parent,
        cover_image=cover_image,
    )
    stats = compute_article_stats(md_text)

    if dry_run:
        return {
            'dry_run': True,
            'media_id': None,
            'title': title,
            'author': resolved_author,
            'digest': resolved_digest,
            'theme': resolve_theme(theme_name, override_color)['name'],
            'has_cover': bool(cover_image and Path(cover_image).exists()),
            'stats': stats,
            'validation': validation,
        }

    if validation['errors']:
        raise ValueError("发布前校验失败：\n  - " + "\n  - ".join(validation['errors']))

    # 凭证：环境变量优先
    app_id = os.environ.get('WECHAT_APP_ID') or wechat_cfg.get('app_id', '')
    app_secret = os.environ.get('WECHAT_APP_SECRET') or wechat_cfg.get('app_secret', '')

    if not app_id or not app_secret:
        raise RuntimeError(
            "缺少公众号凭证。请通过以下任一方式提供：\n"
            "  1. 设置环境变量 WECHAT_APP_ID 和 WECHAT_APP_SECRET\n"
            "  2. 在配置文件的 wechat 节中填写 app_id 和 app_secret"
        )

    print(f"[INFO] AppID: {mask_secret(app_id)}")
    print(f"[INFO] AppSecret: {mask_secret(app_secret)}")
    print(f"[INFO] 文章标题：{title}")

    # 初始化 API（提前初始化，下面图片上传也需要用到）
    api = WechatAPI(app_id, app_secret)

    # 如果正文有本地图片，先批量上传并替换 URL
    md_text = upload_local_images(md_text, api, md_path.parent)

    # 转换为最终 HTML（使用替换 CDN 后的文本）
    html_content = md_to_wechat_html(
        md_text,
        primary_color=override_color,
        theme=theme_name,
        external_link_footnotes=external_link_footnotes,
    )
    print(f"[INFO] HTML 转换完成，约 {len(html_content)} 字符（主题：{theme_name}）")

    # 上传封面图（如果提供）
    thumb_media_id = ''
    if cover_image:
        print(f"[INFO] 上传封面图：{cover_image}")
        thumb_media_id = api.upload_cover_image(cover_image)
        print(f"[INFO] 封面图 media_id：{thumb_media_id[:10]}...")
    else:
        print("[WARN] 未提供封面图，草稿将使用空白封面（可在公众号后台替换）")

    # 构建文章
    article = {
        'title': title,
        'author': resolved_author,
        'digest': resolved_digest,
        'content': html_content,
        'thumb_media_id': thumb_media_id,
        'need_open_comment': int(wechat_cfg.get('need_open_comment', 1)),
        'only_fans_can_comment': int(wechat_cfg.get('only_fans_can_comment', 0)),
        'content_source_url': '',
    }

    # 发布到草稿箱
    print("[INFO] 创建草稿...")
    media_id = api.create_draft([article])
    print(f"[OK] 草稿创建成功！media_id: {media_id}")

    # 记录发布历史
    try:
        append_history(title, media_id, md_file)
    except Exception as e:
        print(f"[WARN] 历史记录写入失败（不影响发布）：{e}", file=sys.stderr)

    return {
        'media_id': media_id,
        'title': title,
        'author': resolved_author,
        'digest': resolved_digest,
        'has_cover': bool(thumb_media_id),
        'theme': theme_name,
        'stats': stats,
    }


def _safe_js_json(value: str) -> str:
    """安全序列化为内嵌 <script> 的 JSON 字符串，防止 </script> 提前闭合。"""
    return json.dumps(value, ensure_ascii=False).replace('</', '<\\/')


def build_preview_html(
    title: str,
    article_html: str,
    primary_color: str = '#F4845F',
    digest: str = '',
    stats: dict = None,
    theme: str = 'warm',
) -> str:
    """构建带手机/桌面预览切换、字数统计和一键复制能力的本地 HTML 预览页。"""
    safe_title = escape_html(title) or '未命名文章'
    article_html_json = _safe_js_json(article_html)
    title_json = _safe_js_json(title or '')
    digest_json = _safe_js_json(digest or '')
    stats = stats or {}
    word_count = stats.get('word_count')
    read_minutes = stats.get('read_minutes')

    stats_block = ''
    if word_count is not None:
        stats_block = (
            f'<div class="meta-card">'
            f'<div><strong>字数</strong>：约 {word_count} 字</div>'
            f'<div><strong>预计阅读</strong>：{read_minutes} 分钟</div>'
            f'<div><strong>排版主题</strong>：{escape_html(theme)}</div>'
            f'</div>'
        )

    digest_btn = (
        '<button class="sub-btn" onclick="copyPlain(ARTICLE_DIGEST, this, \'复制摘要\')">复制摘要</button>'
        if digest else ''
    )

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{safe_title} — 微信公众号预览</title>
<style>
  :root {{ --primary: {primary_color}; }}
  *, *::before, *::after {{ box-sizing: border-box; }}
  body {{
    margin: 0; padding: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    background: #f0f2f5;
    display: flex;
    min-height: 100vh;
  }}
  /* ── 左侧预览 ── */
  #preview-wrap {{
    flex: 1;
    overflow-y: auto;
    padding: 36px 24px;
    display: flex;
    justify-content: center;
    align-items: flex-start;
  }}
  #preview {{
    background: #fff;
    width: 100%;
    max-width: 680px;
    min-height: 100vh;
    padding: 40px 32px 60px;
    border-radius: 12px;
    box-shadow: 0 4px 24px rgba(0,0,0,.08);
    transition: max-width .2s ease, padding .2s ease, border-radius .2s ease;
  }}
  #preview.mobile-view {{
    max-width: 375px;
    padding: 24px 16px 48px;
    border-radius: 28px;
    border: 8px solid #1f2937;
  }}
  /* ── 右侧操作面板 ── */
  #sidebar {{
    width: 248px;
    flex-shrink: 0;
    padding: 36px 16px;
    display: flex;
    flex-direction: column;
    gap: 14px;
    position: sticky;
    top: 0;
    height: 100vh;
    overflow-y: auto;
  }}
  #sidebar h2 {{
    font-size: 13px;
    font-weight: 600;
    color: #888;
    text-transform: uppercase;
    letter-spacing: .06em;
    margin: 0;
  }}
  .view-switch {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 6px;
    background: #e5e7eb;
    padding: 4px;
    border-radius: 10px;
  }}
  .view-btn {{
    border: none;
    background: transparent;
    color: #555;
    font-size: 12.5px;
    font-weight: 600;
    padding: 7px 0;
    border-radius: 7px;
    cursor: pointer;
    transition: background .15s, color .15s;
  }}
  .view-btn.active {{
    background: #fff;
    color: var(--primary);
    box-shadow: 0 1px 4px rgba(0,0,0,.08);
  }}
  .meta-card {{
    background: #fff;
    border: 1px solid #e8e8e8;
    border-radius: 8px;
    padding: 10px 12px;
    font-size: 12.5px;
    color: #555;
    line-height: 1.8;
  }}
  .meta-card strong {{ color: #222; }}
  #copy-btn {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    width: 100%;
    padding: 13px 0;
    background: var(--primary);
    color: #fff;
    border: none;
    border-radius: 10px;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
    transition: opacity .15s, transform .1s, box-shadow .15s;
    box-shadow: 0 4px 12px rgba(0,0,0,.15);
  }}
  #copy-btn:hover {{ opacity: .92; box-shadow: 0 6px 16px rgba(0,0,0,.20); }}
  #copy-btn:active {{ transform: scale(.97); }}
  #copy-btn.success {{ background: #34c759; box-shadow: 0 4px 12px rgba(52,199,89,.35); }}
  #copy-btn svg {{ width: 18px; height: 18px; fill: currentColor; flex-shrink: 0; }}
  .sub-actions {{
    display: flex;
    gap: 8px;
  }}
  .sub-btn {{
    flex: 1;
    padding: 8px 6px;
    background: #fff;
    color: #333;
    border: 1px solid #d9d9d9;
    border-radius: 8px;
    font-size: 12.5px;
    font-weight: 500;
    cursor: pointer;
    transition: border-color .15s, color .15s;
  }}
  .sub-btn:hover {{ border-color: var(--primary); color: var(--primary); }}
  .sub-btn.success {{ border-color: #34c759; color: #34c759; }}
  #status {{
    font-size: 12.5px;
    color: #555;
    line-height: 1.7;
    background: #fff;
    border-radius: 8px;
    padding: 12px 14px;
    border: 1px solid #e8e8e8;
  }}
  #status strong {{ color: var(--primary); }}
  .step {{
    display: flex;
    align-items: flex-start;
    gap: 8px;
    font-size: 12.5px;
    color: #555;
    line-height: 1.6;
  }}
  .step-num {{
    flex-shrink: 0;
    width: 20px;
    height: 20px;
    background: var(--primary);
    color: #fff;
    border-radius: 50%;
    font-size: 11px;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-top: 1px;
  }}
  #err {{
    font-size: 12px;
    color: #e74c3c;
    display: none;
    background: #fff5f5;
    border: 1px solid #fecaca;
    border-radius: 8px;
    padding: 10px 12px;
    line-height: 1.6;
  }}
</style>
</head>
<body>

<!-- 左侧文章预览 -->
<div id="preview-wrap">
  <div id="preview">
    {article_html}
  </div>
</div>

<!-- 右侧操作面板 -->
<div id="sidebar">
  <h2>预览视图</h2>
  <div class="view-switch">
    <button id="btn-desktop" class="view-btn active" onclick="setView('desktop')">桌面 680px</button>
    <button id="btn-mobile" class="view-btn" onclick="setView('mobile')">手机 375px</button>
  </div>

  {stats_block}

  <h2>复制操作</h2>

  <button id="copy-btn" onclick="copyArticle()">
    <svg viewBox="0 0 24 24"><path d="M16 1H4C2.9 1 2 1.9 2 3v14h2V3h12V1zm3 4H8C6.9 5 6 5.9 6 7v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg>
    一键复制正文
  </button>

  <div class="sub-actions">
    <button class="sub-btn" onclick="copyPlain(ARTICLE_TITLE, this, '复制标题')">复制标题</button>
    {digest_btn}
  </div>

  <div id="err"></div>

  <div id="status">
    复制后打开微信公众号编辑器，<strong>直接 ⌘V / Ctrl+V 粘贴</strong>，样式完整保留。
  </div>

  <div class="step">
    <span class="step-num">1</span>
    <span>切到「手机 375px」检查首屏与分段</span>
  </div>
  <div class="step">
    <span class="step-num">2</span>
    <span>点击「一键复制正文」并粘贴到编辑器</span>
  </div>
  <div class="step">
    <span class="step-num">3</span>
    <span>按需复制标题/摘要并上传封面图</span>
  </div>
</div>

<script>
// 正文 HTML（只含文章内容，不含预览页框架）
const ARTICLE_HTML = {article_html_json};
const ARTICLE_TITLE = {title_json};
const ARTICLE_DIGEST = {digest_json};

function setView(mode) {{
  const preview = document.getElementById('preview');
  const isMobile = mode === 'mobile';
  preview.classList.toggle('mobile-view', isMobile);
  document.getElementById('btn-mobile').classList.toggle('active', isMobile);
  document.getElementById('btn-desktop').classList.toggle('active', !isMobile);
}}

function fallbackCopyHtml(html) {{
  const div = document.createElement('div');
  div.innerHTML = html;
  div.style.cssText = 'position:fixed;left:-9999px;top:0;opacity:0;';
  document.body.appendChild(div);
  try {{
    const sel = window.getSelection();
    const range = document.createRange();
    range.selectNodeContents(div);
    sel.removeAllRanges();
    sel.addRange(range);
    const ok = document.execCommand('copy');
    sel.removeAllRanges();
    if (!ok) throw new Error('execCommand copy 返回 false');
  }} finally {{
    document.body.removeChild(div);
  }}
}}

function fallbackCopyText(text) {{
  const ta = document.createElement('textarea');
  ta.value = text;
  ta.style.cssText = 'position:fixed;left:-9999px;top:0;opacity:0;';
  document.body.appendChild(ta);
  try {{
    ta.select();
    const ok = document.execCommand('copy');
    if (!ok) throw new Error('execCommand copy 返回 false');
  }} finally {{
    document.body.removeChild(ta);
  }}
}}

async function copyPlain(text, btn, defaultLabel) {{
  const err = document.getElementById('err');
  err.style.display = 'none';
  try {{
    let copied = false;
    if (navigator.clipboard && navigator.clipboard.writeText) {{
      try {{
        await navigator.clipboard.writeText(text);
        copied = true;
      }} catch (_e) {{
        copied = false;
      }}
    }}
    if (!copied) {{
      fallbackCopyText(text);
    }}
    btn.classList.add('success');
    btn.textContent = '已复制';
    setTimeout(() => {{
      btn.classList.remove('success');
      btn.textContent = defaultLabel;
    }}, 2000);
  }} catch (e) {{
    err.textContent = '复制失败：' + e.message;
    err.style.display = 'block';
  }}
}}

async function copyArticle() {{
  const btn = document.getElementById('copy-btn');
  const err = document.getElementById('err');
  err.style.display = 'none';

  try {{
    let copied = false;
    // 优先用 ClipboardItem API（同时写入 text/html 与 text/plain）
    if (navigator.clipboard && window.ClipboardItem) {{
      try {{
        const htmlBlob = new Blob([ARTICLE_HTML], {{ type: 'text/html' }});
        const previewEl = document.getElementById('preview');
        const plainBlob = new Blob([previewEl ? previewEl.innerText : ''], {{ type: 'text/plain' }});
        await navigator.clipboard.write([new ClipboardItem({{
          'text/html': htmlBlob,
          'text/plain': plainBlob,
        }})]);
        copied = true;
      }} catch (_clipboardErr) {{
        // file:// 或权限受限时回退到 execCommand
        copied = false;
      }}
    }}
    if (!copied) {{
      fallbackCopyHtml(ARTICLE_HTML);
    }}

    // 成功反馈
    btn.classList.add('success');
    btn.innerHTML = '<svg viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z"/></svg> 已复制！去粘贴吧';
    setTimeout(() => {{
      btn.classList.remove('success');
      btn.innerHTML = '<svg viewBox="0 0 24 24"><path d="M16 1H4C2.9 1 2 1.9 2 3v14h2V3h12V1zm3 4H8C6.9 5 6 5.9 6 7v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg> 一键复制正文';
    }}, 3000);

  }} catch (e) {{
    err.textContent = '复制失败：' + e.message + '。请尝试在浏览器地址栏直接打开此文件，或用 Chrome/Edge 打开。';
    err.style.display = 'block';
  }}
}}
</script>

</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(
        description='微信公众号草稿发布工具：Markdown → 草稿箱'
    )
    parser.add_argument('markdown', help='Markdown 文章文件路径')
    parser.add_argument('--cover', help='封面图路径（可选）')
    parser.add_argument('--config', help='配置文件路径（可选）')
    parser.add_argument('--author', help='作者名（可选，覆盖配置）')
    parser.add_argument('--digest', help='摘要（可选，默认自动提取）')
    parser.add_argument('--theme', choices=tuple(HTML_THEMES.keys()),
                        help='HTML 排版主题（warm / minimal / tech）')
    parser.add_argument('--no-link-footnotes', action='store_true',
                        help='禁用外部链接自动转为文末编号脚注')
    parser.add_argument('--html-only', action='store_true',
                        help='只输出 HTML 预览页，不上传到公众号')
    parser.add_argument('--dry-run', action='store_true',
                        help='只执行发布前字段与资源预检，不调用微信 API')

    args = parser.parse_args()

    # 加载配置（各路径都需要，提前到此处）
    config = load_config(args.config)
    brand_cfg = config.get('brand', {})
    wechat_cfg = config.get('wechat', {})
    output_cfg = config.get('output', {})
    theme_name, override_color = _resolve_brand_theme_and_color(brand_cfg, args.theme)
    resolved_theme = resolve_theme(theme_name, override_color)
    link_footnotes = not args.no_link_footnotes

    # 只生成 HTML 模式
    if args.html_only:
        md_path = Path(args.markdown)
        if not md_path.exists():
            print(f"[ERROR] 文件不存在：{args.markdown}", file=sys.stderr)
            sys.exit(1)
        md_text = md_path.read_text(encoding='utf-8')
        article_html = md_to_wechat_html(
            md_text,
            primary_color=override_color,
            theme=theme_name,
            external_link_footnotes=link_footnotes,
        )
        title, _ = extract_title_and_body(md_text)
        preview_digest = args.digest or extract_digest(
            md_text,
            output_cfg.get('digest_max_length', 80) if isinstance(output_cfg.get('digest_max_length', 80), int) else 80,
            wechat_cfg.get('default_digest_source', 'summary_section')
            if wechat_cfg.get('default_digest_source', 'summary_section') in ('summary_section', 'first_paragraph')
            else 'summary_section',
        )
        stats = compute_article_stats(md_text)

        full_page = build_preview_html(
            title,
            article_html,
            primary_color=resolved_theme['accent'],
            digest=preview_digest,
            stats=stats,
            theme=resolved_theme['name'],
        )
        out_path = md_path.with_suffix('.html')
        out_path.write_text(full_page, encoding='utf-8')
        print(f"[OK] HTML 预览页已生成：{out_path}（主题：{resolved_theme['name']}，约 {stats['word_count']} 字）")
        print("[INFO] 用浏览器打开后，可切换手机/桌面视图并点击右侧「一键复制正文」。")
        return

    try:
        result = publish_article(
            md_file=args.markdown,
            cover_image=args.cover,
            config=config,
            author=args.author,
            digest=args.digest,
            theme=args.theme,
            external_link_footnotes=link_footnotes,
            dry_run=args.dry_run,
        )
        if args.dry_run:
            v = result['validation']
            stats = result['stats']
            print("\n" + "=" * 50)
            print("  Dry-Run 发布前预检报告（未调用微信 API）")
            print("=" * 50)
            print(f"  标题（{len(result['title'])}/64 字）：{result['title']}")
            print(f"  作者（{len(result['author'])}/8 字）：{result['author'] or '（未设置）'}")
            print(f"  摘要（{len(result['digest'])}/120 字）：{result['digest'] or '（空）'}")
            print(f"  主题：{result['theme']} | 正文字数：约 {stats['word_count']} 字（约 {stats['read_minutes']} 分钟）")
            print(f"  HTML 体积：{v['html_bytes']} bytes | 本地正文图：{len(v['local_images'])} 张")
            print(f"  封面：{'就绪' if result['has_cover'] else '未设置/缺失'}")
            if v['warnings']:
                print("\n  [WARN] 提醒项：")
                for w in v['warnings']:
                    print(f"    - {w}")
            if v['errors']:
                print("\n  [ERROR] 阻塞项：")
                for e in v['errors']:
                    print(f"    - {e}")
                print("=" * 50)
                sys.exit(1)
            print("\n  [OK] 所有硬校验通过，可执行正式发布。")
            print("=" * 50)
            return

        print("\n" + "=" * 50)
        print("  草稿已成功发布到微信公众号后台！")
        print("=" * 50)
        print(f"  标题：{result['title']}")
        print(f"  作者：{result['author'] or '（未设置）'}")
        print(f"  封面：{'已上传' if result['has_cover'] else '未设置'}")
        print(f"  media_id：{result['media_id']}")
        print()
        print("  查看草稿：https://mp.weixin.qq.com → 内容 → 草稿箱")
        print(f"  找到《{result['title']}》，点击发布。")
        print("=" * 50)
    except (RuntimeError, ValueError, FileNotFoundError) as e:
        # 捕获 ValueError（如无标题或字段超限）以及其他已知错误
        print(f"\n[ERROR] {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[INFO] 已取消", file=sys.stderr)
        sys.exit(130)


if __name__ == '__main__':
    main()
