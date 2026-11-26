#!/usr/bin/env python3
"""
微信公众号发布表现录入与复盘工具
将公众号后台实际可见的数据写入 performance.jsonl，自动关联 history.jsonl 并输出漏斗诊断。

用法:
    python3 tools/record_performance.py --title "文章标题" --reads 1200 --shares 45 --favorites 60
    python3 tools/record_performance.py --latest --reads 800 --shares 20 --notes "首屏完读不错"
    python3 tools/record_performance.py --list 5
"""

import argparse
import datetime
import json
import sys
from pathlib import Path


DEFAULT_HISTORY_FILE = Path.home() / '.local' / 'share' / 'wechat-writer' / 'history.jsonl'
DEFAULT_PERFORMANCE_FILE = Path.home() / '.local' / 'share' / 'wechat-writer' / 'performance.jsonl'


def load_config(config_path: str = None) -> dict:
    """按 Skill 优先级加载配置文件。"""
    candidates = []
    if config_path:
        candidates.append(Path(config_path))
    candidates.append(Path.cwd() / '.wechat-writer-config.json')
    candidates.append(Path.home() / '.config' / 'wechat-writer' / 'config.json')

    for path in candidates:
        if path and path.exists():
            try:
                return json.loads(path.read_text(encoding='utf-8'))
            except json.JSONDecodeError as e:
                print(f"[WARN] 配置文件格式错误：{path} ({e})", file=sys.stderr)
    return {}


def resolve_performance_file(config: dict, override: str = None) -> Path:
    """解析 performance.jsonl 路径，展开 ~。"""
    if override:
        return Path(override).expanduser()
    perf_cfg = config.get('performance', {}) if isinstance(config, dict) else {}
    configured = perf_cfg.get('history_file')
    if configured and isinstance(configured, str):
        return Path(configured).expanduser()
    return DEFAULT_PERFORMANCE_FILE


def read_jsonl(path: Path) -> list:
    """安全读取 JSONL 文件，跳过空行或损坏行。"""
    if not path.exists():
        return []
    records = []
    for line in path.read_text(encoding='utf-8').splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        try:
            records.append(json.loads(stripped))
        except json.JSONDecodeError:
            continue
    return records


def match_publish_history(
    history_records: list,
    title: str = None,
    use_latest: bool = False,
) -> dict:
    """从 history.jsonl 中按标题或最近一条匹配发布记录。"""
    if not history_records:
        return {}
    if title:
        for rec in reversed(history_records):
            if rec.get('title') == title:
                return rec
        for rec in reversed(history_records):
            if title in (rec.get('title') or ''):
                return rec
    if use_latest:
        return history_records[-1]
    return {}


def build_performance_record(
    title: str,
    metrics: dict,
    config: dict = None,
    history_match: dict = None,
    account: str = '',
    article_type: str = '',
    content_pillar: str = '',
    audience: str = '',
    title_angle: str = '',
    title_hook: str = '',
    published_at: str = '',
    distribution_context: str = '常规发布',
    recommendation_observation: str = 'unknown',
    trend_context: str = '',
    notes: str = '',
) -> dict:
    """构建符合 recommendation-loop.md 与 user-config.md 规范的表现记录。"""
    config = config or {}
    positioning = config.get('positioning', {}) if isinstance(config, dict) else {}
    history_match = history_match or {}

    if not published_at:
        raw_time = history_match.get('time', '')
        published_at = raw_time[:10] if len(raw_time) >= 10 else datetime.date.today().isoformat()

    if not audience:
        audience = positioning.get('primary_audience', '')

    metric_keys = [
        'impressions',
        'clicks',
        'reads',
        'read_through_rate',
        'completion_rate',
        'average_read_time',
        'shares',
        'favorites',
        'likes',
        'comments',
        'new_followers',
        'negative_feedback',
    ]
    normalized_metrics = {k: metrics.get(k, None) for k in metric_keys}

    record = {
        'account': account,
        'article_type': article_type,
        'content_pillar': content_pillar,
        'audience': audience,
        'title': title,
        'title_angle': title_angle,
        'title_hook': title_hook,
        'published_at': published_at,
        'media_id': history_match.get('media_id') or None,
        'distribution_context': distribution_context,
        'recommendation_observation': recommendation_observation or 'unknown',
        'trend_context': trend_context,
        'metrics': normalized_metrics,
        'notes': notes,
        'recorded_at': datetime.datetime.now().isoformat(timespec='seconds'),
    }
    return record


def diagnose_record(record: dict) -> list:
    """仅基于实际填写的指标生成可测试的漏斗复盘假设（绝不估算缺失指标）。"""
    m = record.get('metrics', {})
    hints = []

    impressions = m.get('impressions')
    clicks = m.get('clicks')
    reads = m.get('reads')
    shares = m.get('shares')
    favorites = m.get('favorites')
    comments = m.get('comments')
    negative = m.get('negative_feedback')
    completion = m.get('completion_rate')

    if impressions and impressions > 0:
        click_val = clicks if clicks is not None else reads
        if click_val is not None:
            ctr = click_val / impressions
            hints.append(f"同口径打开/点击率约 {ctr:.1%}（点击/阅读 {click_val} / 展示 {impressions}）；若低于账号常态，优先复查标题、摘要与封面一致性。")

    if completion is not None:
        pct = completion * 100 if completion <= 1 else completion
        hints.append(f"完读率 {pct:.1f}%；若偏低，优先检查前 3 段兑现速度与中段信息密度。")

    if reads and reads > 0:
        parts = []
        if shares is not None:
            parts.append(f"转发率 {shares / reads:.1%}")
        if favorites is not None:
            parts.append(f"收藏率 {favorites / reads:.1%}")
        if comments is not None:
            parts.append(f"评论 {comments} 条")
        if parts:
            hints.append("读后行为：" + "，".join(parts) + "；读得多但转发/收藏弱时，下篇强化可复用的清单或对比。")

    if negative is not None and negative > 0:
        hints.append(f"出现负反馈（{negative}）：优先排查题文一致性、广告比例与诱导式文案。")

    if not hints:
        hints.append("已记录可见数据（缺失项保持 null）。同账号累计多篇同口径记录后再归纳稳定偏好。")

    return hints


def append_performance_record(record: dict, perf_file: Path) -> None:
    """追加一条表现记录到 performance.jsonl。"""
    perf_file.parent.mkdir(parents=True, exist_ok=True)
    with open(perf_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(record, ensure_ascii=False) + '\n')


def main():
    parser = argparse.ArgumentParser(
        description='微信公众号发布表现录入与复盘工具（写入 performance.jsonl）'
    )
    parser.add_argument('--title', help='文章标题（不填时可用 --latest 匹配最近发布记录）')
    parser.add_argument('--latest', action='store_true', help='自动匹配 history.jsonl 中最近发布的一篇')
    parser.add_argument('--config', help='配置文件路径（可选）')
    parser.add_argument('--history-file', help='发布历史文件路径（默认 ~/.local/share/wechat-writer/history.jsonl）')
    parser.add_argument('--performance-file', help='表现记录输出路径（覆盖配置）')
    parser.add_argument('--list', nargs='?', const=5, type=int, metavar='N',
                        help='查看最近 N 条表现记录（默认 5 条）')

    # 元信息字段
    parser.add_argument('--account', default='', help='公众号名称（可选）')
    parser.add_argument('--article-type', default='', help='文章类型（如 项目复盘/教程干货/技术科普）')
    parser.add_argument('--pillar', default='', help='内容栏目（content_pillar）')
    parser.add_argument('--audience', default='', help='本篇目标读者')
    parser.add_argument('--title-angle', default='', help='标题传播假设（明确收益/认知冲突/身份共鸣）')
    parser.add_argument('--title-hook', default='', help='标题具体主钩子')
    parser.add_argument('--published-at', default='', help='发布日期 YYYY-MM-DD')
    parser.add_argument('--distribution', default='常规发布', help='分发条件（常规发布/社群分发/投放等）')
    parser.add_argument('--rec-obs', default='unknown', help='推荐入口观察（如 看一看/搜一搜/unknown）')
    parser.add_argument('--trend-context', default='', help='热点/版本背景（可选）')
    parser.add_argument('--notes', default='', help='复盘备注')

    # 后台实际可见指标（缺失即保留 null）
    parser.add_argument('--impressions', type=int, default=None, help='展示量')
    parser.add_argument('--clicks', type=int, default=None, help='点击量')
    parser.add_argument('--reads', type=int, default=None, help='阅读量')
    parser.add_argument('--read-through-rate', type=float, default=None, help='打开率/到达率（0-1 或百分比数值）')
    parser.add_argument('--completion-rate', type=float, default=None, help='完读率（0-1 或百分比数值）')
    parser.add_argument('--avg-read-time', type=float, default=None, help='平均阅读时长（秒）')
    parser.add_argument('--shares', type=int, default=None, help='分享/转发数')
    parser.add_argument('--favorites', type=int, default=None, help='收藏/在看数')
    parser.add_argument('--likes', type=int, default=None, help='点赞数')
    parser.add_argument('--comments', type=int, default=None, help='留言/评论数')
    parser.add_argument('--new-followers', type=int, default=None, help='新增关注数')
    parser.add_argument('--negative-feedback', type=int, default=None, help='负反馈数（投诉/取关等）')

    args = parser.parse_args()
    config = load_config(args.config)
    perf_file = resolve_performance_file(config, args.performance_file)

    if args.list is not None:
        records = read_jsonl(perf_file)
        if not records:
            print(f"[INFO] 暂无表现记录：{perf_file}")
            return
        for rec in records[-args.list:]:
            m = rec.get('metrics', {})
            print(
                f"- [{rec.get('published_at', '?')}] 《{rec.get('title', '未命名')}》 "
                f"阅读={m.get('reads')} 转发={m.get('shares')} 收藏={m.get('favorites')} "
                f"涨粉={m.get('new_followers')} ({rec.get('title_angle') or '未标注角度'})"
            )
        return

    history_file = Path(args.history_file).expanduser() if args.history_file else DEFAULT_HISTORY_FILE
    history_records = read_jsonl(history_file)
    matched = match_publish_history(history_records, title=args.title, use_latest=args.latest)

    final_title = args.title or matched.get('title', '')
    if not final_title:
        print("[ERROR] 请提供 --title，或在存在发布历史时使用 --latest", file=sys.stderr)
        sys.exit(1)

    metrics = {
        'impressions': args.impressions,
        'clicks': args.clicks,
        'reads': args.reads,
        'read_through_rate': args.read_through_rate,
        'completion_rate': args.completion_rate,
        'average_read_time': args.avg_read_time,
        'shares': args.shares,
        'favorites': args.favorites,
        'likes': args.likes,
        'comments': args.comments,
        'new_followers': args.new_followers,
        'negative_feedback': args.negative_feedback,
    }

    record = build_performance_record(
        title=final_title,
        metrics=metrics,
        config=config,
        history_match=matched,
        account=args.account,
        article_type=args.article_type,
        content_pillar=args.pillar,
        audience=args.audience,
        title_angle=args.title_angle,
        title_hook=args.title_hook,
        published_at=args.published_at,
        distribution_context=args.distribution,
        recommendation_observation=args.rec_obs,
        trend_context=args.trend_context,
        notes=args.notes,
    )

    append_performance_record(record, perf_file)
    print(f"[OK] 已写入表现记录：{perf_file}")
    print(f"  标题：《{record['title']}》（发布日期：{record['published_at']}）")
    for hint in diagnose_record(record):
        print(f"  - {hint}")


if __name__ == '__main__':
    main()
