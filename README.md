# WeChat-Insight-Skill

一个面向 Antigravity IDE 的微信公众号写作 Skill。它把想法、项目、技术资料和博客改写成适合微信传播的完整草稿：有人味、有结构、方便扫读，并且默认交付可发布成稿。

## 能做什么

- 技术科普：把复杂概念翻译成泛读者能理解的大白话
- 教程干货：提供明确步骤、结果、踩坑和收藏清单
- 项目复盘：提炼真实结果、工程取舍和失败处理
- 行业观察：形成有证据、有边界的明确观点
- 产品推广：先交付价值，再用真实证据自然引出产品
- 文档改写：把技术博客和项目资料改成手机阅读友好的公众号版本
- 公众号布局：自动处理短段落、标题层级、重点句、列表、引用、图片位置、代码和表格降级
- **一键发布**：生成 Markdown 后可直接推送到公众号草稿箱，正文本地图片自动上传素材库，免去手动复制排版
- **多轮修改**：针对已输出文章的局部调整有标准化修改流程，不全文重写
- **个性化配置**：支持作者信息、品牌色、公众号凭证等持久化配置，不用每次重复指定

完整成稿默认必须包含一段有来源的真实实践，以及一个讲清场景、现象、原因、处理和验证的真实坑点。Skill 会优先从项目代码、日志、提交、测试结果和用户陈述中取证；如果只有主题或参考文档，则主动检索权威资料、真实案例和数据补全文章，而不是把素材缺口直接交还用户。

外部案例会明确标注主体和来源，不会伪装成作者亲历；关键数据会说明时间、范围、统计口径和对比基准。

默认使用独立开发者调性：有人味但不油腻，有观点但不煽动，像一个靠谱的工程师复盘自己做过的事。

## 安装

将整个仓库放入 Antigravity IDE 的 Skills 目录，并确保目录名为 `wechat-article-writer`：

```text
~/.antigravity/skills/wechat-article-writer/
```

也可以放到项目级 Skills 目录，具体位置以当前 IDE 版本的配置为准。重新加载 Skills 后即可通过自然语言触发。

## 使用

```text
帮我写一篇公众号，介绍我用 Python 做的自动剪视频工具
```

```text
把这篇技术博客改写成公众号版本，读者是泛技术爱好者
```

```text
写一篇推广 Seedance API 的软文，用独立开发者调性
```

```text
把这篇文章发到公众号草稿箱，封面用刚才生成的图
```

```text
标题再改改，换成更有悬念的风格
```

Skill 会优先根据素材推断文章类型、目标读者和核心目标；只有信息缺失会明显改变文章方向、造成事实错误或引发合规风险时才追问。

默认按以下顺序输出：

1. 使用假设
2. 5 个备选标题，并标记 1 个推荐标题
3. 40-80 字公众号摘要
4. 完整正文，包含小标题、重点、图片和 CTA
5. 1-2 条朋友圈或社群转发文案
6. 只包含真实待办的发布前检查

## 图片模式

### 完整图文模式

环境有可用图片工具，且用户没有要求只输出文字时，Skill 会：

- 主动判断哪些段落值得可视化
- 优先使用用户提供的真实截图和素材
- 生成叙事插图、流程图、原理图或封面
- 将图片以 Markdown 图片语法嵌入正文
- 用户未选标题时，用标记为“推荐”的标题生成封面

### 纯文字降级模式

图片工具不可用，或用户明确只要文字稿时，Skill 会输出包含图片类型、画面内容、关键标注和比例的配图建议，并在发布前检查中明确说明图片尚未生成。

## 发布到公众号草稿箱

生成完稿后可以直接推送到微信公众号草稿箱，免去手动复制、粘贴和排版调整。

### 前置条件

- 已认证的微信公众号（服务号或订阅号）
- 公众号 AppID 和 AppSecret
- 服务器 IP 已加入公众号 IP 白名单

### 配置凭证

**推荐：环境变量**

```bash
export WECHAT_APP_ID="你的AppID"
export WECHAT_APP_SECRET="你的AppSecret"
```

**或：配置文件**

复制 `config.example.json` 为 `.wechat-writer-config.json`，填入 wechat 节的 app_id 和 app_secret。

### 触发方式

#### 方式一：自然语言触发（Skill 模式）

在 IDE 中用 Skill 生成文章后，直接说：

```text
把这篇发到公众号草稿箱
```

```text
发布一下，封面用刚才生成的图
```

```text
存草稿箱
```

Skill 会自动保存 Markdown、调用发布脚本、返回结果。失败时（如 IP 不在白名单）会给出具体原因和操作指引。

#### 方式二：命令行调用（脚本模式）

已有 Markdown 文件时，直接运行脚本：

```bash
# 发布文章（自动从配置文件读取凭证）
python tools/publish_to_wechat.py article.md

# 指定封面图
python tools/publish_to_wechat.py article.md --cover cover.jpg

# 指定配置文件
python tools/publish_to_wechat.py article.md --config ~/.config/wechat-writer/config.json

# 指定作者名（覆盖配置文件）
python tools/publish_to_wechat.py article.md --author "张三"

# 指定摘要（不自动提取）
python tools/publish_to_wechat.py article.md --digest "这篇文章讲了..."

# 只生成 HTML 预览，不上传
python tools/publish_to_wechat.py article.md --html-only
```

发布脚本会自动完成以下工作：

- 将 Markdown 转换为公众号兼容的 inline-style HTML
- 扫描正文中的本地图片，自动上传到素材库并替换为 CDN URL
- 上传封面图为永久素材，获取 thumb_media_id
- 自动提取摘要（过滤 Skill 元信息标签）
- access_token 过期时自动刷新重试
- 创建草稿，记录发布历史
- 配置文件格式错误时给出明确警告

详细说明见 [`references/wechat-publish.md`](./references/wechat-publish.md)。

### 发布历史

每次成功发布后，记录会自动追加到：

```text
~/.local/share/wechat-writer/history.jsonl
```

每条记录包含：发布时间、文章标题、media_id、源文件路径，方便回溯和管理。

## 个性化配置

支持通过配置文件持久化用户偏好，避免每次重复指定。

配置文件优先级：

1. 当前项目根目录 `.wechat-writer-config.json`（项目级）
2. `~/.config/wechat-writer/config.json`（用户级）

可配置项：

| 分类 | 字段 | 说明 |
|------|------|------|
| 作者 | name / bio / tone / fixed_cta | 作者名、简介、默认调性、固定 CTA |
| 公众号 | app_id / app_secret / default_author | 发布凭证和默认作者 |
| 品牌 | primary_color / secondary_color / cover_style | 主辅色、默认封面风格 |
| 输出 | title_count / digest_length / forward_copy_count | 标题数量、摘要长度、转发文案数 |

配置模板见 [`config.example.json`](./config.example.json)，详细说明见 [`references/user-config.md`](./references/user-config.md)。

## 文件结构

| 文件 | 作用 | 何时读取 |
|------|------|----------|
| [`SKILL.md`](./SKILL.md) | 触发条件、核心流程、输出契约和 reference 路由 | Skill 触发时 |
| [`references/writing-playbook.md`](./references/writing-playbook.md) | 资料研究、真实案例、数据、标题、结构、调性、CTA 和合规细则 | 生成或改写完整文章时 |
| [`references/wechat-layout.md`](./references/wechat-layout.md) | 公众号正文骨架、留白、标题、列表、图片、代码、表格和编辑器兼容 | 生成完整文章和发布前检查时 |
| [`references/design-system.md`](./references/design-system.md) | 正文图片的全局配色、线条、留白和选图原则 | 生成正文图片前 |
| [`references/cartoon-illustrations.md`](./references/cartoon-illustrations.md) | 叙事、比喻和情绪插图，固定橘猫 IP | 生成叙事插图时 |
| [`references/flowchart-style.md`](./references/flowchart-style.md) | A-E 五类流程、架构、原理和对比图 | 生成信息图时 |
| [`references/cover-image.md`](./references/cover-image.md) | 封面规格、素材合成和三套风格 | 生成封面时 |
| [`references/user-config.md`](./references/user-config.md) | 用户个性化配置文件格式和读取规则 | Skill 启动时 |
| [`references/iteration-mode.md`](./references/iteration-mode.md) | 多轮修改模式工作流和常见场景处理 | 用户提出修改要求时 |
| [`references/wechat-publish.md`](./references/wechat-publish.md) | 公众号草稿箱发布前置条件、流程和错误处理 | 用户要求发布到公众号时 |
| [`tools/publish_to_wechat.py`](./tools/publish_to_wechat.py) | Markdown 转 HTML 并发布到草稿箱的 Python 脚本 | 实际执行发布时 |
| [`examples/demo-article.md`](./examples/demo-article.md) | 完整成稿示例（项目复盘调性，纯文字降级模式） | 需要查看输出形态时 |
| [`config.example.json`](./config.example.json) | 配置文件模板 | 用户需要配置个性化设置时 |

## 视觉规则

- 正文图共享暖白底、手绘线条和暖橙强调色
- 橘猫只能承担具体人物、状态或流程角色，并通过动作帮助解释主题
- 加猫前必须能说清“它代表谁、正在做什么、对理解有什么帮助”
- 不能把橘猫当背景、角落贴纸、品牌水印或无意义装饰
- 叙事插图通常由橘猫承担核心动作；流程图和封面按内容判断，不强制出现
- 图片只在提高理解、记忆或可信度时生成，不做纯装饰
- 微信正文不使用 Mermaid 或网页交互组件

## 适用边界

| 目标读者 | 建议 |
|----------|------|
| 刷到后顺便阅读的微信用户 | 使用本 Skill |
| 主动学习完整代码和架构的开发者 | 先写技术博客，再提炼公众号版本 |

## License

[MIT](./LICENSE) © 2025
