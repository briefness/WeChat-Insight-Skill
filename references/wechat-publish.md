# 公众号发布集成

本 Skill 支持将生成的 Markdown 文章直接发布到微信公众号草稿箱，免去手动复制粘贴和排版调整的麻烦。

## 前置条件

发布功能需要满足以下条件，缺一不可：

### 1. 公众号类型与认证

- **必须**是已认证的微信公众号（服务号或订阅号均可，但必须完成微信认证）
- 未认证的订阅号没有素材管理和草稿箱 API 权限

### 2. 凭证获取

需要在微信公众平台获取：
- **AppID**：开发者 ID
- **AppSecret**：开发者密码

路径：设置与开发 → 基本配置 → 公众号开发信息

### 3. IP 白名单

调用 API 的服务器公网 IP 必须加入公众号的 IP 白名单。

路径：设置与开发 → 基本配置 → IP 白名单

如果调用时返回 `errcode: 40164`，就是 IP 不在白名单。把报错信息里提示的 IP 加进去即可。

### 4. 安全提醒

- **绝对不要**把 AppSecret 提交到公开仓库或分享给他人
- 优先使用环境变量注入，不要明文写在配置文件里
- 配置文件如果包含凭证，必须加入 `.gitignore`

## 使用方法

### 方式一：命令行发布

```bash
# 最简用法（需要先配置凭证）
python tools/publish_to_wechat.py article.md

# 指定封面图
python tools/publish_to_wechat.py article.md --cover cover.jpg

# 指定配置文件
python tools/publish_to_wechat.py article.md --config ~/.config/wechat-writer/config.json

# 只生成 HTML 预览，不上传
python tools/publish_to_wechat.py article.md --html-only
```

### 完稿后按需转换 HTML

生成完整文章并保存为 Markdown 文件后，必须先询问用户：`Markdown 文章已生成，是否需要转换为 HTML？`

只有用户明确选择“是”后，才执行以下命令，并把参数替换为实际 Markdown 文件绝对路径：

```bash
python3 /Users/lucas/Desktop/WeChat-Insight-Skill/tools/publish_to_wechat.py "<Markdown 文件绝对路径>" --html-only
```

用户拒绝或尚未确认时不执行。转换成功后，脚本会在 Markdown 文件同目录生成同名 `.html` 文件；向用户返回该文件的实际路径。转换失败时返回原始错误，不得声称文件已生成。

### 方式二：通过环境变量注入凭证（推荐）

```bash
export WECHAT_APP_ID="你的AppID"
export WECHAT_APP_SECRET="你的AppSecret"
python tools/publish_to_wechat.py article.md --cover cover.jpg
```

### 方式三：通过配置文件

在项目根目录创建 `.wechat-writer-config.json`，或在 `~/.config/wechat-writer/config.json` 创建用户级配置：

```json
{
  "wechat": {
    "app_id": "你的AppID",
    "app_secret": "你的AppSecret",
    "default_author": "作者名",
    "need_open_comment": true
  }
}
```

然后直接运行：

```bash
python tools/publish_to_wechat.py article.md
```

## Markdown 格式要求

发布工具对输入的 Markdown 有以下要求：

1. **首行必须是一级标题**（`# 标题`），作为文章标题
2. 正文支持以下 Markdown 语法：
   - 二级/三级标题（`##` / `###`）
   - 加粗（`**文字**`）
   - 行内代码（`` `代码` ``）
   - 代码块（``` ``` ```）
   - 引用块（`> `）
   - 无序列表（`- `）
   - 有序列表（`1. `）
   - 图片（`![alt](url)`）
   - 链接（`[文字](url)`）
   - 分隔线（`---`）

3. 不支持的语法会被当作普通段落处理

## HTML 排版规则

发布工具自动将 Markdown 转换为公众号编辑器兼容的 HTML，特点：

- 使用 inline 样式，不依赖外部 CSS，粘贴/上传后样式不丢失
- 字体大小、行高、间距按移动端阅读优化
- 主色调使用配置文件中的品牌色（默认暖橙 `#F4845F`）
- 代码块有背景色和圆角
- 引用块左侧有色块标识
- 图片居中显示，最大宽度自适应

## 发布流程（由 Skill 自动调用时）

当用户要求"发布到公众号"或"发到草稿箱"时，Skill 按以下流程执行：

1. **检查前置条件**
   - 确认 `tools/publish_to_wechat.py` 文件存在于当前项目目录
   - 检查是否配置了 AppID 和 AppSecret（环境变量或配置文件）
   - 缺少任何一项，列出需要用户补齐的内容，不继续

2. **生成完整文章**
   - 按正常写作流程生成 Markdown 格式的完整文章
   - 保存为临时文件

3. **生成封面图（如有图片工具）**
   - 如果有图片生成工具，用推荐标题生成封面
   - 保存为临时图片文件

4. **调用发布脚本**
   - 执行 `python tools/publish_to_wechat.py <文章路径> --cover <封面路径>`
   - 捕获输出和错误

5. **返回结果**
   - 成功：返回 media_id 和草稿箱查看指引
   - 失败（40164 IP 白名单）：告知用户需要添加的 IP，等待用户完成后重试
   - 失败（其他错误）：展示原始错误信息，给出排查建议

## 常见错误与处理

| 错误码 | 原因 | 处理方法 |
|--------|------|---------|
| 40164 | IP 不在白名单 | 把报错提示的 IP 加到公众号 IP 白名单 |
| 40001 | AppSecret 错误或 token 失效 | 检查 AppID / AppSecret 是否正确 |
| 40007 | media_id 无效 | 封面图上传失败，检查图片格式和大小 |
| 45009 | 接口调用超过上限 | 等待次日重置，或减少调用频率 |
| 45047 | 草稿数量超过上限 | 删除一些旧草稿 |
| 48001 | 账号未认证（正文图片上传） | 未认证公众号无正文图片上传权限，改用外部图片链接或手动替换 |
| 网络错误 | 无法连接微信服务器 | 检查网络连接和防火墙 |

## 能力边界

- ✅ **支持**：创建草稿、上传封面图、Markdown 转公众号 HTML
- ✅ **支持**：正文本地图片自动上传到素材库并替换为 CDN URL
- ❌ **不支持**：直接群发/发布（必须在公众号后台手动确认发布）
- ❌ **不支持**：批量发布多篇
- ❌ **不支持**：排版模板自定义（使用内置的移动端优化样式）
- ❌ **不支持**：远程 URL 图片转存（远程图片保留原 URL）

> 为什么不支持自动发布？微信公众号平台要求发布前必须有人工确认环节，这是平台规则，也是对内容负责。自动发布存在误发风险。
