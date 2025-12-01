# Environment Setup Instructions

## Required Environment Variable

Create a `.env.local` file in the `nextjs/` directory with the following content:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

**Note**: Replace `http://localhost:8000/api` with your actual Python API URL if different.

## Why This File Isn't Created Automatically

The `.env.local` file is gitignored for security reasons (it may contain sensitive API keys in production). You need to create it manually.

## Production Setup

For production deployment, set the environment variable through your hosting platform's dashboard:
- **Vercel**: Project Settings → Environment Variables
- **Netlify**: Site Settings → Build & Deploy → Environment
- **Other platforms**: Consult their documentation for environment variable configuration

The variable should point to your production Python API URL.
