"""Read-only lexical overlap screening, not proof of training-set independence."""
import argparse
import collections
import hashlib
import json
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def tokens(text):
    # Mask numbers so simple numeric substitutions cannot hide lexical reuse.
    return re.findall(r'[a-z]+|NUM', re.sub(r'\d[\d,.]*', 'NUM', text.lower()))

def shingles(words, n=3):
    return set(zip(*(words[i:] for i in range(n))))

def screen(corpus):
    questions = json.loads((ROOT/'questions.json').read_text())
    texts = [q['question'].split('\nGive practical advice')[0] for q in questions]
    normalized = [' '.join(tokens(t)) for t in texts]
    sets = [shingles(tokens(t)) for t in texts]
    inverted = collections.defaultdict(list)
    for i, ss in enumerate(sets):
        for s in ss:
            inverted[s].append(i)
    nearest = [[] for _ in questions]
    exact = []
    h = hashlib.sha256()
    rows = 0
    with corpus.open('rb') as f:
        for line_no, raw in enumerate(f, 1):
            h.update(raw)
            obj = json.loads(raw)
            rows += 1
            for field, text in obj.items():
                if not isinstance(text, str):
                    continue
                words = tokens(text)
                norm = ' '.join(words)
                for i, target in enumerate(normalized):
                    if target in norm:
                        exact.append(dict(question_id=questions[i]['id'], line=line_no, field=field))
                counts = collections.Counter()
                for s in shingles(words):
                    for i in inverted.get(s, ()):
                        counts[i] += 1
                for i, count in counts.items():
                    coverage = count/len(sets[i])
                    if len(nearest[i]) < 3 or coverage > nearest[i][-1]['coverage']:
                        item = dict(line=line_no, field=field, coverage=coverage,
                                    excerpt=text[:1800])
                        nearest[i] = sorted(nearest[i]+[item], key=lambda x: -x['coverage'])[:3]
    report = dict(corpus=str(corpus), corpus_sha256=h.hexdigest(), records=rows,
                  candidate_only=True, actual_finetune_rows_available=False,
                  method='number-masked word-trigram containment; exact masked full-scenario substring; top 3 fields per scenario',
                  flag_threshold=0.55, exact_masked_matches=exact,
                  limitations='Lexical screening misses nonlexical/semantic paraphrases. Shared topics are not contamination. No claim of complete independence or confirmed training lineage.',
                  nearest=[dict(question_id=q['id'], matches=m, flagged=bool(m and m[0]['coverage']>=0.55)) for q,m in zip(questions,nearest)])
    (ROOT/'evidence/overlap.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k != 'nearest'},indent=2))
    print('Flagged:',[r['question_id'] for r in report['nearest'] if r['flagged']])

if __name__ == '__main__':
    p=argparse.ArgumentParser(); p.add_argument('corpus',type=Path); screen(p.parse_args().corpus)
