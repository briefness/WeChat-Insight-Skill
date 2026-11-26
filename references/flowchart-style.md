# 微信公众号流程图图片生成

只有当文章需要流程图（工作流、步骤图、架构图、决策树等）时才读取这个 reference。

纯叙事性插图（场景/比喻图）走 `cartoon-illustrations.md`。流程图以信息为主；当 `brand.use_orange_cat_ip` 为 `true`（默认）时，AI 生成流程图须让橘猫承担明确信息角色；关闭时直接生成无吉祥物的手绘信息图。

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
| 多步骤操作教程（≥ 3 步） | ✅ 如「安装 → 配置 → 运行 → 验证」 |
| 决策分支 | ✅ 如「有 Key？→ 是/否 分支」 |
| 技术架构关系 | ✅ 如模块间数据流 |
| 简单的因果或顺序关系 | ❌ ≤ 2 步且无分支，用文字 + 序号即可，不用生成图 |

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

与橘猫插图保持同一手绘风格，并把橘猫作为语义参与者融入图表。图表仍以信息优先，不能为了放猫压缩节点、遮挡文字或制造无关装饰。

生成任何图表前，先读取 `references/design-system.md`，获取全局风格 token 和配色系统。图表类图片的专属风格词如下，叠加在全局 token 之后使用。

> ⚠️ 实际生成 prompt 时，先将 `design-system.md` 全局视觉 Token 代码块的内容（从 `Hand-drawn aesthetic...` 行起）内联写入，**不要把 `[GLOBAL STYLE — ...]` 标识行复制进 prompt**，再在其后追加以下专属风格词：

```text
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

## 橘猫融入规则（仅 `brand.use_orange_cat_ip: true` 时执行）

当配置 `brand.use_orange_cat_ip` 为 `true`（默认）时，橘猫是每张 AI 生成正文图的固定 IP，生成前必须为其指定功能角色——流程发起者、结果接收者、状态对比体验者、概念使用者或检查执行者；找不到角色时重构图表，不得删猫了事。若配置为 `false`，跳过本节及下方模板中的橘猫块，保持手绘节点和简洁信息表达即可。

### 判断方式

先写出角色说明：`橘猫代表谁，正在做什么，帮助理解哪段流程或关系？`

- 能写出来 → 把角色、动作和节点绑定关系写进 prompt
- 写不出来（猫只是站在旁边看）→ 重选入口/结果节点、简化图表或改用另一种带猫图型

> ⚠️ **流程图中橘猫必须介入某个节点的内容，禁止站在节点外侧或流程图旁边作装饰。** 橘猫必须在节点内部执行动作，它的肢体动作本身等于该节点描述的步骤。移除橘猫后该节点的核心动作必须明显缺失；如果移除后流程图依然完整，说明橘猫只是背景，必须重新设计角色位置再生成。

### 核心设计原则：动作即内容

**猫的动作必须是图中某个节点或概念的具象化，不是旁观者姿态。**

猫"站在节点旁边指一下"是最低限度，更好的做法是让猫的肢体动作本身就等于那个流程步骤：

| 节点内容 | 差的融入方式 | 好的融入方式 |
|----------|------------|------------|
| 用户提问 | 猫站在节点左边看着 | 猫双手捧着写有「?」的纸条，把它递进节点 |
| 检索知识库 | 猫指向书架 | 猫趴在书架上翻书，手指滑过书脊找目标页 |
| 生成回答 | 猫站在节点右边 | 猫从最后节点接过一张答案纸，点头确认 |
| 旧方案痛点 | 左列放一只看起来不高兴的猫 | 猫坐在散落的文件堆里抓头，状态本身就是"信息混乱" |
| 向量相似度 | 猫指向两个圆圈 | 猫拿着放大镜对比两张卡片，眉头紧锁找相似点 |

**一句话检验：** 把猫的动作用一个动词描述出来，这个动词应该和节点的标签词直接对应。对应得上 → 融入合理。对应不上 → 改动作、节点或图表结构，不能删猫了事。

### 各图类型的强制融入方式

| 图类型 | 橘猫的叙事角色 | 加法 |
|--------|--------------|------|
| 线性流程图（A） | 流程的「发起者」或「接收者」 | 猫在第一个节点内提交输入，或在最后节点内验收结果 |
| 原理示意图（D） | 机制的「触发者」或结果验证者 | 猫操作输入控件、投放对象或接住输出，让动作直接触发机制 |
| 对比清单图（E） | 左右两种状态的体验者 | 同一只猫在两侧执行对应动作，用动作差异承载对比，不只改变表情 |
| 分支决策图（B） | 决策的发起者 | 猫位于分支入口节点内，手持真实选项并执行选择动作 |
| 架构关系图（C） | 系统使用者或结果接收者 | 增加明确的“用户入口”或“结果接收”节点，让猫在节点内提交请求或验收输出；节点过密时先简化架构，不把猫移到图外 |

### Prompt 写法

加猫前先确定"动作动词"，再写 prompt。动词要和节点标签直接对应。

每张图都在 prompt 末尾补充与当前图型匹配的橘猫角色描述：

```text
# 流程图起点加猫（动作即内容写法）
Add a small cute chubby orange tabby cat (round body, dot eyes, warm orange fur #F4845F,
hand-drawn ink style) representing [the specific user role].
The cat's body action IS the first step: [具体肢体动作描述，动词对应节点标签].
Example actions:
- "用户提问" → cat holds up a small paper card with a "?" written on it with both paws,
  actively handing/pushing it into the first node
- "检索知识库" → cat leans into a bookshelf, one paw sliding along the book spines,
  scanning for the right page
- "生成回答" → cat receives a paper coming out of the last node, reads it and nods
The cat should be small — no larger than the node height. Do not overlap with any label text.

# 对比图两侧加猫（动作即内容写法）
Left column: the cat embodies the before-state through a specific action —
  [描述猫的身体姿态，如：sitting in a pile of scattered papers, pawing at its head in confusion]
Right column: the same cat embodies the after-state through a contrasting action —
  [描述猫的身体姿态，如：sitting upright, holding a neat single sheet, looking satisfied]
Both cats same hand-drawn ink style, small size, not overlapping any labels.

# 原理图加猫（动作即内容写法）
Add a small orange tabby cat representing the user.
The cat's action concretely represents the input step:
  [描述猫的身体动作，如：holding a speech bubble card and feeding it into the mechanism's input]
Small size, does not overlap any content.
```


### 加猫的边界

- **猫的尺寸**：不超过最小节点的高度，猫是配角不是主角
- **不遮挡文字**：猫位于内容节点的视觉区域或专用交互边界内，但不压住节点标签、箭头或关键数据
- **风格一致**：和正文叙事插图里的橘猫保持同一造型（圆润身体、点状眼睛、橘色虎斑）
- **克制**：一张图里最多一只猫（对比图例外，左右各一只）
- **不做背景**：不能放在角落旁观、躲在节点后面、做水印或只负责“可爱”

---

## 配色方案

所有正文流程图统一继承 `design-system.md` 全局色板（暖白背景 `#FAFAF8` + 墨黑手绘线 `#1A1A1A`），单图不超过 3 种主色，暖橙 `#F4845F` 始终保持为视觉重心：

| 方案 | 主色 | 辅色 | 适用调性 |
|------|------|------|----------|
| **暖橙常规**（默认） | 暖橙 `#F4845F` | 浅黄 `#FDE68A` + 暖白 `#FAFAF8` | 独立开发者 / 教程 / 产品流程 |
| **暖橙深蓝对比** | 暖橙 `#F4845F`（视觉重心） | 深海蓝 `#0F172A`（次级/底层模块）+ 暖白 `#FAFAF8` | 硬核技术 / 系统架构 |

在 prompt 里用自然语言描述配色，例如：
- 暖橙常规：`warm orange (#F4845F) primary nodes with light yellow (#FDE68A) highlights on warm white (#FAFAF8) background`
- 暖橙深蓝对比：`warm orange (#F4845F) focal nodes with deep navy (#0F172A) supporting system nodes on warm white (#FAFAF8) background`

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
# 必填：按上方「橘猫融入规则」补充橘猫在起点或终点节点内执行的具体动作
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
# 必填：按上方「橘猫融入规则」让橘猫在分支入口节点内手持选项执行决策动作
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
# 必填：提供明确的“用户入口”或“结果接收”节点，让橘猫在节点内提交请求或验收输出
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

> ⚠️ 实际生成 prompt 时，先将 `design-system.md` 全局视觉 Token 代码块的内容（从 `Hand-drawn aesthetic...` 行起）内联写入，**不要把 `[GLOBAL STYLE — ...]` 标识行复制进 prompt**，再在其后追加以下原理图专属风格词：

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
- 原理图的核心元素是一个「能被一眼认出来的具体物件」（书架、计价器、过滤网、工作台），避免泛化的“大脑”意象
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
Visual metaphor: [用什么具体比喻或意象来承载这个概念]
Key elements to label: [需要标注的 2-4 个关键词，直接复用文章里的词]
Layout: [描述图的大致构图，如「中心一个大元素，四周标注」或「左右对比」]
# 必填：按上方「橘猫融入规则」让橘猫触发机制输入或验收输出结果
```

**示例：**

- RAG 检索增强生成：
```text
Hand-drawn concept diagram, loose sketchy ink outlines, flat warm orange fills,
light yellow accents, white background, handwritten labels. No PPT style. WeChat 4:3.

Concept: RAG retrieval-augmented generation — AI looks up a knowledge base before answering
Visual metaphor: a bookshelf connected to an answer workbench by a dotted search arrow
Key elements: left bookshelf labeled "知识库", dotted arrow labeled "查资料",
center workbench labeled "大模型", output card on right labeled "回答"
Layout: left to right flow, labels in small handwritten Chinese.
Orange tabby cat leans into the bookshelf sliding a paw along book spines to pull out the matching card and pass it along the dotted arrow.
```

- Token 计费原理：
```text
Hand-drawn concept diagram, loose sketchy ink outlines, flat warm orange fills,
white background, handwritten-style Chinese annotations. No PPT style. WeChat 4:3.

Concept: the more text you send and receive, the more tokens are consumed and billed
Visual metaphor: an old-fashioned taxi meter with a speech bubble feeding into it
Key elements: speech bubble on left labeled "你说的话", meter in center labeled "Token 计数",
coin dropping at bottom labeled "计费", small number display labeled "上下文窗口"
Layout: horizontal, left to right flow, meter is the visual anchor in the center.
Small orange tabby cat holds up the speech bubble card and feeds it into the meter slot.
```

---

### 类型 E：对比清单图

适用：两组内容的对比展示，如「适合 vs 不适合」「方案 A vs 方案 B」「之前 vs 之后（数据维度多）」。与类型 D 的区别：原理图用意象承载概念，对比图用分栏结构承载列表。

常见触发场景：

- 「适合/不适合」「推荐/不推荐」「✅ / ❌」的对比列表
- 两种或多种方案并列，有明确比较维度（成本、速度、适用场景）
- 具体数字的多维度前后对比

**视觉风格定义（生成时必带）：**

> ⚠️ 实际生成 prompt 时，先内联 `design-system.md` 全局视觉 Token（从 `Hand-drawn aesthetic...` 行起），**不复制 `[GLOBAL STYLE — ...]` 标识行**，再追加以下对比图专属风格词：

```text
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

**Prompt 模板（使用时将全局 token 内联在开头，再拼接以下内容，不要保留方括号占位符）：**

```text
# 先内联 design-system.md 全局视觉 Token（Hand-drawn aesthetic... 起的全部内容）
# 再接以下对比图描述：

Comparison chart style: hand-drawn two-column layout, dotted vertical divider,
warm orange rounded header on left, light gray rounded header on right,
white background, handwritten Chinese text, loose hand-drawn borders. 4:3 aspect ratio.

Left column header: "[填入正面标签，如「✅ 适合」]"
Left column items (handwritten-style):
- "[填入条目1]"
- "[填入条目2]"
- "[填入条目3]"

Right column header: "[填入负面或对比标签，如「❌ 不适合」]"
Right column items:
- "[填入条目1]"
- "[填入条目2]"

# 必填：左右两列各放同一只小橘猫，用截然不同的肢体动作体现两种状态对比
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
| 节点数上限 | 推荐 **3–5 个节点**，硬上限 **7 个节点**；超过 5 个优先考虑拆图，超过 7 个必须拆成两张竖向拼接 |
| 文字标注 | 单条中文标注推荐 **2–4 个汉字**（硬上限 **6 个汉字**），单图中文标注 **≤ 4 处**（节点较多的流程优先用英文专有名词或拆图） |
| 背景 | 暖白 `#FAFAF8`，不用深色底（微信夜间模式会反色） |

> 节点超过 7 个时，将流程拆成两张图分别生成，每张不超过 7 个节点。用 PIL 脚本竖向拼接，在两张图中间插入一条深色横向标注条（如「第一阶段」/「第二阶段」），标注条背景色用 `#1A1A1A`，白色文字。拼接后总高度不超过宽度的 2 倍，避免手机滑动过多。

---

## 工作流

### Step 1：判断是否需要图表

通读文章，标出有以下特征的段落：

**触发流程图/架构图（A/B/C）：**
- 出现了「流程」「步骤」「先…再…然后」「流水线」「pipeline」
- 有明确的节点数（≥ 3 步）且顺序重要
- 有条件分支（「如果…就…否则…」）
- 技术架构涉及多个模块交互

**触发原理示意图（D）：**
- 在解释一个技术概念/机制的「为什么」或「怎么工作的」
- 文章里出现了生活化比喻，且比喻需要标注 2 个以上技术概念
- 涉及 AI 原理（RAG、Embedding、Attention）、协议机制（缓存、Token 计费）等抽象概念

**触发对比清单图（E）：**
- 两组方案、优缺点、适用 vs 不适用场景并列对比

**不生成图，改用文字 + 序号（① ② ③）：**
- 步骤 ≤ 2 且无分支、逻辑简单
- 概念可以一句大白话说清，不需要视觉辅助

### Step 2：选图表类型和配色

| 内容特征 | 选择类型 |
|----------|----------|
| 步骤明确、单向推进（≥ 3 步） | A（线性流程图）|
| 有条件判断、分叉 | B（分支决策图）|
| 多模块交互、数据流向 | C（架构关系图）|
| 技术概念/机制原理解释 | D（原理示意图）|
| 两组方案/优缺点/适用边界对比 | E（对比清单图）|

配色默认暖橙常规，硬核技术或系统架构需要深色对比时选暖橙深蓝对比（参考上方配色方案表）。

### Step 3：写 Prompt 并生成

套用对应模板，填入文章里的真实节点名称和标注。节点标注**直接复用文章里已有的词**，不另起新词；再追加橘猫的角色、动作、节点绑定、布局位置和移除测试描述。

用当前环境可用的图片生成工具（如 `generate_image`）生成后，立即用 `![流程图：XXX](路径)` 嵌入正文对应位置。

### Step 4：生成后检查

- [ ] 不读正文也能看懂这张图在说什么
- [ ] 节点文字在手机屏幕上清晰可读（不小于正文字号）
- [ ] 箭头方向明确，不产生歧义
- [ ] 橘猫位于明确的节点或交互边界内，动作与节点标签直接对应
- [ ] 移除橘猫后至少一个动作、状态或交互边界的表达会缺失
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

**按功能决定怎么加橘猫，不决定加不加。** 每张 AI 生成正文图都必须让橘猫承担信息角色、执行与流程直接相关的动作，且移除后会损失至少一个节点、状态或交互边界的表达。检查不通过时重构图表，不能把猫作为背景或装饰来维持视觉 IP。
