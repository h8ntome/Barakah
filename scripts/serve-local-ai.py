#!/usr/bin/env python3
"""Private loopback-only, single-generation full-checkpoint server; see docs/local-ai.md."""
import hashlib
import hmac
import json
import math
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MODEL = 'h8notme/barakah1'
REVISION = '912a5697cf9d85adf065ee512f509cfa236459d4'
SYSTEM_PROMPT = ('You are Barakah, an educational Islamic finance assistant. '
                 'Be concise and acknowledge uncertainty. Do not claim to be a scholar or financial adviser. '
                 'Do not invent account data, sources or religious rulings. '
                 'Do not recommend interest-bearing savings, CDs, conventional bonds or loans. '
                 'Do not certify any investment as halal; explain that product terms need qualified review. '
                 'Your responses are not authoritative; suggest qualified professional advice when appropriate.')


def validate_request(data):
    if not isinstance(data, dict) or set(data) != {'message', 'history'}:
        raise ValueError('Invalid request')
    if not isinstance(data['message'], str) or not data['message'].strip() or len(data['message']) > 1000:
        raise ValueError('Invalid message')
    history = data['history']
    if not isinstance(history, list) or len(history) > 12:
        raise ValueError('Invalid history')
    size = 0
    for item in history:
        if (not isinstance(item, dict) or set(item) != {'role', 'text'}
                or item['role'] not in ('user', 'assistant')
                or not isinstance(item['text'], str) or not item['text'].strip()):
            raise ValueError('Invalid history')
        size += len(item['text'])
    if size > 12000:
        raise ValueError('History too large')
    return data


class Model:
    def __init__(self, timeout):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        torch.set_num_threads(8)
        torch.manual_seed(2026)
        self.torch, self.timeout = torch, timeout
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        dtype = torch.bfloat16 if self.device == 'cuda' else torch.float32
        # Both weights and any custom code are pinned; never use a PEFT/base-model substitution.
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL, revision=REVISION,
                                                       code_revision=REVISION, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            MODEL, revision=REVISION, code_revision=REVISION, trust_remote_code=True,
            dtype=dtype, attn_implementation='sdpa').to(self.device).eval()
        self.template_hash = hashlib.sha256(self.tokenizer.get_chat_template().encode()).hexdigest()

    def generate(self, data):
        from transformers import StoppingCriteria, StoppingCriteriaList
        messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]
        messages += [{'role': item['role'], 'content': item['text']} for item in data['history']]
        messages.append({'role': 'user', 'content': data['message']})
        prompt = self.tokenizer.apply_chat_template(messages, tokenize=False,
                                                    add_generation_prompt=True, enable_thinking=False)
        inputs = self.tokenizer(prompt, return_tensors='pt', add_special_tokens=False).to(self.device)
        input_tokens = inputs.input_ids.shape[1]
        if input_tokens > 4096:
            raise ValueError('Token budget exceeded')
        started = time.monotonic()
        deadline = started + self.timeout

        class Deadline(StoppingCriteria):
            def __call__(self, input_ids, scores, **kwargs):
                return time.monotonic() >= deadline

        with self.torch.inference_mode():
            output = self.model.generate(
                **inputs, max_new_tokens=384, do_sample=False, num_beams=1, repetition_penalty=1.0, use_cache=True,
                pad_token_id=(self.tokenizer.pad_token_id if self.tokenizer.pad_token_id is not None
                              else self.tokenizer.eos_token_id),
                stopping_criteria=StoppingCriteriaList([Deadline()]))
        if self.device == 'cuda':
            self.torch.cuda.synchronize()
        elapsed = time.monotonic() - started
        if elapsed >= self.timeout:
            raise TimeoutError('Generation deadline')
        tokens = output[0, input_tokens:]
        text = self.tokenizer.decode(tokens, skip_special_tokens=True)
        if not text.strip() or len(text) > 6000:
            raise ValueError('Output bounds')
        return {'text': text, 'metadata': {
            'model': MODEL, 'revision': REVISION,
            'prompt_sha256': hashlib.sha256(prompt.encode()).hexdigest(),
            'template_sha256': self.template_hash,
            'input_tokens': input_tokens, 'output_tokens': len(tokens),
            'generation_seconds': elapsed,
        }}


def handler_for(model, token):
    lock = threading.Lock()

    class Handler(BaseHTTPRequestHandler):
        # Never emit request paths, authorization headers, prompts or generated text.
        def log_message(self, *_):
            pass

        def setup(self):
            super().setup()
            self.connection.settimeout(5)

        def reply(self, status, body):
            encoded = json.dumps(body, ensure_ascii=False).encode()
            self.send_response(status)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(encoded)))
            self.send_header('Connection', 'close')
            self.end_headers()
            self.wfile.write(encoded)

        def do_POST(self):
            if not hmac.compare_digest(self.headers.get('Authorization', '').encode(),
                                       ('Bearer ' + token).encode()):
                self.reply(401, {'error': 'unauthorized'})
                return
            if self.path != '/generate':
                self.reply(404, {'error': 'not_found'})
                return
            if not lock.acquire(blocking=False):
                self.reply(503, {'error': 'busy'})
                return
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 < length <= 65536 or self.headers.get('Transfer-Encoding'):
                    raise ValueError('Request size')
                data = validate_request(json.loads(self.rfile.read(length)))
                self.reply(200, model.generate(data))
            except TimeoutError:
                self.reply(504, {'error': 'timeout'})
            except (ValueError, TypeError):
                self.reply(400, {'error': 'invalid_request_or_output'})
            except Exception:
                self.reply(503, {'error': 'generation_failed'})
            finally:
                lock.release()

    return Handler


class PrivateServer(ThreadingHTTPServer):
    daemon_threads = True
    # Suppress traceback details (including model exceptions) on disconnected clients.
    def handle_error(self, request, client_address):
        pass


def main():
    token = os.environ.get('AI_TOKEN', '')
    if len(token) < 32 or not token.isascii() or any(char.isspace() for char in token):
        raise SystemExit('Set AI_TOKEN to a random URL-safe secret of at least 32 characters')
    timeout = float(os.environ.get('AI_GENERATION_TIMEOUT', '75'))
    if not math.isfinite(timeout) or not 1 <= timeout <= 290:
        raise SystemExit('AI_GENERATION_TIMEOUT must be 1..290 seconds')
    model = Model(timeout)
    # Do not listen until warmup succeeds. Timeout is cooperative between generation steps.
    model.generate({'message': 'Briefly introduce yourself.', 'history': []})
    port = int(os.environ.get('AI_PORT', '8765'))
    server = PrivateServer(('127.0.0.1', port), handler_for(model, token))
    print(f'Local AI ready on loopback port {port}; model={MODEL} revision={REVISION}', flush=True)
    server.serve_forever()


if __name__ == '__main__':
    main()
