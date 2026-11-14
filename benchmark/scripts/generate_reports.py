"""Render narrative tables and measured findings from saved processed result files."""
import argparse
import json
from common import ROOT, load_jsonl
from compare_models import processed, compare

def pct(metric):
    if not metric['denominator']:return 'Unavailable (0 independently reviewed)'
    return f"{metric['numerator']}/{metric['denominator']} ({metric['rate']*100:.2f}%)"

def num(value,places=3):
    return f'{value:.{places}f}' if value is not None else 'Unavailable'

def gib(value):return num(value/1024**3,2)+' GiB' if value is not None else 'Unavailable'

def generate(original,rules):
    s=original['summary'];meta=original['metadata'];p=s['performance'];n=s['automatic_numeric_correctness']
    raw=load_jsonl(ROOT/'results/raw'/(original['run_id']+'.jsonl'));lookup={r['question_id']:r for r in raw}
    comparison=compare(original,rules);paired=comparison['paired_numeric_n']
    base=comparison['numeric_correctness'];local=json.loads((ROOT/'results/hardware/local.json').read_text())
    server=json.loads((ROOT/'results/hardware/server2.json').read_text())
    smoke=json.loads((ROOT/'results/hardware/smoke.json').read_text())
    manifest=json.loads((ROOT/'datasets/dataset_manifest.json').read_text())
    ci=n['wilson_95_interval'];ci_text=f'{100*ci[0]:.2f}%–{100*ci[1]:.2f}%' if ci else 'Unavailable'
    table=lambda field:'\n'.join(f"| {k.title()} | {v['sample_size']} | {pct(v['automatic_numeric_correctness']) if v['automatic_numeric_correctness']['denominator'] else 'Not a numeric task'} | {v['pending_correctness_review']} |" for k,v in s['by_'+field].items())
    examples=[]
    for status,heading in [('correct','Successful numeric example'),('incorrect','Incorrect numeric example'),('unparseable','Formatting / parse failure example')]:
        choices=[q for q in original['scores'] if q.get('status')==status]
        if not choices:
            examples.append(f'### {heading}\n\nNo observed examples of this status in the saved run.\n');continue
        q=choices[0];r=lookup[q['question_id']]
        examples.append(f"### {heading}: {q['question_id']}\n\n**Question:** {r['question']}\n\n**Actual model output:**\n\n```text\n{r['response']}\n```\n\nAutomatic numeric status: **{status}**. Surrounding prose is not expert-certified.\n")
    truncated=[r for r in raw if r.get('truncated')]
    if truncated:
        r=truncated[0]
        examples.append(f"### Observed output-limit failure: {r['question_id']}\n\nThis response reached the configured cap. Its conceptual truth remains unadjudicated; truncation is a measured completion-limit event, not a verified hallucination.\n\n**Question:** {r['question']}\n\n```text\n{r['response']}\n```\n")
    count=s['automatic_status_counts']
    report=f'''# Barakah original LFM3 benchmark report

## 1. Executive summary

The original instruction-tuned **LiquidAI/LFM3-1.7B** was actually loaded and run against **{s['sample_size']}/{s['dataset_size']}** frozen held-out questions on **server2**. The run achieved **{pct(n)}** on automatically verified final numeric quantities. **{s['pending_correctness_review']} conceptual answers remain pending expert correctness review**. This is not an overall Islamic-finance correctness percentage.

On the identical {paired} explicit-eligibility zakat calculations, LFM3 scored **{base['baseline']*paired:.0f}/{paired} ({100*base['baseline']:.2f}%)** and the deterministic formula baseline scored **{base['candidate']*paired:.0f}/{paired} ({100*base['candidate']:.2f}%)**. The narrow calculator is not a religious eligibility engine. No fine-tuned model exists in these results.

Median generation latency was **{num(p['median_latency_seconds'])} seconds**; aggregate output throughput was **{num(p['aggregate_output_tokens_per_second'])} tokens/second**. These are measured server2 batch-one timings, not estimated Mac speedups.

## 2. Model description

Creator: **Liquid AI**. Evaluated repository: `LiquidAI/LFM3-1.7B`, instruction-tuned, **not `-Base`**. Exact revision: `{meta.get('checkpoint_revision')}`. Official BF16 safetensors; no quantization. The existing cache was verified by required-file checks, safetensors opening and file SHA256s. Model/tokenizer loading and actual GPU smoke generation succeeded before full evaluation. See [MODEL_CARD.md](MODEL_CARD.md) and the official LFM Open License v1.0 before deployment.

## 3. Dataset description

Dataset version {manifest['version']}; JSON SHA256 `{manifest['sha256']}`. Zakat 25, investing 25, principles 20, budgeting 20 and safety 10. Difficulty totals: {', '.join(k+' '+str(v) for k,v in manifest['difficulty_counts'].items())}. Forty numeric tasks are code-verified; sixty institutional conceptual references are checked but not independently expert-approved. No human expert has adjudicated conceptual model correctness in this release. Read [DATASET_CARD.md](../datasets/DATASET_CARD.md) and [SOURCE_EVIDENCE.md](../datasets/SOURCE_EVIDENCE.md).

## 4. Evaluation methodology

Greedy deterministic decoding, seed 2026, batch one, thinking disabled through the official chat template, 384-token output cap, SDPA attention and a neutral accuracy/uncertainty system instruction. Full prompt/template/configuration hashes and generation settings are preserved in run metadata. One short warm-up is excluded from answer latencies. The vendor's sampled generation recommendations are not the protocol used here.

Numerical grading checks an explicit terminal answer and unit using Decimal and 0.01 absolute tolerance. Correct final values are independently checkable; all other claims remain outside automatic certification. Errors and unparseable numeric answers remain in the numeric denominator. Factual/religious answer grading requires a transparent evidence-based human rubric; there is no invented keyword-accuracy or LLM-judge score. See [METHODOLOGY.md](METHODOLOGY.md).

## 5. Execution environment

- Host: {meta.get('execution_host')} / {meta['hardware']['hostname']}.
- CPU: AMD Ryzen AI MAX+ 395; {meta['hardware']['logical_cores']} logical cores.
- GPU: {meta['hardware']['gpu'].get('name')}; PyTorch device `{meta.get('device')}` is ROCm, not NVIDIA CUDA.
- System RAM: {gib(meta['hardware']['ram_total_bytes'])}; available at in-run inspection: {gib(meta['hardware']['ram_available_bytes'])}.
- Reported accelerator memory: {gib(meta['hardware']['gpu'].get('total_bytes'))}; shared-memory system, not additional independent RAM.
- Precision: {meta.get('precision')}; backend: {meta.get('backend')}.
- Python: `{meta['versions']['python']}`.
- PyTorch: `{meta['versions']['torch']}`; Transformers: `{meta['versions']['transformers']}`; Hugging Face Hub: `{meta['versions']['huggingface_hub']}`.
- Run ID: `{original['run_id']}`.
- Start: {meta.get('started_at')}; completion: {meta.get('completed_at')}.
- Total measured run segment time: {num(meta.get('total_execution_seconds'))} seconds (includes setup; excludes downtime between resumes).

The Mac was inspected but not inference-benchmarked. Other server workloads were observed and not stopped. See [HARDWARE_COMPARISON.md](HARDWARE_COMPARISON.md).

## 6. Overall results

| Channel | Measurement | Interpretation |
|---|---|---|
| Verified final numeric correctness | {pct(n)} | Numeric tasks only; not full-response correctness |
| Numeric Wilson 95% interval | {ci_text} | Descriptive, authored nonrandom sample |
| Human-reviewed correctness | {pct(s['human_reviewed_correctness'])} | Not yet independently adjudicated |
| Conceptual correctness pending | {s['pending_correctness_review']}/{s['sample_size']} responses | Not included as verified successes/failures |
| Missing responses | {s['missing_responses']}/{s['dataset_size']} | Unattempted rows disclosed separately |
| Generation failures | {pct(s['generation_failure_rate'])} | All attempted responses |

Numeric statuses: correct {count['correct']}, incorrect {count['incorrect']}, unparseable {count['unparseable']}, numeric generation errors {s['automatic_generation_errors']}. No difficult questions were dropped after generation.

![Matched-task correctness](../visuals/png/01_overall_performance.png)

## 7. Results by category

| Category | Attempted responses | Verified final numeric correctness | Conceptual pending |
|---|---:|---|---:|
{table('category')}

Investing and safety do not have automatically verified numeric tasks. “Not a numeric task” means missing applicable evidence, not 0% domain competence.

![Categories](../visuals/png/02_category_performance.png)

## 8. Results by difficulty

| Difficulty | Attempted responses | Verified final numeric correctness | Conceptual pending |
|---|---:|---|---:|
{table('difficulty')}

Difficulty is author-assigned and task mixes differ. Do not infer a calibrated ability curve.

![Difficulty](../visuals/png/03_difficulty_performance.png)

## 9. Latency and resource usage

Successful generation denominator: {p['successful_n']}. Mean **{num(p['mean_latency_seconds'])} s**, median **{num(p['median_latency_seconds'])} s**, nearest-rank P95 **{num(p['p95_latency_seconds'])} s**. Total generated output tokens **{p['output_tokens']}**; aggregate output throughput **{num(p['aggregate_output_tokens_per_second'])} tokens/s**.

Timing includes prompt prefill, decode and synchronized completion, but excludes tokenization, model loading and application networking. Output length varies; this is not a controlled fixed-token device comparison. Baseline arithmetic times are measured on a different host and are not a model speed improvement.

- Peak PyTorch GPU allocated memory after warm-up: {gib(meta.get('peak_gpu_allocated_bytes'))}.
- Peak PyTorch GPU reserved memory: {gib(meta.get('peak_gpu_reserved_bytes'))}.
- Peak sampled process RSS: {gib(meta.get('peak_process_rss_bytes'))}.
- Responses reaching the output cap: **{s['truncated_responses']}/{s['sample_size']}**; these are conservatively marked truncated rather than hidden.
- Warm-up measured generation: {num(meta.get('warmup',{}).get('latency_seconds'))} s, {meta.get('warmup',{}).get('output_tokens')} output tokens; recorded separately.

GPU counters are process allocator measures, not full shared-memory pressure or other users' memory. RSS is sampled after responses. Complete versions, workload snapshots and smoke output are under `results/hardware/`.

![Latency](../visuals/png/04_latency_distribution.png)
![Observed automatic outcomes](../visuals/png/05_error_distribution.png)

## 10. Safety analysis

Candidate heuristic flags occur in **{pct(s['candidate_flagged_responses'])}**. They require contextual review: “do not trust guaranteed returns” may correctly trigger a guarantee-language pattern. They are **not confirmed safety violations**. Verified safety failure rate: **{pct(s['verified_safety_failure_rate'])}**. Pending safety review: {s['safety_review_pending']}/{s['sample_size']}.

## 11. Hallucination analysis

Verified hallucination rate: **{pct(s['verified_hallucination_rate'])}**. Pending hallucination review: {s['hallucination_review_pending']}/{s['sample_size']}. Citation-pattern flags are only leads for source checking; neither a URL nor absence of a flag establishes truth. No model-generated judgment is described as independently verified religious correctness. All raw answers are available for independent review.

![Safety review coverage](../visuals/png/06_safety_hallucination.png)

## 12. Successful examples / 13. Failure examples

{''.join(examples)}
## 14. Baseline comparison

The baseline parses the eligible amount from public question text and multiplies by 0.025 using Decimal. It never reads reference answer values. It has no conversational, jurisprudential or stock-screening capability. On the matched zakat subset: LFM3 {base['baseline']*paired:.0f}/{paired}; rules {base['candidate']*paired:.0f}/{paired}. Rules minus original change: **{base['percentage_points']:.2f} percentage points**; relative change {num(base['relative_change']*100 if base['relative_change'] is not None else None,2)}%. No incompatible overall accuracy scores are combined. Comparison JSON preserves question-level disagreements and hardware differences.

## 15. Limitations

Read [LIMITATIONS.md](LIMITATIONS.md). The most important constraints are an authored small English sample, repeated arithmetic templates, no independent religious response review, heuristic-only safety triage, a single greedy run, finite output cap, a non-isolated shared-memory accelerator and unknown source overlap with original pretraining. Numeric accuracy cannot establish trustworthy religious advice or deployment readiness.

## 16. Practical implications for Barakah

Keep money calculations in deterministic, tested tools and expose eligibility assumptions separately. Use the assistant for explanations only within carefully bounded workflows, source-backed retrieval and explicit uncertainty. Never label a stock halal from its name or marketing alone. Human escalation is necessary for differing interpretations and personalized financial decisions. The existing frontend remains a mock prototype; this benchmark does not integrate inference into it.

## 17. Fine-tuning evaluation plan

No adapted model has been supplied or evaluated. Train only on a separate corpus, exclude this held-out dataset and its references/answers from adaptation and retrieval, document overlap checks, freeze all inference settings and rerun the same questions. Compare paired numeric outcomes, independently reviewed conceptual/safety channels, regressions and disagreements. Measure speed on the same host/runtime before making efficiency claims. The configurable runner and comparison command already accept future local or pinned Hugging Face candidates.

![Adapted evidence unavailable](../visuals/png/07_model_comparison.png)
![One measured inference host](../visuals/png/08_hardware_performance.png)

## 18. Conclusions

This release provides real raw model outputs, reproducible numeric scoring, a genuinely simpler matched-task baseline and explicit missing-evidence channels. It establishes an original-model starting point, **not proven Islamic-finance correctness or fine-tuning improvement**. The next scientific step is independent qualified review and stronger unseen tests, not rebranding pending judgments as accuracy.
'''
    (ROOT/'reports/BENCHMARK_REPORT.md').write_text(report)
    summary=f'''# Executive summary

**What we tested.** The official instruction-tuned Liquid AI LFM3-1.7B, unmodified BF16 weights, on {s['sample_size']} held-out Barakah questions across zakat, investing, Islamic-finance principles, budgeting and financial safety. The model actually ran on server2's AMD Radeon 8060S; no adapted model has been tested.

**What it achieved.** {pct(n)} correct final numeric answers on {n['denominator']} code-verifiable tasks. This is numerical correctness, **not an overall Islamic-finance accuracy score**. {s['pending_correctness_review']} conceptual answers still need qualified review. Generation errors: {pct(s['generation_failure_rate'])}.

**Where it failed or remains uncertain.** {count['incorrect']} incorrect numerical answers, {count['unparseable']} unparseable final answers and {s['truncated_responses']}/{s['sample_size']} responses reaching the output cap. Safety and hallucination rates are unavailable until independent review; heuristic flags are not proof of violations. The complete answers, including failures, are published for inspection.

**Simple baseline.** On the same {paired} explicit-eligibility zakat questions, LFM3 achieved {base['baseline']*paired:.0f}/{paired}; a formula calculator achieved {base['candidate']*paired:.0f}/{paired}. The calculator cannot decide religious eligibility. Its lesson for Barakah is straightforward: deterministic code should do the money arithmetic.

**Practical performance.** Median {num(p['median_latency_seconds'])} seconds per response; {num(p['aggregate_output_tokens_per_second'])} output tokens/second across successful generation. These are server2 timings, not a measured speedup over the inspected Mac.

**Next step.** Have qualified reviewers adjudicate conceptual correctness and every response's safety and source claims. Keep this dataset out of training. Evaluate any future adapted checkpoint on the frozen holdout before claiming gains. The mocked frontend was not modified or connected to this model.

[Offline dashboard](../visuals/html/index.html) · [Full report](BENCHMARK_REPORT.md) · [Reproduction commands](../README.md)
'''
    (ROOT/'reports/EXECUTIVE_SUMMARY.md').write_text(summary)
    hw=f'''# Hardware inspection and execution decision

## Local Mac (actually inspected)
- OS: {local['os']}; hostname {local['hostname']}.
- CPU: {local['cpu']}; logical/physical cores {local['logical_cores']}/{local['physical_cores']}.
- RAM total / available: {gib(local['ram_total_bytes'])} / {gib(local['ram_available_bytes'])}.
- Free disk at probe: {gib(local['disk_free_bytes'])}.
- CPU utilization during sample: {local['cpu_utilization_percent']}%; load averages {local['load_average']}.
- Python: `{local['versions']['python']}`. GPU runtime probe: `{local['gpu']}`.
- Apple M4 integrated GPU/unified memory is part of the Mac hardware, but no functioning local PyTorch inference configuration was claimed by the initial probe.

## Server2 (actually inspected and used)
- OS: {server['os']}; hostname {server['hostname']}.
- CPU: AMD Ryzen AI MAX+ 395; logical/physical cores {server['logical_cores']}/{server['physical_cores']}.
- RAM total / available: {gib(server['ram_total_bytes'])} / {gib(server['ram_available_bytes'])}.
- GPU: {server['gpu'].get('name')}; total/free reported accelerator memory {gib(server['gpu'].get('total_bytes'))} / {gib(server['gpu'].get('free_bytes'))}.
- ROCm/HIP: {server['gpu'].get('hip')}; NVIDIA CUDA: {server['gpu'].get('cuda')}. ROCm is exposed through torch.cuda.
- Free disk: {gib(server['disk_free_bytes'])}; CPU utilization {server['cpu_utilization_percent']}%; load averages {server['load_average']}.
- PyTorch `{server['versions']['torch']}`; Transformers `{server['versions']['transformers']}`.
- Exact official checkpoint already cached. No second model copy or quantization was needed.

## Decision before download/inference

**Selected server2.** It had substantially more free RAM/disk and the exact existing BF16 checkpoint, plus a verified compatible AMD GPU runtime. The Mac's roughly four GiB free disk offered little margin for a roughly 3.3 GiB checkpoint and Python/runtime overhead. Server2 avoided both a redundant model download and a local backend setup. These are measured resource/compatibility advantages, **not a claimed measured inference speedup**.

Network model-download speeds were not compared: the exact snapshot was already present and hash-verified. SSH and script/result transfer succeeded; small result transfer is far cheaper than another checkpoint transfer. No bandwidth benchmark or invented throughput estimate is included.

## Actual compatibility and performance evidence

Cold first smoke: model load {num(smoke['load_seconds'])} seconds; {smoke['output_tokens']} generated tokens in {num(smoke['latency_seconds'])} seconds ({num(smoke['tokens_per_second'])} tokens/second), including possible compilation. It answered the arithmetic prompt. This short cold test is **not** a steady-state hardware benchmark.

Full original-model run: {s['sample_size']} attempted responses, mean {num(p['mean_latency_seconds'])} s, median {num(p['median_latency_seconds'])} s, P95 {num(p['p95_latency_seconds'])} s, aggregate {num(p['aggregate_output_tokens_per_second'])} output tokens/s. Peak PyTorch allocated/reserved GPU memory: {gib(meta.get('peak_gpu_allocated_bytes'))} / {gib(meta.get('peak_gpu_reserved_bytes'))}. Peak sampled RSS: {gib(meta.get('peak_process_rss_bytes'))}.

## Workload safety and comparison limits

Other memory/CPU workloads were observed in process snapshots, including existing Python/ComfyUI activity. None was stopped, reconfigured or overwritten. No root/system package, SSH, firewall or inference-routing configuration was changed. The existing compatible Python environment was used read-only in a new user-owned benchmark work directory.

The logged rocSHMEM libnuma warning and unreadable unrelated Hugging Face tree-cache warning did not prevent verified model loading/inference. No shared cache permissions were changed to suppress them. Logs preserve them.

Only server2 was inference-tested. Local Mac vs server2 inference throughput is **unavailable**; there is no direct two-host chart or speedup ratio. The simple formula baseline ran locally, but this is a different workload and cannot establish an LLM hardware speed comparison. The GPU uses shared system memory; do not add its reported memory to host RAM as separate capacity.

Snapshots: `../results/hardware/local.json`, `server2.json`, run metadata, `smoke.json`, `model_download.json`; sysfs GPU counters and active workloads are recorded where accessible. Resource values vary over time. The Mac workspace experienced iCloud dataless-file errors; selected files were explicitly materialized and the local analysis interpreter was outside the synced directory. No unrelated files were deleted to create space.

![Measured host only](../visuals/png/08_hardware_performance.png)
'''
    (ROOT/'reports/HARDWARE_COMPARISON.md').write_text(hw)
    print('Generated measured benchmark report, executive summary and hardware comparison')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run',default='original');p.add_argument('--baseline',default='rules');a=p.parse_args();generate(processed(a.run),processed(a.baseline))
