# 微信公众号封面图生成

只有当需要为文章实际生成封面图时才读取这个 reference。

写文章草稿阶段不需要读取本文，用 `> 【封面图：XXX】` 标注位置即可。

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

生成时始终使用 **16:9** 比例（最接近 2.35:1 且图像模型支持稳定），再在 prompt 里指定主体居中。

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

生成前先读取 `references/design-system.md`，获取全局配色系统和线条规范。封面图有以下覆盖规则：

- **背景色覆盖**：封面图使用深色底（`#0F172A`），覆盖全局的白底规定——这是有意为之的风格差异，让封面与正文插图形成视觉区分
- **配色部分继承**：暖橙（`#F4845F`）作为标题或标签的强调色，与正文插图保持呼应
- **线条风格不适用**：封面图不是手绘图，不需要 sketchy ink outlines，改用简洁设计感

---

## 调性风格

### 风格一：独立开发者（默认）

手绘海报风，有个性、有温度、有记忆点。与正文插图风格语言完全一致，整篇文章从封面到内文视觉统一。

**视觉特征：**
- 暖白底（`#FAFAF8`），角落有极低透明度手绘纹理，像一张手绘海报
- 橘猫 IP 为主视觉，尺寸大、存在感强，周围有少量手绘漂浮小元素（灯泡、放大镜、书页等，与文章主题相关）
- 加粗手写感主标题 + 副标题，无分类 tag
- 唯一强调色：暖橙（`#F97316`），不引入其他颜色
- 靠温度和个性吸引眼球，不靠装饰堆叠

**Prompt 模板：**

```text
WeChat article cover image in hand-drawn poster style, wide 16:9 format, centered safe zone with 20% margins.

Background: warm off-white (#FAFAF8), very subtle hand-drawn sketch texture —
faint loose pencil-stroke hatching at extremely low opacity in the corners,
giving a paper-like tactile feel. Not distracting.

Main illustration (right-center, large, ~40% of image height):
- Cute chubby orange tabby cat IP: round body, dot eyes, warm orange fur (#F97316)
  with hand-drawn brown stripes, expressive face
- Cat is actively doing: [cat action related to article topic]
- Around the cat: 2-3 small hand-drawn floating elements related to the topic
  (e.g., lightbulb, magnifying glass, book pages, code brackets)
- All elements in sketchy ink style, warm orange or dark ink color
- Everything feels loose, organic, hand-crafted

Typography (left side, vertically centered):
- Main title "[文章标题]" in large bold dark ink (#1A1A1A), strong weight,
  slightly imperfect edges suggesting hand lettering
- Subtitle "[副标题]" in medium dark gray (#4B5563), smaller, one line below title
- NO category tag, NO badge, NO pill label of any kind

Color palette: warm white + dark ink + warm orange (#F97316) only.
No harsh blacks, no neon, no gradients.
Feels like a hand-illustrated zine or indie tech blog cover.
Eye-catching through character and warmth, not loud colors.
```

**示例：**

```text
WeChat article cover in hand-drawn poster style, wide 16:9, centered safe zone.

Background: warm off-white (#FAFAF8), faint corner hatching texture.

Right side illustration: chubby orange tabby cat sitting and reading a book,
paws holding it open, curious happy expression.
Floating elements: small lightbulb, magnifying glass, loose book pages — sketchy ink style.

Left side typography:
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

**Prompt 模板：**

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

**Prompt 模板：**

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

取文章已确定的标题。若用户尚未选定标题，先让用户从备选标题里选一个再生成封面。

### Step 3：生成

套用对应 prompt 模板，填入标题和关键视觉元素，用 `generate_image` 生成。

生成后立即检查（见下方），不满足则调整 prompt 重新生成。

---

## 生成后检查

- [ ] 主视觉和标题文字都在画面**水平垂直居中**区域，两侧留有边距
- [ ] 模拟裁成 1:1（只看中间正方形区域）：标题仍然完整可读
- [ ] 配色与文章调性匹配，不过度花哨
- [ ] 标题文字清晰，手机屏幕小图预览时仍可辨认
- [ ] 没有出现模糊的 AI 人脸或手（如有立刻重新生成）
- [ ] 独立开发者风格：没有营销感，看起来像真人做的东西
