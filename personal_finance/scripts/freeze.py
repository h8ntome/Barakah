"""One-way release freeze; refuses to replace an existing manifest."""
import json
from benchmark_lib import ROOT, digest, now, save

def main():
    target=ROOT/'freeze_manifest.json'
    if target.exists(): raise FileExistsError('Release already frozen')
    files=[]
    for name in ['questions.json','rubric.json','numeric_rules.json','inference_config.json','PROVENANCE.md']:
        files.append(ROOT/name)
    for folder in ['scripts','tests','evidence']:
        files.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pid')
    files.extend(ROOT.parent/'benchmark/results/hardware'/name for name in ['original_checkpoint.json','barakah1_checkpoint.json'])
    files.extend(ROOT.parent/'benchmark/scripts'/name for name in ['checkpoint.py','common.py','check_hardware.py'])
    import os
    manifest=dict(title='Personal Finance Domain Adaptation Benchmark v1.0',frozen_at=now(),
                  author='Implementation AI assistant; not independent human reviewer',
                  evaluation_model_outputs_inspected_before_freeze=False,
                  expected_questions=50,expected_numeric=23,
                  files={os.path.relpath(p,ROOT):digest(p) for p in sorted(files)})
    save(target,manifest)
    (ROOT/'freeze_manifest.sha256').write_text(digest(target)+'  freeze_manifest.json\n')
    print(json.dumps(dict(frozen_at=manifest['frozen_at'],manifest_sha256=digest(target),
        questions_sha256=digest(ROOT/'questions.json'),rubric_sha256=digest(ROOT/'rubric.json'),
        numeric_rules_sha256=digest(ROOT/'numeric_rules.json'),inference_config_sha256=digest(ROOT/'inference_config.json')),indent=2))

if __name__=='__main__': main()
