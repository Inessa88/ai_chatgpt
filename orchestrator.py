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

    task = jira.get_next_task()

    if not task:
        print("No tasks in Jira")
        return

    print("\n📌 TASK FOUND:", task["key"])

    branch = task["key"]

    git.checkout_new_branch(branch)

    result = agent.run(task)

    print("\n🧠 RESULT:", result)

    git.commit_all(f"{task['key']}: done by agent")

    git.push(branch)

    jira.mark_done(task["key"])

    print("\n✅ CYCLE COMPLETE")


if __name__ == "__main__":
    run()