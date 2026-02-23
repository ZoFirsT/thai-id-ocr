# Frontend Roadmap & Guidelines

The frontend (Next.js 14 + TypeScript + Tailwind CSS) will provide an upload UI, show OCR/LLM results, and surface debug metadata. This document outlines the plan until the UI is fully implemented.

## Project Structure
```
frontend/
├── package.json            # scripts, deps (Next.js 16, React 19)
├── tsconfig.json
└── src/app/
    ├── layout.tsx          # Root layout w/ Geist fonts
    ├── globals.css         # Tailwind entry + CSS variables
    └── page.tsx            # Landing page (to be replaced by OCR UI)
```

## Planned Pages & Components
1. **UploadPage (Home)**
   - Drag-and-drop upload zone + fallback file input
   - Display max upload MB (`NEXT_PUBLIC_MAX_UPLOAD_MB`)
   - Button to trigger API call (`POST /api/v1/extract-id`)
2. **ResultCard**
   - Struct display of `id_number`, `name_th`, `name_en`, `dob`, `religion`, `address`
   - Metadata badges (`is_masked`, `process_time_ms`)
3. **RawTextPanel**
   - Expandable area showing `debug.raw_text`
4. **StatusBanner**
   - Loading / success / error states, including LLM error details.

## API Interaction
- Use `axios` or native `fetch` with `FormData`
- API base taken from `NEXT_PUBLIC_API_BASE_URL`
- On success show structured results + metadata; on failure show error toast with `detail`

## State Management
- Local state via React hooks (`useState` + `useReducer`)
- Consider `useTransition` for upload progress
- For larger-scale features, add Zustand or React Query later

## Styling & UX
- Tailwind CSS (v4) already configured
- Define custom color tokens for trustworthy ID processing feel (grays, deep green/blue accents)
- Add subtle micro-interactions (hover states, skeleton loaders)
- Provide file validation message if size exceeds `NEXT_PUBLIC_MAX_UPLOAD_MB`

## Future Enhancements
- Persist recent results in local storage for quick comparison
- Provide manual correction inputs + re-send to LLM
- Integrate PDF export or share link once backend includes persistence
- Add PWA install prompt for kiosks

## Frontend Tasks Checklist
- [ ] Replace default Next.js page with Upload UI
- [ ] Implement file input + preview + size validation
- [ ] Call backend API and render results
- [ ] Handle errors (LLM failure, invalid content type, file too large)
- [ ] Display metadata/debug info with toggle
- [ ] Add integration tests (Playwright/Testing Library)
