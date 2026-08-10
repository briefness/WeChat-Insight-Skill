# WeChat Insight Skill

面向 Codex、Antigravity IDE 及其他兼容本地 Skills 的智能体环境，将主题、项目资料、技术文档和博客整理成可发布的微信公众号图文稿。

它覆盖写前定向研究、证据核验、标题筛选、移动端排版、动态封面、正文配图、HTML 转换和公众号草稿箱发布。

> 微信没有公开完整的推荐算法。本项目优化选题匹配、点击理由、阅读体验和真实反馈，但不承诺文章一定获得推荐。

## 目录

- [核心能力](#核心能力)
- [工作流程](#工作流程)
- [环境要求](#环境要求)
- [安装](#安装)
- [快速开始](#快速开始)
- [示例](#示例)
- [输出格式](#输出格式)
- [图片规则](#图片规则)
- [配置](#配置)
- [HTML 与公众号发布](#html-与公众号发布)
- [安全](#安全)
- [项目结构](#项目结构)
- [开发与测试](#开发与测试)
- [适用边界](#适用边界)
- [贡献](#贡献)
- [许可证](#许可证)

## 核心能力

- **默认写前研究**：生成完整文章前，围绕标题承诺和正文主线检索最新事实、官方资料、真实案例、反例与适用边界。
- **证据优先**：区分用户亲历、项目证据和外部案例；不编造数据、经验时长、结果或来源。
- **五类文章路由**：支持技术科普、教程干货、项目复盘、行业观察和产品推广。
- **标题筛选**：内部生成 6-9 个候选，通过真实性、正文兑现、信息差、账号匹配和移动端可读性门槛后，默认输出 3 个传播假设不同的标题。
- **推荐友好包装**：联动标题、摘要、封面、首屏、正文节奏和 CTA，并使用同账号可比历史表现形成弱证据。
- **移动端排版**：处理短段落、标题层级、重点句、列表、引用、图片、代码和复杂表格降级。
- **内容驱动图片**：封面根据当前文章动态生成；正文图片只在提高理解、记忆或可信度时生成。
- **多轮修改**：局部反馈只修改相关内容，并回扫标题、摘要、正文、图片和 CTA 的一致性。
- **完整交付**：保存 Markdown，并可按需转换 HTML 或发布到微信公众号草稿箱。

写前联网研究默认执行。用户明确要求仅使用所给素材、任务只是局部文字修改或排版，或当前环境无法联网时才跳过。无法联网时，Skill 不会声称已核实最新状态。

## 工作流程

1. 读取用户素材、项目文件、日志、截图、测试结果和历史对话。
2. 提炼标题承诺与正文主线需要补充或核实的信息。
3. 优先检索官方文档、原始数据、标准和 release note，再补充真实案例、issue、公开复盘、反例和限制。
4. 确定具体读者、触发场景、单一收益、独特证据和账号匹配。
5. 生成标题候选并通过内部硬门槛与评分。
6. 按文章类型完成正文、摘要、转发文案、动态封面和必要正文图。
7. 执行事实、合规、移动端排版和承诺一致性检查。
8. 保存 Markdown，再根据用户确认转换 HTML 或发布到草稿箱。

研究只补文章主线需要的信息。核心结论、时效性事实、必要案例或反例和适用边界已有足够支撑时停止，不为增加来源数量堆砌旁支资料。

## 环境要求

### 使用 Skill

- 支持本地 Skills 的 Codex、Antigravity IDE 或兼容智能体环境
- 联网检索能力，推荐启用；不可用时自动降级并标记时效性风险
- 图片生成能力，可选；不可用时输出可执行的配图建议

仓库以根目录中的 `SKILL.md` 和相对路径 `references/` 作为兼容结构。不同客户端的 Skills 目录、联网权限和图片工具可能不同；安装位置与能力授权以对应客户端当前文档为准。

### 使用发布脚本

- Python 3.8 或更高版本
- 无第三方 Python 依赖，脚本仅使用标准库
- 发布到草稿箱时，需要已认证的微信公众号、AppID、AppSecret 和已配置的 IP 白名单

## 安装

### Codex

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/briefness/WeChat-Insight-Skill.git ~/.codex/skills/wechat-article-writer
```

### Antigravity IDE

```bash
mkdir -p ~/.antigravity/skills
git clone https://github.com/briefness/WeChat-Insight-Skill.git ~/.antigravity/skills/wechat-article-writer
```

安装后重新加载 Skills。目标目录根部应直接包含 `SKILL.md`，目录名保持为 `wechat-article-writer`。

项目级 Skills 的位置由具体客户端决定；将本仓库复制或克隆到客户端约定的项目级目录即可。

## 快速开始

安装后直接使用自然语言触发：

```text
帮我写一篇公众号，介绍我用 Python 做的自动剪视频工具
```

```text
把这篇技术博客改写成公众号版本，读者是泛技术爱好者
```

```text
写一篇推广 Seedance API 的文章，用独立开发者调性
```

```text
标题不够吸引人，保留正文事实再优化一版
```

```text
把这篇文章发到公众号草稿箱，封面用刚才生成的图
```

Skill 会优先自主获取可以从上下文、工作区和公开资料取得的信息。只有缺失内容会改变文章立场、核心事实或案例真实性时，才向用户追问最少量信息。

## 示例

[`examples/demo-article.md`](./examples/demo-article.md) 展示了一份完整交付稿，包含使用假设、3 个备选标题、摘要、正文、转发文案和发布前检查。

可以直接验证 HTML 转换：

```bash
python3 tools/publish_to_wechat.py examples/demo-article.md --html-only
```

命令会生成 `examples/demo-article.html`。该 HTML 是带公众号正文预览和复制按钮的本地页面，不会修改 Markdown 源文件。

## 输出格式

完整文章默认按以下顺序交付：

1. 使用假设
2. 3 个备选标题，并标记 1 个推荐标题
3. 40-80 字公众号摘要
4. 完整正文，包含小标题、重点、图片和单一 CTA
5. 1-2 条朋友圈或社群转发文案
6. 只列真实待办的发布前检查

修改完整文章时会追加“本次修改说明”。素材不足以支撑可发布状态时，Skill 会补充证据、提出最少量问题，或明确降级为方法论草稿，不把推测包装成事实。

## 图片规则

### 封面

- 使用微信公众号头条封面比例 `2.35:1`，关键内容兼容中心区域 `1:1` 裁切。
- 从完整正文提取核心对象、真实冲突、结果和证据，不只根据标题生成通用图片。
- 不使用橘猫、动物吉祥物或任何固定 IP。
- 不继承正文的手绘风格或暖白、暖橙、墨黑固定色板。
- 根据文章内容和真实素材动态选择编辑概念、成果聚焦或技术精度方向。

### 正文图片

- 每篇完整图文稿至少包含 1 张有信息价值的正文图。
- 正文图可以使用统一的暖白底、手绘线条和暖橙强调色。
- 默认启用橘猫 IP；启用时必须承担明确的读者、开发者、状态或流程角色，不能作为背景贴纸、水印或无关装饰。
- 流程图、原理图和对比图优先服务理解，不使用 Mermaid 或网页交互组件。

图片工具不可用、生成失败或用户明确要求纯文字时，Skill 会输出包含图片类型、画面内容、关键标注和比例的配图建议，并在发布前检查中说明未生成原因。

## 配置

复制配置模板：

```bash
cp config.example.json .wechat-writer-config.json
```

配置读取优先级：

1. 用户本次明确指定
2. 项目根目录 `.wechat-writer-config.json`
3. `~/.config/wechat-writer/config.json`
4. Skill 内置默认值

主要配置项：

| 分类 | 字段 | 作用 |
|------|------|------|
| 作者 | `name`, `bio`, `signature`, `tone`, `fixed_cta` | 作者信息、签名、默认调性和固定 CTA |
| 定位 | `primary_audience`, `content_pillars`, `reader_problems`, `avoid_topics` | 账号长期读者、栏目和选题边界 |
| 公众号 | `app_id`, `app_secret`, `default_author`, `need_open_comment`, `only_fans_can_comment` | 发布凭证、默认作者和评论设置 |
| 品牌 | `primary_color`, `secondary_color`, `cover_style`, `use_orange_cat_ip` | 正文色板、封面兜底方向和正文 IP 设置 |
| 输出 | `title_count`, `digest_min_length`, `digest_max_length`, `forward_copy_count`, `image_mode` | 标题、摘要、转发文案和图片模式 |
| 表现 | `history_file`, `lookback_count` | 历史表现文件和回看数量 |

完整字段说明见 [`references/user-config.md`](./references/user-config.md)。配置模板见 [`config.example.json`](./config.example.json)。

## HTML 与公众号发布

### 只生成 HTML

Markdown 首行必须是一级标题：

```markdown
# 文章标题
```

运行：

```bash
python3 tools/publish_to_wechat.py article.md --html-only
```

脚本会在 Markdown 同目录生成同名 `.html` 预览页。转换时会移除“使用假设”“备选标题”“摘要”和“正文”包装标题，并截掉“转发文案”“发布前检查”及其后的交付信息，只保留可发布正文。

转换器支持二级/三级标题、粗体、斜体、行内代码、代码块、引用、列表、图片、链接和分隔线。Markdown 表格及复杂 HTML 不受支持，应先改成列表、短段落或图片。

### 发布到草稿箱

优先通过环境变量提供凭证：

```bash
export WECHAT_APP_ID="your_app_id"
export WECHAT_APP_SECRET="your_app_secret"
python3 tools/publish_to_wechat.py article.md --cover cover.jpg
```

常用参数：

```bash
python3 tools/publish_to_wechat.py article.md
python3 tools/publish_to_wechat.py article.md --cover cover.jpg
python3 tools/publish_to_wechat.py article.md --config ~/.config/wechat-writer/config.json
python3 tools/publish_to_wechat.py article.md --author "作者名"
python3 tools/publish_to_wechat.py article.md --digest "公众号摘要"
```

发布脚本会转换 Markdown、上传本地正文图片、按需上传封面、创建草稿并记录发布历史。成功记录保存在：

```text
~/.local/share/wechat-writer/history.jsonl
```

未传入 `--digest` 时，脚本优先使用交付稿中的“摘要”区块；没有该区块时才从正文首段自动提取。

标题及推荐表现由用户按公众号后台实际可见指标补充到：

```text
~/.local/share/wechat-writer/performance.jsonl
```

详细前置条件、Markdown 支持范围和错误处理见 [`references/wechat-publish.md`](./references/wechat-publish.md)。

当前发布边界：

- 只创建公众号草稿，不会自动群发或正式发布。
- 本地正文图片会上传并替换为微信 CDN URL；远程图片保留原 URL，不会自动转存。
- 封面参数可省略，但草稿会使用空白封面，需要在公众号后台补充。
- 每次只发布一篇文章，不支持批量发布。

## 安全

- 不要把 AppSecret、访问令牌或含凭证的配置文件提交到 Git。
- 优先使用 `WECHAT_APP_ID` 和 `WECHAT_APP_SECRET` 环境变量。
- `.wechat-writer-config.json`、`config.local.json`、`.env` 和 `.env.local` 已加入 `.gitignore`。
- 发布前确认服务器公网 IP 已加入微信公众号后台白名单。
- 外部案例必须保留来源归属，不能改写成作者亲历。
- 图片只能使用用户授权、可商用或自行生成的素材。

## 项目结构

| 路径 | 作用 |
|------|------|
| [`SKILL.md`](./SKILL.md) | Skill 触发条件、核心流程、输出契约和 reference 路由 |
| [`references/writing-playbook.md`](./references/writing-playbook.md) | 写前研究、证据、结构、调性、CTA 和合规规则 |
| [`references/recommendation-loop.md`](./references/recommendation-loop.md) | 选题准入、标题筛选、传播包装和历史表现复盘 |
| [`references/wechat-layout.md`](./references/wechat-layout.md) | 公众号移动端排版规则 |
| [`references/cover-image.md`](./references/cover-image.md) | 内容驱动的封面生成与检查规则 |
| [`references/design-system.md`](./references/design-system.md) | 正文图片的视觉系统 |
| [`references/cartoon-illustrations.md`](./references/cartoon-illustrations.md) | 正文叙事插图和橘猫角色规则 |
| [`references/flowchart-style.md`](./references/flowchart-style.md) | 流程、架构、原理和对比图规则 |
| [`references/iteration-mode.md`](./references/iteration-mode.md) | 多轮修改和一致性回扫规则 |
| [`references/wechat-publish.md`](./references/wechat-publish.md) | HTML 转换和公众号发布规则 |
| [`tools/publish_to_wechat.py`](./tools/publish_to_wechat.py) | 无第三方依赖的 Markdown 转换与发布脚本 |
| [`tests/test_publish_to_wechat.py`](./tests/test_publish_to_wechat.py) | 发布脚本回归测试 |
| [`examples/demo-article.md`](./examples/demo-article.md) | 完整文章输出示例 |
| [`config.example.json`](./config.example.json) | 配置模板 |

## 开发与测试

运行回归测试：

```bash
python3 -m unittest discover -s tests -v
```

检查发布脚本命令行参数：

```bash
python3 tools/publish_to_wechat.py --help
```

修改 Skill 规则后，同时检查 `SKILL.md`、相关 `references/` 和 README 是否保持一致。

## 适用边界

| 目标 | 建议 |
|------|------|
| 面向微信信息流读者的科普、教程、复盘、观察或产品文章 | 使用本 Skill |
| 面向专业开发者的完整代码、架构和长期系列内容 | 先写技术博客，再提炼公众号版本 |
| 只需要原样保存用户文字 | 明确要求仅使用所给素材，跳过外部研究 |

## 贡献

欢迎通过 [Issue](https://github.com/briefness/WeChat-Insight-Skill/issues) 报告问题或提出改进建议，也欢迎提交 [Pull Request](https://github.com/briefness/WeChat-Insight-Skill/pulls)。提交前请：

1. 保持改动聚焦，不顺带重写无关规则。
2. 更新与行为变化直接相关的文档。
3. 运行现有回归测试。
4. 确认没有提交本地凭证、缓存或生成产物。

## 许可证

本项目采用 [MIT License](./LICENSE)。
