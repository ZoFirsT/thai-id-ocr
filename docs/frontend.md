# Frontend Implementation Guide

The frontend (Next.js 16 + React 19 + Tailwind CSS v4) now ships a complete UX for uploading Thai ID cards, toggling LLM usage, and reviewing OCR/LLM results along with raw text/debug metadata.

## Project Structure
```
frontend/
├── package.json            # scripts, deps (Next.js 16, React 19)
├── tsconfig.json
└── src/app/
    ├── layout.tsx          # Root layout w/ Geist fonts
    ├── globals.css         # Tailwind entry + design tokens
    └── page.tsx            # Upload UI + status/result panels
```

## Implemented Components
1. **UploadZone** – drag & drop + click-to-upload, size validation, live preview state.
2. **LLM Toggle Card** – switch between EasyOCR-only vs OCR+LLM, reflects env defaults.
3. **Status Banner** – dynamic messaging for idle/uploading/success/error stages.
4. **ResultCard** – displays structured fields plus badges for masking, LLM model, processing time.
5. **Raw Text Panel** – accordion showing `debug.raw_text`, includes JSON download button.
6. **Error Toast** – highlights backend errors (413/415/502/503) with copy-friendly text.

## UX Flow
1. **Landing** – Hero headline + description, instructions for drag/drop.
2. **Upload Interaction** – Animated border, helper text for JPG/PNG + size limit.
3. **Processing State** – Banner indicates EasyOCR-only vs OCR+LLM path per toggle.
4. **Result Display** – Two-column layout; left manages upload controls, right shows ResultCard + Raw Text accordion.
5. **Error State** – Stage-aware banner plus dedicated error card near results.

```
<AppLayout>
  <HeroHeader />
  <UploadPanel>
    <UploadZone />
    <ProcessingControls />
    <StatusBanner />
  </UploadPanel>
  <ResultPanel>
    <ResultCard />
    <RawTextPanel />
  </ResultPanel>
</AppLayout>
```

## API Interaction
- ใช้ native `fetch` + `FormData`
- Base URL จาก `NEXT_PUBLIC_API_BASE_URL`
- Query string `use_llm=${useLLM}` ผูกกับ toggle
- ถ้า `response.ok` เป็น false พยายามอ่าน `detail/message` แล้ว surface ผ่าน error banner

## State Management
- ใช้ `useState` สำหรับ `stage`, `useLLM`, `selectedFile`, `result`, `error`, `rawExpanded`
- `statusBanner` คำนวณผ่าน `useMemo` เพื่อลด re-render
- อนาคตสามารถย้าย logic ไป custom hook เช่น `useOcrMutation`

## Styling & UX
- Tailwind CSS (v4) already configured
- Define custom color tokens for trustworthy ID processing feel (grays, deep green/blue accents)
- Add subtle micro-interactions (hover states, skeleton loaders)
- Provide file validation message if size exceeds `NEXT_PUBLIC_MAX_UPLOAD_MB`
- Use responsive grid: stacked layout < 768px, two-column ≥ 1024px
- Typography pairing: display font for headings (e.g., Prompt) + readable body (Inter/TH Sarabun)
- Provide dark-mode ready tokens (via CSS variables) for future toggle

## Future Enhancements
- Persist recent results in local storage for quick comparison
- Provide manual correction inputs + re-send to LLM
- Integrate PDF export or share link once backend includes persistence
- Add PWA install prompt for kiosks
- Multi-language UI (TH/EN toggle)
- Accessibility review: keyboard navigation + screen-reader labels for each field

## Frontend Tasks Checklist
- [x] Replace default Next.js page with Upload UI
- [x] Implement file input + preview + size validation
- [x] Call backend API and render results
- [x] Handle errors (LLM failure, invalid content type, file too large)
- [x] Display metadata/debug info with toggle + raw text panel
- [ ] Add integration tests (Playwright/Testing Library)
