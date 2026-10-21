# Support Evidence API and Apple Support routing prototype

An independent Python portfolio project, not affiliated with Apple.

## New: source-grounded FastAPI service

The optional `src.evidence.api` entry point ingests native-text PDFs, TXT and
Markdown; chunks source pages; computes local pretrained dense embeddings; stores
normalized vectors in SQLite; retrieves cited excerpts; and requires review of
an exact evidence snapshot before export. Optional Gemini drafting returns
structured quotes and separately labelled campaign hypotheses.

Run instructions, deployment preparation and explicit limits are in
[docs/EVIDENCE_API.md](docs/EVIDENCE_API.md). The legacy standard-library server
remains separately runnable. No hosted service or new live Gemini run is claimed.

## Legacy routing prototype

The original `src/agent` pipeline uses rules, BM25 lexical retrieval and selection
of a stored reply. It invokes no generative model. Its six-intent classification,
escalation logic and offline evaluation remain available:

```sh
python eval/reproduce_headline.py
python -m unittest discover -s tests -p "test_pipeline.py"
python server.py
```

### Evaluation integrity

`data/generate_data.py` authors seed examples and templates expanded into 200
synthetic development items. Some items reuse retrieval seeds. They are not a
held-out Kaggle customer-conversation sample. `eval/judge.py` is a deterministic
heuristic rubric, not an LLM judge. ROUGE-L measures token overlap. There are no
independently collected human ratings or valid human/judge agreement results;
the previous simulated calibration routine has been removed.

Current legacy results are in `reports/evaluation_results.json`. They establish
behavior only on these synthetic development fixtures, not production safety.

The evidence service has separate tests and a real embedding evaluation in
`reports/evidence-evaluation.json`. Its metrics disclose missing-evidence failure
cases; exact quote validation is not semantic faithfulness, relevance or truth.
