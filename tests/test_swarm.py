import asyncio
import json
import unittest
from instruct_swarm import Swarm, Config

class Fake:
    def __init__(self, malformed=False, fail=False):
        self.active = self.peak = 0
        self.malformed, self.fail = malformed, fail
    async def complete(self, messages, temperature, max_tokens):
        self.active += 1
        self.peak = max(self.peak, self.active)
        try:
            await asyncio.sleep(.002)
            p = messages[0]['content']
            if self.fail:
                raise ConnectionError('test')
            if p.startswith('Evaluate'):
                if self.malformed:
                    return 'not json'
                data = json.loads(p[p.index('{"task"'):])
                return json.dumps([dict(id=x['id'], score=.8, critique='Check assumptions')
                                   for x in data['material']])
            return 'Synthetic fixture answer; not a real model output.'
        finally:
            self.active -= 1

class Tests(unittest.IsolatedAsyncioTestCase):
    async def test_rounds_budget_and_concurrency(self):
        backend = Fake()
        r = await Swarm(backend, Config(concurrency=2)).run('test')
        self.assertEqual(r.calls, 17)
        self.assertEqual(len(r.candidates), 4)
        self.assertEqual(len(r.reviews), 12)
        self.assertTrue(all(x['id'] != x['reviewer'] for x in r.reviews))
        self.assertEqual(backend.peak, 2)
    async def test_malformed_reviews(self):
        r = await Swarm(Fake(malformed=True)).run('test')
        self.assertEqual(r.reviews, [])
        self.assertTrue(r.warnings)
        self.assertTrue(all(x['peer_score'] is None for x in r.candidates))
    async def test_total_failure(self):
        with self.assertRaises(RuntimeError):
            await Swarm(Fake(fail=True)).run('test')
    async def test_bad_budget(self):
        with self.assertRaises(ValueError):
            Config(max_calls=3)
    async def test_zero_rounds(self):
        r = await Swarm(Fake(), Config(rounds=0)).run('test')
        self.assertEqual(r.calls, 9)
    async def test_partial_and_synthesis_failure(self):
        class Partial(Fake):
            async def complete(self, messages, temperature, max_tokens):
                p = messages[0]['content']
                if p.startswith('Solve directly') or p.startswith('Produce the best'):
                    raise TimeoutError()
                return await super().complete(messages, temperature, max_tokens)
        r = await Swarm(Partial()).run('test')
        self.assertEqual(len(r.candidates), 3)
        self.assertEqual(r.answer, r.candidates[0]['text'])
        self.assertTrue(any('Synthesis failed' in w for w in r.warnings))
    async def test_empty_task(self):
        with self.assertRaises(ValueError):
            await Swarm(Fake()).run(' ')

if __name__ == '__main__':
    unittest.main()
