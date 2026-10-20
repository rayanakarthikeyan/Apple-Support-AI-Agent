# Source-grounded product research

This optional entry point adds dense semantic retrieval, persisted vectors,
cited excerpts, optional Gemini drafting and an explicit review/export gate.
The legacy BM25/rule-based Apple Support demo remains separately runnable.

## Run locally

```sh
python -m pip install -r requirements-evidence.txt
# Set EVIDENCE_TOKEN to a newly generated secret of at least 32 characters.
# PowerShell example (kept in the current process; never commit its value):
$env:EVIDENCE_TOKEN = [guid]::NewGuid().ToString('N')
python -m uvicorn src.evidence.api:create_app --factory --host 127.0.0.1 --port 8767 --workers 1
```

Open `http://127.0.0.1:8767` and enter the token. The token is not stored by the
page. Upload fictional product PDFs/TXT/Markdown, ask a question, inspect page
citations, record a review note, approve the snapshot and download the brief.
The first use downloads the public BAAI/bge-small-en-v1.5 model (MIT, via
FastEmbed); later inference is local. Keep its cache between restarts.

## Architecture and limits

`ingest -> chunk -> embed -> SQLite -> retrieve -> draft -> validate quotes -> review -> export`

- 180-word page windows with 40-word overlap preserve document/page/chunk IDs.
- FastEmbed produces normalized pretrained dense vectors. SQLite persists them;
  cosine search scans the small index exactly. It is not an ANN vector database.
- 2,000 chunks per collection, 10,000 globally; 500 chunks per ingest batch.
- Bearer authentication, a shared 60-request/minute budget, two processing slots,
  bounded uploads, 30-second model HTTP timeout and logs without document text.
- A private, single-reviewer demo: one token grants the whole workspace. It does
  not offer tenant isolation, user roles, horizontal scaling or durability without
  persistent storage. Use one worker. Do not upload personal records to a demo.
- Native text PDFs only in this endpoint; image-only pages are rejected rather
  than silently omitted. OCR is not part of this evidence endpoint; provide extracted text for scans.
- Exact quote validation establishes source correspondence, not truth, relevance,
  absence of contradictions or permission to publish a claim. Human review remains
  mandatory. Retrieval similarity alone is imperfect evidence of answerability.
- Runs contain immutable evidence snapshots. Re-indexing a document does not
  rewrite prior evidence. Approval requires its SHA-256 snapshot; failed, pending
  and abstained runs cannot be exported as approved briefs.

## Optional Gemini

Set `GEMINI_API_KEY` and optionally `GEMINI_MODEL` in the server environment.
Select Gemini and authorize sending the question/retrieved excerpts to Google.
Structured JSON contains only verbatim source quotes plus a separately labelled
campaign hypothesis. Invalid quotes, unknown sources, malformed responses and
provider failures fail the run. The request reservation is saved first; interrupted
requests are never automatically resent. A new user-triggered run is a new request
and may incur a charge. Token usage is provider-reported; no currency estimate is
inferred from it. Document content cannot invoke tools or execute code.

## Evaluation

```sh
python -m pytest tests/test_evidence_api.py -q
python eval/evidence_evaluation.py
```

The first command uses labelled test doubles for deterministic API/failure tests.
The second runs the real embedding model against nine fictional documents and
24 authored development queries, including missing evidence, conflicting pricing
and injection attempts. Read every result in `reports/evidence-evaluation.json`.
No hidden benchmark, independent human evaluation or general LLM-quality score
is claimed. Offline extractive evaluation makes zero generation API requests.

## Deployment prepared for review

`Dockerfile.evidence` runs as a non-root user. `render-evidence.yaml` configures a
private-token web service and persistent disk. It specifies a paid Starter plan;
review the provider's current charges before creating the service. No cloud service
is provisioned by checking in this blueprint. Set provider secrets in its dashboard,
use HTTPS, keep `/data` persistent, and review retention for your own documents.

On a development machine, a SQLite file is durable across application restarts,
but not across loss of that machine or an ephemeral hosting filesystem.
