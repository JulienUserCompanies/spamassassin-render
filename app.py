import re
import subprocess
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


class CheckRequest(BaseModel):
    content: str


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/check")
def check(req: CheckRequest):
    if not req.content.strip():
        raise HTTPException(status_code=400, detail="content is required")

    try:
        result = subprocess.run(
            ["spamassassin", "-t"],
            input=req.content.encode(),
            capture_output=True,
            timeout=20,
            check=False,
        )

        output = result.stdout.decode(errors="replace")

        if not output.strip():
            raise HTTPException(status_code=502, detail="empty response from spamassassin")

        score = 0.0
        threshold = 5.0
        rules = []

        # Parse X-Spam-Status header, example:
        # X-Spam-Status: Yes, score=6.2 required=5.0 tests=...
        status_match = re.search(
            r"X-Spam-Status:\s+\w+,\s+score=([-]?\d+(?:\.\d+)?)\s+required=([-]?\d+(?:\.\d+)?)",
            output,
            re.IGNORECASE,
        )
        if status_match:
            score = float(status_match.group(1))
            threshold = float(status_match.group(2))

        # Parse tests list if present
        tests_match = re.search(r"tests=([^\n\r]*)", output, re.IGNORECASE)
        if tests_match:
            test_names = [t.strip() for t in tests_match.group(1).split(",") if t.strip()]
            rules = [{"name": name, "score": 0.0, "description": ""} for name in test_names]

        return {
            "score": score,
            "threshold": threshold,
            "rules": rules,
            "version": "SpamAssassin CLI service",
        }

    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="SpamAssassin timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
