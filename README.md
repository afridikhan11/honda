# Honda Islamabad — Parts & Service Management

NextGen AI Developers pattern par bana workshop + parts management system.
Bike/motorcycle dealer ke liye — 13 modules, 3 zabaan (EN/Urdu/Roman), login + trial/block licensing,
Supabase backend, Cloudflare Pages auto-deploy.

## Modules
Dashboard · Parts/Stock · Reorder List · Purchases · Parts Sale (POS) · Suppliers ·
Service Jobs · Warranty Claims · Mechanics (payroll+advance) · Kharadia ·
Employees (payroll+advance) · Expenses · Reports

## Structure
```
public/index.html          poora app (single-file, structured — har module apna function)
public/admin.html          NextGen HQ panel (shop banao, trial, block, password reset)
functions/api/[[route]].js Cloudflare Function → Supabase REST
schema.sql                 saari tables + bootstrap + transaction RPCs
wrangler.toml              project name + SUPABASE_URL + TOKEN_SECRET
```

## Deploy — ek dafa ki setup

### 1) Supabase (database)
- Supabase project kholein (wahi jo wrangler.toml mein hai, ya naya banayein).
- SQL Editor → `schema.sql` ka poora content paste kar ke **Run** karein.
- (Naya project ho to wrangler.toml mein `SUPABASE_URL` update karein.)

### 2) GitHub
```
cd D:\Project\HondaWorkshopWeb
git init
git branch -M main
git remote add origin https://github.com/<aap-ka-user>/honda.git
git add -A
git commit -m "Honda Islamabad — first"
git push -u origin main
```
(Agli dafa sirf `PUSH-Honda.bat` chalayein.)

### 3) Cloudflare Pages
- Pages → **Connect to Git** → yeh repo select karein.
- Build command: khali chhor dein · Build output directory: `public`
- **Settings → Environment variables (Secrets)** mein daalein:
  - `SUPABASE_SERVICE_KEY` = Supabase project ki **service_role** key
  - `ADMIN_PASSWORD` = NextGen HQ panel ka password (aap ka apna)
  - (`SUPABASE_URL` aur `TOKEN_SECRET` pehle se wrangler.toml mein hain)
- Deploy hone dein (1–2 minute). Custom domain: `honda.nextgenaidevelopers.com` add karein.

### 4) Pehli dukan banayein (client login)
- `https://<site>/admin.html` kholein → `ADMIN_PASSWORD` se login.
- **+ New Shop**: dukan ka naam, username, password, aur trial days (chahein to).
- Client us username/password se main site par login karega.
- Trial khatam / paisa na de → admin panel se **block** kar dein.

## Notes
- Multi-tenant: har dukan ka data `shop_id` se alag. Ek hi deploy kai clients ko de saktay hain.
- Stock automatic ghatta/barhta hai (sale − , purchase + , service job − , delete par wapas +).
- Roles: owner (sab), salesman/cashier (mehdood screens) — `ROLE_ACCESS` mein.
- Bara data (hazaron records) ho to bootstrap limit badha saktay hain (schema.sql fn_hw_bootstrap).

Software by **NextGen AI Developers** · 0312-2546562

## AI Voice Assistant
Alag tool: `voice-assistant/` — awaaz se PC, Chrome, Facebook/TikTok chalana (free, Gemini). Detail: `voice-assistant/README.md`.
