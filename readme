USAGE

Create `.env` at the root directory and populate:

```
GOOGLE_API_KEY=[Your API Key Here]
```

Install `uv` if you haven't already done so.

Install dependencies by running:

```
uv sync
```

Activate virual environment:

```
source .venv/bin/activate
```

Run:

```
python3 main.py
```

Run this `curl` command for a sample conversation:

```
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello!", "history": [], "config": {"model_name":"gemini-2.5-flash","max_tokens":150,"temperature":0.7}}'
```
