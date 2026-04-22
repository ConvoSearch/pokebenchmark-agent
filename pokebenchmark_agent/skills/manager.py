"""File-based CRUD for skill markdown files.

Directory layout:
    <skills_dir>/common/*.md        — shared across all games
    <skills_dir>/<game>/*.md         — game-specific (e.g. firered, emerald)

A skill is referenced by (scope, name) where scope is "common" or a game name,
and name is the filename without .md.
"""
import os
from dataclasses import dataclass


SKILL_FILE_SUFFIX = ".md"
COMMON_SCOPE = "common"


@dataclass
class Skill:
    scope: str  # "common" or game name
    name: str   # filename without .md
    content: str

    def to_dict(self) -> dict:
        return {"scope": self.scope, "name": self.name, "content": self.content}


class SkillManager:
    def __init__(self, skills_dir: str, allowed_games: list[str]):
        self.skills_dir = skills_dir
        self.allowed_games = allowed_games
        self.allowed_scopes = [COMMON_SCOPE] + list(allowed_games)
        os.makedirs(skills_dir, exist_ok=True)
        for scope in self.allowed_scopes:
            os.makedirs(os.path.join(skills_dir, scope), exist_ok=True)

    def _validate_scope(self, scope: str):
        if scope not in self.allowed_scopes:
            raise ValueError(f"Invalid scope '{scope}'. Must be one of {self.allowed_scopes}")

    def _validate_name(self, name: str):
        if not name or "/" in name or "\\" in name or name.startswith("."):
            raise ValueError(f"Invalid skill name: '{name}'")

    def _path(self, scope: str, name: str) -> str:
        return os.path.join(self.skills_dir, scope, name + SKILL_FILE_SUFFIX)

    def list_skills(self, scope: str | None = None) -> list[Skill]:
        scopes = [scope] if scope else self.allowed_scopes
        skills = []
        for s in scopes:
            self._validate_scope(s)
            dir_path = os.path.join(self.skills_dir, s)
            if not os.path.isdir(dir_path):
                continue
            for f in sorted(os.listdir(dir_path)):
                if not f.endswith(SKILL_FILE_SUFFIX):
                    continue
                name = f[: -len(SKILL_FILE_SUFFIX)]
                with open(os.path.join(dir_path, f), "r") as fh:
                    content = fh.read()
                skills.append(Skill(scope=s, name=name, content=content))
        return skills

    def get_skill(self, scope: str, name: str) -> Skill | None:
        self._validate_scope(scope)
        self._validate_name(name)
        path = self._path(scope, name)
        if not os.path.isfile(path):
            return None
        with open(path, "r") as f:
            return Skill(scope=scope, name=name, content=f.read())

    def write_skill(self, scope: str, name: str, content: str) -> Skill:
        self._validate_scope(scope)
        self._validate_name(name)
        path = self._path(scope, name)
        with open(path, "w") as f:
            f.write(content)
        return Skill(scope=scope, name=name, content=content)

    def delete_skill(self, scope: str, name: str) -> bool:
        self._validate_scope(scope)
        self._validate_name(name)
        path = self._path(scope, name)
        if not os.path.isfile(path):
            return False
        os.remove(path)
        return True
