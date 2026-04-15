import re
import subprocess
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class CheckRequest(BaseModel):
    content: str

@app.get("/health")
def health():
    try:
        result = subprocess.run(
            ["spamc", "-R", "-d", "127.0.0.1", "-p", "1783", "-t", "5"],
            input="Subject: healthcheck\n\nhello".encode(),
            capture_output=True,
            timeout=8,
            check=False,
        )
        ok = result.returncode == 0
        return {"ok": ok}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@app.post("/check")
def check(req: CheckRequest):
    if not req.content.strip():
        raise HTTPException(status_code=400, detail="content is required")

    try:
        result = subprocess.run(
            ["spamc", "-R", "-d", "127.0.0.1", "-p", "1783", "-t", "8"],
            input=req.content.encode(),
            capture_output=True,
            timeout=12,
            check=False,
        )

        output = result.stdout.decode(errors="replace").strip()

        if not output:
            raise HTTPException(status_code=502, detail="empty response from spamc")

        lines = output.splitlines()
        first = lines[0].strip()

        score = 0.0
        threshold = 5.0

        m = re.match(r"^\s*(-?\d+(?:\.\d+)?)\s*/\s*(-?\d+(?:\.\d+)?)", first)
        if m:
            score = float(m.group(1))
            threshold = float(m.group(2))

        rules = []

        for line in lines[1:]:
            rule_match = re.match(r"^\s*(-?\d+(?:\.\d+)?)\s+([A-Z0-9_]+)\s+(.*)$", line)
            if rule_match:
                rules.append({
                    "name": rule_match.group(2),
                    "score": float(rule_match.group(1)),
                    "description": rule_match.group(3).strip(),
                })

        return {
            "score": score,
            "threshold": threshold,
            "rules": rules,
            "version": "SpamAssassin external service",
        }

    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="SpamAssassin timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
