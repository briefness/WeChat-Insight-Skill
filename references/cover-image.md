# 微信公众号封面图生成

只有当需要为文章实际生成封面图时才读取这个 reference。

纯文字降级模式不需要读取本文，按 `SKILL.md` 的格式输出封面建议。

## 目录

1. 规格与安全区
2. 两种生成路径
3. 调性风格
4. 文字标注规则
5. 工作流
6. 生成后检查

---

## 规格与安全区

| 用途 | 比例 | 推荐尺寸 | 备注 |
|------|------|----------|------|
| 头条封面 | 2.35:1 | 1068×455px | 主视觉必须在中心安全区内 |
| 次条封面 | 1:1 | 300×300px | 头条图中心区域会被自动裁成 1:1 |

**安全区规则：** 头条封面在订阅号列表和朋友圈分享时会被裁成约 1:1，只保留中间部分。因此：

- 标题文字、主视觉元素必须放在**水平居中、垂直居中**的区域
- 两侧各留约 20% 的边距作为裁切缓冲
- 不能把关键信息放在图片边缘

生成时直接使用 **2.35:1** 比例，在 prompt 中明确写 `ultra-wide 2.35:1 cinematic aspect ratio`，并强调所有主视觉元素集中在画面中央 60% 区域内，两侧留空。无需生成后手动裁切。

---

## 两种生成路径

### 路径 A：有真实素材（优先）

用户提供了项目截图、效果帧、产品界面等真实素材时，优先用 PIL 脚本合成封面，不用纯 AI 生成。真实素材比 AI 生成图更有说服力，尤其是技术文章。

合成逻辑：
1. 底图：深色纯色底（`#1A1A2E` 或 `#0F172A`）
2. 主视觉：将真实素材居中放置，适当缩放留出边距
3. 标题文字：叠加在主视觉上方或下方，用高亮色（白色或品牌色）
4. 宽度输出 1068px，高度按 2.35:1 计算约 455px

> 如需 PIL 合成脚本，直接生成并运行，不依赖本 reference。

---

### 路径 B：纯 AI 生成

没有真实素材，或用户明确要求 AI 生成封面时使用。根据文章调性选对应风格。

生成前先读取 `references/design-system.md`，只取「全局配色系统」中的色板数值和「IP 角色：橘猫」定义。**不要把正文图片的全局风格 token（`Hand-drawn aesthetic...` 那段）粘贴进封面 prompt**——封面有独立的风格模板，直接按下方「调性风格」对应的 Prompt 模板重新写。封面图按所选风格使用以下覆盖规则：

- **背景按风格覆盖**：独立开发者风格使用暖白底；推广种草和硬核技术风格可使用深色底
- **配色部分继承**：暖橙（`#F4845F`）作为强调色，与正文插图保持呼应
- **线条按风格覆盖**：独立开发者风格保留手绘感；其他风格使用各自模板定义的设计语言

---

## 调性风格

### 风格一：独立开发者（默认）

手绘海报风，有个性、有温度、有记忆点。与正文插图风格语言一致，但不强制为了统一 IP 而加入橘猫。

**视觉特征：**
- 暖白底（`#FAFAF8`），角落有极低透明度手绘纹理，像一张手绘海报
- 只有能把文章主题转成明确动作时，才让橘猫成为主视觉；例如 RAG 文章中“翻资料再回答”，自动化文章中“按下按钮触发流程”
- 如果橘猫只能站在标题旁边、充当背景或增加可爱感，改用真实成果、核心物件或主题意象作为主视觉
- 加粗手写感主标题 + 副标题，无分类 tag
- 唯一强调色：暖橙（`#F4845F`），不引入其他颜色
- 靠温度和个性吸引眼球，不靠装饰堆叠

**Prompt 模板：**

```text
WeChat article cover image in hand-drawn poster style.
ultra-wide 2.35:1 cinematic aspect ratio (much wider than tall).

SAFE ZONE: All text and illustration MUST be placed within the CENTER 60% of the image width.
The leftmost 20% and rightmost 20% must remain empty background only —
this ensures content survives a 1:1 center crop on WeChat feeds.

Background: warm off-white (#FAFAF8), very subtle hand-drawn sketch texture —
faint loose pencil-stroke hatching at extremely low opacity in the corners,
giving a paper-like tactile feel. Not distracting.

Center zone layout (within middle 60% of width, vertically centered):
- LEFT HALF of center zone — Typography block:
  - Main title "[文章标题]" in large bold dark ink (#1A1A1A), strong weight,
    slightly imperfect edges suggesting hand lettering
  - Subtitle "[副标题]" in medium dark gray (#4B5563), smaller, one line below title
  - NO category tag, NO badge, NO pill label of any kind

- RIGHT HALF of center zone — Illustration:
  - Use the orange cat only when it has a functional narrative role.
  - The cat represents [specific person or state] and actively performs [topic-defining action].
  - Its action helps explain [core topic, contrast, or outcome]. Never use it as background decoration.
  - Cat design when used: round body, dot eyes, warm orange fur (#F4845F), hand-drawn brown stripes.
  - Around the cat: 2-3 small hand-drawn floating elements related to the topic
    (e.g., lightbulb, magnifying glass, book pages, code brackets)
  - All elements in sketchy ink style, warm orange or dark ink color
  - Everything feels loose, organic, hand-crafted

Color palette: warm white + dark ink + warm orange (#F4845F) only.
No harsh blacks, no neon, no gradients.
Feels like a hand-illustrated zine or indie tech blog cover.
Eye-catching through character and warmth, not loud colors.
```

**示例：**

```text
WeChat article cover in hand-drawn poster style.
ultra-wide 2.35:1 cinematic aspect ratio.

SAFE ZONE: all content within center 60% of width. Left 20% and right 20% are empty background.

Background: warm off-white (#FAFAF8), faint corner hatching texture.

Center zone — right half illustration:
A chubby orange tabby cat represents the person asking an AI question.
The cat actively searches an open reference book, finds the relevant page, and then points toward an answer bubble.
This action visually explains "retrieve information before answering", rather than using the cat as decoration.
Floating elements: small lightbulb, magnifying glass, loose book pages — sketchy ink style.

Center zone — left half typography:
- Title "RAG 是什么" in large bold dark ink (#1A1A1A)
- Subtitle "让 AI 先查资料再回答" in dark gray (#4B5563)
- NO tag, NO label, NO badge

Color: warm white + dark ink + warm orange only. Hand-crafted zine aesthetic.
```

---

### 风格二：推广种草

有设计感，视觉冲击力更强。适合产品推广、工具测评类文章。

**视觉特征：**
- 渐变底（深色到中色，如深蓝 → 紫，深绿 → 青）
- 标题文字加光晕或描边效果
- 主视觉区放产品截图 mockup 或效果对比
- 可以有少量装饰性光点/粒子，不过度

**Prompt 模板（使用时将方括号内容替换为具体值，不要把方括号文字输出进 prompt）：**

```text
Modern tech product cover image, gradient background from [深色] to [中色],
bold centered title text with subtle glow effect,
product screenshot or UI mockup placed center-right with perspective tilt,
small accent particles or light dots in background (sparse, not cluttered),
high contrast, visually striking but not garish,
suitable for WeChat article header, wide 16:9 format, centered safe zone.

Title text: "[文章标题]"
Product name label: "[产品名]"
```

---

### 风格三：硬核技术

信息图风格，代码感强。适合架构分析、源码解读、深度技术文章。

**视觉特征：**
- 深黑底（纯黑 `#000000` 或 `#0D1117` GitHub 风）
- 主视觉是代码块、终端截图或架构图的局部放大
- 标题文字用等宽字体风格（prompt 里描述，不是真的等宽）
- 配色用终端绿 `#00FF41` 或蓝 `#58A6FF` 作为强调色

**Prompt 模板（使用时将方括号内容替换为具体值，不要把方括号文字输出进 prompt）：**

```text
Dark hacker-aesthetic tech cover, pure black or very dark background (#0D1117),
monospace-style bold title text in terminal green or code blue centered in image,
background texture suggestion of code lines (faint, low opacity, not distracting),
one focused visual element: a code block fragment or terminal output mockup,
high contrast minimal design, no stock photo people,
suitable for WeChat article header, wide 16:9 format, centered safe zone.

Title text: "[文章标题]"
```

---

## 文字标注规则

- 封面标题直接用文章的**最终选定标题**，不用备选标题
- 字数超过 18 字的标题，考虑拆成主标题 + 副标题两行
- 中英文之间加空格（盘古之白）
- 专有名词按官方写法（Seedance / FFmpeg / Node.js）

---

## 工作流

### Step 1：确认调性和路径

- 用户有真实素材 → 路径 A（PIL 合成）
- 无素材，独立开发者调性 → 路径 B 风格一
- 无素材，推广种草调性 → 路径 B 风格二
- 无素材，硬核技术调性 → 路径 B 风格三

### Step 2：确认标题文字

取文章已确定的标题。若用户尚未选择，直接使用备选标题中标记为“推荐”的标题生成封面，不中断本轮交付。

### Step 3：生成

套用对应 prompt 模板，填入标题和关键视觉元素，用当前环境可用的图片生成工具（如 `generate_image`）生成。

生成后立即检查（见下方），不满足则调整 prompt 重新生成。

---

## 生成后检查

- [ ] 主视觉和标题文字都在画面**水平垂直居中**区域，两侧留有边距
- [ ] 模拟裁成 1:1（只看中间正方形区域）：标题仍然完整可读
- [ ] 配色与文章调性匹配，不过度花哨
- [ ] 标题文字清晰，手机屏幕小图预览时仍可辨认
- [ ] 没有出现模糊的 AI 人脸或手（如有立刻重新生成）
- [ ] 独立开发者风格：没有营销感，看起来像真人做的东西
- [ ] 如使用橘猫，能明确说出它代表谁、正在做什么、如何帮助理解主题；不能只是背景或装饰
