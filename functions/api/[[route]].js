// Honda Islamabad — cloud API (Cloudflare Pages Function + Supabase Postgres)
// Multi-tenant: har row shop_id ke saath (hw_ tables).
// Env vars: SUPABASE_URL, SUPABASE_SERVICE_KEY, TOKEN_SECRET, ADMIN_PASSWORD
const enc = s => new TextEncoder().encode(s);
const b64url = buf => btoa(String.fromCharCode(...new Uint8Array(buf))).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');
const fromB64url = s => { s=s.replace(/-/g,'+').replace(/_/g,'/'); const b=atob(s); const a=new Uint8Array(b.length); for(let i=0;i<b.length;i++)a[i]=b.charCodeAt(i); return a; };

async function hmacKey(secret){ return crypto.subtle.importKey('raw', enc(secret), {name:'HMAC',hash:'SHA-256'}, false, ['sign','verify']); }
async function signToken(payload, secret){
  const data = b64url(enc(JSON.stringify(payload)));
  const key = await hmacKey(secret);
  const sig = await crypto.subtle.sign('HMAC', key, enc(data));
  return data + '.' + b64url(sig);
}
async function verifyToken(token, secret){
  if(!token) return null;
  const [data, sig] = token.split('.');
  if(!data || !sig) return null;
  try{
    const key = await hmacKey(secret);
    const ok = await crypto.subtle.verify('HMAC', key, fromB64url(sig), enc(data));
    if(!ok) return null;
    const p = JSON.parse(new TextDecoder().decode(fromB64url(data)));
    if(p.exp && Date.now() > p.exp) return null;
    return p;
  }catch(e){ return null; }
}

const CORS = { 'Access-Control-Allow-Origin':'*', 'Access-Control-Allow-Methods':'GET,POST,OPTIONS', 'Access-Control-Allow-Headers':'Content-Type,Authorization' };
const json = (obj, status=200) => new Response(JSON.stringify(obj), { status, headers: { 'Content-Type':'application/json', ...CORS } });

async function auth(request, secret){
  const h = request.headers.get('Authorization') || '';
  const token = h.startsWith('Bearer ') ? h.slice(7) : '';
  return await verifyToken(token, secret);
}

function makeSB(env){
  const base = (env.SUPABASE_URL || '').replace(/\/$/, '');
  const key  = env.SUPABASE_SERVICE_KEY || '';
  const H = { 'apikey': key, 'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json' };
  async function req(method, path, body, prefer){
    const headers = { ...H };
    if(prefer) headers['Prefer'] = prefer;
    const r = await fetch(base + '/rest/v1/' + path, { method, headers, body: body===undefined?undefined:JSON.stringify(body) });
    const text = await r.text();
    if(!r.ok) throw new Error('supabase ' + r.status + ': ' + text.slice(0,300));
    return text ? JSON.parse(text) : null;
  }
  return {
    get:    (path)        => req('GET', path),
    insert: (table, row)  => req('POST', table, row, 'return=representation'),
    update: (path, body)  => req('PATCH', path, body, 'return=minimal'),
    updateR:(path, body)  => req('PATCH', path, body, 'return=representation'),
    del:    (path)        => req('DELETE', path, undefined, 'return=minimal'),
    rpc:    (name, args)  => req('POST', 'rpc/' + name, args),
  };
}

const RABTA = 'NextGen AI Developers se rabta karein (0312-2546562)';

export async function onRequest(context){
  const { request, env } = context;
  const SECRET = env.TOKEN_SECRET || 'dev-secret';
  const sb = makeSB(env);
  if(request.method === 'OPTIONS') return new Response(null, { headers: CORS });
  const url = new URL(request.url);
  const path = url.pathname.replace(/^\/api\/?/, '');

  try{
    // ---------- Admin (NextGen HQ ke liye) ----------
    if(path.startsWith('admin/')){
      const sub = path.slice(6);
      if(sub === 'login' && request.method === 'POST'){
        const { password } = await request.json();
        const AP = env.ADMIN_PASSWORD || '';
        if(!AP) return json({ error:'ADMIN_PASSWORD abhi set nahi hai' }, 500);
        if(!password || password !== AP) return json({ error:'Ghalat password' }, 401);
        const token = await signToken({ role:'ngadmin', exp: Date.now()+1000*60*60*24*7 }, SECRET);
        return json({ token });
      }
      const adm = await auth(request, SECRET);
      if(!adm || adm.role !== 'ngadmin') return json({ error:'unauthorized' }, 401);

      if(sub === 'shops' && request.method === 'GET'){
        const shops = await sb.get('hw_shops?select=id,name,tagline,phone,address,status,trial_ends,created_at,hw_users(id,username,name,role)&order=id');
        return json({ shops: shops.map(s => ({ ...s, users: s.hw_users, hw_users: undefined })) });
      }
      if(sub === 'shop.create' && request.method === 'POST'){
        const p = await request.json();
        if(!p.name || !p.username || !p.password) return json({ error:'Dukan ka naam, username aur password zaroori hain' }, 400);
        const ex = await sb.get('hw_users?username=eq.' + encodeURIComponent(p.username) + '&select=id');
        if(ex && ex.length) return json({ error:'Ye username pehle se maujood hai' }, 400);
        let trial_ends = null;
        if(p.trial_days && Number(p.trial_days) > 0){
          const d = new Date(); d.setDate(d.getDate() + Number(p.trial_days));
          trial_ends = d.toISOString().slice(0,10);
        }
        const shop = first(await sb.insert('hw_shops', { name:p.name, tagline:p.tagline||'', phone:p.phone||'', address:p.address||'', status: trial_ends ? 'trial' : 'active', trial_ends }));
        await sb.insert('hw_users', { shop_id: shop.id, username:p.username, password:p.password, name:p.ownerName||'Owner', role:'owner' });
        /* SEED: default rows for new shop */
        try{ await sb.insert('hw_suppliers', { shop_id: shop.id, name:'General Supplier', phone:'', bal:0, incentive:0, ts:Date.now() }); }catch(e){}
        // HQ registry (best-effort) — NextGen HQ admin.nextgenaidevelopers.com ki `clients` table
        try{
          await sb.insert('clients', { name: p.ownerName||'Owner', shop_name: p.name, phone: p.phone||'', city: p.city||'', software: 'Honda Islamabad', kind: 'online', status: trial_ends ? 'trial' : 'active', trial_ends, monthly_fee: Number(p.monthly_fee)||0, notes: 'hw:' + shop.id });
        }catch(e){}
        return json({ ok:true, id: shop.id });
      }
      if(sub === 'shop.update' && request.method === 'POST'){
        const p = await request.json();
        if(!p.id) return json({ error:'id zaroori hai' }, 400);
        const body = {};
        for(const k of ['name','tagline','phone','address','status','trial_ends']) if(p[k] !== undefined) body[k] = p[k];
        await sb.update('hw_shops?id=eq.' + p.id, body);
        try{
          const cb = {};
          if(body.name !== undefined) cb.shop_name = body.name;
          if(body.phone !== undefined) cb.phone = body.phone;
          if(body.status !== undefined) cb.status = body.status;
          if(body.trial_ends !== undefined) cb.trial_ends = body.trial_ends;
          if(Object.keys(cb).length) await sb.update('clients?notes=eq.' + encodeURIComponent('hw:' + p.id), cb);
        }catch(e){}
        return json({ ok:true });
      }
      if(sub === 'user.setpass' && request.method === 'POST'){
        const p = await request.json();
        if(!p.user_id || !p.shop_id || !p.password) return json({ error:'user_id, shop_id, password zaroori hain' }, 400);
        await sb.update('hw_users?id=eq.' + p.user_id + '&shop_id=eq.' + p.shop_id, { password: p.password });
        return json({ ok:true });
      }
      return json({ error:'not found' }, 404);
    }

    // ---------- Shop app ----------
    if(path === 'login' && request.method === 'POST'){
      const { username, password } = await request.json();
      const rows = await sb.get('hw_users?username=eq.' + encodeURIComponent((username||'').trim()) + '&select=*');
      const u = rows && rows[0];
      if(!u || u.password !== password) return json({ error:'Wrong username or password' }, 401);
      const shops = await sb.get('hw_shops?id=eq.' + u.shop_id + '&select=status,trial_ends');
      const shop = shops && shops[0];
      if(shop){
        if(shop.status === 'blocked') return json({ error:'Software band hai — ' + RABTA }, 403);
        if(shop.status === 'trial' && shop.trial_ends && new Date(shop.trial_ends + 'T23:59:59') < new Date())
          return json({ error:'Trial khatam ho gaya — ' + RABTA }, 403);
      }
      const token = await signToken({ uid:u.id, sid:u.shop_id, role:u.role, exp: Date.now()+1000*60*60*24*30 }, SECRET);
      return json({ token, user:{ username:u.username, name:u.name, role:u.role }, shopId:u.shop_id });
    }

    const session = await auth(request, SECRET);
    if(!session) return json({ error:'unauthorized' }, 401);
    const sid = session.sid;

    if(path === 'bootstrap' && request.method === 'GET'){
      const data = await sb.rpc('fn_hw_bootstrap', { p_sid: sid });
      if(data && data.status === 'blocked') return json({ error:'Software band hai — ' + RABTA }, 403);
      if(data) delete data.status;
      return json(data);
    }

    if(path === 'action' && request.method === 'POST'){
      const { action, payload } = await request.json();
      const res = await applyAction(sb, sid, session, action, payload||{});
      return json(res || { ok:true });
    }

    return json({ error:'not found' }, 404);
  }catch(e){
    return json({ error:'server error', detail:String(e&&e.message||e) }, 500);
  }
}

const first = rows => Array.isArray(rows) ? rows[0] : rows;
const num = v => { const n = Number(v); return isFinite(n) ? n : 0; };

async function applyAction(sb, sid, session, action, p){
  const now = Date.now();
  const owner = () => session.role === 'owner';
  const scoped = (table) => table + '?id=eq.' + p.id + '&shop_id=eq.' + sid;

  switch(action){
    // ===================== PARTS / STOCK =====================
    case 'part.add': {
      const r = first(await sb.insert('hw_parts', { shop_id:sid, name:p.name, nick:p.nick||'', model:p.model||'', code:p.code||'', loc:p.loc||'', stock:num(p.stock), min_qty:num(p.min_qty), cost:num(p.cost), price:num(p.price), ts:now }));
      return { ok:true, id: r && r.id };
    }
    case 'part.update':
      await sb.update(scoped('hw_parts'), { name:p.name, nick:p.nick||'', model:p.model||'', code:p.code||'', loc:p.loc||'', stock:num(p.stock), min_qty:num(p.min_qty), cost:num(p.cost), price:num(p.price) }); return { ok:true };
    case 'part.delete':
      if(!owner()) return { error:'owner only' };
      await sb.del(scoped('hw_parts')); return { ok:true };

    // ===================== SUPPLIERS =====================
    case 'supplier.add': {
      const r = first(await sb.insert('hw_suppliers', { shop_id:sid, name:p.name, phone:p.phone||'', address:p.address||'', bal:num(p.bal), incentive:num(p.incentive), ts:now }));
      return { ok:true, id: r && r.id };
    }
    case 'supplier.update':
      await sb.update(scoped('hw_suppliers'), { name:p.name, phone:p.phone||'', address:p.address||'', bal:num(p.bal), incentive:num(p.incentive) }); return { ok:true };
    case 'supplier.delete':
      if(!owner()) return { error:'owner only' };
      await sb.del(scoped('hw_suppliers')); return { ok:true };

    // ===================== MECHANICS =====================
    case 'mech.add': {
      const r = first(await sb.insert('hw_mechanics', { shop_id:sid, name:p.name, mobile:p.mobile||'', cnic:p.cnic||'', dob:p.dob||'', designation:p.designation||'Mechanic', commission:num(p.commission), active:p.active!==false, ts:now }));
      return { ok:true, id: r && r.id };
    }
    case 'mech.update':
      await sb.update(scoped('hw_mechanics'), { name:p.name, mobile:p.mobile||'', cnic:p.cnic||'', dob:p.dob||'', designation:p.designation||'Mechanic', commission:num(p.commission), active:p.active!==false }); return { ok:true };
    case 'mech.delete':
      if(!owner()) return { error:'owner only' };
      await sb.del(scoped('hw_mechanics')); return { ok:true };
    case 'mech.ledger.add': {
      const r = first(await sb.insert('hw_mech_ledger', { shop_id:sid, mech_id:p.mech_id, kind:p.kind||'settle', amt:num(p.amt), date:p.date||'', note:p.note||'', ts:now }));
      return { ok:true, id: r && r.id };
    }
    case 'mech.ledger.delete':
      if(!owner()) return { error:'owner only' };
      await sb.del('hw_mech_ledger?id=eq.'+p.id+'&shop_id=eq.'+sid); return { ok:true };

    // ===================== EMPLOYEES =====================
    case 'emp.add': {
      const r = first(await sb.insert('hw_employees', { shop_id:sid, code:p.code||'', name:p.name, designation:p.designation||'', role:p.role||'', salary:num(p.salary), active:p.active!==false, ts:now }));
      return { ok:true, id: r && r.id };
    }
    case 'emp.update':
      await sb.update(scoped('hw_employees'), { code:p.code||'', name:p.name, designation:p.designation||'', role:p.role||'', salary:num(p.salary), active:p.active!==false }); return { ok:true };
    case 'emp.delete':
      if(!owner()) return { error:'owner only' };
      await sb.del(scoped('hw_employees')); return { ok:true };
    case 'emp.ledger.add': {
      const r = first(await sb.insert('hw_emp_ledger', { shop_id:sid, emp_id:p.emp_id, kind:p.kind||'salary', amt:num(p.amt), month:p.month||'', date:p.date||'', note:p.note||'', ts:now }));
      return { ok:true, id: r && r.id };
    }
    case 'emp.ledger.delete':
      if(!owner()) return { error:'owner only' };
      await sb.del('hw_emp_ledger?id=eq.'+p.id+'&shop_id=eq.'+sid); return { ok:true };

    // ===================== EXPENSES =====================
    case 'expense.add': {
      const r = first(await sb.insert('hw_expenses', { shop_id:sid, title:p.title||'', cat:p.cat||'General', amt:num(p.amt), date:p.date||'', ts:now }));
      return { ok:true, id: r && r.id };
    }
    case 'expense.update':
      await sb.update(scoped('hw_expenses'), { title:p.title||'', cat:p.cat||'General', amt:num(p.amt), date:p.date||'' }); return { ok:true };
    case 'expense.delete':
      await sb.del(scoped('hw_expenses')); return { ok:true };

    // ===================== KHARADIA =====================
    case 'khar.add': {
      const r = first(await sb.insert('hw_kharadia', { shop_id:sid, descr:p.descr||'', customer:p.customer||'', bike:p.bike||'', paid_out:num(p.paid_out), charged:num(p.charged), date:p.date||'', ts:now }));
      return { ok:true, id: r && r.id };
    }
    case 'khar.update':
      await sb.update(scoped('hw_kharadia'), { descr:p.descr||'', customer:p.customer||'', bike:p.bike||'', paid_out:num(p.paid_out), charged:num(p.charged), date:p.date||'' }); return { ok:true };
    case 'khar.delete':
      await sb.del(scoped('hw_kharadia')); return { ok:true };

    // ===================== WARRANTY =====================
    case 'warranty.add': {
      const r = first(await sb.insert('hw_warranty', { shop_id:sid, job_id:p.job_id||null, job_no:p.job_no||'', customer:p.customer||'', bike:p.bike||'', descr:p.descr||'', date:p.date||'', claimed:num(p.claimed), approved:num(p.approved), status:p.status||'pending', ts:now }));
      return { ok:true, id: r && r.id };
    }
    case 'warranty.update':
      await sb.update(scoped('hw_warranty'), { customer:p.customer||'', bike:p.bike||'', descr:p.descr||'', date:p.date||'', claimed:num(p.claimed), approved:num(p.approved), status:p.status||'pending' }); return { ok:true };
    case 'warranty.delete':
      if(!owner()) return { error:'owner only' };
      await sb.del(scoped('hw_warranty')); return { ok:true };

    // ===================== TRANSACTIONS (RPC) =====================
    case 'sale':            return await sb.rpc('fn_hw_sale',            { p_sid: sid, p });
    case 'sale.delete':     if(!owner()) return { error:'owner only' };
                            return await sb.rpc('fn_hw_sale_delete',     { p_sid: sid, p });
    case 'purchase':        return await sb.rpc('fn_hw_purchase',        { p_sid: sid, p });
    case 'purchase.delete': if(!owner()) return { error:'owner only' };
                            return await sb.rpc('fn_hw_purchase_delete', { p_sid: sid, p });
    case 'job.create':      return await sb.rpc('fn_hw_job_create',      { p_sid: sid, p });
    case 'job.update':      return await sb.rpc('fn_hw_job_update',      { p_sid: sid, p });
    case 'job.delete':      if(!owner()) return { error:'owner only' };
                            return await sb.rpc('fn_hw_job_delete',      { p_sid: sid, p });

    // ---- danger zone ----
    case 'data.reset': {
      if(!owner()) return { error:'owner only' };
      for(const tbl of ['hw_sale_items','hw_purchase_items','hw_job_parts','hw_mech_ledger','hw_emp_ledger','hw_warranty','hw_sales','hw_purchases','hw_jobs','hw_kharadia','hw_expenses','hw_mechanics','hw_employees','hw_suppliers','hw_parts']){
        await sb.del(tbl + '?shop_id=eq.' + sid);
      }
      await sb.update('hw_shops?id=eq.' + sid, { inv_no:4000, po_no:1000, srv_no:3000 });
      return { ok:true };
    }

    case 'shop.update':
      if(!owner()) return { error:'owner only' };
      await sb.update('hw_shops?id=eq.' + sid, { name:p.name, tagline:p.tagline||'', phone:p.phone||'', address:p.address||'' }); return { ok:true };

    // ---- users ----
    case 'user.add': {
      if(!owner()) return { error:'owner only' };
      const ex = await sb.get('hw_users?username=eq.' + encodeURIComponent(p.username) + '&select=id');
      if(ex && ex.length) return { error:'username exists' };
      try{
        const r = first(await sb.insert('hw_users', { shop_id:sid, username:p.username, password:p.password, name:p.name||p.username, role:p.role||'cashier' }));
        return { ok:true, id: r && r.id };
      }catch(e){ return { error:'username exists' }; }
    }
    case 'user.update':
      if(!owner()) return { error:'owner only' };
      if(p.password) await sb.update(scoped('hw_users'), { name:p.name, role:p.role, password:p.password });
      else await sb.update(scoped('hw_users'), { name:p.name, role:p.role });
      return { ok:true };
    case 'user.delete':
      if(!owner()) return { error:'owner only' };
      if(p.id === session.uid) return { error:'cannot delete self' };
      await sb.del(scoped('hw_users')); return { ok:true };
    case 'password.change':
      await sb.update('hw_users?id=eq.' + session.uid, { password:p.password }); return { ok:true };

    default:
      return { error:'unknown action: '+action };
  }
}
