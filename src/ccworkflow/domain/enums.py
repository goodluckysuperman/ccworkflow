from enum import StrEnum


class ObjectType(StrEnum):
    SKILL = "skill"
    HOOK = "hook"
    MCP = "mcp"


class PackageCategory(StrEnum):
    SKILLS = "skills"
    HOOKS = "hooks"
    MCP = "mcp"
    MIXED = "mixed"


class InstallScope(StrEnum):
    PROJECT = "project"
    GLOBAL = "global"
