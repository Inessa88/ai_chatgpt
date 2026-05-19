class Agent:
    def run(self, task: dict) -> str:
        print("\n🤖 AGENT START")
        print("Task:", task["summary"])
        print("Description:", task["description"])

        # пока просто имитация работы
        result = f"Implemented: {task['summary']}"

        print("🤖 AGENT DONE\n")
        return result