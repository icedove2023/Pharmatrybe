# Switch backend target back to Vercel before Git push

Use this checklist when you want the frontend to point at the deployed Vercel backend instead of the local FastAPI instance.

## 1) Update the root frontend env file

File: `.env`

Change these values from localhost to the Vercel deployment URL:

```env
VITE_LOCAL_API_BASE_URL=http://localhost:8000/api/v1
VITE_VERCEL_API_BASE_URL=https://pharmatrybe-api.vercel.app/api/v1
VITE_API_BASE_URL=https://pharmatrybe-api.vercel.app/api/v1
API_BASE_URL=https://pharmatrybe-api.vercel.app/api/v1
```

This is the main switch used by the app at runtime.

## 2) Confirm the frontend client uses the correct base URL

File: `src/api/client.ts`

The relevant logic is:

```ts
const LOCAL_API_BASE_URL = (viteEnv?.VITE_LOCAL_API_BASE_URL || 'http://localhost:8000/api/v1').replace(/\/$/, '');
const VERCEL_API_BASE_URL = (viteEnv?.VITE_VERCEL_API_BASE_URL || viteEnv?.VITE_API_BASE_URL || 'http://localhost:8000/api/v1').replace(/\/$/, '');

function resolveApiBaseUrl(): string {
  const explicitBase = (viteEnv?.VITE_API_BASE_URL || LOCAL_API_BASE_URL).trim();
  if (explicitBase) return explicitBase.replace(/\/$/, '');

  if (typeof window !== 'undefined' && /localhost|127\.0\.0\.1|0\.0\.0\.0/.test(window.location.hostname)) {
    return LOCAL_API_BASE_URL;
  }

  return VERCEL_API_BASE_URL;
}
```

For production/Vercel deployment, make sure `VITE_API_BASE_URL` is set to the Vercel backend URL.

## 3) If using a deployed environment on Vercel itself

In the Vercel project settings, add or update these environment variables:

```env
VITE_API_BASE_URL=https://pharmatrybe-api.vercel.app/api/v1
```

This ensures the deployed frontend points to the hosted API instead of localhost.

## 4) Safe push workflow

When preparing to commit back to Git:

1. Set `.env` to the Vercel URL.
2. Ensure `src/api/client.ts` resolves to the Vercel URL.
3. Commit and push.
4. Redeploy the frontend if needed.

## Quick summary

The app is controlled by these keys:

- `VITE_API_BASE_URL`
- `VITE_VERCEL_API_BASE_URL`
- `API_BASE_URL`

For Vercel, always set the value to:

```env
https://pharmatrybe-api.vercel.app/api/v1
```

If you want the app to work locally again later, switch those same entries back to:

```env
http://localhost:8000/api/v1
```
