# Barakah

Islamic Finance for a Blessed Tomorrow.

The runnable **frontend-only** application is in [barakah-ui/](barakah-ui/README.md).

```sh
cd barakah-ui
npm install
npm run dev
```

## Vercel

Import this repository with **Root Directory `.`** (the repository root). The committed `vercel.json` installs and builds `barakah-ui/`, serves `barakah-ui/dist/`, and falls back to `index.html` for frontend paths. No environment variables are needed.

Use `feat/barakah-frontend` as the Production Branch for this frontend deployment. Leave Build & Output overrides disabled; the repository configuration supplies them. Redeploy after changing project settings. If you instead select `barakah-ui` as the project Root Directory, use Vercel's Vite preset with output `dist` and default npm install/build commands.

- [Frontend guide and acceptance checklist](barakah-ui/README.md)
- [Draft backend integration contract](barakah-ui/API_CONTRACT.md)
- [Local validation record](barakah-ui/QA.md)
- [Design system](DESIGN.md)

All service data is mocked locally. No backend, real payments, account authentication, market services or live AI is included.
