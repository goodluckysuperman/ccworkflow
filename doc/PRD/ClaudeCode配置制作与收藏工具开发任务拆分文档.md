# Claude Code 配置制作、收藏与安装工具开发任务拆分文档（一期）

## 1. 文档目标

1. 本文档用于把一期技术方案拆成可执行开发任务。
2. 本文档只规定：
   1. 项目目录结构。
   2. 模块边界。
   3. 模块输入输出接口。
   4. 开发阶段顺序。
   5. 每个任务的交付物与验收点。
3. 本文档不写具体代码实现细节。
4. 本文档默认遵循以下原则：
   1. 模块小。
   2. 职责单一。
   3. 接口稳定。
   4. 文件系统优先。
   5. 一期不提前抽象二期能力。

## 2. 模块设计原则

1. 一个模块只处理一类职责。
2. 一个服务只负责一个用例。
3. 类型差异放到类型适配模块，不放到通用服务里硬分支。
4. Web 层只做请求解析与响应组装，不写业务逻辑。
5. Service 层只编排流程，不直接操作框架对象。
6. Repository 层只负责持久化，不负责业务判断。
7. 文件系统访问统一收口，不允许业务代码到处直接读写文件。
8. Claude Code 调用统一收口，不允许散落在多个模块。
9. 安装、卸载、迁移都是独立用例，不能塞进一个“大而全服务”。

## 3. 建议目录结构

```text
ccworkflow/
├─ main.py                                # 程序入口，只负责启动应用
├─ pyproject.toml
├─ src/
│  └─ ccworkflow/
│     ├─ app/
│     │  ├─ bootstrap.py                  # 启动、初始化、打开浏览器
│     │  └─ factory.py                    # 组装应用与依赖
│     ├─ web/
│     │  ├─ routes/
│     │  │  ├─ page_routes.py             # 页面路由
│     │  │  ├─ package_routes.py          # 配置包接口
│     │  │  ├─ generate_routes.py         # AI 生成接口
│     │  │  ├─ install_routes.py          # 安装/卸载接口
│     │  │  ├─ record_routes.py           # 安装记录接口
│     │  │  └─ settings_routes.py         # 设置接口
│     │  ├─ templates/
│     │  └─ static/
│     ├─ domain/
│     │  ├─ enums.py                      # 枚举
│     │  ├─ package_schema.py             # 配置包数据结构
│     │  ├─ record_schema.py              # 安装记录数据结构
│     │  ├─ settings_schema.py            # 设置数据结构
│     │  └─ common_schema.py              # 通用结果/错误结构
│     ├─ services/
│     │  ├─ root_init_service.py          # 收藏根目录初始化
│     │  ├─ package_query_service.py      # 列表/详情查询
│     │  ├─ package_save_service.py       # 新建/编辑保存
│     │  ├─ package_delete_service.py     # 删除
│     │  ├─ package_copy_service.py       # 复制
│     │  ├─ package_validation_service.py # 保存前校验
│     │  ├─ generate_draft_service.py     # AI 生成草稿
│     │  ├─ install_preview_service.py    # 安装预检查
│     │  ├─ install_execute_service.py    # 安装执行
│     │  ├─ uninstall_service.py          # 卸载执行
│     │  ├─ settings_query_service.py     # 读取设置
│     │  ├─ settings_update_service.py    # 更新设置
│     │  └─ root_migration_service.py     # 收藏根目录迁移
│     ├─ repositories/
│     │  ├─ package_repository.py         # 配置包读写
│     │  ├─ install_record_repository.py  # 安装记录读写
│     │  └─ settings_repository.py        # 设置读写
│     ├─ installers/
│     │  ├─ target_path_resolver.py       # 目标路径解析
│     │  ├─ script_materializer.py        # 脚本复制与占位符替换
│     │  ├─ skill_installer.py            # skill 类型安装/卸载辅助
│     │  ├─ hook_installer.py             # hook 类型安装/卸载辅助
│     │  ├─ mcp_installer.py              # MCP 类型安装/卸载辅助
│     │  └─ conflict_detector.py          # 冲突检测
│     ├─ integrations/
│     │  └─ claude_cli_adapter.py         # Claude Code 调用适配
│     └─ infra/
│        ├─ fs_gateway.py                 # 文件系统收口
│        ├─ json_gateway.py               # JSON 文件收口
│        ├─ hash_gateway.py               # 哈希计算
│        ├─ path_policy.py                # 路径白名单与合法性判断
│        └─ time_gateway.py               # 时间获取
└─ doc/
   └─ PRD/
```

## 4. 模块依赖规则

1. `web` 只能依赖 `services` 与 `domain`。
2. `services` 可以依赖 `repositories`、`installers`、`integrations`、`infra`、`domain`。
3. `repositories` 只能依赖 `infra` 与 `domain`。
4. `installers` 只能依赖 `infra` 与 `domain`。
5. `integrations` 只能依赖 `infra` 与 `domain`。
6. `domain` 不依赖任何业务模块。
7. 不允许 `web` 直接依赖 `repositories`。
8. 不允许 `services` 互相循环依赖。
9. 不允许一个服务直接承担“查询 + 保存 + 安装 + 卸载”多个职责。

## 5. 通用接口约定

### 5.1 通用结果结构

所有 Service 层输出统一使用以下结果形状。

```json
{
  "success": true,
  "message": "",
  "errors": [],
  "data": {}
}
```

字段说明：

1. `success`：布尔值。
2. `message`：给前端展示的结果说明。
3. `errors`：错误列表。
4. `data`：成功结果主体。

### 5.2 通用错误结构

```json
{
  "code": "PACKAGE_NAME_REQUIRED",
  "field": "name",
  "target": "package",
  "detail": "配置包名称不能为空"
}
```

### 5.3 通用分页结构

一期收藏数量不大，但列表接口仍使用统一列表返回结构。

```json
{
  "items": [],
  "total": 0,
  "filters": {}
}
```

## 6. 核心数据结构约定

### 6.1 PackageObjectDraft

```json
{
  "object_id": "obj_xxx",
  "type": "skill|hook|mcp",
  "name": "",
  "description": "",
  "body": {},
  "extra": {}
}
```

约束：

1. `skill` 的 `body` 是 Markdown 字符串。
2. `hook` 的 `body` 是 JSON 对象。
3. `mcp` 的 `body` 是 JSON 对象。
4. `extra` 用于承载类型专属字段。

### 6.2 ScriptDraft

```json
{
  "script_id": "script_xxx",
  "name": "",
  "source_path": "",
  "applies_to": []
}
```

### 6.3 PackageDraft

```json
{
  "package_id": null,
  "name": "",
  "summary": "",
  "tags": [],
  "objects": [],
  "scripts": []
}
```

### 6.4 ConflictItem

```json
{
  "object_id": "obj_xxx",
  "type": "skill|hook|mcp",
  "object_name": "",
  "target_file": "",
  "conflict_key": "",
  "reason": "same_name|same_key|same_server_name"
}
```

### 6.5 InstallResolution

```json
{
  "object_id": "obj_xxx",
  "action": "replace|skip|cancel"
}
```

## 7. 模块清单与接口定义

## 7.1 app.bootstrap

### 职责

1. 启动应用。
2. 初始化收藏根目录。
3. 启动本地 HTTP 服务。
4. 打开浏览器。

### 接口

#### `start_app(input) -> result`

输入：

```json
{
  "host": "127.0.0.1",
  "port": 0,
  "open_browser": true
}
```

输出：

```json
{
  "success": true,
  "data": {
    "host": "127.0.0.1",
    "port": 8848,
    "url": "http://127.0.0.1:8848/",
    "collection_root": "D:/Programming_tools/.ccworkflow"
  }
}
```

## 7.2 services.root_init_service

### 职责

1. 初始化默认收藏目录。
2. 初始化 `system/settings.json`。
3. 初始化必要子目录。

### 接口

#### `ensure_root_ready(input) -> result`

输入：

```json
{
  "default_root": "D:/Programming_tools/.ccworkflow"
}
```

输出：

```json
{
  "success": true,
  "data": {
    "collection_root": "D:/Programming_tools/.ccworkflow",
    "created_paths": []
  }
}
```

## 7.3 services.package_validation_service

### 职责

1. 校验配置包。
2. 校验对象类型字段。
3. 校验脚本引用完整性。

### 接口

#### `validate_package(input) -> result`

输入：

```json
{
  "package": {
    "package_id": null,
    "name": "",
    "summary": "",
    "tags": [],
    "objects": [],
    "scripts": []
  }
}
```

输出：

```json
{
  "success": true,
  "data": {
    "valid": true,
    "category": "skills|hooks|mcp|mixed",
    "object_summaries": [
      {
        "object_id": "obj_xxx",
        "valid": true,
        "errors": []
      }
    ]
  }
}
```

## 7.4 services.package_save_service

### 职责

1. 新建配置包。
2. 更新配置包。
3. 触发保存前校验。
4. 调用仓储落盘。

### 接口

#### `save_package(input) -> result`

输入：

```json
{
  "package": {
    "package_id": null,
    "name": "",
    "summary": "",
    "tags": [],
    "objects": [],
    "scripts": []
  },
  "save_mode": "create|update"
}
```

输出：

```json
{
  "success": true,
  "data": {
    "package_id": "pkg_xxx",
    "category": "mixed",
    "package_dir": "D:/Programming_tools/.ccworkflow/mixed/pkg_xxx",
    "updated_at": "2026-04-26T12:00:00+08:00"
  }
}
```

## 7.5 services.package_query_service

### 职责

1. 列表查询。
2. 详情查询。
3. 过滤条件处理。

### 接口

#### `list_packages(input) -> result`

输入：

```json
{
  "keyword": "",
  "tags": [],
  "type": "all|skill|hook|mcp|mixed"
}
```

输出：

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "package_id": "pkg_xxx",
        "name": "",
        "summary": "",
        "tags": [],
        "category": "mixed",
        "object_types": [],
        "updated_at": ""
      }
    ],
    "total": 1,
    "filters": {
      "keyword": "",
      "tags": [],
      "type": "all"
    }
  }
}
```

#### `get_package_detail(input) -> result`

输入：

```json
{
  "package_id": "pkg_xxx"
}
```

输出：

```json
{
  "success": true,
  "data": {
    "package": {
      "package_id": "pkg_xxx",
      "name": "",
      "summary": "",
      "tags": [],
      "objects": [],
      "scripts": [],
      "created_at": "",
      "updated_at": ""
    }
  }
}
```

## 7.6 services.package_delete_service

### 职责

1. 删除配置包。
2. 仅删除收藏区内容。
3. 不自动卸载已安装内容。

### 接口

#### `delete_package(input) -> result`

输入：

```json
{
  "package_id": "pkg_xxx"
}
```

输出：

```json
{
  "success": true,
  "data": {
    "package_id": "pkg_xxx",
    "deleted": true
  }
}
```

## 7.7 services.package_copy_service

### 职责

1. 复制已有配置包。
2. 生成新 `package_id`。
3. 复制对象与脚本副本。

### 接口

#### `copy_package(input) -> result`

输入：

```json
{
  "package_id": "pkg_xxx",
  "new_name": ""
}
```

输出：

```json
{
  "success": true,
  "data": {
    "source_package_id": "pkg_xxx",
    "new_package_id": "pkg_new_xxx"
  }
}
```

## 7.8 services.generate_draft_service

### 职责

1. 组织 AI 生成请求。
2. 调用 Claude CLI 适配层。
3. 解析结构化草稿。
4. 不写入磁盘。

### 接口

#### `generate_draft(input) -> result`

输入：

```json
{
  "name": "",
  "summary": "",
  "tags": [],
  "target_types": ["skill", "hook"],
  "prompt": "用户自然语言描述"
}
```

输出：

```json
{
  "success": true,
  "data": {
    "draft": {
      "package_id": null,
      "name": "",
      "summary": "",
      "tags": [],
      "objects": [],
      "scripts": []
    },
    "warnings": []
  }
}
```

## 7.9 integrations.claude_cli_adapter

### 职责

1. 探测 Claude Code 是否可用。
2. 发起非交互生成调用。
3. 返回原始文本结果。

### 接口

#### `check_available(input) -> result`

输入：

```json
{}
```

输出：

```json
{
  "success": true,
  "data": {
    "available": true,
    "version": ""
  }
}
```

#### `run_generate(input) -> result`

输入：

```json
{
  "prompt": "",
  "timeout_seconds": 60
}
```

输出：

```json
{
  "success": true,
  "data": {
    "raw_text": "{}"
  }
}
```

## 7.10 services.install_preview_service

### 职责

1. 读取配置包。
2. 计算安装目标路径。
3. 检查脚本依赖。
4. 检测冲突。
5. 返回安装预览。

### 接口

#### `preview_install(input) -> result`

输入：

```json
{
  "package_id": "pkg_xxx",
  "scope": "project|global",
  "project_root": "D:/demo/project"
}
```

输出：

```json
{
  "success": true,
  "data": {
    "package_id": "pkg_xxx",
    "scope": "project",
    "target_files": [
      "D:/demo/project/.claude/settings.json",
      "D:/demo/project/.mcp.json"
    ],
    "missing_scripts": [],
    "conflicts": [],
    "cancel_allowed": true
  }
}
```

## 7.11 services.install_execute_service

### 职责

1. 根据预览结果执行安装。
2. 按对象分别安装。
3. 生成安装记录。
4. 返回成功项与失败项。

### 接口

#### `execute_install(input) -> result`

输入：

```json
{
  "package_id": "pkg_xxx",
  "scope": "project|global",
  "project_root": "D:/demo/project",
  "resolutions": [
    {
      "object_id": "obj_xxx",
      "action": "replace|skip|cancel"
    }
  ]
}
```

输出：

```json
{
  "success": true,
  "data": {
    "install_record_id": "inst_xxx",
    "installed_objects": ["obj_1"],
    "skipped_objects": ["obj_2"],
    "failed_objects": [],
    "written_files": [],
    "copied_scripts": []
  }
}
```

## 7.12 installers.target_path_resolver

### 职责

1. 计算每个对象项目级目标路径。
2. 计算每个对象全局目标路径。
3. 拒绝白名单外路径。

### 接口

#### `resolve_targets(input) -> result`

输入：

```json
{
  "scope": "project|global",
  "project_root": "D:/demo/project",
  "objects": []
}
```

输出：

```json
{
  "success": true,
  "data": {
    "targets": [
      {
        "object_id": "obj_xxx",
        "target_file": "D:/demo/project/.claude/settings.json",
        "target_kind": "skill_file|settings_json|mcp_json"
      }
    ]
  }
}
```

## 7.13 installers.conflict_detector

### 职责

1. 按对象识别冲突。
2. 输出用户可决策的冲突项。

### 接口

#### `detect_conflicts(input) -> result`

输入：

```json
{
  "targets": [],
  "objects": []
}
```

输出：

```json
{
  "success": true,
  "data": {
    "conflicts": [
      {
        "object_id": "obj_xxx",
        "type": "hook",
        "object_name": "format-on-write",
        "target_file": "D:/demo/project/.claude/settings.json",
        "conflict_key": "format-on-write",
        "reason": "same_key"
      }
    ]
  }
}
```

## 7.14 installers.script_materializer

### 职责

1. 复制附加脚本到目标目录。
2. 解析对象正文里的脚本占位符。
3. 返回替换后的正文与脚本落地结果。

### 接口

#### `materialize_scripts(input) -> result`

输入：

```json
{
  "scope": "project|global",
  "project_root": "D:/demo/project",
  "objects": [],
  "scripts": []
}
```

输出：

```json
{
  "success": true,
  "data": {
    "resolved_objects": [],
    "copied_scripts": [
      {
        "script_id": "script_xxx",
        "target_path": "D:/demo/project/.claude/scripts/format.py"
      }
    ]
  }
}
```

## 7.15 installers.skill_installer

### 职责

1. 安装单个 skill。
2. 卸载单个 skill。
3. 只处理 skill，不处理 hook / MCP。

### 接口

#### `install_skill(input) -> result`

输入：

```json
{
  "object": {},
  "target_file": "",
  "resolution": "replace|skip|cancel"
}
```

输出：

```json
{
  "success": true,
  "data": {
    "object_id": "obj_xxx",
    "written_file": "",
    "snapshot": {}
  }
}
```

#### `uninstall_skill(input) -> result`

输入：

```json
{
  "record_entry": {},
  "target_file": ""
}
```

输出：

```json
{
  "success": true,
  "data": {
    "object_id": "obj_xxx",
    "removed": true
  }
}
```

## 7.16 installers.hook_installer

### 职责

1. 安装单个 hook。
2. 卸载单个 hook。
3. 只处理 `.claude/settings.json` 合并逻辑。

### 接口

#### `install_hook(input) -> result`

输入：

```json
{
  "object": {},
  "target_file": "",
  "resolution": "replace|skip|cancel"
}
```

输出：

```json
{
  "success": true,
  "data": {
    "object_id": "obj_xxx",
    "written_file": "",
    "snapshot": {}
  }
}
```

#### `uninstall_hook(input) -> result`

输入：

```json
{
  "record_entry": {},
  "target_file": ""
}
```

输出：

```json
{
  "success": true,
  "data": {
    "object_id": "obj_xxx",
    "removed": true
  }
}
```

## 7.17 installers.mcp_installer

### 职责

1. 安装单个 MCP。
2. 卸载单个 MCP。
3. 只处理 `mcpServers` 合并逻辑。

### 接口

#### `install_mcp(input) -> result`

输入：

```json
{
  "object": {},
  "target_file": "",
  "resolution": "replace|skip|cancel"
}
```

输出：

```json
{
  "success": true,
  "data": {
    "object_id": "obj_xxx",
    "written_file": "",
    "snapshot": {}
  }
}
```

#### `uninstall_mcp(input) -> result`

输入：

```json
{
  "record_entry": {},
  "target_file": ""
}
```

输出：

```json
{
  "success": true,
  "data": {
    "object_id": "obj_xxx",
    "removed": true
  }
}
```

## 7.18 services.uninstall_service

### 职责

1. 加载安装记录。
2. 校验当前目标内容是否仍可安全卸载。
3. 调用类型安装器执行卸载。
4. 更新卸载状态。

### 接口

#### `uninstall_by_record(input) -> result`

输入：

```json
{
  "install_record_id": "inst_xxx"
}
```

输出：

```json
{
  "success": true,
  "data": {
    "install_record_id": "inst_xxx",
    "removed_objects": [],
    "removed_scripts": [],
    "blocked_objects": []
  }
}
```

## 7.19 services.settings_query_service

### 职责

1. 读取系统设置。
2. 返回页面所需设置视图。

### 接口

#### `get_settings(input) -> result`

输入：

```json
{}
```

输出：

```json
{
  "success": true,
  "data": {
    "collection_root": "D:/Programming_tools/.ccworkflow",
    "last_generate_mode": "ai",
    "last_install_scope": "project",
    "last_filters": {}
  }
}
```

## 7.20 services.settings_update_service

### 职责

1. 更新非迁移型设置。
2. 不负责根目录迁移。

### 接口

#### `update_settings(input) -> result`

输入：

```json
{
  "last_generate_mode": "form|ai",
  "last_install_scope": "project|global",
  "last_filters": {}
}
```

输出：

```json
{
  "success": true,
  "data": {
    "updated": true
  }
}
```

## 7.21 services.root_migration_service

### 职责

1. 校验新收藏根目录。
2. 复制旧数据。
3. 校验复制结果。
4. 切换设置。
5. 失败时保持旧目录可用。

### 接口

#### `migrate_root(input) -> result`

输入：

```json
{
  "new_root": "D:/NewPath/.ccworkflow"
}
```

输出：

```json
{
  "success": true,
  "data": {
    "old_root": "D:/Programming_tools/.ccworkflow",
    "new_root": "D:/NewPath/.ccworkflow",
    "migrated": true
  }
}
```

## 7.22 repositories.package_repository

### 职责

1. 落盘配置包。
2. 读取配置包。
3. 枚举配置包。
4. 删除配置包目录。

### 接口

#### `save_bundle(input) -> result`

输入：

```json
{
  "package": {},
  "category": "skills|hooks|mcp|mixed"
}
```

输出：

```json
{
  "success": true,
  "data": {
    "package_id": "pkg_xxx",
    "package_dir": ""
  }
}
```

#### `load_bundle(input) -> result`

输入：

```json
{
  "package_id": "pkg_xxx"
}
```

输出：

```json
{
  "success": true,
  "data": {
    "package": {}
  }
}
```

#### `list_manifests(input) -> result`

输入：

```json
{}
```

输出：

```json
{
  "success": true,
  "data": {
    "items": []
  }
}
```

## 7.23 repositories.install_record_repository

### 职责

1. 保存安装记录。
2. 读取安装记录。
3. 列出安装记录。
4. 更新卸载状态。

### 接口

#### `save_record(input) -> result`
#### `load_record(input) -> result`
#### `list_records(input) -> result`
#### `mark_uninstall_result(input) -> result`

输入输出统一约定：

1. 输入必须包含记录 ID 或完整记录对象。
2. 输出必须返回最新记录视图。

## 7.24 repositories.settings_repository

### 职责

1. 读取设置。
2. 保存设置。

### 接口

#### `load_settings(input) -> result`
#### `save_settings(input) -> result`

## 7.25 infra.fs_gateway

### 职责

1. 统一处理目录创建。
2. 统一处理文件复制。
3. 统一处理文本读写。
4. 统一处理删除。

### 接口

#### `ensure_dir(path) -> result`
#### `copy_file(input) -> result`
#### `write_text(input) -> result`
#### `read_text(input) -> result`
#### `delete_path(input) -> result`

## 7.26 infra.path_policy

### 职责

1. 校验路径合法性。
2. 校验是否落在白名单目录。
3. 校验项目根目录是否有效。

### 接口

#### `validate_project_root(input) -> result`
#### `validate_collection_root(input) -> result`
#### `validate_target_path(input) -> result`

## 8. Web API 任务边界

## 8.1 package_routes

接口：

1. `GET /api/packages`
2. `GET /api/packages/{package_id}`
3. `POST /api/packages`
4. `PUT /api/packages/{package_id}`
5. `DELETE /api/packages/{package_id}`
6. `POST /api/packages/{package_id}/copy`

要求：

1. 只做请求解析。
2. 调用对应 service。
3. 返回统一 JSON 结构。

## 8.2 generate_routes

接口：

1. `POST /api/generate-draft`
2. `GET /api/generate-status` 可不做，一期非必需。

## 8.3 install_routes

接口：

1. `POST /api/install/preview`
2. `POST /api/install/execute`
3. `POST /api/uninstall/{install_record_id}`

## 8.4 record_routes

接口：

1. `GET /api/install-records`
2. `GET /api/install-records/{install_record_id}`

## 8.5 settings_routes

接口：

1. `GET /api/settings`
2. `PUT /api/settings`
3. `POST /api/settings/migrate-root`

## 9. 页面开发边界

### 9.1 列表页

职责：

1. 分类查看。
2. 关键字检索。
3. 标签筛选。
4. 跳转详情、新建、AI 生成。

依赖接口：

1. `GET /api/packages`

### 9.2 编辑页

职责：

1. 编辑配置包基础信息。
2. 编辑对象列表。
3. 编辑附加脚本列表。
4. 本地预览。
5. 保存。

依赖接口：

1. `GET /api/packages/{package_id}`
2. `POST /api/packages`
3. `PUT /api/packages/{package_id}`

### 9.3 AI 生成页

职责：

1. 输入自然语言描述。
2. 展示草稿。
3. 允许用户继续编辑。
4. 手动保存。

依赖接口：

1. `POST /api/generate-draft`
2. `POST /api/packages`

### 9.4 配置包详情页

职责：

1. 展示元信息。
2. 展示对象与脚本。
3. 发起安装预览。
4. 提交安装执行。

依赖接口：

1. `GET /api/packages/{package_id}`
2. `POST /api/install/preview`
3. `POST /api/install/execute`

### 9.5 安装记录页

职责：

1. 查看安装记录列表。
2. 查看单次安装详情。
3. 发起卸载。

依赖接口：

1. `GET /api/install-records`
2. `GET /api/install-records/{install_record_id}`
3. `POST /api/uninstall/{install_record_id}`

### 9.6 设置页

职责：

1. 展示当前收藏根目录。
2. 更新普通设置。
3. 迁移收藏根目录。

依赖接口：

1. `GET /api/settings`
2. `PUT /api/settings`
3. `POST /api/settings/migrate-root`

## 10. 开发阶段任务拆分

## 阶段 A：项目骨架与基础约束

### T01 搭建目录骨架

1. 目标：建立第 3 节目录结构。
2. 模块：`app`、`web`、`domain`、`services`、`repositories`、`installers`、`integrations`、`infra`。
3. 交付物：
   1. 目录就位。
   2. 空模块文件就位。
   3. 依赖装配入口就位。
4. 验收：
   1. 程序可启动。
   2. 本地首页路由可访问。

### T02 定义领域数据结构

1. 目标：固化通用 DTO 与结果结构。
2. 模块：`domain/common_schema.py`、`package_schema.py`、`record_schema.py`、`settings_schema.py`、`enums.py`。
3. 交付物：
   1. 通用结果结构。
   2. PackageDraft。
   3. PackageObjectDraft。
   4. ScriptDraft。
   5. ConflictItem。
   6. InstallResolution。
4. 验收：
   1. 所有 service 输入输出结构可引用统一 schema。

### T03 建立基础基础设施模块

1. 目标：建立统一文件系统与路径策略入口。
2. 模块：`infra/fs_gateway.py`、`json_gateway.py`、`hash_gateway.py`、`path_policy.py`、`time_gateway.py`。
3. 交付物：
   1. 统一文件读写接口。
   2. 统一路径校验接口。
4. 验收：
   1. 后续模块不需要直接操作底层文件 API。

## 阶段 B：收藏根目录与设置

### T04 实现收藏根目录初始化

1. 目标：程序首次启动时可自动准备默认目录。
2. 模块：`root_init_service`、`settings_repository`。
3. 依赖：T02、T03。
4. 交付物：
   1. `ensure_root_ready` 接口。
   2. 默认目录初始化逻辑。
   3. `system/settings.json` 初始化。
5. 验收：
   1. 目录不存在时能自动创建。
   2. 重复启动不报错。

### T05 实现设置读取与普通更新

1. 目标：支持页面读取和更新普通设置。
2. 模块：`settings_query_service`、`settings_update_service`、`settings_routes`。
3. 依赖：T04。
4. 交付物：
   1. `get_settings`。
   2. `update_settings`。
5. 验收：
   1. 设置页可读取设置。
   2. 普通设置可更新并落盘。

## 阶段 C：配置包收藏能力

### T06 实现配置包仓储

1. 目标：能保存、读取、列举配置包。
2. 模块：`package_repository`。
3. 依赖：T02、T03、T04。
4. 交付物：
   1. `save_bundle`。
   2. `load_bundle`。
   3. `list_manifests`。
5. 验收：
   1. 配置包可按分类目录落盘。
   2. 详情可完整读回。

### T07 实现配置包校验服务

1. 目标：保存前能做统一校验。
2. 模块：`package_validation_service`。
3. 依赖：T02。
4. 交付物：
   1. `validate_package`。
5. 验收：
   1. 名称为空时阻止保存。
   2. 对象为空时阻止保存。
   3. 类型字段缺失时阻止保存。
   4. 脚本缺失引用时阻止保存。

### T08 实现配置包保存服务

1. 目标：支持新建与编辑保存。
2. 模块：`package_save_service`。
3. 依赖：T06、T07。
4. 交付物：
   1. `save_package`。
5. 验收：
   1. 可新建 skill 包。
   2. 可新建 hook 包。
   3. 可新建 MCP 包。
   4. 可新建混合包。

### T09 实现配置包查询服务

1. 目标：支持列表与详情查询。
2. 模块：`package_query_service`。
3. 依赖：T06。
4. 交付物：
   1. `list_packages`。
   2. `get_package_detail`。
5. 验收：
   1. 支持关键字过滤。
   2. 支持标签过滤。
   3. 支持类型过滤。

### T10 实现复制与删除服务

1. 目标：支持复制与删除配置包。
2. 模块：`package_copy_service`、`package_delete_service`。
3. 依赖：T06。
4. 交付物：
   1. `copy_package`。
   2. `delete_package`。
5. 验收：
   1. 复制后产生新包。
   2. 删除只影响收藏，不影响已安装内容。

### T11 实现配置包 API

1. 目标：把保存、查询、复制、删除暴露为接口。
2. 模块：`package_routes`。
3. 依赖：T08、T09、T10。
4. 交付物：
   1. `GET /api/packages`
   2. `GET /api/packages/{package_id}`
   3. `POST /api/packages`
   4. `PUT /api/packages/{package_id}`
   5. `DELETE /api/packages/{package_id}`
   6. `POST /api/packages/{package_id}/copy`
5. 验收：
   1. 前端页面可完整串通配置包 CRUD。

## 阶段 D：页面基础能力

### T12 实现列表页与详情页

1. 目标：先打通收藏浏览链路。
2. 模块：`page_routes`、列表页模板、详情页模板。
3. 依赖：T11。
4. 交付物：
   1. 列表页。
   2. 详情页。
5. 验收：
   1. 可查看分类、标签、关键字结果。
   2. 可进入详情页。

### T13 实现编辑页与本地预览

1. 目标：打通表单制作与保存。
2. 模块：编辑页模板、前端静态脚本。
3. 依赖：T11。
4. 交付物：
   1. 新建页。
   2. 编辑页。
   3. 本地预览能力。
5. 验收：
   1. 可添加多个对象。
   2. 可编辑附加脚本信息。
   3. 预览跟随输入变化。

## 阶段 E：AI 草稿生成

### T14 实现 Claude CLI 适配层

1. 目标：统一 Claude Code 调用入口。
2. 模块：`claude_cli_adapter`。
3. 依赖：T03。
4. 交付物：
   1. `check_available`。
   2. `run_generate`。
5. 验收：
   1. 可检测 Claude Code 可用性。
   2. 调用失败能返回明确错误。

### T15 实现草稿生成服务

1. 目标：把自然语言转换成结构化草稿。
2. 模块：`generate_draft_service`。
3. 依赖：T14、T02。
4. 交付物：
   1. `generate_draft`。
5. 验收：
   1. 结果不自动落盘。
   2. 结果结构非法时返回失败。

### T16 实现 AI 生成 API 与页面

1. 目标：用户可从页面生成并继续编辑草稿。
2. 模块：`generate_routes`、AI 生成页模板。
3. 依赖：T15、T13。
4. 交付物：
   1. `POST /api/generate-draft`
   2. AI 生成页
5. 验收：
   1. Claude 不可用时页面能显示不可用原因。
   2. Claude 可用时能生成草稿并进入编辑态。

## 阶段 F：安装预览与执行

### T17 实现目标路径解析

1. 目标：把对象映射到项目级或全局级标准路径。
2. 模块：`target_path_resolver`、`path_policy`。
3. 依赖：T02、T03。
4. 交付物：
   1. `resolve_targets`。
5. 验收：
   1. skill、hook、MCP 都能产出标准目标路径。
   2. 白名单外路径被拒绝。

### T18 实现脚本落地与占位符解析

1. 目标：附加脚本可以参与安装。
2. 模块：`script_materializer`。
3. 依赖：T17、T06。
4. 交付物：
   1. `materialize_scripts`。
5. 验收：
   1. 脚本可复制到目标目录。
   2. 缺失脚本时阻止安装。

### T19 实现冲突检测

1. 目标：安装前可返回用户决策项。
2. 模块：`conflict_detector`。
3. 依赖：T17、T06。
4. 交付物：
   1. `detect_conflicts`。
5. 验收：
   1. skill 同名冲突可识别。
   2. hook 冲突可识别。
   3. MCP 同名冲突可识别。

### T20 实现安装预览服务

1. 目标：打通安装前检查。
2. 模块：`install_preview_service`。
3. 依赖：T17、T18、T19。
4. 交付物：
   1. `preview_install`。
5. 验收：
   1. 可返回目标文件列表。
   2. 可返回冲突列表。
   3. 可返回脚本缺失列表。

### T21 实现类型安装器

1. 目标：按类型拆开安装逻辑，避免一个安装器过大。
2. 模块：`skill_installer`、`hook_installer`、`mcp_installer`。
3. 依赖：T17、T18。
4. 交付物：
   1. `install_skill` / `uninstall_skill`
   2. `install_hook` / `uninstall_hook`
   3. `install_mcp` / `uninstall_mcp`
5. 验收：
   1. 单个类型对象可独立安装。
   2. 安装器输出安装快照。

### T22 实现安装记录仓储

1. 目标：持久化安装结果，支持后续卸载。
2. 模块：`install_record_repository`。
3. 依赖：T03。
4. 交付物：
   1. `save_record`
   2. `load_record`
   3. `list_records`
   4. `mark_uninstall_result`
5. 验收：
   1. 安装记录可保存并查询。

### T23 实现安装执行服务

1. 目标：正式执行安装并落安装记录。
2. 模块：`install_execute_service`。
3. 依赖：T20、T21、T22。
4. 交付物：
   1. `execute_install`。
5. 验收：
   1. 支持项目级安装。
   2. 支持全局安装。
   3. 安装结果包含成功项、跳过项、失败项。

### T24 实现安装 API 与详情页安装交互

1. 目标：页面可执行安装预览与安装。
2. 模块：`install_routes`、详情页前端交互。
3. 依赖：T20、T23、T12。
4. 交付物：
   1. `POST /api/install/preview`
   2. `POST /api/install/execute`
5. 验收：
   1. 页面可展示冲突并提交处理策略。
   2. 页面可展示安装结果。

## 阶段 G：卸载能力

### T25 实现卸载服务

1. 目标：按安装记录安全卸载。
2. 模块：`uninstall_service`。
3. 依赖：T21、T22。
4. 交付物：
   1. `uninstall_by_record`。
5. 验收：
   1. 未被修改的内容可卸载。
   2. 被手工修改的内容会阻止卸载。

### T26 实现安装记录 API 与页面

1. 目标：用户可查看记录并发起卸载。
2. 模块：`record_routes`、安装记录页模板、`install_routes` 卸载接口。
3. 依赖：T22、T25。
4. 交付物：
   1. `GET /api/install-records`
   2. `GET /api/install-records/{install_record_id}`
   3. `POST /api/uninstall/{install_record_id}`
5. 验收：
   1. 可查看已安装记录列表。
   2. 可查看单条记录详情。
   3. 可从记录页发起卸载。

## 阶段 H：收藏根目录迁移

### T27 实现根目录迁移服务

1. 目标：支持修改收藏根目录并迁移旧数据。
2. 模块：`root_migration_service`。
3. 依赖：T05、T06、T03。
4. 交付物：
   1. `migrate_root`。
5. 验收：
   1. 成功迁移后新目录可继续使用。
   2. 迁移失败时保留旧目录。

### T28 实现设置页迁移交互

1. 目标：页面可发起迁移并展示结果。
2. 模块：设置页模板、`settings_routes`。
3. 依赖：T27、T05。
4. 交付物：
   1. 设置页迁移流程。
5. 验收：
   1. 用户可输入新路径。
   2. 迁移成功后页面刷新到新设置。
   3. 迁移失败时提示原因。

## 阶段 I：启动与打包交付

### T29 实现启动链路

1. 目标：双击程序后自动打开浏览器。
2. 模块：`bootstrap`、`factory`。
3. 依赖：T04、T12。
4. 交付物：
   1. 启动入口。
   2. 浏览器自动打开逻辑。
5. 验收：
   1. 页面可在 5 秒目标内打开。

### T30 实现打包与交付校验

1. 目标：生成 Windows 可分发产物。
2. 模块：打包配置。
3. 依赖：T29、全部核心功能。
4. 交付物：
   1. `.exe` 发布方案。
   2. 运行说明。
5. 验收：
   1. 新环境可启动。
   2. 收藏、AI、安装、卸载、迁移核心链路可冒烟通过。

## 11. 任务依赖与并行建议

### 11.1 必须串行的主干

1. T01 -> T02 -> T03 -> T04
2. T06 -> T07 -> T08 -> T11
3. T17 -> T18 -> T19 -> T20 -> T21 -> T23 -> T24
4. T22 -> T25 -> T26
5. T27 -> T28

### 11.2 可并行任务

1. T05 与 T06 可并行。
2. T09 与 T10 可并行。
3. T12 与 T13 可并行。
4. T14 与 T13 可并行。
5. T22 与 T21 可并行。

### 11.3 推荐实施顺序

1. 先做收藏闭环：T01-T13。
2. 再做 AI 草稿：T14-T16。
3. 再做安装闭环：T17-T24。
4. 再做卸载：T25-T26。
5. 再做迁移：T27-T28。
6. 最后做启动打包：T29-T30。

## 12. 每阶段完成定义

### 12.1 收藏闭环完成定义

1. 用户可新建、编辑、查看、复制、删除配置包。
2. 可按类型、标签、关键字检索。
3. 可保存多对象、多类型配置包。

### 12.2 AI 闭环完成定义

1. 用户可输入自然语言生成草稿。
2. 结果不会自动保存。
3. 生成失败时有明确提示。

### 12.3 安装闭环完成定义

1. 用户可预览安装结果。
2. 冲突可选替换、跳过、取消。
3. 安装后生成记录。

### 12.4 卸载闭环完成定义

1. 用户可按安装记录卸载。
2. 非本工具内容不会被误删。
3. 被人工修改的内容会阻止卸载。

### 12.5 迁移闭环完成定义

1. 用户可修改收藏根目录。
2. 旧数据可迁移到新目录。
3. 失败时不会进入不完整状态。

## 13. 当前阶段必须先定的接口决策

以下 4 项若不先拍板，后续模块接口会反复改：

1. hook 是否强制要求 `hook_key`。
   1. 建议：强制要求。
   2. 原因：否则无法稳定识别冲突与卸载目标。
2. 附加脚本占位符是否固定为 `{{script:<filename>}}`。
   1. 建议：固定。
   2. 原因：否则脚本替换接口无法稳定。
3. Claude CLI 生成接口是否能稳定返回 JSON。
   1. 建议：先按“必须返回 JSON”设计。
   2. 原因：否则 `generate_draft_service` 难以稳定输出结构化草稿。
4. 全局 MCP 最终目标文件是否确认是 `~/.claude.json`。
   1. 建议：实现前先实测确认。
   2. 原因：这会影响 `target_path_resolver` 和 `mcp_installer` 的接口契约。

## 14. 建议的首批开发包

如果要按最小可交付批次推进，建议先拆成 4 个开发包：

1. 开发包 A：收藏闭环
   1. T01-T13
2. 开发包 B：AI 草稿闭环
   1. T14-T16
3. 开发包 C：安装与卸载闭环
   1. T17-T26
4. 开发包 D：迁移、启动、打包
   1. T27-T30

这样安排的好处：

1. 每一包都能形成可演示结果。
2. 收藏能力先落地，能尽早验证数据模型是否合理。
3. 安装与卸载放到后半段，避免前期被复杂文件合并逻辑拖慢。
4. 打包放最后，避免前期频繁变动时反复处理发布问题。
