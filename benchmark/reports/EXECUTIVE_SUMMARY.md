# Executive summary

**What we tested.** The official instruction-tuned Liquid AI LFM3-1.7B, unmodified BF16 weights, on 100 held-out Barakah questions across zakat, investing, Islamic-finance principles, budgeting and financial safety. The model actually ran on server2's AMD Radeon 8060S; no adapted model has been tested.

**What it achieved.** 36/40 (90.00%) correct final numeric answers on 40 code-verifiable tasks. This is numerical correctness, **not an overall Islamic-finance accuracy score**. 60 conceptual answers still need qualified review. Generation errors: 0/100 (0.00%).

**Where it failed or remains uncertain.** 4 incorrect numerical answers, 0 unparseable final answers and 2/100 responses reaching the output cap. Safety and hallucination rates are unavailable until independent review; heuristic flags are not proof of violations. The complete answers, including failures, are published for inspection.

**Simple baseline.** On the same 15 explicit-eligibility zakat questions, LFM3 achieved 12/15; a formula calculator achieved 15/15. The calculator cannot decide religious eligibility. Its lesson for Barakah is straightforward: deterministic code should do the money arithmetic.

**Practical performance.** Median 13.426 seconds per response; 15.268 output tokens/second across successful generation. These are server2 timings, not a measured speedup over the inspected Mac.

**Next step.** Have qualified reviewers adjudicate conceptual correctness and every response's safety and source claims. Keep this dataset out of training. Evaluate any future adapted checkpoint on the frozen holdout before claiming gains. The mocked frontend was not modified or connected to this model.

[Offline dashboard](../visuals/html/index.html) · [Full report](BENCHMARK_REPORT.md) · [Reproduction commands](../README.md)
