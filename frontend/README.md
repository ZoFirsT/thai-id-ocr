# Thai ID OCR Frontend

Next.js 16 + React 19 + Tailwind CSS v4 UI for uploading Thai ID card images, toggling LLM usage, and inspecting OCR/LLM output.

## Prerequisites
- Node.js 20+
- Backend FastAPI server running (default http://localhost:8000)
- Environment variables (optional):
  - `NEXT_PUBLIC_API_BASE_URL` (default `http://localhost:8000`)
  - `NEXT_PUBLIC_MAX_UPLOAD_MB` (default `8`)

Create a `.env.local` if you need to override defaults:

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:9000
NEXT_PUBLIC_MAX_UPLOAD_MB=10
```

## Install & Develop
```bash
npm install
npm run dev
```

Visit http://localhost:3000 and you should see:
- Drag & drop upload zone with size validation
- LLM toggle mapped to `use_llm` query param
- Status banner + error handling (413/415/502/503)
- Result card with metadata badges + raw text accordion + JSON download button

## Build & Preview
```bash
npm run build
npm start   # serves production build on port 3000
```

## Linting & Formatting
```bash
npm run lint
```

## Directory Highlights
```
src/
├── app/
│   ├── globals.css     # Tailwind entry + tokens
│   ├── layout.tsx      # Root layout, Geist fonts
│   └── page.tsx        # Upload/status/results UI
├── components/
│   ├── UploadZone.tsx  # Drag/drop + helper text
│   └── ResultCard.tsx  # Structured result display
└── types/
    └── index.ts        # Shared API response contracts
```

## Deployment Notes
- Set `NEXT_PUBLIC_API_BASE_URL` to your deployed backend URL.
- Behind reverse proxies, remember to expose the backend CORS origin for the frontend host.

For broader architecture details, see the root `README.md` and `docs/frontend.md`.
