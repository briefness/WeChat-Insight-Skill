#!/usr/bin/env python3
"""
微信公众号草稿发布工具
将 Markdown 文章转换为公众号兼容 HTML 并上传到草稿箱

用法:
    python publish_to_wechat.py <markdown_file> [--cover <cover_image>] [--config <config_file>]

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


def md_to_wechat_html(md_text: str) -> str:
    """
    将 Markdown 转换为公众号编辑器兼容的 HTML。
    使用 inline 样式，不依赖外部 CSS，确保粘贴后样式不丢失。
    """
    _, body = extract_title_and_body(md_text)
    lines = body.split('\n')
    html_parts = []
    in_list = False
    list_type = None

    i = 0
    while i < len(lines):
        line = lines[i].rstrip()

        # 空行
        if not line.strip():
            if in_list:
                html_parts.append(f'</{list_type}>')
                in_list = False
                list_type = None
            i += 1
            continue

        # 二级标题
        if line.startswith('## '):
            if in_list:
                html_parts.append(f'</{list_type}>')
                in_list = False
            text = line[3:].strip()
            html_parts.append(
                f'<h2 style="font-size: 18px; font-weight: bold; '
                f'margin: 24px 0 12px 0; color: #1a1a1a; '
                f'line-height: 1.6;">{inline_format(text)}</h2>'
            )
            i += 1
            continue

        # 三级标题
        if line.startswith('### '):
            if in_list:
                html_parts.append(f'</{list_type}>')
                in_list = False
            text = line[4:].strip()
            html_parts.append(
                f'<h3 style="font-size: 16px; font-weight: bold; '
                f'margin: 20px 0 10px 0; color: #1a1a1a; '
                f'line-height: 1.6;">{inline_format(text)}</h3>'
            )
            i += 1
            continue

        # 引用块
        if line.startswith('> '):
            if in_list:
                html_parts.append(f'</{list_type}>')
                in_list = False
            quote_lines = []
            while i < len(lines) and lines[i].startswith('> '):
                quote_lines.append(inline_format(lines[i][2:].strip()))
                i += 1
            # P1: 保留引用块内的换行，不压成一行
            quote_inner = '<br/>'.join(quote_lines)
            html_parts.append(
                f'<blockquote style="border-left: 4px solid #F4845F; '
                f'padding: 12px 16px; margin: 16px 0; '
                f'background: #FFF7F3; color: #4a4a4a; '
                f'font-size: 14px; line-height: 1.8;">'
                f'{quote_inner}</blockquote>'
            )
            continue

        # 无序列表
        if re.match(r'^[-*+] ', line):
            if not in_list or list_type != 'ul':
                if in_list:
                    html_parts.append(f'</{list_type}>')
                html_parts.append(
                    '<ul style="margin: 12px 0; padding-left: 24px; '
                    'font-size: 15px; line-height: 2;">'
                )
                in_list = True
                list_type = 'ul'
            text = re.sub(r'^[-*+] ', '', line).strip()
            html_parts.append(
                f'<li style="margin-bottom: 6px;">{inline_format(text)}</li>'
            )
            i += 1
            continue

        # 有序列表
        if re.match(r'^\d+\. ', line):
            if not in_list or list_type != 'ol':
                if in_list:
                    html_parts.append(f'</{list_type}>')
                html_parts.append(
                    '<ol style="margin: 12px 0; padding-left: 24px; '
                    'font-size: 15px; line-height: 2;">'
                )
                in_list = True
                list_type = 'ol'
            text = re.sub(r'^\d+\. ', '', line).strip()
            html_parts.append(
                f'<li style="margin-bottom: 6px;">{inline_format(text)}</li>'
            )
            i += 1
            continue

        # 代码块
        if line.startswith('```'):
            if in_list:
                html_parts.append(f'</{list_type}>')
                in_list = False
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith('```'):
                code_lines.append(lines[i])
                i += 1
            i += 1  # 跳过结束 ```
            code_text = '\n'.join(code_lines)
            html_parts.append(
                f'<pre style="background: #f6f8fa; border-radius: 6px; '
                f'padding: 12px 16px; margin: 16px 0; '
                f'font-size: 13px; font-family: Consolas, Monaco, monospace; '
                f'line-height: 1.6; overflow-x: auto; '
                f'color: #333;"><code>{escape_html(code_text)}</code></pre>'
            )
            continue

        # 图片
        img_match = re.match(r'!\[([^\]]*)\]\(([^)]+)\)', line.strip())
        if img_match:
            if in_list:
                html_parts.append(f'</{list_type}>')
                in_list = False
            alt = img_match.group(1)
            src = img_match.group(2)
            html_parts.append(
                f'<p style="text-align: center; margin: 16px 0;">'
                f'<img src="{escape_html(src)}" alt="{escape_html(alt)}" '
                f'style="max-width: 100%; height: auto; '
                f'border-radius: 4px; display: block; margin: 0 auto;" />'
                f'</p>'
            )
            i += 1
            continue

        # 分隔线
        if line.strip() in ('---', '***', '___'):
            if in_list:
                html_parts.append(f'</{list_type}>')
                in_list = False
            html_parts.append(
                '<hr style="border: none; border-top: 1px solid #e5e5e5; '
                'margin: 24px 0;" />'
            )
            i += 1
            continue

        # 普通段落
        if in_list:
            html_parts.append(f'</{list_type}>')
            in_list = False
            list_type = None

        para_lines = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not is_block_start(lines[i]):
            para_lines.append(lines[i].rstrip())
            i += 1

        para_text = ' '.join(para_lines).strip()
        html_parts.append(
            f'<p style="font-size: 15px; line-height: 2; '
            f'margin: 0 0 16px 0; color: #333; '
            f'text-align: justify;">{inline_format(para_text)}</p>'
        )

    if in_list:
        html_parts.append(f'</{list_type}>')

    return '\n'.join(html_parts)


def is_block_start(line: str) -> bool:
    """判断一行是否是块级元素的开始。"""
    stripped = line.strip()
    if stripped.startswith('## '): return True
    if stripped.startswith('### '): return True
    if stripped.startswith('> '): return True
    if re.match(r'^[-*+] ', stripped): return True
    if re.match(r'^\d+\. ', stripped): return True
    if stripped.startswith('```'): return True
    if stripped.startswith('!['): return True
    if stripped in ('---', '***', '___'): return True
    return False


def inline_format(text: str) -> str:
    """处理行内格式：加粗、行内代码、链接。"""
    # 行内代码
    text = re.sub(
        r'`([^`]+)`',
        lambda m: (
            f'<code style="background: #f6f8fa; padding: 2px 6px; '
            f'border-radius: 3px; font-size: 13px; '
            f'font-family: Consolas, Monaco, monospace; '
            f'color: #d6336c;">{escape_html(m.group(1))}</code>'
        ),
        text
    )
    # 加粗
    text = re.sub(
        r'\*\*([^*]+)\*\*',
        lambda m: f'<strong style="font-weight: bold; color: #1a1a1a;">{m.group(1)}</strong>',
        text
    )
    # 斜体
    text = re.sub(
        r'(?<!\*)\*([^*]+)\*(?!\*)',
        lambda m: f'<em>{m.group(1)}</em>',
        text
    )
    # 链接
    text = re.sub(
        r'\[([^\]]+)\]\(([^)]+)\)',
        lambda m: (
            f'<a href="{escape_html(m.group(2))}" '
            f'style="color: #F4845F; text-decoration: none;">{m.group(1)}</a>'
        ),
        text
    )
    return text


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

    def _upload_media(self, file_path: str, media_type: str = 'image') -> dict:
        """上传永久素材，返回 media_id。"""
        token = self.get_access_token()
        url = (
            f'{self.BASE_URL}/cgi-bin/material/add_material?'
            f'access_token={urllib.parse.quote(token)}'
            f'&type={media_type}'
        )

        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"封面图不存在：{file_path}")

        file_size = path.stat().st_size
        if file_size > 10 * 1024 * 1024:
            raise ValueError("封面图不能超过 10MB")

        # P4: 校验文件类型必须是图片
        mime_type = mimetypes.guess_type(file_path)[0] or 'image/jpeg'
        if not mime_type.startswith('image/'):
            raise ValueError(f"封面图必须是图片文件，当前文件类型：{mime_type}")
        boundary = f'----WebKitFormBoundary{uuid.uuid4().hex}'

        body = []
        body.append(f'--{boundary}')
        body.append(f'Content-Disposition: form-data; name="media"; filename="{path.name}"')
        body.append(f'Content-Type: {mime_type}')
        body.append('')
        body.append(path.read_bytes())
        body.append(f'--{boundary}--')
        body.append('')

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
                return json.loads(resp.read().decode('utf-8'))
        except urllib.error.URLError as e:
            raise RuntimeError(f"上传素材失败：{e}")

    def upload_cover_image(self, image_path: str) -> str:
        """上传封面图为永久素材，返回 media_id（用作草稿 thumb_media_id）。"""
        # P6: 微信永久素材接口返回 media_id，草稿接口的 thumb_media_id 字段使用同一 ID
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
        token = self.get_access_token()
        url = (
            f'{self.BASE_URL}/cgi-bin/media/uploadimg?'
            f'access_token={urllib.parse.quote(token)}'
        )

        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"正文图片不存在：{image_path}")

        mime_type = mimetypes.guess_type(image_path)[0] or 'image/jpeg'
        if not mime_type.startswith('image/'):
            raise ValueError(f"正文图片必须是图片文件，当前类型：{mime_type}")

        boundary = f'----WebKitFormBoundary{uuid.uuid4().hex}'
        body = []
        body.append(f'--{boundary}')
        body.append(f'Content-Disposition: form-data; name="media"; filename="{path.name}"')
        body.append(f'Content-Type: {mime_type}')
        body.append('')
        body.append(path.read_bytes())
        body.append(f'--{boundary}--')
        body.append('')

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
            raise RuntimeError(f"上传正文图片失败：{e}")

        if 'url' not in result:
            err_code = result.get('errcode', 'unknown')
            if err_code == 48001:
                raise RuntimeError(
                    f"上传正文图片失败：账号未认证（errcode=48001）。"
                    f"正文本地图片上传需要已认证的公众号，"
                    f"请在公众号后台手动替换图片，或改用外部图片链接。"
                )
            raise RuntimeError(
                f"上传正文图片失败：errcode={err_code}, "
                f"errmsg={result.get('errmsg', 'unknown')}"
            )
        return result['url']


# ─── 主流程 ────────────────────────────────────────────────────────────

def upload_local_images(md_text: str, api: 'WechatAPI', md_dir: Path) -> str:
    """扫描 Markdown 正文中的本地图片路径，上传到微信素材库并替换为 CDN URL。

    只处理非 http/https 的本地路径。远程 URL 原样保留。
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

    return re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_img, md_text)


def validate_config(config: dict) -> None:
    """校验配置文件结构和必填字段类型，发现问题时打印具体提示。

    只做警告，不抛异常——凭证缺失由 publish_article 负责报错。
    """
    wechat = config.get('wechat', {})
    if not isinstance(wechat, dict):
        print("[WARN] 配置文件 wechat 节必须是对象（{}），当前格式有误", file=sys.stderr)
        return

    str_fields = ['app_id', 'app_secret', 'default_author']
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


def extract_digest(md_text: str, max_len: int = 120) -> str:
    """从正文提取摘要：取第一段非标题、非空行的文本。

    过滤策略：
    - 跳过标题行（# 开头）
    - 加粗开头的引用块（> ** 开头）是 Skill 元信息标签，整行跳过
    - 普通引用块去掉 > 前缀后纳入候选
    """
    lines = md_text.strip().split('\n')
    content_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith('#'):
            continue
        if stripped.startswith('> '):
            inner = stripped[2:].strip()
            # 加粗开头的引用块是 Skill 元信息（如「使用假设」「输出格式」），跳过
            if inner.startswith('**'):
                continue
            stripped = inner
        if not stripped:
            continue
        content_lines.append(stripped)
        if sum(len(l) for l in content_lines) >= max_len:
            break

    digest = ''.join(content_lines)[:max_len]
    return digest



def publish_article(
    md_file: str,
    cover_image: str = None,
    config: dict = None,
    author: str = None,
    digest: str = None
) -> dict:
    """
    将 Markdown 文章发布到微信公众号草稿箱。

    返回包含 media_id 和文章信息的字典。
    """
    config = config or {}
    wechat_cfg = config.get('wechat', {})
    brand_cfg = config.get('brand', {})

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

    # 读取 Markdown 文件
    md_path = Path(md_file)
    if not md_path.exists():
        raise FileNotFoundError(f"Markdown 文件不存在：{md_file}")

    md_text = md_path.read_text(encoding='utf-8')
    title, body = extract_title_and_body(md_text)

    if not title:
        raise ValueError("Markdown 文件中未找到一级标题（# 开头的行）")

    print(f"[INFO] 文章标题：{title}")

    # 初始化 API（提前初始化，下面图片上传也需要用到）
    api = WechatAPI(app_id, app_secret)

    # 如果正文有本地图片，先批量上传并替换 URL
    md_text = upload_local_images(md_text, api, md_path.parent)

    # 转换为 HTML
    html_content = md_to_wechat_html(md_text)
    print(f"[INFO] HTML 转换完成，约 {len(html_content)} 字符")

    # 上传封面图（如果提供）
    thumb_media_id = ''
    if cover_image:
        print(f"[INFO] 上传封面图：{cover_image}")
        thumb_media_id = api.upload_cover_image(cover_image)
        print(f"[INFO] 封面图 media_id：{thumb_media_id[:10]}...")
    else:
        print("[WARN] 未提供封面图，草稿将使用空白封面（可在公众号后台替换）")

    # 摘要
    if not digest:
        digest = extract_digest(md_text, 120)

    # 作者
    if not author:
        author = wechat_cfg.get('default_author', '')

    # 构建文章
    article = {
        'title': title,
        'author': author,
        'digest': digest,
        'content': html_content,
        'thumb_media_id': thumb_media_id,
        'need_open_comment': int(wechat_cfg.get('need_open_comment', 0)),
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
        'author': author,
        'digest': digest,
        'has_cover': bool(thumb_media_id),
    }


def main():
    parser = argparse.ArgumentParser(
        description='微信公众号草稿发布工具：Markdown → 草稿箱'
    )
    parser.add_argument('markdown', help='Markdown 文章文件路径')
    parser.add_argument('--cover', help='封面图路径（可选）')
    parser.add_argument('--config', help='配置文件路径（可选）')
    parser.add_argument('--author', help='作者名（可选，覆盖配置）')
    parser.add_argument('--digest', help='摘要（可选，默认自动提取）')
    parser.add_argument('--html-only', action='store_true',
                        help='只输出 HTML，不上传到公众号')

    args = parser.parse_args()

    # 只生成 HTML 模式
    if args.html_only:
        md_path = Path(args.markdown)
        if not md_path.exists():
            print(f"[ERROR] 文件不存在：{args.markdown}", file=sys.stderr)
            sys.exit(1)
        md_text = md_path.read_text(encoding='utf-8')
        html = md_to_wechat_html(md_text)
        out_path = md_path.with_suffix('.html')
        out_path.write_text(html, encoding='utf-8')
        print(f"[OK] HTML 已生成：{out_path}")
        return

    # 加载配置
    config = load_config(args.config)

    try:
        result = publish_article(
            md_file=args.markdown,
            cover_image=args.cover,
            config=config,
            author=args.author,
            digest=args.digest,
        )
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
        # P2: 捕获 ValueError（如无标题）以及其他已知错误
        print(f"\n[ERROR] {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[INFO] 已取消", file=sys.stderr)
        sys.exit(130)


if __name__ == '__main__':
    main()
