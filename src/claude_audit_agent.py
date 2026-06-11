from __future__ import annotations

"""
Optional runner using the Claude Agent SDK.

Install:
    pip install -r requirements-agent.txt
    export ANTHROPIC_API_KEY=...

Run:
    python src/claude_audit_agent.py --gaps outputs/gaps.csv --backlog outputs/editorial_backlog.csv
"""

import argparse
import asyncio
from pathlib import Path


async def run_audit(gaps_path: str, backlog_path: str) -> None:
    try:
        from claude_agent_sdk import ClaudeAgentOptions, query
    except ImportError as exc:
        raise RuntimeError("Install requirements-agent.txt to use the Claude Agent SDK runner.") from exc

    prompt = f"""
You are auditing an SEO/GEO entity-gap pipeline.

Read these files:
- {gaps_path}
- {backlog_path}

Return:
1. Top 10 opportunities.
2. Which gaps are probably false positives.
3. Which should become new articles vs updates.
4. Measurement plan in Search Console.

Be critical. Do not invent traffic data.
""".strip()

    options = ClaudeAgentOptions(allowed_tools=["Read", "Grep", "Bash"], max_turns=6)
    async for message in query(prompt=prompt, options=options):
        print(message)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gaps", default="outputs/gaps.csv")
    parser.add_argument("--backlog", default="outputs/editorial_backlog.csv")
    args = parser.parse_args()
    if not Path(args.gaps).exists():
        raise FileNotFoundError(args.gaps)
    if not Path(args.backlog).exists():
        raise FileNotFoundError(args.backlog)
    asyncio.run(run_audit(args.gaps, args.backlog))


if __name__ == "__main__":
    main()
