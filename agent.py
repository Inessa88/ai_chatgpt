import json
from openai import OpenAI

from tools import (
    list_files,
    read_file,
    write_file,
)

client = OpenAI()


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List project files",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read file content",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write file content",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["path", "content"],
            },
        },
    },
]


class Agent:
    def run(self, task):
        messages = [
            {
                "role": "system",
                "content": """
You are a senior Django developer.

You solve tasks by:
- exploring project files
- reading code
- editing files

Be careful and pragmatic.
You must NEVER explore:
- .venv
- __pycache__
- .git
- database files
- dependency folders

Only work with application code.
""",
            },
            {
                "role": "user",
                "content": f"""
TASK:
{task["summary"]}

DESCRIPTION:
{task["description"]}
""",
            },
        ]

        for step in range(10):
            print(f"\n======== STEP {step} ========")

            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=messages,
                tools=TOOLS,
            )

            msg = response.choices[0].message

            if msg.tool_calls:
                messages.append(msg)

                for tool_call in msg.tool_calls:
                    name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)

                    print("\nTOOL:", name)
                    print(args)

                    result = self.execute_tool(name, args)

                    print("\nRESULT:")
                    print(result)

                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": str(result),
                        }
                    )

            else:
                print("\nASSISTANT:")
                print(msg.content)

                return msg.content

    def execute_tool(self, name, args):
        if name == "list_files":
            return list_files()

        elif name == "read_file":
            return read_file(args["path"])

        elif name == "write_file":
            return write_file(
                args["path"],
                args["content"],
            )

        return "UNKNOWN TOOL"