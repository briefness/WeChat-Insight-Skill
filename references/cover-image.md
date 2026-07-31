# 微信公众号封面图生成

只有当需要为文章实际生成封面图时才读取这个 reference。

纯文字降级模式不需要读取本文，按 `SKILL.md` 的格式输出封面建议。

## 目录

1. 规格与安全区
2. 内容视觉简报
3. 两种生成路径
4. 内容风格路由
5. 文字标注规则
6. 工作流
7. 生成后检查

---

## 规格与安全区

| 用途 | 比例 | 推荐尺寸 | 备注 |
|------|------|----------|------|
| 头条封面 | 2.35:1 | 1068×455px | 主视觉必须在中心安全区内 |
| 次条封面 | 1:1 | 300×300px | 头条图中心区域会被自动裁成 1:1 |

**安全区规则：** 头条封面在订阅号列表和朋友圈分享时会被裁成约 1:1，只保留中间部分。因此：

- 封面短句和主视觉元素必须放在**水平居中、垂直居中**的区域
- 两侧各留约 20% 的边距作为裁切缓冲
- 不能把关键信息放在图片边缘

生成时直接使用 **2.35:1** 比例，在 prompt 中明确写 `ultra-wide 2.35:1 cinematic aspect ratio`，并强调所有主视觉元素集中在画面中央 60% 区域内，两侧留空。无需生成后手动裁切。

---

## 内容视觉简报

封面必须在完整正文完成后，重新从当前文章内容生成视觉概念。禁止沿用固定吉祥物、通用科技背景或与主题无关的模板图。

生成前在内部提取：

1. **核心对象**：文章真正讨论的产品、工具、界面、代码、流程、场景或结果
2. **最强钩子**：正文中最值得点开的真实冲突、变化、反常识判断或可见成果
3. **视觉动作**：什么动作或关系能把钩子变成一眼可懂的画面
4. **证据素材**：是否有截图、效果帧、终端结果、前后对比或实物照片可以直接使用
5. **情绪基调**：克制、紧张、清晰、轻快、专业或实验感，只选一个主基调

主视觉按以下优先级选择：

1. 真实成果或证据素材
2. 与主题直接相关的核心物件或界面
3. 能展示变化的前后对比或动作瞬间
4. 能准确解释核心判断的原创视觉隐喻

**封面禁止使用橘猫、动物吉祥物或任何固定 IP。** 也不要默认使用机器人、大脑电路、灯泡、火箭、漂浮图标、无关人物或抽象科技光效。除非它们就是文章讨论的真实对象，否则都属于通用装饰。

吸引力来自清楚的视觉焦点、真实冲突、可见结果和适度反差，不来自堆元素、夸张表情或高饱和装饰。

---

## 两种生成路径

### 路径 A：有真实素材（优先）

用户提供了项目截图、效果帧、产品界面等真实素材时，优先用 PIL 脚本合成封面，不用纯 AI 生成。真实素材比 AI 生成图更有说服力，尤其是技术文章。

合成逻辑：
1. 底图：从真实素材或文章语义中提取配色，选择能与主体形成明显明暗或冷暖反差的底色
2. 主视觉：将真实素材居中放置，适当缩放留出边距
3. 封面短句：只在有助于识别主题时叠加，从动态封面色板选择高对比文字色；只有用户明确要求品牌统一时才使用品牌色
4. 宽度输出 1068px，高度按 2.35:1 计算约 455px

> 如需 PIL 合成脚本，直接生成并运行，不依赖本 reference。

---

### 路径 B：纯 AI 生成

没有真实素材，或用户明确要求 AI 生成封面时使用。先根据内容视觉简报确定主视觉，再选择最匹配的风格。

封面不继承 `references/design-system.md` 的正文手绘风格或暖白、暖橙、墨黑色板，也不读取橘猫 IP。先从正文内容和真实素材确定独立视觉方向：

- **主体色**：优先取自真实产品、截图、物件或场景；没有素材时根据文章主题和情绪选择
- **对比色**：与主体形成清晰的明暗、冷暖或饱和度反差，保证缩略图仍有视觉焦点
- **强调色**：只用于一个关键动作、结果或短句；不默认使用暖橙
- **品牌色**：只有用户明确要求品牌统一时才使用配置中的品牌色，不因配置存在而自动套用

单张封面通常使用 2-4 种有明确分工的颜色，避免同一色相铺满画面、默认紫蓝渐变、固定深色科技背景或高饱和撞色堆叠。

---

## 内容风格路由

只根据文章内容和可用证据选择：

- 观点、方法、过程故事或抽象概念：编辑概念风格
- 产品体验、工具测评、项目成果或前后变化：成果聚焦风格
- 架构、源码、协议、性能和工程原理：技术精度风格
- 同时符合多类时，选择最能呈现文章核心证据的一类，不混合三套视觉语言

### 风格一：编辑概念（默认）

像杂志专题头图或纪录片主视觉，用一个内容专属的物件、动作或隐喻建立强焦点。适合没有产品截图，但有明确观点、冲突或过程的文章。

**视觉特征：**
- 使用摄影感、真实材质或清晰的数字拼贴，不使用手绘、卡通、纸张纹理或儿童插画感
- 主体占据画面中心，允许局部放大、遮挡或尺度反差，形成明确视觉张力
- 配色从主题语义或主体材质中生成，至少有一组清晰明暗或冷暖反差
- 封面短句使用清晰的现代无衬线字体感，无副标题、无分类 tag
- 只保留能解释核心钩子的辅助元素，不用抽象形状和科技图标填空

**Prompt 模板：**

```text
Premium editorial key art for a WeChat article, cinematic and highly specific to the article.
ultra-wide 2.35:1 cinematic aspect ratio (much wider than tall).

SAFE ZONE: All text and illustration MUST be placed within the CENTER 60% of the image width.
The leftmost 20% and rightmost 20% must remain empty background only —
this ensures content survives a 1:1 center crop on WeChat feeds.

Color direction:
- dominant color: [从文章核心对象、场景或真实素材提取]
- contrasting color: [与主体形成明显明暗或冷暖反差]
- accent color: [只强调核心动作、结果或短句]
- do not default to warm white, warm orange, black, or purple-blue gradients

Center zone layout (within middle 60% of width, vertically centered):
- Typography:
  - Short cover phrase "[封面短句]" in large, bold, modern sans-serif editorial typography
  - The phrase summarizes one visual conflict or result and does not copy the full article title
  - NO subtitle, NO category tag, NO badge, NO pill label of any kind

- Article-specific hero visual:
  - Primary subject: [文章中的核心对象、界面、动作或结果]
  - Visual action or contrast: [把最强钩子转成一个具体动作、前后变化或关系]
  - Evidence cue: [来自正文的真实截图特征、结果形态或可验证细节]
  - Use photorealistic material, crisp digital collage, or a precise conceptual composition depending on the subject
  - One dominant focal point, strong depth or scale contrast, readable at thumbnail size
  - Use only supporting elements that directly explain the subject
  - No mascot, no orange cat, no animal character, no generic robot, brain circuit, lightbulb, rocket, or floating tech icons
  - No hand-drawn poster, sketch lines, paper texture, cartoon style, or generic stock composition

Polished editorial art direction, strong visual hierarchy, intentional negative space,
eye-catching through article-specific tension, scale, contrast, and clarity.
```

**示例：**

```text
Premium editorial key art for a WeChat article.
ultra-wide 2.35:1 cinematic aspect ratio.

SAFE ZONE: all content within center 60% of width. Left 20% and right 20% are empty background.

Hero visual:
A cinematic macro composition of scattered source documents suspended in depth,
narrowing toward one sharply focused reference page and a clean answer panel.
The selected source sentence is visibly highlighted, making
"retrieve evidence before answering" understandable at a glance.
No mascot, no animal character, no generic AI robot or decorative tech icons.

Typography:
- Short cover phrase "先查资料，再回答" in large bold modern sans-serif type
- NO tag, NO label, NO badge

Color: derive the dominant and contrasting colors from the source-document scene,
with one clearly different evidence mark. High editorial contrast, realistic document surfaces,
crisp depth, no hand-drawn treatment.
```

---

### 风格二：成果聚焦

把真实产品、结果界面或前后变化作为第一视觉信号。适合产品体验、工具测评、项目成果和案例复盘。

**视觉特征：**
- 背景颜色从产品或结果素材中提取，并与截图形成清晰边界
- 封面短句使用高对比现代字体，不默认使用光晕、描边或渐变
- 主视觉区放文章实际涉及的产品截图、结果界面、实物或前后对比，保证小图仍能看清结果
- 不添加与产品、结果或文章冲突无关的粒子和科技装饰

**Prompt 模板（使用时将方括号内容替换为具体值，不要把方括号文字输出进 prompt）：**

```text
Premium result-led editorial cover for a WeChat article,
content-derived background color: [从真实产品或结果素材中提取],
high-contrast short cover phrase in modern sans-serif typography,
article-specific primary subject: [正文中的真实产品、界面、结果或对比],
visual hook: [正文中最强的真实冲突、变化或可见成果],
evidence detail: [来自正文或真实素材的具体界面特征、输出或结果],
placed center-right with clear hierarchy,
preserve the real interface or result without inventing UI details,
high contrast, visually striking, readable at thumbnail size,
no mascot, no orange cat, no animal character, no generic robot, brain circuit, lightbulb, rocket, particles, or floating tech icons,
suitable for WeChat article header, ultra-wide 2.35:1 format, centered safe zone.

Short cover phrase: "[封面短句]"
Product name label: "[产品名]"
```

---

### 风格三：技术精度

精密、克制但有张力，适合架构分析、源码解读、性能对比和深度技术文章。

**视觉特征：**
- 背景可明可暗，由真实代码、终端、架构或数据主体决定，不默认使用纯黑或 GitHub 风
- 主视觉是正文实际讨论的代码块、终端结果、性能差异或架构关系的局部放大
- 封面短句用等宽字体风格（prompt 里描述，不是真的等宽）
- 用一组内容相关的对比色区分输入、异常、变化或结果，不默认使用终端绿或代码蓝

**Prompt 模板（使用时将方括号内容替换为具体值，不要把方括号文字输出进 prompt）：**

```text
Precision editorial technology cover for a WeChat article,
content-derived light or dark background: [根据真实代码、终端、架构或数据主体决定],
monospace-style bold short cover phrase with strong readable contrast,
article-specific primary subject: [正文实际讨论的代码、终端结果、性能差异或架构关系],
visual hook: [正文中最强的工程冲突、异常或结果],
evidence detail: [真实字段名、命令结果形态或架构节点，但不编造数值],
one focused technical visual with clear hierarchy,
do not invent code, metrics, logs, or interface details not present in the source,
high contrast editorial design, readable at thumbnail size, no stock photo people,
no mascot, no orange cat, no animal character, no generic robot, brain circuit, lightbulb, rocket, particles, or floating tech icons,
suitable for WeChat article header, ultra-wide 2.35:1 format, centered safe zone.

Short cover phrase: "[封面短句]"
```

---

## 文字标注规则

- 先根据最终选定标题提炼一个封面短句，只保留核心物件、结果或冲突，不复制完整标题
- 封面短句保持一眼可识别；表达不清时宁可不加文字，用真实结果或核心物件承担主题
- 不同时放主标题、副标题和分类标签
- 中英文之间加空格（盘古之白）
- 专有名词按官方写法（Seedance / FFmpeg / Node.js）

---

## 工作流

### Step 1：生成内容视觉简报

从完整正文提取核心对象、最强钩子、视觉动作、证据素材和情绪基调。不能只看标题猜画面。

### Step 2：确认路径和内容风格

- 用户有真实素材 → 路径 A（PIL 合成）
- 无素材，观点、方法、过程故事或抽象概念 → 路径 B 编辑概念
- 无素材，产品体验、工具测评或成果展示 → 路径 B 成果聚焦
- 无素材，架构、源码、协议或工程原理 → 路径 B 技术精度
- 内容无法明确路由时 → 使用 `brand.cover_style` 的兜底方向，但仍按当前文章重新生成主体和配色

### Step 3：确认封面短句

从文章已确定的标题中提炼封面短句。若用户尚未选择，使用备选标题中标记为“推荐”的标题确定主题并提炼，不中断本轮交付。

### Step 4：生成

套用对应 prompt 模板，填入封面短句、文章核心对象、视觉动作、证据细节和情绪基调，用当前环境可用的图片生成工具（如 `generate_image`）生成。

生成后立即检查（见下方），不满足则调整 prompt 重新生成。

---

## 生成后检查

- [ ] 主视觉和封面短句都在画面**水平垂直居中**区域，两侧留有边距
- [ ] 模拟裁成 1:1（只看中间正方形区域）：封面短句和主视觉仍然完整可读
- [ ] 主视觉能对应正文中的核心对象、真实冲突、结果或判断，不是只根据标题生成的通用图
- [ ] 封面没有橘猫、动物吉祥物或任何固定 IP
- [ ] 没有机器人、大脑电路、灯泡、火箭、漂浮图标等与文章无直接关系的通用装饰
- [ ] 没有手绘海报、纸张底纹、卡通线稿或暖白 + 暖橙 + 墨黑固定配色
- [ ] 配色来自文章内容或真实素材，有清楚的明暗、冷暖或饱和度反差，不是同色相铺满画面
- [ ] 封面短句没有复制完整标题，手机屏幕小图预览时仍可辨认；未使用文字时，主视觉本身能识别主题
- [ ] 没有出现模糊的 AI 人脸或手（如有立刻重新生成）
