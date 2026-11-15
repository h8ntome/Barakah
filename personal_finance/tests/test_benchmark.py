import collections
import json
import sys
import unittest
from decimal import Decimal as D
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from benchmark_lib import score_numeric, verify_freeze

class BenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=json.loads((ROOT/'questions.json').read_text())
        cls.by_id={q['id']:q for q in cls.rows}

    def test_authored_distribution_and_unique_questions(self):
        self.assertEqual(collections.Counter(q['category'] for q in self.rows),dict(budgeting=10,saving=8,debt=8,decisions=8,literacy=8,conversations=8))
        self.assertEqual(len(self.by_id),50)
        self.assertEqual(len({q['question'] for q in self.rows}),50)
        self.assertTrue(all(q['subjective_scores'] is None and q['human_reference'] for q in self.rows))

    def test_independent_decimal_references_from_scenario_facts(self):
        # Deliberately independent expressions, not the builder's operation dispatch or intermediate operands.
        expressions={
            'budgeting-01':D(3180)-D(1240)-D(185)-D(420)-D(165)-D(110)-D(210)-D(300),
            'budgeting-02':D(2460)-sum(map(D,[1050,190,360,145,500,180,65,100])),
            'budgeting-04':D(1340)*26,'budgeting-05':D(780)/6,
            'budgeting-06':D(1800)*D(2400)/(D(2400)+D(3600)),
            'budgeting-08':D(295)-72-138,'budgeting-10':D(4100)-3620-350-200,
            'saving-01':D(1850)*3-1100,'saving-02':(D(960)-160)/8,
            'saving-03':D(2500)*D('4.2')/100,'saving-05':D(275)*12+900,
            'saving-07':D(210)/2800*100,'debt-02':D(900)*(1+D('0.24')/12)-75,
            'debt-05':D(1450)-D(125)*11,'debt-07':D(2600)*3/100,
            'decisions-01':D(35)*12+90,'decisions-03':D(350)-120-175,
            'decisions-04':D(480)/4,'decisions-06':D(65)*10,
            'literacy-05':D(2100)-600,'literacy-08':D(750)*6/100,
            'conversations-03':D(3000)-850-400,'conversations-07':(D(1200)-300)/5}
        self.assertEqual(set(expressions),{q['id'] for q in self.rows if q['numeric']})
        for key,value in expressions.items():
            self.assertEqual(value,D(self.by_id[key]['numeric']['expected']),key)

    def test_strict_numeric_extraction_does_not_search_prose(self):
        q=self.by_id['budgeting-01']
        examples=[('You have 550.00 dollars.', 'unparseable'),
                  ('550.00 is one possibility.\nANSWER_AMOUNT: 99.00\nANSWER_UNIT: USD','incorrect'),
                  ('ANSWER_AMOUNT: 550.00\nANSWER_UNIT: USD','correct'),
                  ('ANSWER_AMOUNT: 550.01\nANSWER_UNIT: USD','correct'),
                  ('ANSWER_AMOUNT: 550.02\nANSWER_UNIT: USD','incorrect'),
                  ('ANSWER_AMOUNT: 550.00\nANSWER_UNIT: percent','incorrect'),
                  ('ANSWER_AMOUNT: 550.00\nANSWER_AMOUNT: 550.00\nANSWER_UNIT: USD','unparseable'),
                  ('ANSWER_AMOUNT: 550.00\nANSWER_UNIT: USD\nextra','unparseable'),
                  ('ANSWER_AMOUNT: $550.00\nANSWER_UNIT: USD','unparseable'),
                  ('ANSWER_AMOUNT: 550\nANSWER_UNIT: USD','unparseable'),
                  ('ANSWER_AMOUNT: 5.50e2\nANSWER_UNIT: USD','unparseable')]
        for text,status in examples:
            self.assertEqual(score_numeric(q,dict(response=text,error=None))['status'],status,text)
        self.assertEqual(score_numeric(q,dict(response='',error='failure'))['status'],'inference_error')
        self.assertIsNone(score_numeric(self.by_id['debt-01'],dict(response=''))['score'])

    def test_negative_and_percent(self):
        self.assertEqual(score_numeric(self.by_id['budgeting-02'],dict(response='ANSWER_AMOUNT: -130.00\nANSWER_UNIT: USD'))['score'],1)
        self.assertEqual(score_numeric(self.by_id['saving-07'],dict(response='ANSWER_AMOUNT: 7.50\nANSWER_UNIT: percent'))['score'],1)

    def test_rubric_and_subset(self):
        rubric=json.loads((ROOT/'rubric.json').read_text())
        self.assertEqual(len(rubric['dimensions']),5)
        for anchors in rubric['dimensions'].values(): self.assertEqual(set(anchors),set('01234'))
        subset=[q for q in self.rows if int(q['id'].rsplit('-',1)[1])<=2]
        self.assertEqual(len(subset),12)
        self.assertEqual(set(collections.Counter(q['category'] for q in subset).values()),{2})

    def test_release_integrity_when_frozen(self):
        if (ROOT/'freeze_manifest.json').exists(): verify_freeze()

if __name__=='__main__': unittest.main()
