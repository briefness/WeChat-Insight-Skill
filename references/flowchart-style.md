# 微信公众号流程图图片生成

只有当文章需要流程图（工作流、步骤图、架构图、决策树等）时才读取这个 reference。

纯叙事性插图（橘猫场景图）走 `cartoon-illustrations.md`。流程图以信息为主，只在橘猫承担明确的信息角色时例外加入。

## 目录

1. 什么时候用流程图
2. 内容创作原则
3. 视觉风格与橘猫规则
4. 配色方案
5. A-E 图表类型与 Prompt 模板
6. 图片规格
7. 生成工作流与检查

---

## 什么时候用流程图

| 场景 | 适合用流程图 |
|------|------------|
| 工具/系统的处理流程 | ✅ 如「输入 → API 调用 → 后处理 → 输出」 |
| 多步骤操作教程 | ✅ 如「安装 → 配置 → 运行 → 验证」 |
| 决策分支 | ✅ 如「有 Key？→ 是/否 分支」 |
| 技术架构关系 | ✅ 如模块间数据流 |
| 简单的因果或顺序关系 | ❌ 3 步以内，用文字 + emoji 序号即可，不用生成图 |

---

## 内容创作原则（先于风格执行）

**核心目标：读者不看正文只看图，也能理解这个概念或流程。**

图不是文字的重复，是文字的替代。如果图只是把正文里的词抄进方框，这张图是失败的。

### 浅显易懂原则

**① 用日常意象，不用技术黑话**

| ❌ 不好 | ✅ 更好 |
|--------|--------|
| 节点标注「向量检索」 | 节点标注「搜相关内容」 |
| 节点标注「Embedding 层」 | 节点标注「把文字变成数字」 |
| 原理图主体是「数据库」图标 | 原理图主体是「书架」 |

在 prompt 里写节点文字时，先问自己：**一个没学过这个技术的人，能不能秒懂这个词？** 不能就换。

**② 每张图只讲一件事**

- 流程图只展示步骤顺序，不在图里同时解释每个步骤的原理
- 原理图只展示一个核心机制，不把所有相关概念都塞进去
- 超过 5 个节点/元素，优先考虑拆成两张图

**③ 图和文字互补，不重复**

- 图要可视化「关系」和「流向」，文字负责「解释」和「举例」
- 如果正文已经有文字说明了步骤顺序，图的价值是让读者「一眼看懂全貌」，不是再抄一遍

### 讲清楚原则

**① 流程图：每一步都要有动词**

节点文字必须是动作描述，不是名词堆叠：

| ❌ | ✅ |
|----|-----|
| 「用户输入」 | 「用户提问」 |
| 「知识库」 | 「搜知识库」 |
| 「模型」 | 「模型生成回答」 |

**② 原理图：意象必须和概念有因果关联**

选意象时，不是「这个东西看起来像」，而是「这个意象的工作方式和概念的工作方式是一样的」：

- ✅ 用「书架 + 检索箭头」比喻 RAG——因为 RAG 就是「先查书再回答」
- ✅ 用「计价器」比喻 Token 计费——因为两者都是「用多少算多少」
- ❌ 用「大脑」比喻所有 AI 概念——太泛，没有说明力

**③ 标注要指向「为什么」，不只是「是什么」**

标注文字优先用动作或结果描述，而不是名称标签：

| ❌ 名称标签 | ✅ 动作/结果描述 |
|------------|----------------|
| 「知识库」 | 「存你的文档」 |
| 「检索」 | 「找最相关的」 |
| 「上下文」 | 「一起喂给模型」 |

---

## 视觉风格定义

与橘猫插图保持同一手绘风格，默认去除 IP 角色，采用信息优先的图表布局。

生成任何图表前，先读取 `references/design-system.md`，获取全局风格 token 和配色系统。图表类图片的专属风格词如下，叠加在全局 token 之后使用：

```text
[GLOBAL STYLE — 见 design-system.md]

Chart-specific style:
Hand-drawn infographic style, loose sketchy ink outlines with slight wobble,
flat color node fills using the global palette — warm orange (#F4845F) for primary nodes,
light yellow (#FDE68A) for secondary/supporting nodes, white (#FAFAF8) background,
handwritten-style Chinese label text inside or below each node,
arrows with slight curves and hand-drawn arrowheads,
generous whitespace between nodes,
no photorealism, no 3D, no slick gradients, no corporate PowerPoint style,
friendly and approachable, suitable for WeChat mobile reading.
```

---

## 橘猫融入规则

技术图不为维持 IP 曝光而加猫。只有猫承担“用户、流程发起者、决策者或结果接收者”等信息角色，并通过动作帮助解释流程时才可加入。

### 判断要不要加

先完成角色说明：`橘猫代表谁，正在做什么，帮助理解哪段流程或关系？` 然后再问：**如果把猫从图里拿掉，图的信息完整度有没有变化？**

- 没有变化 → 猫只是装饰，不加
- 有变化（猫在扮演某个角色）→ 可以加

### 哪些图适合加

| 图类型 | 橘猫的叙事角色 | 加法 |
|--------|--------------|------|
| 线性流程图（A） | 流程的「发起者」或「接收者」 | 猫站在第一个节点左侧提问，或站在最后节点右侧拿到结果 |
| 原理示意图（D） | 「用户」视角，观察机制运转 | 猫站在意象旁边，带出「它在使用这个东西」的感觉 |
| 对比清单图（E） | 左右两种状态的体验者 | 左列一只困惑猫，右列一只满意猫，强化对比感 |
| 架构关系图（C） | ❌ 通常不加 | 节点密集，猫挤进去会让图变乱 |
| 分支决策图（B） | 视情况 | 只在分支入口处放一只「选择中」的猫，不放在每个分支上 |

### Prompt 写法

加入橘猫时，在图的 prompt 末尾补充：

```text
# 流程图起点加猫
Add a small cute chubby orange tabby cat (round body, dot eyes, warm orange fur #F4845F,
hand-drawn ink style) representing [the specific user role] at the first node.
The cat actively performs [the action that starts the workflow] and directs the result into the first node.
The cat should be small — no larger than the node height. Do not overlap with any label text.

# 对比图两侧加猫
Left column: the cat represents [the before-state user] and actively struggles with [the old process].
Right column: the same cat represents [the after-state user] and actively completes [the improved process].
Both cats in the same hand-drawn ink style, small size, not overlapping any labels.

# 原理图旁边加猫
Add a small orange tabby cat representing the user at the input side of the mechanism,
actively pointing to the first input. Small size, does not overlap any content.
```

### 加猫的边界

- **猫的尺寸**：不超过最小节点的高度，猫是配角不是主角
- **不遮挡文字**：猫的位置必须在留白区域，不压在任何标注或节点上
- **风格一致**：和正文叙事插图里的橘猫保持同一造型（圆润身体、点状眼睛、橘色虎斑）
- **克制**：一张图里最多一只猫（对比图例外，左右各一只）
- **不做背景**：不能放在角落旁观、躲在节点后面、做水印或只负责“可爱”

---

## 配色方案

每张流程图只用一套配色，不混搭。根据文章调性选：

| 方案 | 主色 | 辅色 | 适用调性 |
|------|------|------|----------|
| **暖橙**（默认） | 橙色 `#F4845F` | 浅黄 `#FDE68A` + 白 | 独立开发者 / 教程 |
| **冷蓝** | 钢蓝 `#5B8DEF` | 浅蓝 `#BFDBFE` + 白 | 硬核技术 / 系统架构 |
| **深绿** | 墨绿 `#3D9970` | 浅绿 `#A7F3D0` + 白 | 产品流程 / 自动化 |

默认使用**暖橙**方案，与橘猫插图视觉一致。

在 prompt 里用自然语言描述配色，例如：
- 暖橙：`warm orange nodes with light yellow highlights`
- 冷蓝：`steel blue nodes with light blue accent fills`

---

## 图表类型与 Prompt 模板

### 类型 A：线性流程图（最常用）

适用：步骤明确、单向推进、无分支。

**Prompt 模板：**

```text
Hand-drawn infographic style, loose sketchy ink outlines, flat color fills,
warm orange nodes with light yellow highlights, clean white background,
handwritten-style label text, curved arrows with hand-drawn arrowheads,
generous whitespace. No corporate PowerPoint style. Suitable for WeChat.

Linear flowchart with [N] steps arranged horizontally (or vertically if N > 4):
[步骤1描述] → [步骤2描述] → [步骤3描述] → [步骤N描述]
Each step in a rounded rectangle node. Handwritten Chinese label inside each node.
Brief annotation below each node in smaller text.
```

**示例：**

```text
Hand-drawn infographic style, loose sketchy ink outlines, flat warm orange fills,
light yellow accent, white background, handwritten-style labels, curved arrows.
No PPT style. WeChat mobile reading.

Horizontal linear flowchart, 4 steps:
Node 1 "输入脚本" → Node 2 "调用 API" → Node 3 "后处理" → Node 4 "导出成片"
Rounded rectangle nodes, hand-drawn connecting arrows. Small annotation below each:
"纯文本" / "Seedance" / "FFmpeg 拼接" / "MP4"
```

---

### 类型 B：分支决策图

适用：有条件判断、是/否分叉、多路径。

**Prompt 模板：**

```text
Hand-drawn infographic style, loose sketchy ink outlines, flat color fills,
warm orange rounded rectangles for process nodes,
light yellow diamond shapes for decision nodes,
clean white background, handwritten-style labels, curved arrows with labels "是"/"否".
Generous whitespace. No corporate style. WeChat-friendly.

Decision flowchart:
Start node "[起点描述]"
↓
Diamond decision node "[判断条件]?"
  → 是 → "[结果A节点]"
  → 否 → "[结果B节点]"
[继续描述后续分支]
```

---

### 类型 C：架构关系图

适用：模块间关系、数据流向、系统组成。

**Prompt 模板：**

```text
Hand-drawn infographic style, loose sketchy ink outlines,
flat color fills with warm orange for core modules, light yellow for supporting modules,
clean white background, handwritten-style labels,
bidirectional or directional arrows showing data flow, slight curve on arrows.
Generous whitespace. No 3D. No gradients. WeChat-friendly.

System diagram with [N] components:
[模块A描述] ←→ [模块B描述] → [模块C描述]
Each component in a rounded rectangle. Arrow labels in small handwritten text.
Group related components with a loose dashed boundary if needed.
```

---

### 类型 D：原理示意图

适用：技术概念解释、机制说明、抽象原理可视化。与类型 C 的区别是：架构图侧重「模块之间怎么连」，原理图侧重「一个概念/机制是怎么工作的」。

常见触发场景：

- 解释 AI 技术原理，如 RAG、Attention、Embedding
- 解释协议或机制，如 HTTP 缓存、Token 计费、向量检索
- 解释「之所以这样，是因为……」的因果关系
- 文章里已有生活化比喻，需要把比喻画出来

**与橘猫插图的边界：**
- 纯比喻场景（「Token 像计价器」）→ 优先走橘猫叙事插图，情感优先
- 比喻 + 需要标注多个技术概念（「Token 像计价器，但要同时标出 Input/Output/上下文窗口」）→ 走原理示意图，信息优先

**视觉风格定义（生成时必带）：**

```text
Hand-drawn concept diagram style, loose sketchy ink outlines with slight wobble,
flat color fills — warm orange (#F4845F) for the core concept element or visual anchor,
light yellow (#FDE68A) for supporting/secondary elements,
thin gray or beige for background context elements,
clean white background, generous whitespace,
handwritten-style Chinese label annotations with small dotted leader lines pointing to key parts,
simple iconic illustration to embody the abstract concept (avoid literal diagrams),
no photorealism, no 3D rendering, no slick vector gradients,
no corporate infographic style, no color-coded legend boxes,
friendly and approachable, suitable for WeChat mobile reading. 4:3 aspect ratio.
```

与 A/B/C 类型的视觉差异：
- A/B/C 以**节点 + 箭头**为主结构，原理图以**隐喻意象**为主结构
- 原理图的核心元素是一个「能被一眼认出来的物体」（大脑、书架、计价器），不是方框
- 标注用虚线引出，贴在元素旁边，不在节点内部

**Prompt 模板：**

```text
Hand-drawn concept diagram style, loose sketchy ink outlines,
flat color fills with warm orange for the core concept element,
light yellow for supporting/contextual elements, clean white background,
handwritten-style label annotations pointing to key parts,
simple iconic visual metaphor to represent the abstract concept,
sparse layout with generous whitespace, no busy decorations,
no photorealism, no 3D, no PPT infographic style. WeChat-friendly. 4:3 aspect ratio.

Concept: [用一句话描述要解释的原理或概念]
Visual metaphor: [用什么比喻或意象来承载这个概念]
Key elements to label: [需要标注的 2-4 个关键词，直接复用文章里的词]
Layout: [描述图的大致构图，如「中心一个大元素，四周标注」或「左右对比」]
```

**示例：**

- RAG 检索增强生成：
```text
Hand-drawn concept diagram, loose sketchy ink outlines, flat warm orange fills,
light yellow accents, white background, handwritten labels. No PPT style. WeChat 4:3.

Concept: RAG retrieval-augmented generation — AI looks up a knowledge base before answering
Visual metaphor: a brain connected to a bookshelf by a dotted search arrow
Key elements: center oval labeled "大模型", left bookshelf labeled "知识库",
dotted arrow from bookshelf to brain labeled "检索", output arrow right labeled "回答"
Layout: three elements in a row, center brain is largest, labels in small handwritten Chinese
```

- Token 计费原理：
```text
Hand-drawn concept diagram, loose sketchy ink outlines, flat warm orange fills,
white background, handwritten-style Chinese annotations. No PPT style. WeChat 4:3.

Concept: the more text you send and receive, the more tokens are consumed and billed
Visual metaphor: an old-fashioned taxi meter with a speech bubble feeding into it
Key elements: speech bubble on left labeled "你说的话", meter in center labeled "Token 计数",
coin dropping at bottom labeled "计费", small number display labeled "上下文窗口"
Layout: horizontal, left to right flow, meter is the visual anchor in the center
```

---

### 类型 E：对比清单图

适用：两组内容的对比展示，如「适合 vs 不适合」「方案 A vs 方案 B」「之前 vs 之后（数据维度多）」。与类型 D 的区别：原理图用意象承载概念，对比图用分栏结构承载列表。

常见触发场景：

- 「适合/不适合」「推荐/不推荐」「✅ / ❌」的对比列表
- 两种或多种方案并列，有明确比较维度（成本、速度、适用场景）
- 具体数字的多维度前后对比

**视觉风格定义（生成时必带）：**

```text
[GLOBAL STYLE — 见 design-system.md]

Comparison chart style:
Hand-drawn two-column layout with a dotted vertical divider in the center,
warm orange (#F4845F) rounded label for the positive/left column header,
light gray rounded label for the negative/right column header,
clean white background (#FAFAF8), handwritten-style Chinese text for all items,
hand-drawn border or loose rectangle around each column,
each item as a short line with a small hand-drawn bullet or icon prefix,
generous whitespace above and below, no corporate table style,
no color-coded rows, no grid lines. 4:3 aspect ratio.
```

与其他类型的视觉差异：
- 核心结构是**两栏分列**，不是节点+箭头，不是意象图
- 分栏线用手绘虚线，不是实线表格边框
- 每项内容控制在 **4-6 个汉字**，超过则拆成两行或缩短表达

**Prompt 模板：**

```text
[GLOBAL STYLE — 见 design-system.md]

Comparison chart style: hand-drawn two-column layout, dotted vertical divider,
warm orange rounded header on left, light gray rounded header on right,
white background, handwritten Chinese text, loose hand-drawn borders. 4:3 aspect ratio.

Left column header: "[正面标签，如「✅ 适合」]"
Left column items (handwritten-style):
- "[条目1]"
- "[条目2]"
- "[条目3]"

Right column header: "[负面或对比标签，如「❌ 不适合」]"
Right column items:
- "[条目1]"
- "[条目2]"

Generous whitespace above and below. Clean, minimal, no decorative noise.
```

**示例：**

```text
Hand-drawn infographic style, loose sketchy ink outlines, flat color fills,
warm orange and light gray headers, white background, handwritten Chinese labels.
No PPT style. WeChat 4:3.

Two-column comparison, dotted divider:
Left header "✅ 适合" in warm orange rounded label:
- "企业内部问答"
- "客服机器人"
- "时效性内容"
- "需要溯源"
Right header "❌ 不适合" in light gray rounded label:
- "纯创意任务"
- "知识库为空"
Generous whitespace. Hand-drawn loose borders around each column.
```

---

## 图片规格

| 参数 | 值 |
|------|----|
| 宽高比 | **4:3**（竖屏手机上比 16:9 更好读） |
| 节点数上限 | 单图不超过 **7 个节点**，超过则拆成两张竖向拼接 |
| 文字标注 | 每个节点标注**不超过 6 个汉字**，保证手机屏幕可读 |
| 背景 | 白色或极浅暖灰，不用深色底（微信夜间模式会反色） |

> 节点超过 7 个时，用 PIL 脚本竖向拼接两张图，中间加深色标注条区分「第一阶段」/「第二阶段」。参考 SKILL.md 多图拼接规范。

---

## 工作流

### Step 1：判断是否需要图表

通读文章，标出有以下特征的段落：

**触发流程图/架构图（A/B/C）：**
- 出现了「流程」「步骤」「先…再…然后」「流水线」「pipeline」
- 有明确的节点数（≥ 4 步）且顺序重要
- 有条件分支（「如果…就…否则…」）
- 技术架构涉及多个模块交互

**触发原理示意图（D）：**
- 在解释一个技术概念/机制的「为什么」或「怎么工作的」
- 文章里出现了生活化比喻，且比喻需要标注 2 个以上技术概念
- 涉及 AI 原理（RAG、Embedding、Attention）、协议机制（缓存、Token 计费）等抽象概念

**不生成图，改用文字 + emoji 序号（① ② ③）：**
- 步骤 ≤ 3 且逻辑简单
- 概念可以一句大白话说清，不需要视觉辅助

### Step 2：选图表类型和配色

| 内容特征 | 选择类型 |
|----------|----------|
| 步骤明确、单向推进 | A（线性流程图）|
| 有条件判断、分叉 | B（分支决策图）|
| 多模块交互、数据流向 | C（架构关系图）|
| 技术概念/机制原理解释 | D（原理示意图）|

配色默认暖橙，按文章调性选（参考上方配色方案表）。

### Step 3：写 Prompt 并生成

套用对应模板，填入文章里的真实节点名称和标注。节点标注**直接复用文章里已有的词**，不另起新词。

用当前环境可用的图片生成工具（如 `generate_image`）生成后，立即用 `![流程图：XXX](路径)` 嵌入正文对应位置。

### Step 4：生成后检查

- [ ] 不读正文也能看懂这张图在说什么
- [ ] 节点文字在手机屏幕上清晰可读（不小于正文字号）
- [ ] 箭头方向明确，不产生歧义
- [ ] 配色统一，同图不超过 3 种颜色
- [ ] 手绘感明显，不是光滑的矢量图或 PPT 截图风格
- [ ] 留白充足，节点之间不拥挤

不满足则调整 prompt 重新生成。

---

## 与橘猫插图的组合使用

同一篇文章里，流程图和橘猫插图可以共存，但要分工明确：

| 图类型 | 作用 |
|--------|------|
| 流程图 | 解释结构、流程、关系——信息优先 |
| 橘猫插图 | 传递情绪、比喻、场景——情感优先 |

**按功能决定是否加橘猫。** 只有它承担明确的信息角色、执行与流程直接相关的动作，且移除后会损失表达时才加入。不能把猫作为背景或装饰来维持视觉 IP。
