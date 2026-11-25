# 用户个性化配置

本 Skill 支持通过本地配置文件持久化用户偏好，避免每次使用都重复指定账号定位、作者调性、品牌色、公众号凭证等信息。

## 配置文件位置

按以下优先级查找配置文件，找到即停：

1. **项目级配置**：当前项目根目录下的 `.wechat-writer-config.json`
2. **用户级配置**：用户主目录下的 `~/.config/wechat-writer/config.json`
3. **Skill 内置默认值**：无配置文件时使用默认参数

配置文件为私有文件，不应提交到版本控制。`.gitignore` 中已排除。

## 配置项说明

### author — 作者与调性

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `name` | string | `""` | 作者署名，用于文末或公众号原文作者字段 |
| `bio` | string | `""` | 一句话个人简介，有需要时可以作为固定结尾 |
| `signature` | string | `""` | 固定签名档，追加在每篇文章末尾（留空则不追加） |
| `tone` | string | `"indie-dev"` | 默认作者调性：`indie-dev` / `hardcore-tech` / `promo` |
| `fixed_cta` | string | `""` | 固定 CTA 文案，有需要时覆盖自动生成的 CTA |
| `voice_samples` | string[] | `[]` | 作者历史代表作本地文件路径（建议 1–3 篇），写前抽样对齐个人句长、节奏和语感（不照搬旧文事实） |

### positioning — 账号定位

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `primary_audience` | string | `""` | 账号长期服务的具体读者；比“泛技术爱好者”更具体 |
| `content_pillars` | string[] | `[]` | 稳定内容栏目，用于判断选题是否偏离账号定位 |
| `reader_problems` | string[] | `[]` | 目标读者反复遇到的问题，用于确定点击理由和核心收益 |
| `avoid_topics` | string[] | `[]` | 明确不做或已验证不适合账号的主题 |

生成文章时优先使用这里的长期定位，再结合用户本次要求确定具体读者。配置为空时从用户素材和历史文章推断，不为了填配置而中断写作。

### wechat — 公众号发布

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `app_id` | string | `""` | 微信公众号 AppID（发布到草稿箱时必需） |
| `app_secret` | string | `""` | 微信公众号 AppSecret（发布到草稿箱时必需，**严禁提交到公开仓库**） |
| `default_author` | string | `""` | 草稿的默认作者名 |
| `default_digest_source` | string | `"summary_section"` | 摘要来源：`summary_section` / `first_paragraph` / `manual`；手动模式必须传入 `--digest` |
| `need_open_comment` | boolean | `true` | 是否打开评论；默认核心目标包含互动，因此默认开启 |
| `only_fans_can_comment` | boolean | `false` | 是否仅粉丝可评论 |

**安全提醒：** `app_secret` 是敏感凭证。建议通过环境变量 `WECHAT_APP_SECRET` 注入，不要明文写在配置文件里。如果写在配置文件中，确保配置文件已加入 `.gitignore`。

### brand — 品牌视觉

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `primary_color` | string | `"#F4845F"` | 正文图片和 HTML 的主强调色（十六进制）；封面仅在用户明确要求品牌统一时使用 |
| `secondary_color` | string | `"#FDE68A"` | 正文图片的辅助色（十六进制）；封面默认不继承 |
| `html_theme` | string | `"warm"` | HTML 转换与预览内置主题：`warm`（暖橙默认）/ `minimal`（极简黑白）/ `tech`（深蓝科技） |
| `cover_style` | string | `"editorial"` | 内容无法明确路由时的封面兜底风格：`editorial` / `result-led` / `technical` |
| `use_orange_cat_ip` | boolean | `true` | 是否允许生成 AI 正文图；生成的正文图必须使用橘猫。设为 `false` 时仅使用原始真实素材或纯文字降级，不生成无橘猫的正文图；封面始终禁用固定 IP |

### output — 输出偏好

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `title_count` | number | `3` | 备选标题数量（3-5），默认覆盖明确收益、认知冲突和身份共鸣三种传播假设 |
| `digest_min_length` | number | `40` | 摘要最小字数 |
| `digest_max_length` | number | `80` | 摘要最大字数 |
| `forward_copy_count` | number | `2` | 转发文案数量（1-3） |
| `image_mode` | string | `"auto"` | 配图模式：`auto` / `full` / `text-only` |

### performance — 发布表现

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `history_file` | string | `"~/.local/share/wechat-writer/performance.jsonl"` | 手工记录文章表现的 JSONL 文件；路径中的 `~` 按用户主目录解析 |
| `lookback_count` | number | `10` | 生成前最多参考多少条最近的同栏目记录 |

表现文件每行一个 JSON 对象。除最终标题和传播假设外，记录标题的具体主钩子、目标读者和分发条件，避免把不可比文章混在一起。指标只填写公众号后台实际可见的数据；没有的指标保留 `null`，不要估算：

```json
{"account":"示例账号","article_type":"项目复盘","content_pillar":"AI 编程实战","audience":"使用 AI 工具的独立开发者","title":"AI 没让流程更简单，它只是把难点换到了验证","title_angle":"认知冲突","title_hook":"效率直觉与验证成本的冲突","published_at":"2026-07-27","distribution_context":"常规发布，无额外社群分发","metrics":{"impressions":null,"reads":null,"average_read_time":null,"shares":null,"favorites":null,"likes":null,"comments":null,"new_followers":null},"notes":"首屏反馈较好，转发较少"}
```

字段名称可以随公众号后台实际提供的指标调整。只有后台实际提供 `impressions` 时才填写并比较同口径点击表现；只有阅读量时，不把差异单独归因给标题。Skill 只比较同一账号、同一口径、相近主题且分发条件相近的记录，不把单篇波动当成稳定结论。详细读取和使用规则见 `recommendation-loop.md`。

推荐友好复盘可选增加 `clicks`、`read_through_rate`、`completion_rate`、`negative_feedback`、`recommendation_observation` 和 `trend_context`。只有后台实际提供的指标才填写；推荐入口未知时写 `unknown`，不要把未观察到推荐当成没有推荐。`trend_context` 记录当时的事件/版本、核实来源和分发条件，避免把热点带来的短期波动误判成标题公式。

## 配置优先级

当用户输入与配置文件不一致时，按以下优先级覆盖（高优先级覆盖低优先级）：

1. **用户本次明确指定**（如"用推广种草调性"）
2. **项目级配置文件**（`.wechat-writer-config.json`）
3. **用户级配置文件**（`~/.config/wechat-writer/config.json`）
4. **Skill 内置默认值**

## 配置读取规则

- Skill 触发时先检查是否存在配置文件
- 只读取与当前任务相关的配置项，不需要每次全量加载
- 配置缺失时静默回退到默认值，不报错
- 敏感字段（`app_secret`）检查环境变量优先：若环境变量 `WECHAT_APP_SECRET` 存在，则覆盖配置文件中的值
