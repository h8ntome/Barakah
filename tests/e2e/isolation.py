"""Two-account ownership probes from real Chromium against the real API."""
import json
import secrets
from urllib.parse import urlparse
import journey as j


def main():
    assert urlparse(j.URL).hostname in {'127.0.0.1', 'localhost', '::1'}
    j.browser('open', j.URL)
    seed = secrets.token_hex(8)
    # credentials:omit keeps these synthetic API sessions separate from browser cookies.
    result = j.browser('eval', f'''(async () => {{
      const seed = {json.dumps(seed)}, password = {json.dumps(secrets.token_urlsafe(24))};
      async function api(path, method = 'GET', body, token) {{
        const response = await fetch('/api/v1' + path, {{method, credentials:'omit', headers:{{'Content-Type':'application/json', ...(token ? {{Authorization:'Bearer ' + token}} : {{}})}}, ...(body ? {{body:JSON.stringify(body)}} : {{}})}});
        return {{status:response.status, data:response.status === 204 ? null : await response.json()}};
      }}
      const a = await api('/auth/register','POST',{{email:'isolation-a-' + seed + '@example.com',password,display_name:'Owner A'}});
      const b = await api('/auth/register','POST',{{email:'isolation-b-' + seed + '@example.com',password,display_name:'Owner B'}});
      if (a.status !== 201 || b.status !== 201) throw new Error('Registration failed');
      const ta=a.data.access_token, tb=b.data.access_token;
      const day=new Date().toISOString().slice(0,10);
      const account=(await api('/accounts','POST',{{name:'A private cash',currency:'USD',opening_balance:'1000.00'}},ta)).data;
      const txBody={{account_id:account.id,kind:'income',amount:'500.00',category:'Salary',occurred_on:day}};
      const tx=(await api('/transactions','POST',txBody,ta)).data;
      const budgetBody={{category:'Food',currency:'USD',amount:'400.00',month:day.slice(0,7)}};
      const budget=(await api('/budgets','POST',budgetBody,ta)).data;
      const givingBody={{amount:'50.00',currency:'USD',paid_on:day,recipient:'A private recipient'}};
      const giving=(await api('/sadaqah','POST',givingBody,ta)).data;
      const goalBody={{name:'A private goal',currency:'USD',target_amount:'5000.00'}};
      const goal=(await api('/goals','POST',goalBody,ta)).data;
      const holding=(await api('/portfolio/holdings','POST',{{symbol:'PRIVATE',name:'Private holding',currency:'USD'}},ta)).data;
      const probes=[];
      for (const [path, body] of [
        ['/accounts/'+account.id,{{name:'Intruder'}}], ['/transactions/'+tx.id,txBody],
        ['/budgets/'+budget.id,budgetBody], ['/sadaqah/'+giving.id,givingBody],
        ['/goals/'+goal.id,goalBody], ['/portfolio/holdings/'+holding.id,{{symbol:'PRIVATE',name:'Intruder'}}]
      ]) {{
        for (const method of ['PATCH','DELETE']) {{
          const r=await api(path,method,method==='PATCH'?body:undefined,tb);
          if(r.status!==404) throw new Error(method+' ownership failure '+path+' '+r.status);
          probes.push(method+' '+path.split('/')[1]+' denied');
        }}
      }}
      const invalid=await api('/transactions','POST',txBody,tb);
      if(invalid.status!==404) throw new Error('Foreign account reference accepted');
      probes.push('foreign account reference denied');
      for (const path of ['/accounts','/transactions','/budgets','/sadaqah','/goals']) {{
        const r=await api(path,'GET',undefined,tb);
        if(r.status!==200 || r.data.length) throw new Error('Read isolation failure '+path);
        probes.push(path+' listing isolated');
      }}
      const unauth=await api('/dashboard'); if(unauth.status!==401) throw new Error('Unauthenticated dashboard exposed');
      probes.push('unauthenticated dashboard denied');
      const admin=await api('/admin/causes','POST',{{title:'Intruder',category:'test',description:'test',currency:'USD'}},tb);
      if(admin.status!==403) throw new Error('Admin escalation');
      probes.push('admin operation denied');
      const owner=await api('/accounts','GET',undefined,ta);
      if(owner.data[0].name!=='A private cash' || Number(owner.data[0].balance)!==1500) throw new Error('Owner records changed');
      probes.push('owner data unchanged after attacks');
      return {{passed:probes.length,failed:0,checks:probes}};
    }})()''')
    data = json.loads(result)
    assert data['passed'] == 21 and data['failed'] == 0, data
    assert not j.browser('errors').strip()
    print(json.dumps(data, indent=2))


if __name__ == '__main__':
    try:
        main()
    finally:
        j.browser('close')
