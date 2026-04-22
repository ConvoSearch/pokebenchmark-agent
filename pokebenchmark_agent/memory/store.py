import os

class MemoryStore:
    def __init__(self, memory_dir: str):
        self.memory_dir = memory_dir
        os.makedirs(memory_dir, exist_ok=True)

    def _path(self, name: str) -> str:
        return os.path.join(self.memory_dir, f"{name}.md")

    def write(self, name: str, content: str):
        with open(self._path(name), "w") as f:
            f.write(content)

    def read(self, name: str) -> str | None:
        path = self._path(name)
        if not os.path.isfile(path):
            return None
        with open(path, "r") as f:
            return f.read()

    def append(self, name: str, content: str):
        with open(self._path(name), "a") as f:
            f.write("\n" + content)

    def delete(self, name: str):
        path = self._path(name)
        if os.path.isfile(path):
            os.remove(path)

    def list_entries(self) -> list[str]:
        if not os.path.isdir(self.memory_dir):
            return []
        return sorted(f.removesuffix(".md") for f in os.listdir(self.memory_dir)
                      if f.endswith(".md") and os.path.isfile(os.path.join(self.memory_dir, f)))

    def format_for_context(self) -> str:
        entries = self.list_entries()
        if not entries:
            return ""
        sections = []
        for name in entries:
            content = self.read(name)
            sections.append(f"### {name}\n\n{content}")
        return "## Agent Memory\n\n" + "\n\n".join(sections)
