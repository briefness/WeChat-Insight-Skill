# 微信公众号卡通插图生成

只有当用户明确需要为公众号文章生成插图、封面图或具体图片 prompt 时，才读取这个 reference。

如果只是写文章草稿，不需要读取本文；在正文里用 `> 【配图位：XXX】` 标清楚即可。

---

## IP 角色：橘猫

每张插图的固定主角是同一只可爱简笔画橘猫。每次生成时都必须带上以下 IP 描述，确保跨图一致性：

```text
Recurring IP character: a cute chubby orange tabby cat in simple sketch style —
round body, small dot eyes, tiny nose, orange fur with light brown stripes,
little paws, expressive face. Same consistent design across all illustrations.
The cat must actively perform the core action of the scene, not stand decoratively beside it.
```

**橘猫典型动作池**（根据场景选一个）：

| 场景 | 动作 |
|------|------|
| 写代码/工作 | 坐在笔记本前专注敲键盘，表情略紧张 |
| 踩坑/出错 | 被一堆文件压住，或盯着报错信息发呆 |
| 前后对比·左 | 焦虑地抱着乱糟糟的东西 |
| 前后对比·右 | 放松地举着整洁的成果，表情满足 |
| 流程步骤 | 在每个节点做对应的小动作（翻书、敲键盘、按发布键） |
| 比喻场景 | 直接成为比喻的一部分（如坐在出租车计价器旁边） |
| 思考/洞察 | 托腮沉思，旁边飘着灯泡 |
| 完成/庆祝 | 举着爪子，表情开心 |

---

## 工作流

### Step 1：找配图锚点

通读文章草稿，标出适合用插图提升理解、记忆或转发意愿的位置。

好的配图锚点：

- **概念比较**：两种方案、两种状态、前后对比
- **流程或因果**：A 导致 B，或步骤 1 -> 步骤 2 -> 步骤 3
- **核心比喻**：文章里已经出现的生活化比喻，例如「Token 像出租车计价器」
- **情绪节点**：开头的痛点场景、结尾的行动号召

每篇文章通常配 2–4 张插图。不要每节都配，插图太密会分散注意力。

### Step 2：规划 Shot List

生成前，先为每张图写一个简短规划：

```markdown
【插图 N】
- 位置：第 X 节「XXX」段落之后
- 主题：用一句话说清楚要传递的信息
- 构图模式：左右对比 / 流程箭头 / 单场景 / 数据示意
- 橘猫动作：橘猫在做什么（必须是执行动作）
- 画面描述：具体元素、道具、文字标注
```

标注文字优先直接复用文章里已有的比喻、关键词或小标题，不另起新词。

### Step 3：用统一风格生成

生成前先读取 `references/design-system.md`，获取全局风格 token 和配色系统。叙事插图的专属风格词如下，叠加在全局 token 之后使用：

```text
[GLOBAL STYLE — 见 design-system.md]

Illustration-specific style:
Hand-drawn cartoon illustration style, loose sketchy ink outlines with slight wobble,
flat color fills using the global palette (warm orange #F4845F as accent, light yellow #FDE68A as highlight),
clean white background (#FAFAF8), generous whitespace with subject occupying 40%-60% of the frame,
friendly and approachable tone, slight imperfections in line work to feel human and organic,
sparse handwritten-style Chinese annotations in the scene,
no photorealism, no 3D rendering, no slick vector gradients, no PPT infographic style,
suitable for WeChat articles. Aspect ratio 16:9, wide format.

Recurring IP character: a cute chubby orange tabby cat in simple sketch style —
round body, small dot eyes, tiny nose, orange fur with light brown stripes,
little paws, expressive face. Same consistent design across all illustrations.
The cat must actively perform the core action of the scene, not stand decoratively beside it.
```

Prompt 结构：

```text
[风格定义 + IP描述] + [构图模式] + [场景描述] + [橘猫动作] + [需要出现的文字标注]
```

示例 prompt：

- 对比类：`Hand-drawn cartoon illustration, loose sketchy ink outlines, flat color fills, white background. Recurring IP: cute chubby orange tabby cat, round body, dot eyes, light brown stripes, consistent design. Two panels side by side: left panel shows the orange cat buried under a pile of tangled files looking overwhelmed, right panel shows the same cat relaxed holding up a single clean document with a satisfied expression. Sparse handwritten-style Chinese label "之前" on left and "之后" on right.`
- 流程类：`Hand-drawn cartoon illustration, loose sketchy ink outlines, flat color fills, white background. Recurring IP: cute chubby orange tabby cat, round body, dot eyes, light brown stripes. Three steps connected by hand-drawn arrows: Step 1 the orange cat reading notes with a thinking expression, Step 2 the cat typing on a laptop with focus, Step 3 the cat pressing a publish button with a happy paw-raise. Handwritten-style labels below each step. Generous whitespace above and below.`
- 比喻类：`Hand-drawn cartoon illustration, loose sketchy ink outlines, flat color fills, white background. Recurring IP: cute chubby orange tabby cat, round body, dot eyes, light brown stripes. The orange cat sitting beside a large old-fashioned taxi meter, talking into it with a speech bubble full of scribbled text, coins dropping from the meter's bottom. Sparse handwritten Chinese annotations: "说得越多" near the speech bubble, "花得越多" near the coins, "Token" on the meter face.`

---

## 生成后检查

- 不读正文也能一眼看懂这张图在表达什么。
- 橘猫是画面主角，在执行核心动作，不是站在旁边装饰。
- 颜色明快，手机屏幕上对比度够用。
- 线条有手绘抖动感，不是光滑的矢量线。
- 画面有足够留白，不拥挤。
- 如果有文字标注，经过微信压缩后仍然清晰可读。
- 图片是在帮文章解释和留住读者，而不是单纯装饰。

如果不满足这些检查项，调整 prompt 重新生成，不要将就使用。
