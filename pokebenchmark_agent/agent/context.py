class ContextBuilder:
    def build(self, state_text: str, skills_text: str = "", plan_text: str = "", memory_text: str = "") -> str:
        sections = []
        if skills_text:
            sections.append(skills_text)
        if plan_text:
            sections.append(plan_text)
        if memory_text:
            sections.append(memory_text)
        sections.append(f"## Current game state:\n\n{state_text}")
        return "\n\n---\n\n".join(sections)
