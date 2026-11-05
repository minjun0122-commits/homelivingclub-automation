"""Claude Code 훅 스크립트.

  guard.py env   (PreToolUse)  : .env 를 읽거나 고치려는 도구 호출을 막아요. .env.example 은 허용.
  guard.py yaml  (PostToolUse) : products/*.yaml 을 고치면 register.py check 를 자동으로 돌려요.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# ".env" 단독만 잡고 ".env.example", "my.env.bak" 같은 건 통과
ENV_RE = re.compile(r"(?<![\w.])\.env(?![\w.])", re.IGNORECASE)

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")


def read_input():
    # utf-8-sig: PowerShell 파이프가 붙이는 BOM 도 처리
    return json.loads(sys.stdin.buffer.read().decode("utf-8-sig") or "{}")


def guard_env(data):
    tool_input = data.get("tool_input") or {}
    fields = ("file_path", "path", "pattern", "glob", "command", "notebook_path")
    text = " ".join(str(tool_input.get(f, "")) for f in fields)
    if ENV_RE.search(text):
        print(
            ".env 에는 커머스 API 시크릿이 들어 있어서 Claude 가 읽거나 고칠 수 없어요. "
            "값이 필요하면 사용자에게 직접 확인해 달라고 요청하세요 (.env.example 은 읽어도 돼요).",
            file=sys.stderr,
        )
        sys.exit(2)


def check_yaml(data):
    tool_input = data.get("tool_input") or {}
    path = Path(tool_input.get("file_path", ""))
    if path.suffix.lower() not in (".yaml", ".yml"):
        return
    try:
        rel = path.resolve().relative_to(ROOT / "products")
    except ValueError:
        return

    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    result = subprocess.run(
        [sys.executable, "register.py", "check", str(Path("products") / rel)],
        cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", timeout=60,
    )
    report = (result.stdout + result.stderr).strip()
    # 이미 등록된 상품의 already_registered ❌ 는 의도된 표시라 오류로 치지 않아요
    error_lines = [l for l in report.splitlines()
                   if l.strip().startswith("❌") and "already_registered" not in l]
    has_errors = result.returncode != 0 or bool(error_lines)

    out = {"hookSpecificOutput": {"hookEventName": "PostToolUse",
                                  "additionalContext": f"[자동 검사] register.py check products/{rel.as_posix()}\n{report}"}}
    if has_errors:
        out["decision"] = "block"
        out["reason"] = f"products/{rel.as_posix()} 검사에서 ❌ 항목이 나왔어요. 위 결과를 보고 고쳐주세요."
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    data = read_input()
    if mode == "env":
        guard_env(data)
    elif mode == "yaml":
        check_yaml(data)
