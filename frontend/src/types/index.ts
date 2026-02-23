// frontend/src/types/index.ts

export interface OcrMetadata {
  is_masked: boolean;
  process_time_ms: number;
}

export interface OcrData {
  id_number: string | null;
  name_th: string | null;
  name_en: string | null;
  dob: string | null;
  religion: string | null;
  address: string | null;
  metadata: OcrMetadata;
}

export interface DebugInfo {
  raw_text_count: number;
  raw_text: string[];
  llm_model: string;
}

export interface OcrResponse {
  status: string;
  message?: string;
  request_id?: string;
  timestamp?: string;
  data: OcrData;
  debug: DebugInfo;
}

export interface ApiErrorPayload {
  detail?: string;
  message?: string;
  status?: string;
}