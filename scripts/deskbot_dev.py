#!/usr/bin/env python3
"""
DESKBOT Development Manager CLI

Subcommands:
  check   - parse IMPLEMENTATION_PLAN.md and report stage progress
  mark    - mark a stage complete / incomplete in the plan
  review  - snapshot project state, diff against the last snapshot, append to CHANGELOG.md
  cmdlog  - look up / record shell commands in COMMAND_LOG.md (check the file BEFORE running)
  commit  - git add/commit/push (requires --approved, i.e. the user finalized the changes)
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SOURCE_EXTENSIONS = {
    ".py", ".js", ".html", ".css", ".ino", ".scad", ".yaml", ".yml",
    ".json", ".md", ".toml", ".cfg", ".ini", ".sh", ".bat", ".ps1", ".txt",
}
SKIP_DIRS = {"__pycache__", ".git", "node_modules", ".venv", "venv", "dist", "build", "models"}
STATE_FILE = ".deskbot_state.json"
STAGE_RE = re.compile(r"^###\s+Stage\s+(\d+):\s*(.+?)\s*$", re.MULTILINE)
DONE_MARK = "\u2705"


def fail(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


# -- check / mark ------------------------------------------------------------

def parse_stages(text):
    stages = []
    for m in STAGE_RE.finditer(text):
        title = m.group(2)
        done = DONE_MARK in title
        stages.append({
            "stage": int(m.group(1)),
            "title": title.replace(DONE_MARK, "").strip(),
            "status": "complete" if done else "pending",
        })
    return stages


def cmd_check(args):
    plan = Path(args.plan)
    if not plan.exists():
        fail(f"plan file not found: {plan}")
    stages = parse_stages(plan.read_text(encoding="utf-8"))
    done = [s for s in stages if s["status"] == "complete"]
    nxt = next((s for s in stages if s["status"] == "pending"), None)
    result = {
        "total_stages": len(stages),
        "completed": len(done),
        "pending": len(stages) - len(done),
        "completion_pct": round(100 * len(done) / len(stages), 1) if stages else 0,
        "next_stage": nxt,
        "stages": stages,
    }
    if args.output:
        Path(args.output).write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"Success! Progress report written to: {args.output}")
    # Always print a short human summary (never the full JSON) to keep stdout small.
    print(f"{len(done)}/{len(stages)} stages complete ({result['completion_pct']}%)")
    print(f"Next stage: {nxt['stage']} - {nxt['title']}" if nxt else "All stages complete.")


def cmd_mark(args):
    plan = Path(args.plan)
    if not plan.exists():
        fail(f"plan file not found: {plan}")
    text = plan.read_text(encoding="utf-8")
    found = False

    def repl(m):
        nonlocal found
        if int(m.group(1)) != args.stage:
            return m.group(0)
        found = True
        title = m.group(2).replace(DONE_MARK, "").strip()
        if args.undo:
            return f"### Stage {m.group(1)}: {title}"
        return f"### Stage {m.group(1)}: {title} {DONE_MARK}"

    new = STAGE_RE.sub(repl, text)
    if not found:
        fail(f"stage {args.stage} not found in {plan}")
    plan.write_text(new, encoding="utf-8")
    print(f"Stage {args.stage} marked {'incomplete' if args.undo else 'complete'}.")


# -- review ------------------------------------------------------------------

def snapshot(project):
    files = {}
    for root, dirs, names in os.walk(project):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for n in names:
            p = Path(root) / n
            if p.suffix.lower() in SOURCE_EXTENSIONS and n not in {STATE_FILE, "CHANGELOG.md", "COMMAND_LOG.md"}:
                data = p.read_bytes()
                files[str(p.relative_to(project)).replace("\\", "/")] = {
                    "sha": hashlib.sha1(data).hexdigest(),
                    "lines": data.count(b"\n") + 1,
                }
    return files


def cmd_review(args):
    project = Path(args.project).resolve()
    if not project.is_dir():
        fail(f"project directory not found: {project}")
    new = snapshot(project)
    state_path = project / STATE_FILE
    old = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}

    added = sorted(set(new) - set(old))
    removed = sorted(set(old) - set(new))
    modified = sorted(k for k in set(new) & set(old) if new[k]["sha"] != old[k]["sha"])
    first_run = not old

    report = {
        "project_root": str(project),
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "total_files": len(new),
        "total_lines": sum(v["lines"] for v in new.values()),
        "added": added, "modified": modified, "removed": removed,
        "files": {k: v["lines"] for k, v in sorted(new.items())},
    }

    changed = added or modified or removed
    if changed or first_run:
        entry = [f"\n## [{report['timestamp']}] {'Baseline snapshot' if first_run else 'Review'}"]
        entry.append(f"- Files: {report['total_files']}, lines: {report['total_lines']}")
        for label, items in (("Added", added), ("Modified", modified), ("Removed", removed)):
            if items and not first_run:
                entry.append(f"- {label}: " + ", ".join(items))
        if args.note:
            entry.append(f"- Note: {args.note}")
        cl = project / "CHANGELOG.md"
        if not cl.exists():
            cl.write_text("# DESKBOT Changelog\n", encoding="utf-8")
        with open(cl, "a", encoding="utf-8") as f:
            f.write("\n".join(entry) + "\n")
        print(f"Changelog updated: {cl}")
    else:
        print("No changes since last review; changelog untouched.")

    state_path.write_text(json.dumps(new, indent=2), encoding="utf-8")
    if args.output:
        Path(args.output).write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"Success! Review report written to: {args.output}")
    print(f"{report['total_files']} files / {report['total_lines']} lines; "
          f"+{len(added)} ~{len(modified)} -{len(removed)}")


# -- cmdlog ------------------------------------------------------------------

def cmd_cmdlog(args):
    project = Path(args.project).resolve()
    log = project / "COMMAND_LOG.md"
    if not log.exists():
        log.write_text("# DESKBOT Command Log\n\nCheck this file before running a new command.\n\n", encoding="utf-8")
    lines = log.read_text(encoding="utf-8").splitlines()
    prior = [l for l in lines if l.startswith("- ") and args.command in l]
    if args.action == "lookup":
        if prior:
            print("Already recorded:")
            for l in prior:
                print("  " + l)
        else:
            print("Not recorded yet - new command.")
    else:  # record
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        with open(log, "a", encoding="utf-8") as f:
            f.write(f"- `{args.command}` | {stamp} | {args.result or 'ok'}\n")
        print(f"Recorded in {log}")


# -- commit ------------------------------------------------------------------

def git(project, *a):
    return subprocess.run(["git", *a], cwd=str(project), capture_output=True, text=True)


def cmd_commit(args):
    project = Path(args.project).resolve()
    if not args.approved:
        fail("refusing to commit: pass --approved only after the user has finalized the changes.")
    if not (project / ".git").exists():
        git(project, "init")
        git(project, "branch", "-M", "main")
    if git(project, "add", "-A").returncode != 0:
        fail("git add failed")
    if not git(project, "status", "--porcelain").stdout.strip():
        print("Nothing to commit - working tree clean.")
        return
    r = git(project, "commit", "-m", args.message)
    if r.returncode != 0:
        fail(f"git commit failed: {r.stderr.strip() or r.stdout.strip()}")
    print(f"Committed: {args.message}")
    if not git(project, "remote", "-v").stdout.strip():
        print("No git remote configured - committed locally. Add one: git remote add origin <url>")
        return
    branch = git(project, "branch", "--show-current").stdout.strip() or "main"
    r = git(project, "push", "-u", "origin", branch)
    if r.returncode != 0:
        print(f"WARNING: push failed: {r.stderr.strip()}", file=sys.stderr)
        sys.exit(2)
    print(f"Pushed to origin/{branch}.")


def main():
    ap = argparse.ArgumentParser(prog="deskbot_dev", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="subcmd", required=True)

    p = sub.add_parser("check", help="stage progress")
    p.add_argument("--plan", required=True)
    p.add_argument("--output")

    p = sub.add_parser("mark", help="mark a stage done/undone")
    p.add_argument("--plan", required=True)
    p.add_argument("--stage", type=int, required=True)
    p.add_argument("--undo", action="store_true")

    p = sub.add_parser("review", help="diff vs last snapshot, append CHANGELOG.md")
    p.add_argument("--project", required=True)
    p.add_argument("--output")
    p.add_argument("--note", help="free-text note for the changelog entry")

    p = sub.add_parser("cmdlog", help="lookup/record commands in COMMAND_LOG.md")
    p.add_argument("--project", required=True)
    p.add_argument("--action", choices=["lookup", "record"], required=True)
    p.add_argument("--command", required=True)
    p.add_argument("--result")

    p = sub.add_parser("commit", help="git add/commit/push after user approval")
    p.add_argument("--project", required=True)
    p.add_argument("--message", required=True)
    p.add_argument("--approved", action="store_true")

    a = ap.parse_args()
    {"check": cmd_check, "mark": cmd_mark, "review": cmd_review,
     "cmdlog": cmd_cmdlog, "commit": cmd_commit}[a.subcmd](a)


if __name__ == "__main__":
    main()

