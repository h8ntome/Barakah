"""Pre-dataset load/inference compatibility probe; not a scored benchmark."""
import time
from common import ROOT, config, save, now, versions

def main():
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    c=config();torch.manual_seed(c['seed']);torch.set_num_threads(c['cpu_threads'])
    device='cuda' if torch.cuda.is_available() else 'cpu'
    dtype=torch.bfloat16 if device=='cuda' else torch.float32
    start=time.perf_counter()
    tok=AutoTokenizer.from_pretrained(c['model'],revision=c['revision'],trust_remote_code=True)
    model=AutoModelForCausalLM.from_pretrained(c['model'],revision=c['revision'],code_revision=c['revision'],trust_remote_code=True,dtype=dtype,attn_implementation=c['attention']).to(device).eval()
    load_seconds=time.perf_counter()-start
    messages=[{'role':'system','content':c['system_prompt']},{'role':'user','content':'What is 2.5% of 10000? Answer briefly.'}]
    text=tok.apply_chat_template(messages,tokenize=False,add_generation_prompt=True,enable_thinking=False)
    inputs=tok(text,return_tensors='pt',add_special_tokens=False).to(device)
    if device=='cuda':torch.cuda.synchronize()
    start=time.perf_counter()
    with torch.inference_mode():out=model.generate(**inputs,max_new_tokens=48,do_sample=False,pad_token_id=tok.pad_token_id)
    if device=='cuda':torch.cuda.synchronize()
    latency=time.perf_counter()-start
    tokens=out[0,inputs.input_ids.shape[1]:]
    result={'timestamp':now(),'model':c['model'],'revision':c['revision'],'device':device,'dtype':str(dtype),'load_seconds':load_seconds,'latency_seconds':latency,'output_tokens':len(tokens),'tokens_per_second':len(tokens)/latency,'response':tok.decode(tokens,skip_special_tokens=True),'versions':versions(),'note':'Cold first generation including possible kernel compilation; not steady-state benchmark.'}
    save(ROOT/'results/hardware/smoke.json',result);print(result)

if __name__=='__main__':main()
