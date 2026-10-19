# Hosting RecruitAI on Cloudflare

The short version: **the frontend is hosted on Cloudflare Pages; the backends
run in Docker on a host you control and are published through a Cloudflare
Tunnel.** Cloudflare is the front door and the CDN, not the compute.

## Why the backends can't live on Cloudflare

Not a configuration problem — the platform can't run this code.

* **Workers.** Python Workers run CPython compiled to WebAssembly (Pyodide), so
  any package with a native C/C++/Rust extension needs a WASM-targeted wheel.
  Cloudflare names `numpy`, `pandas` and `cryptography` as unsupported, and
  `component2/backend/requirements.txt` is entirely that class of package
  (`torch`, `scikit-learn`, `scipy`, `sentence-transformers`, `pymongo`,
  `bcrypt`, `python-jose[cryptography]`). Workers also have no raw TCP, so
  `motor`/`pymongo` can't reach MongoDB (Hyperdrive covers PostgreSQL/MySQL
  only).
* **Containers.** The lighter services could fit, but `c2` cannot: it grades
  candidate code by launching a container through `/var/run/docker.sock`, and
  Cloudflare Containers give you no Docker daemon and no nested containers. The
  images would also have to get under the ~2 GB compressed cap, which `torch` +
  `sentence-transformers` + `scikit-learn` + `PyMuPDF` will not.

So the split is: **Pages** for `frontend/`, **Tunnel** for the five FastAPI
services. The sandbox keeps a real Docker daemon, which is what it needs.

## Hostname layout

Five subdomains, one per backend service. Five is not a choice — `api.js`
resolves each component to its own origin.

| Hostname | Compose service | Port | Component |
|---|---|---|---|
| `c0.example.com` | `backend` | 8000 | unified: auth, jobs, resume, export |
| `c1.example.com` | `c1` | 8001 | CV analysis |
| `c2.example.com` | `c2` | 8002 | AI interview **and the code sandbox** |
| `c3.example.com` | `c3` | 8003 | candidate ranking |
| `c4.example.com` | `c4` | 8004 | skill gap and career development |
| `app.example.com` | Cloudflare Pages | – | the React app |

## Prerequisites

* A Cloudflare account, with a domain already added to it (a tunnel can only
  claim hostnames in a zone you control).
* The host running Docker: Docker daemon up, this repo checked out, `.env`
  present (copy `.env.example`).
* `wrangler` for the frontend — `npx wrangler` works, no install needed.

---

## Part 1 — Frontend on Cloudflare Pages

The build must be told the five API origins. They are baked into the bundle at
build time, so a build without them falls back to `http://127.0.0.1:8000-8004`
and every visitor's browser calls its own machine.

```powershell
cd frontend
Copy-Item .env.production.example .env.production
# edit .env.production: replace c0..c4.example.com with your hostnames
npm ci
npm run build          # emits dist/
npx wrangler pages deploy
```

Wrangler prints the deployment URL. Add your custom domain under
**Workers & Pages → your project → Custom domains**, e.g. `app.example.com`.

Then set `ALLOWED_ORIGINS` in the root `.env` to exactly that origin:

```
ALLOWED_ORIGINS=https://app.example.com
```

If you skip this the app loads and then every request fails CORS, which looks
like a backend outage. Note it is the *frontend* origin, not the API hostnames.

`frontend/public/_redirects` handles the SPA fallback (`BrowserRouter` deep
links like `/login/company` have no file on disk), and
`frontend/public/_headers` sets the security and cache headers.

## Part 2 — Backends through the Tunnel

The tunnel connects *out* to Cloudflare, so no public IP, no port forwarding and
no inbound firewall rule are needed.

### Option A — token (routes in the dashboard)

1. **Zero Trust → Networks → Tunnels → Create a tunnel**, pick *Cloudflared*,
   name it e.g. `r26-it-148`, and copy the token.
2. Add a **Public hostname** for each row of the table above, pointing at the
   compose service name and port — e.g. `c2.example.com` → `http://c2:8002`.
   These are reachable because `cloudflared` joins the compose network.
3. Put the token in `.env` as `TUNNEL_TOKEN=...`.
4. Start the stack:

```powershell
docker compose -f docker-compose.yml `
               -f deploy/cloudflare/docker-compose.prod-env.yml `
               -f deploy/cloudflare/docker-compose.tunnel.yml up -d
```

### Option B — config file (routes in the repo)

```powershell
cloudflared tunnel login
cloudflared tunnel create r26-it-148
cloudflared tunnel route dns r26-it-148 c0.example.com   # ...and c1-c4
```

Save the credentials JSON that `tunnel create` prints as
`deploy/cloudflare/credentials.json` (git-ignored), edit the hostnames in
`deploy/cloudflare/config.locally-managed.yml`, then:

```powershell
docker compose -f docker-compose.yml `
               -f deploy/cloudflare/docker-compose.prod-env.yml `
               -f deploy/cloudflare/docker-compose.local-config.yml up -d
```

### What the prod-env overlay does

* Sets `ALLOWED_ORIGINS` on all five services. The base compose file only sets
  it on `backend`, so without this `c1`–`c4` keep the `http://localhost:5174`
  default and reject the deployed frontend.
* Sets `ALLOW_LOCALHOST_ORIGINS=0`, which removes the dev-only regex that
  otherwise accepts a request from any localhost port.

---

## Verifying it

```powershell
docker compose ps                          # cloudflared should be Up
docker compose logs -f cloudflared         # look for the registered hostnames
```

Then, from outside the host:

```powershell
curl https://c2.example.com/interview/health
curl -I https://app.example.com            # expect 200 and the _headers
```

`/interview/health` reports the resolved sandbox backend under `code_sandbox`.
On the tunnel deployment it should say `docker` — if it says `subprocess`, the
candidate's code is running with only the import guard and you should stop and
fix the daemon access before letting anyone use it.

Finally, open `https://app.example.com` and walk a candidate flow end to end
(login, start an interview, submit code) — that exercises all five services and
the sandbox in one pass.

## Security checklist

Ordered by what actually matters.

1. **Rotate the leaked MongoDB Atlas credentials.** `.env.example` is tracked by
   git and has carried a live-looking connection string
   (`mongodb+srv://admin:…@coordinator.ljarc.mongodb.net/HR`) since commit
   `f5b5acf`, and it is on the remote. Anyone with the repo has that cluster.
   Change the password in Atlas → Database Access and treat the old one as
   public. The same applies to the committed `INTERNAL_API_KEY`.
2. **Do not publish the backend ports.** The base `docker-compose.yml` publishes
   8000–8004 on the host. With a tunnel you don't need that, and on a cloud VM
   it puts the services on the public internet, bypassing Cloudflare entirely —
   including `:8002`, which runs candidate code. Remove the `ports:` blocks for
   the deployment or firewall them (`ufw deny 8000:8004`). Compose cannot delete
   a port mapping in an override file, so this is an edit to `docker-compose.yml`
   on the deployment host.
3. **Set a real `JWT_SECRET`.** It signs every session token; a guessable value
   means anyone can mint an admin token. Generate one:
   `python -c "import secrets; print(secrets.token_hex(32))"`.
4. **Add a Content-Security-Policy.** There is deliberately none yet, because
   the API origins are build-time values and a wrong CSP breaks the deployed app
   (see `frontend/public/_headers`). Once the hostnames are settled, the policy
   needs at least `default-src 'self'; connect-src 'self' https://c0.… c1.… c2.…
   c3.… c4.…; img-src 'self' data: blob:; style-src 'self' 'unsafe-inline'`.
   This matters more than it sounds: the session JWT lives in `localStorage`, so
   a CSP is the main limit on the damage any XSS can do.
5. **Put Cloudflare Access in front of anything not meant to be public.** The
   tunnel is a front door, not an auth layer — every route it exposes is
   reachable by anyone who knows the hostname.

## Known limits

* **The host has to stay up.** If this runs on a laptop, the site goes down when
  it sleeps. `c2` needs a Docker daemon, so it cannot be a serverless target.
* **The sandbox image must exist** (`recruitai-py-sandbox:1`). It is built on
  demand by default (`CODE_SANDBOX_AUTOBUILD=1`, a few seconds), or explicitly
  with `docker build -t recruitai-py-sandbox:1 component2/backend/sandbox`.
* **MongoDB.** The compose stack runs `mongodb` locally; for a deployment you'll
  usually point `MONGODB_URI` at Atlas instead. Either works, but a local
  container means the data lives and dies with the host's volume.
* **Cost.** Pages and Tunnel are free at this scale. You pay for the host and
  for Cloudflare Access if you enable it beyond the free seat count.
