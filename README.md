# Fabric Patchwork Skill

把照片或文字需求变成手工拼布画。支持三种输出：

1. **照片 + 拼布双区画纸**：浅黄色布面画纸，上方放原照片、下方放拼布，两者不重叠；照片更大，照片外沿有棕色针脚。
2. **照片转独立拼布画**：以照片主体为参考，生成一张完整的 3:4 拼布画。
3. **文字生成拼布画**：根据描述生成独立作品。

风格核心是 **subject-as-fabric**：主体必须由剪裁、拼接、缝制的布片构成，不是给插画盖一层布纹。默认严格平面，不做填充、鼓包、倒角或立体投影。

## 模式 A 的成品契约

- 整张画纸是浅暖黄色布面（默认 `#F4E6C4`），四周有棕色细线和棕色缝线。
- 原照片放在上方，约占画布面积 60–65%，尺寸、裁切、光影和颜色保持不变。
- 拼布放在下方独立区域，约占画布 20–25%，直接落在浅黄布面上，不加卡片或第二层背景。
- 两个区域之间留 3–5% 的间隙，绝不重叠。
- 照片外沿有棕色针脚，针脚不画进照片像素。
- 拼布保持严格平面，无填充、鼓包或投影。

## 目录

```text
SKILL.md                      技能入口（Agent Skills 格式）
references/
  style-system.md             视觉规范
  prompt-recipes.md           提示词模板与回退方案
assets/style-references/      风格参考图与索引
scripts/compose_corner_patch.py  模式 A 确定性合成器
dist/fabric-patchwork.portable.md  单文件便携版
agents/openai.yaml            Codex 界面元数据
```

## 环境要求

- 图像生成：使用宿主自带的图像生成/编辑能力，或由用户提供透明 RGBA 拼布主体。技能不绑定某一家模型。
- 确定性合成：Python 3.10+ 和 Pillow。只有模式 A 的精确叠加需要它。
- 不要求 API Key。只有选择宿主的 CLI/API 回退时才需要对应服务的 Key。

## 安装与调用

### Codex

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills/make-fabric-patchwork"
cp -R SKILL.md README.md references assets scripts agents dist \
  "${CODEX_HOME:-$HOME/.codex}/skills/make-fabric-patchwork/"
```

在 Codex 中可用 `$make-fabric-patchwork` 或自然语言触发。

### Claude Code / Claude Agent Skills

把整个文件夹复制到：

```text
~/.claude/skills/make-fabric-patchwork/
```

复制 `SKILL.md`、`references/`、`assets/`、`scripts/`、`agents/`、`dist/` 和 `README.md`，不要复制 `.git/` 或 `output/`。Claude 读取同名的 `SKILL.md` 即可。若 Claude 环境没有图像生成工具，让它使用当前对话中的图片工具，或请用户提供透明 PNG。

### Trae / WorkBuddy / 其他支持自定义规则的工具

- 如果工具支持 Agent Skills 目录或自定义技能文件夹，直接复制整个项目。
- 如果只支持单个自定义指令/规则文件，把 `dist/fabric-patchwork.portable.md` 的内容粘贴进去。
- 同时把 `assets/style-references/` 作为风格参考上传；不要把参考图当成可复制主体。

### 纯聊天工具（ChatGPT、Claude 网页等）

上传 `dist/fabric-patchwork.portable.md` 作为说明，附上用户照片；如果宿主能生成图片，就让它按模式 A/B/C 的提示词工作。不能生成透明图时，请用户提供透明 PNG，再用本地脚本合成。

## 使用示例

### 照片 + 拼布双区画纸

```text
使用 $make-fabric-patchwork，把这张照片做成双区拼布画纸：
浅黄色布面背景，上方放原照片、下方放拼布，两者不重叠；
照片占约 62%，外沿加棕色针脚；整张画纸四周有棕色线；
拼布保持平面贴布，不要卡片、不要阴影、不要改变照片像素。
```

### 照片转独立拼布画

```text
使用 $make-fabric-patchwork，把这张照片做成一张独立的 3:4 拼布画，
保留主体轮廓，用棉麻布片拼成，平面拼接，不要立体填充。
```

### 文字生成

```text
使用 $make-fabric-patchwork，生成一张关于雨天咖啡馆的拼布画，
鼠尾草绿、雾蓝、奶油白，平面贴布，少量毛边和缝线。
```

## 本地合成器

```bash
python scripts/compose_corner_patch.py \
  --photo photo.jpeg \
  --motif motif-rgba.png \
  --output result.png \
  --placement sheet \
  --patch-fraction 0.30
```

先运行 `--plan` 预览画布、照片区和拼布区。`--placement direct` 或 `--placement card` 仅在用户明确要求时使用。

## 无 Python 回退

如果宿主不能运行 Python：

1. 优先使用宿主的图层/合成能力叠加透明主体。
2. 若只能单次生成，使用 `references/prompt-recipes.md` 末尾的“无脚本直出”模板。
3. 检查成品是否重绘或改动了原照片；若改动明显，拒绝该结果。

## 兼容性说明

- 本仓库遵循通用的 Agent Skills 布局：`SKILL.md` + `references/` + `assets/` + `scripts/`。
- 参考资源使用相对路径，复制整个文件夹即可保持可用。
- 图像生成与 Python 合成分离；没有图像生成器时可以只使用用户提供的透明主体，没有 Python 时可以使用宿主原生合成。
- 本版本在 Codex 本地环境验证过合成器和文档校验；其他宿主按其自定义技能/规则机制接入。

