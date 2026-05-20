from dotenv import load_dotenv

from jira_client import JiraClient
from git_client import GitClient
from agent import Agent

load_dotenv()

jira = JiraClient()
git = GitClient()
agent = Agent()


def run():
    print("\n===== AI ORCHESTRATOR START =====")

    max_tasks = 5  # защита от бесконечного цикла

    for i in range(max_tasks):
        print(f"\n\n===== TASK LOOP {i} =====")

        task = jira.get_next_task()

        if not task:
            print("No more tasks in Jira")
            break

        print("\n📌 TASK FOUND:", task["key"])

        branch = task["key"]

        git.checkout_new_branch(branch)

        result = agent.run(task)

        print("\n🧠 RESULT:", result)

        committed = git.commit_all(f"{task['key']}: done by agent")

        if not committed:
            print("⚠️ Skipping push + jira done (no changes)")
            continue

        git.push(branch)

        jira.mark_done(task["key"])

    print("\n\n✅ ALL TASKS COMPLETE")


if __name__ == "__main__":
    run()