# 用户个性化配置

本 Skill 支持通过本地配置文件持久化用户偏好，避免每次使用都重复指定作者调性、品牌色、公众号凭证等信息。

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

### wechat — 公众号发布

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `app_id` | string | `""` | 微信公众号 AppID（发布到草稿箱时必需） |
| `app_secret` | string | `""` | 微信公众号 AppSecret（发布到草稿箱时必需，**严禁提交到公开仓库**） |
| `default_author` | string | `""` | 草稿的默认作者名 |
| `default_digest_source` | string | `"first_paragraph"` | 摘要来源：`first_paragraph` / `manual` |
| `need_open_comment` | boolean | `false` | 是否打开评论 |
| `only_fans_can_comment` | boolean | `false` | 是否仅粉丝可评论 |

**安全提醒：** `app_secret` 是敏感凭证。建议通过环境变量 `WECHAT_APP_SECRET` 注入，不要明文写在配置文件里。如果写在配置文件中，确保配置文件已加入 `.gitignore`。

### brand — 品牌视觉

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `primary_color` | string | `"#F4845F"` | 主强调色（十六进制） |
| `secondary_color` | string | `"#FDE68A"` | 辅助色（十六进制） |
| `cover_style` | string | `"indie-dev"` | 封面默认风格：`indie-dev` / `promo` / `hardcore-tech` |
| `use_orange_cat_ip` | boolean | `true` | 是否启用橘猫 IP |

### output — 输出偏好

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `title_count` | number | `5` | 备选标题数量（3-7） |
| `digest_min_length` | number | `40` | 摘要最小字数 |
| `digest_max_length` | number | `80` | 摘要最大字数 |
| `forward_copy_count` | number | `2` | 转发文案数量（1-3） |
| `image_mode` | string | `"auto"` | 配图模式：`auto` / `full` / `text-only` |

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
