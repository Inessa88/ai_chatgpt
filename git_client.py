import subprocess


class GitClient:
    def checkout_new_branch(self, branch: str):
        print(f"\n🌿 Checkout branch: {branch}")
        subprocess.run(["git", "checkout", "-b", branch], check=False)

    def commit_all(self, message: str):
        print("\n📦 Commit changes")
        subprocess.run(["git", "add", "-A"], check=True)
        subprocess.run(["git", "commit", "-m", message], check=True)

    def push(self, branch: str):
        print("\n🚀 Push branch")
        subprocess.run(["git", "push", "-u", "origin", branch], check=True)