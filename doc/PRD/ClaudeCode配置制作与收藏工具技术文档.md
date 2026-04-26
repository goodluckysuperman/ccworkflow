# Claude Code 配置制作、收藏与安装工具技术文档（一期）

## 1. 文档目标

1. 本文档用于把 `doc/PRD/ClaudeCode配置制作与收藏工具PRD.md` 落成可实现的技术方案。
2. 本文档只覆盖一期范围。
3. 本文档优先解决以下问题：
   1. 本地运行形态。
   2. 模块拆分。
   3. 本地数据结构。
   4. 安装、合并、卸载策略。
   5. AI 生成功能的接入边界。
4. 本文档不把未确认事项伪装成已确定方案。未定项统一放在第 15 节。

## 2. 总体技术方案

### 2.1 运行形态

1. 工具以 Windows `.exe` 形式分发。
2. `.exe` 启动后执行以下动作：
   1. 初始化本地配置目录。
   2. 启动本机 HTTP 服务，只监听 `127.0.0.1`。
   3. 自动打开默认浏览器访问本地页面。
3. 浏览器页面是本地 Web UI，不依赖外网。
4. 除 AI 生成功能外，其余能力均可离线运行。

### 2.2 推荐技术选型

1. Python：3.11。
2. 后端框架：FastAPI。
3. HTTP 服务：Uvicorn。
4. 页面模板：Jinja2。
5. 前端交互：原生 JavaScript + `fetch`。
6. 配置与本地数据读写：Python 标准库 `pathlib`、`json`、`shutil`。
7. 打包：PyInstaller。

### 2.3 选型理由

1. 本项目目标是本地工具，不是 Web 平台。
2. 一期不需要前后端分离部署。
3. 不引入 Node.js 构建链，可降低维护成本。
4. Python 原生文件系统能力足够覆盖收藏、安装、迁移、卸载。
5. PyInstaller 可满足 `.exe` 分发要求。

### 2.4 需要直接说明的风险

1. 若强制使用 PyInstaller 单文件模式，首次启动解包可能压缩 5 秒打开浏览器的目标。
2. 一期建议使用“单目录发布”而不是“单文件发布”。
3. 如果用户坚持单文件 `.exe`，需接受启动耗时风险。

## 3. 系统边界

### 3.1 范围内

1. 配置包制作。
2. 配置包收藏。
3. 配置包检索。
4. AI 生成草稿。
5. 项目级安装。
6. 全局安装。
7. 卸载本工具安装过的内容。
8. 收藏根目录迁移。

### 3.2 范围外

1. 不监听目标项目配置变化。
2. 不实时同步用户手工修改。
3. 不接管 Claude 登录。
4. 不处理 subagents。
5. 不处理 `CLAUDE.md` / rules。
6. 不做云同步。
7. 不做多人协作。
8. 不做任意历史回滚。

## 4. 代码结构规划

> 当前仓库只有 `main.py`。一期落地时建议拆分为以下结构。

```text
ccworkflow/
├─ main.py
├─ src/
│  └─ ccworkflow/
│     ├─ app.py                     # 应用启动入口
│     ├─ config.py                  # 应用配置
│     ├─ models/
│     │  ├─ package_models.py       # 配置包、对象、脚本、安装记录、设置模型
│     │  └─ enums.py                # 状态与类型枚举
│     ├─ services/
│     │  ├─ package_service.py      # 保存、读取、删除、复制、检索
│     │  ├─ generator_service.py    # AI 生成适配层
│     │  ├─ install_service.py      # 安装主流程
│     │  ├─ uninstall_service.py    # 卸载主流程
│     │  ├─ merge_service.py        # hooks / MCP 合并与冲突判断
│     │  ├─ migration_service.py    # 收藏根目录迁移
│     │  └─ validation_service.py   # 类型校验
│     ├─ repositories/
│     │  ├─ package_repository.py   # 本地配置包持久化
│     │  ├─ record_repository.py    # 安装记录持久化
│     │  └─ settings_repository.py  # 系统设置持久化
│     ├─ api/
│     │  ├─ package_api.py
│     │  ├─ generate_api.py
│     │  ├─ install_api.py
│     │  ├─ record_api.py
│     │  └─ settings_api.py
│     ├─ web/
│     │  ├─ templates/
│     │  └─ static/
│     └─ utils/
│        ├─ fs.py
│        ├─ json_ops.py
│        ├─ hashing.py
│        └─ browser.py
└─ doc/
   └─ PRD/
```

## 5. 本地数据存储设计

### 5.1 收藏根目录

1. 默认根目录：`D:\Programming_tools\.ccworkflow`。
2. 用户可在设置中修改。
3. 迁移完成前不得切换到新目录。

### 5.2 收藏根目录结构

```text
<root>/
├─ skills/
│  └─ <package_id>/
├─ hooks/
│  └─ <package_id>/
├─ mcp/
│  └─ <package_id>/
├─ mixed/
│  └─ <package_id>/
├─ install_records/
│  └─ <install_record_id>.json
├─ system/
│  ├─ settings.json
│  └─ app_state.json
└─ trash/
```

### 5.3 单个配置包目录结构

```text
<package_dir>/
├─ manifest.json
├─ objects/
│  ├─ 01_<object_id>.json
│  ├─ 02_<object_id>.json
│  └─ ...
└─ scripts/
   ├─ <script_id>__<filename>
   └─ ...
```

### 5.4 为什么不用数据库

1. 一期收藏数量上限是 500 个。
2. 查询维度只有名称、关键字、标签、类型。
3. 文件系统 + 内存索引即可满足性能目标。
4. 不引入数据库可降低迁移和打包复杂度。

## 6. 数据模型设计

### 6.1 配置包 manifest.json

```json
{
  "package_id": "pkg_01",
  "name": "示例包",
  "summary": "一句话说明",
  "tags": ["hook", "python"],
  "category": "mixed",
  "object_types": ["skill", "hook"],
  "object_ids": ["obj_skill_01", "obj_hook_01"],
  "script_ids": ["script_01"],
  "created_at": "2026-04-26T10:00:00+08:00",
  "updated_at": "2026-04-26T10:05:00+08:00",
  "status": "saved"
}
```

### 6.2 skill 对象文件

```json
{
  "object_id": "obj_skill_01",
  "type": "skill",
  "name": "python-review",
  "description": "Python 代码审查技能",
  "content_format": "markdown",
  "body": "# Skill\n...",
  "project_target": ".claude/skills/python-review/SKILL.md",
  "global_target": "~/.claude/skills/python-review/SKILL.md",
  "validation_status": "passed"
}
```

### 6.3 hook 对象文件

> 这里不能直接把 hook 当成任意文本处理，否则无法做冲突识别、合并安装和安全卸载。

```json
{
  "object_id": "obj_hook_01",
  "type": "hook",
  "name": "format-on-write",
  "hook_key": "format-on-write",
  "description": "写文件后自动格式化",
  "content_format": "json",
  "body": {
    "event": "PostToolUse",
    "matcher": "Write|Edit",
    "hooks": [
      {
        "type": "command",
        "command": "python {{script:format.py}}"
      }
    ]
  },
  "project_target": ".claude/settings.json",
  "global_target": "~/.claude/settings.json",
  "validation_status": "passed"
}
```

### 6.4 MCP 对象文件

```json
{
  "object_id": "obj_mcp_01",
  "type": "mcp",
  "name": "local-docs",
  "server_name": "local-docs",
  "description": "本地文档 MCP",
  "content_format": "json",
  "body": {
    "command": "python",
    "args": ["server.py"],
    "env": {}
  },
  "project_target": ".mcp.json",
  "global_target": "~/.claude.json",
  "validation_status": "passed"
}
```

### 6.5 附加脚本

```json
{
  "script_id": "script_01",
  "name": "format.py",
  "original_filename": "format.py",
  "stored_filename": "script_01__format.py",
  "applies_to": ["obj_hook_01"]
}
```

### 6.6 安装记录

```json
{
  "install_record_id": "inst_01",
  "package_id": "pkg_01",
  "scope": "project",
  "project_root": "D:/demo/project",
  "installed_at": "2026-04-26T10:10:00+08:00",
  "install_status": "success",
  "uninstall_status": "not_uninstalled",
  "conflict_resolutions": [
    {
      "object_id": "obj_hook_01",
      "resolution": "replace"
    }
  ],
  "files": [
    {
      "path": "D:/demo/project/.claude/settings.json",
      "kind": "json_merge",
      "before_hash": "sha256:...",
      "after_hash": "sha256:..."
    }
  ],
  "entries": [
    {
      "object_id": "obj_hook_01",
      "type": "hook",
      "target_file": "D:/demo/project/.claude/settings.json",
      "object_key": "format-on-write",
      "installed_snapshot": {
        "event": "PostToolUse",
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "python D:/demo/project/.claude/scripts/format.py"
          }
        ]
      }
    }
  ],
  "scripts": [
    {
      "script_id": "script_01",
      "target_path": "D:/demo/project/.claude/scripts/format.py",
      "hash": "sha256:..."
    }
  ]
}
```

### 6.7 系统设置

```json
{
  "collection_root": "D:\\Programming_tools\\.ccworkflow",
  "last_generate_mode": "ai",
  "last_install_scope": "project",
  "last_filters": {
    "keyword": "",
    "tags": [],
    "type": "all"
  }
}
```

## 7. 页面与接口设计

### 7.1 页面清单

1. 首页 / 列表页。
2. 新建 / 编辑配置包页。
3. AI 生成页。
4. 配置包详情页。
5. 已安装记录页。
6. 设置页。

### 7.2 后端接口清单

#### 配置包

1. `GET /api/packages`
   1. 支持 `keyword`、`tags`、`type` 查询参数。
2. `GET /api/packages/{package_id}`
3. `POST /api/packages`
4. `PUT /api/packages/{package_id}`
5. `DELETE /api/packages/{package_id}`
6. `POST /api/packages/{package_id}/copy`

#### AI 生成

1. `POST /api/generate-draft`
2. 输入：
   1. 配置包名称。
   2. 简介。
   3. 标签。
   4. 目标对象类型。
   5. 自然语言描述。
3. 输出：
   1. 草稿对象列表。
   2. 草稿脚本列表。
   3. 解析错误信息。

#### 安装与卸载

1. `POST /api/install`
2. `POST /api/uninstall/{install_record_id}`
3. `GET /api/install-records`
4. `GET /api/install-records/{install_record_id}`

#### 设置

1. `GET /api/settings`
2. `PUT /api/settings`
3. `POST /api/settings/migrate-root`

## 8. 核心流程技术设计

### 8.1 保存配置包

1. 前端提交配置包表单。
2. 后端执行统一校验。
3. 根据对象类型集合计算分类目录：
   1. 只含 `skill` -> `skills`
   2. 只含 `hook` -> `hooks`
   3. 只含 `mcp` -> `mcp`
   4. 混合类型 -> `mixed`
4. 若为新包：
   1. 生成 `package_id`。
   2. 创建包目录。
5. 写入 `manifest.json`。
6. 写入 `objects/*.json`。
7. 复制附加脚本到 `scripts/`。
8. 返回保存成功结果。

### 8.2 AI 生成草稿

1. 前端提交自然语言描述。
2. 后端调用 `generator_service`。
3. `generator_service` 只负责：
   1. 组织提示词。
   2. 调用 Claude Code。
   3. 解析结构化输出。
4. 生成结果只返回前端内存态草稿。
5. 不写磁盘。
6. 用户点击“保存”前，不生成配置包目录。

### 8.3 安装流程

1. 读取配置包与对象。
2. 校验安装范围和目标路径。
3. 预计算实际目标文件。
4. 预检查冲突。
5. 前端展示冲突列表。
6. 用户逐项选择：
   1. 替换。
   2. 跳过。
   3. 取消。
7. 后端对每个对象独立安装。
8. 所有对象执行完成后写安装记录。
9. 若任一对象失败：
   1. 安装状态标记为失败。
   2. 返回失败对象明细。

### 8.4 卸载流程

1. 根据安装记录加载历史快照。
2. 按记录中的 `entries` 逐项匹配当前目标内容。
3. 只有当前内容仍等于安装快照时，才允许删除该项。
4. 若当前内容已被人工修改：
   1. 阻止卸载该项。
   2. 返回明确提示。
5. 所有可删除项处理完毕后更新卸载状态。

### 8.5 收藏根目录迁移

1. 前端提交新目录。
2. 后端校验：
   1. 路径合法。
   2. 路径可写。
   3. 目标不是现有根目录的子目录。
   4. 目标不是空目录冲突场景。
3. 迁移步骤：
   1. 复制全部收藏数据到新目录临时区。
   2. 校验目录结构与文件数量。
   3. 校验关键文件哈希。
   4. 原子替换新目录临时区为正式目录。
   5. 更新 `system/settings.json` 中的根目录。
4. 任一步失败：
   1. 不更新当前设置。
   2. 保留旧目录。
   3. 返回失败原因。

## 9. 类型级安装与合并策略

### 9.1 skill

1. skill 是独立文件。
2. 目标路径固定到 `skills/<skill_name>/SKILL.md`。
3. 冲突条件：目标路径已存在同名 skill 文件。
4. 替换：覆盖该 skill 文件。
5. 跳过：不写该 skill。
6. 取消：终止整次安装。
7. 卸载：
   1. 若当前文件哈希仍等于安装后哈希，则删除文件。
   2. 若文件已被人工修改，则阻止卸载。

### 9.2 hook

1. hook 安装目标是 JSON 文件，不允许整文件覆盖。
2. 一期 hook 对象必须使用应用内规范结构：
   1. `hook_key`
   2. `event`
   3. `matcher`
   4. `hooks`
3. 安装时把对象转换为 Claude Code 目标 JSON 结构后再合并。
4. 冲突条件：同一目标文件中已存在相同 `hook_key` 对应的业务项，或存在等价的 `(event, matcher, hooks)` 组合。
5. 替换：删除旧业务项，再写入新业务项。
6. 跳过：不写该 hook。
7. 取消：终止整次安装。
8. 卸载：
   1. 只删除安装记录中的快照项。
   2. 当前项与安装快照不一致时阻止卸载。

### 9.3 MCP

1. MCP 安装目标也是 JSON 文件。
2. 一期 MCP 对象必须使用应用内规范结构：
   1. `server_name`
   2. `command`
   3. `args`
   4. `env`
3. 安装时合并到 `mcpServers`。
4. 冲突条件：同名 `server_name` 已存在。
5. 替换：覆盖该 `server_name` 项。
6. 跳过：不写该 `server_name` 项。
7. 取消：终止整次安装。
8. 卸载：
   1. 只删除该 `server_name` 对应项。
   2. 当前项与安装快照不一致时阻止卸载。

### 9.4 附加脚本

1. 附加脚本在收藏时复制到配置包目录。
2. 安装时复制到目标脚本目录：
   1. 项目级：`<project>/.claude/scripts/`
   2. 全局：`~/.claude/scripts/`
3. 若对象正文包含 `{{script:<filename>}}` 占位符：
   1. 安装前替换为实际脚本目标路径。
   2. 替换后的结果写入安装快照。
4. 若引用了不存在的脚本：
   1. 禁止安装。
   2. 返回缺失脚本名。

## 10. 校验规则

### 10.1 通用校验

1. 配置包名称不能为空。
2. 配置包至少包含 1 个对象。
3. 对象类型不能为空。
4. 对象名称不能为空。
5. 正文不能为空。
6. 标签必须是字符串数组。

### 10.2 skill 校验

1. `name` 不能为空。
2. `body` 必须是非空 Markdown 文本。
3. `project_target` 和 `global_target` 必须可由名称推导，不接受任意路径写入。

### 10.3 hook 校验

1. `hook_key` 不能为空。
2. `event` 不能为空。
3. `hooks` 必须是非空数组。
4. `body` 必须能序列化为 JSON。
5. 一期只做语法与必填字段校验，不做外部命令可执行性校验。

### 10.4 MCP 校验

1. `server_name` 不能为空。
2. `command` 不能为空。
3. `args` 必须是数组。
4. `env` 必须是对象。
5. 一期只做语法与必填字段校验，不校验服务端是否真的可启动。

## 11. Claude Code 接入设计

### 11.1 适配层边界

1. 不在业务代码中直接散落调用 Claude Code 命令。
2. 所有调用统一经过 `generator_service`。
3. `generator_service` 对外只暴露一个方法：`generate_draft(request)`。

### 11.2 输入输出契约

1. 输入：
   1. 配置包基础信息。
   2. 目标对象类型。
   3. 自然语言描述。
2. 输出必须是结构化 JSON。
3. 输出至少包含：
   1. `objects`
   2. `scripts`
   3. `warnings`
4. 若返回内容无法解析为结构化 JSON，则整次生成失败。

### 11.3 错误处理

1. 本机未安装 Claude Code：返回“功能不可用”。
2. Claude Code 调用超时：返回“生成失败”。
3. Claude Code 输出非预期结构：返回“结果不可解析”。
4. 以上失败均不得写入收藏目录。

## 12. 安全与约束

1. HTTP 服务只允许绑定 `127.0.0.1`。
2. 不提供局域网访问。
3. 安装目标路径只允许落在以下白名单：
   1. `<project>/.claude/skills/`
   2. `<project>/.claude/scripts/`
   3. `<project>/.claude/settings.json`
   4. `<project>/.mcp.json`
   5. `~/.claude/skills/`
   6. `~/.claude/scripts/`
   7. `~/.claude/settings.json`
   8. `~/.claude.json`
4. 不允许用户在对象层自定义任意绝对路径。
5. 写文件前必须确保父目录在白名单内。
6. 安装记录中允许保存文件哈希，不保存 Claude 账号信息。

## 13. 性能设计

1. 启动时只建立元信息索引，不预加载所有对象全文。
2. 列表检索优先读取 `manifest.json`。
3. 打开详情页时再读取 `objects/*.json`。
4. 预览更新在前端本地完成，不走后端往返。
5. 安装前冲突检查按对象逐个处理，避免整目录扫描。

## 14. 测试建议

### 14.1 单元测试

1. 分类目录计算。
2. manifest 读写。
3. hook/MCP 语法校验。
4. 路径白名单校验。
5. 占位符脚本替换。
6. 冲突识别。
7. 安装记录生成。
8. 卸载前快照比对。

### 14.2 集成测试

1. 新建 skill 包并保存。
2. 新建 hook 包并保存。
3. 新建 MCP 包并保存。
4. 混合包保存。
5. 项目级安装。
6. 全局安装。
7. 冲突时替换 / 跳过 / 取消。
8. 卸载未被改动的已安装内容。
9. 卸载被手工改动的内容时被阻止。
10. 收藏根目录迁移成功。
11. 收藏根目录迁移失败回滚。
12. Claude Code 不可用时 AI 生成功能降级。

## 15. 待确认技术决策

1. Claude Code 的非交互调用协议未在 PRD 中定义。
   1. 需要确认最终调用命令。
   2. 需要确认是否支持稳定的 JSON 输出。
2. 全局 MCP 的目标文件路径需要再次确认。
   1. PRD 写的是 `~/.claude.json`。
   2. 若实际运行环境不是该文件，安装会失败。
3. hook 业务键是一期必须补充的字段。
   1. PRD 里提到“同名 hook 冲突”。
   2. 但 hook 天然不一定有稳定名称。
   3. 若不补 `hook_key`，无法稳定替换与卸载。
4. 附加脚本占位符语法需要最终拍板。
   1. 本文档建议使用 `{{script:<filename>}}`。
   2. 若用户不接受该语法，需要改成其他明确规则。
5. `.exe` 发布形态需要拍板。
   1. 建议单目录发布。
   2. 若要求单文件发布，需接受冷启动风险。
6. 收藏根目录迁移后的旧目录清理策略待确认。
   1. 本文档保证“迁移成功前不删除旧数据”。
   2. 迁移成功后是立即删除、保留备份，还是提示用户手动清理，PRD 未写死。
