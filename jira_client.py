import os
import requests
from requests.auth import HTTPBasicAuth


class JiraClient:
    def __init__(self):
        self.base_url = os.getenv("JIRA_BASE_URL")
        self.email = os.getenv("JIRA_EMAIL")
        self.token = os.getenv("JIRA_API_TOKEN")
        self.project = os.getenv("JIRA_PROJECT_KEY")

        self.auth = HTTPBasicAuth(self.email, self.token)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
    def get_next_task(self):
        jql = f'project = {self.project} AND status = "To Do" ORDER BY created ASC'

        url = f"{self.base_url}/rest/api/3/search/jql"

        payload = {
            "jql": jql,
            "maxResults": 1,
            "fields": ["summary", "description"]
        }

        r = requests.post(
            url,
            headers=self.headers,
            auth=self.auth,
            json=payload
        )

        print("STATUS:", r.status_code)
        print("TEXT:", r.text)

        r.raise_for_status()
        data = r.json()

        issues = data.get("issues", [])
        if not issues:
            return None

        issue = issues[0]

        return {
            "key": issue["key"],
            "summary": issue["fields"]["summary"],
            "description": str(issue["fields"].get("description", "")),
        }

    def mark_done(self, key: str):
        # получаем transitions
        url = f"{self.base_url}/rest/api/3/issue/{key}/transitions"

        r = requests.get(url, headers=self.headers, auth=self.auth)
        r.raise_for_status()

        transitions = r.json().get("transitions", [])

        done_id = None
        for t in transitions:
            if t["name"].lower() == "done":
                done_id = t["id"]
                break

        if not done_id:
            print("⚠️ No DONE transition found")
            return

        requests.post(
            url,
            headers=self.headers,
            auth=self.auth,
            json={"transition": {"id": done_id}},
        )