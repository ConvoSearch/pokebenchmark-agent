import os

class PlanningWorkspace:
    ACTIVE_FILE = ".active_plan"

    def __init__(self, plans_dir: str):
        self.plans_dir = plans_dir
        os.makedirs(plans_dir, exist_ok=True)

    def write_plan(self, name: str, content: str):
        with open(os.path.join(self.plans_dir, name), "w") as f:
            f.write(content)

    def read_plan(self, name: str) -> str | None:
        path = os.path.join(self.plans_dir, name)
        if not os.path.isfile(path):
            return None
        with open(path, "r") as f:
            return f.read()

    def delete_plan(self, name: str):
        path = os.path.join(self.plans_dir, name)
        if os.path.isfile(path):
            os.remove(path)

    def list_plans(self) -> list[str]:
        if not os.path.isdir(self.plans_dir):
            return []
        return sorted(f for f in os.listdir(self.plans_dir)
                      if f.endswith(".md") and os.path.isfile(os.path.join(self.plans_dir, f)))

    def set_active(self, name: str):
        with open(os.path.join(self.plans_dir, self.ACTIVE_FILE), "w") as f:
            f.write(name)

    def clear_active(self):
        path = os.path.join(self.plans_dir, self.ACTIVE_FILE)
        if os.path.isfile(path):
            os.remove(path)

    def get_active_plan(self) -> str | None:
        active_path = os.path.join(self.plans_dir, self.ACTIVE_FILE)
        if not os.path.isfile(active_path):
            return None
        with open(active_path, "r") as f:
            name = f.read().strip()
        return self.read_plan(name)

    def format_for_context(self) -> str:
        plan = self.get_active_plan()
        if not plan:
            return ""
        return f"## Active Plan\n\n{plan}"
