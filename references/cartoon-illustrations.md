# 微信公众号卡通插图生成

只有当用户明确需要为公众号文章生成插图、封面图或具体图片 prompt 时，才读取这个 reference。

如果只是写文章草稿，不需要读取本文；在正文里用 `> 【配图位：XXX】` 标清楚即可。

## 工作流

用 `generate_image` 为文章生成卡通风格配图，分三步走。

### Step 1：找配图锚点

通读文章草稿，标出适合用插图提升理解、记忆或转发意愿的位置。

好的配图锚点：

- **概念比较**：两种方案、两种状态、前后对比
- **流程或因果**：A 导致 B，或步骤 1 -> 步骤 2 -> 步骤 3
- **核心比喻**：文章里已经出现的生活化比喻，例如“Token 像出租车计价器”
- **情绪节点**：开头的痛点场景、结尾的行动号召

每篇文章通常配 2-4 张插图。不要每节都配，插图太密会分散注意力。

### Step 2：规划 Shot List

生成前，先为每张图写一个简短规划：

```markdown
【插图 N】
- 位置：第 X 节「XXX」段落之后
- 主题：用一句话说清楚要传递的信息
- 构图模式：左右对比 / 流程箭头 / 单场景 / 数据示意
- 画面描述：具体元素、角色动作、道具、文字标注
```

### Step 3：用统一风格生成

每次生成图片时，都带上这段英文风格定义。英文保留是为了让图像模型更稳定地理解视觉风格：

```text
Cartoon illustration style, flat design, vibrant colors, clean white background,
friendly and playful tone, simple bold outlines, 2D vector-like art,
no photorealism, no gradients, no shadows, suitable for WeChat articles.
Aspect ratio 16:9, wide format.
```

Prompt 结构：

```text
[风格定义] + [场景描述] + [核心元素] + [需要出现的文字标注]
```

示例 prompt：

- 对比类：`Cartoon illustration, flat design, vibrant colors, white background, two panels side by side: left panel shows a person drowning in tangled video files looking stressed, right panel shows the same person relaxed with a single clean output file, bold Chinese label "之前" on left and "之后" on right.`
- 流程类：`Cartoon illustration, flat design, vibrant colors, white background, three steps connected by arrows: Step 1 a robot reading a script, Step 2 a film clapperboard with sparks, Step 3 a finished video on a phone screen. Simple bold labels below each step.`
- 比喻类：`Cartoon illustration, flat design, vibrant colors, white background, a taxi meter ticking up coins beside a speech bubble full of text, showing the concept that more words cost more tokens. Playful style.`

## 生成后检查

生成后检查：

- 不读正文也能一眼看懂这张图在表达什么。
- 颜色足够明快，手机屏幕上对比度够用。
- 如果有文字标注，经过微信压缩后仍然清晰可读。
- 图片是在帮文章解释和留住读者，而不是单纯装饰。

如果不满足这些检查项，调整 prompt 重新生成，不要将就使用。
