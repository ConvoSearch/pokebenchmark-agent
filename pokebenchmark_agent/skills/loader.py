import os
import glob

class SkillLoader:
    def __init__(self, skills_dir: str, game: str):
        self.skills_dir = skills_dir
        self.game = game

    def _read_md_files(self, directory: str) -> list[str]:
        if not os.path.isdir(directory):
            return []
        files = sorted(glob.glob(os.path.join(directory, "*.md")))
        results = []
        for f in files:
            with open(f, "r") as fh:
                results.append(fh.read())
        return results

    def load_common(self) -> list[str]:
        return self._read_md_files(os.path.join(self.skills_dir, "common"))

    def load_game_specific(self) -> list[str]:
        return self._read_md_files(os.path.join(self.skills_dir, self.game))

    def load_files(self, paths: list[str]) -> list[str]:
        results = []
        for path in paths:
            if os.path.isfile(path):
                with open(path, "r") as f:
                    results.append(f.read())
        return results

    def load_all(self) -> list[str]:
        return self.load_common() + self.load_game_specific()

    def format_for_context(self) -> str:
        skills = self.load_all()
        if not skills:
            return ""
        sections = []
        for skill in skills:
            first_line = skill.strip().split("\n")[0].lstrip("# ").strip()
            sections.append(f"## Skill: {first_line}\n\n{skill.strip()}")
        return "\n\n---\n\n".join(sections)
