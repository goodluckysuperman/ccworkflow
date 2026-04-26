# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 仓库目标

这个仓库的目标，是逐步演进为一个基于 Python 3.11 的工具，用来方便地管理 Claude Code 中的各类配置与定制能力，尤其包括：skills、commands、hooks、MCP、subagents 和 rules。

## 环境与包管理

- 本仓库统一使用 `uv` 管理依赖与执行命令。
- 本地开发环境应以 Python 3.11 为准，`.python-version` 当前为 `3.11`。
- `pyproject.toml` 当前声明的 Python 范围是 `>=3.10, <3.12`，但除非有明确需要修改项目元数据，否则默认按 3.11 开发。

## 常用命令

### 安装 / 同步依赖

```bash
uv sync
```

### 运行当前入口程序

```bash
uv run python main.py
```

### 测试

当前仓库还没有配置测试框架，也没有 `tests/` 目录。

### Lint / 格式化

当前仓库还没有配置 linter 或 formatter。

## 当前架构

这个代码库目前仍是一个最小可运行的启动骨架。

- `main.py` 是当前唯一的运行入口，全部可执行行为都集中在 `main()` 函数中，目前只输出占位文本。
- `pyproject.toml` 是项目元数据和依赖声明的来源。
- `uv.lock` 是由 `uv` 管理的锁文件；依赖变化后，应同步更新该文件。
- 当前还没有包目录、内部模块分层，也没有测试体系。

## 后续演进时的工作假设

- 应优先把这个项目发展为一个面向 Claude Code 工作流 / 配置管理的小型 Python 应用，而不是通用模板项目。
- 当代码规模超出 `main.py` 单文件时，优先围绕实际配置领域拆分结构，例如：skills、commands、hooks、MCP、subagents、rules。
- 这个文件中的命令说明必须始终和 `pyproject.toml` 里实际配置的工具链保持一致；不要提前写入尚未存在的 lint、test 或 build 命令。
