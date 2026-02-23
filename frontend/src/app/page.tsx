"use client";

import { useMemo, useState } from "react";
import UploadZone from "@/components/UploadZone";
import ResultCard from "@/components/ResultCard";
import { ApiErrorPayload, OcrResponse } from "@/types";
import { AlertTriangle, CheckCircle2, Download, Loader2, RefreshCw, Sparkles, FileJson } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");
const MAX_UPLOAD_MB = Number(process.env.NEXT_PUBLIC_MAX_UPLOAD_MB || "8");

type Stage = "idle" | "uploading" | "success" | "error";

export default function Home() {
  const [stage, setStage] = useState<Stage>("idle");
  const [useLLM, setUseLLM] = useState(true);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [result, setResult] = useState<OcrResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [rawExpanded, setRawExpanded] = useState(false);

  const isProcessing = stage === "uploading";

  const resetState = () => {
    setStage("idle");
    setSelectedFile(null);
    setResult(null);
    setError(null);
    setRawExpanded(false);
  };

  const handleUpload = async (file: File) => {
    if (file.size > MAX_UPLOAD_MB * 1024 * 1024) {
      setError(`ไฟล์มีขนาดเกิน ${MAX_UPLOAD_MB}MB`);
      setStage("error");
      return;
    }

    setSelectedFile(file);
    setStage("uploading");
    setError(null);
    setResult(null);
    setRawExpanded(false);

    const formData = new FormData();
    formData.append("image", file);
    const endpoint = `${API_BASE_URL}/api/v1/extract-id?use_llm=${useLLM}`;

    try {
      const response = await fetch(endpoint, { method: "POST", body: formData });
      if (!response.ok) {
        let payload: ApiErrorPayload | null = null;
        try { payload = (await response.json()) as ApiErrorPayload; } catch (err) {}
        throw new Error(payload?.detail || payload?.message || `เชื่อมต่อไม่สำเร็จ (HTTP ${response.status})`);
      }
      const data: OcrResponse = await response.json();
      setResult(data);
      setStage("success");
    } catch (err) {
      setResult(null);
      setStage("error");
      setError(err instanceof Error ? err.message : "เกิดข้อผิดพลาดบางอย่าง");
    }
  };

  const handleDownload = () => {
    if (!result) return;
    const blob = new Blob([JSON.stringify(result, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `thai-id-ocr-${result.request_id || "result"}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const statusBanner = useMemo(() => {
    const banners = {
      idle: {
        icon: Sparkles, color: "text-blue-500", bg: "bg-white", border: "border-slate-200",
        title: "พร้อมประมวลผล", desc: "อัปโหลดภาพบัตรและเลือกว่าจะใช้ AI LLM ช่วยวิเคราะห์หรือไม่"
      },
      uploading: {
        icon: Loader2, color: "text-blue-600 animate-spin", bg: "bg-blue-50/80", border: "border-blue-200",
        title: "กำลังประมวลผลด้วย AI", desc: "ระบบกำลังทำงานเบื้องหลัง กรุณารอสักครู่..."
      },
      success: {
        icon: CheckCircle2, color: "text-emerald-600", bg: "bg-emerald-50/80", border: "border-emerald-200",
        title: "สกัดข้อมูลสำเร็จ", desc: "ตรวจสอบความถูกต้องของข้อมูลได้ที่การ์ดด้านขวา"
      },
      error: {
        icon: AlertTriangle, color: "text-red-500", bg: "bg-red-50/80", border: "border-red-200",
        title: "เกิดข้อผิดพลาด", desc: error
      }
    };

    const current = banners[stage];
    const Icon = current.icon;

    return (
      <motion.div 
        key={stage} initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}
        className={`flex items-start gap-4 backdrop-blur-sm ${current.bg} border ${current.border} rounded-2xl p-5 shadow-sm`}
      >
        <div className={`p-2 rounded-full bg-white/60 shadow-sm ${current.color}`}>
          <Icon className="h-5 w-5" />
        </div>
        <div>
          <p className="font-bold text-slate-800 text-[15px]">{current.title}</p>
          <p className="text-sm text-slate-600 mt-1">{current.desc}</p>
        </div>
      </motion.div>
    );
  }, [stage, error]);

  return (
    <main className="min-h-screen relative flex flex-col items-center py-16 px-4 sm:px-6 lg:px-8 font-sans selection:bg-blue-100 selection:text-blue-900">
      {/* Modern Background */}
      <div className="absolute inset-0 -z-10 h-full w-full bg-slate-50 bg-[radial-gradient(#e5e7eb_1px,transparent_1px)] [background-size:16px_16px] [mask-image:radial-gradient(ellipse_50%_50%_at_50%_0%,#000_70%,transparent_100%)]"></div>
      
      <div className="text-center mb-12 relative z-10">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white border border-slate-200 shadow-sm mb-6">
          <span className="flex h-2 w-2 rounded-full bg-blue-600 animate-pulse"></span>
          <span className="text-sm font-medium text-slate-600">EasyOCR + Local LLM Engine</span>
        </motion.div>
        <h1 className="text-4xl md:text-5xl font-extrabold text-slate-900 tracking-tight mb-4">
          Thai ID Card <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">eKYC</span>
        </h1>
        <p className="max-w-xl mx-auto text-base text-slate-500">
          ระบบสกัดข้อมูลจากบัตรประชาชนไทยอัตโนมัติ แม่นยำ และปลอดภัย
        </p>
      </div>

      <div className="w-full max-w-6xl grid grid-cols-1 lg:grid-cols-[1.1fr_0.9fr] gap-10 items-start relative z-10">
        {/* Left Column - Controls */}
        <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.1 }} className="space-y-6">
          <UploadZone onUpload={handleUpload} isLoading={isProcessing} maxSizeMB={MAX_UPLOAD_MB} />

          <div className="bg-white/70 backdrop-blur-xl border border-white/50 shadow-lg shadow-slate-200/40 rounded-3xl p-7 space-y-7">
            <div className="flex items-center justify-between p-2">
              <div className="pr-4">
                <h2 className="text-base font-bold text-slate-900">ใช้ LLM ช่วยวิเคราะห์</h2>
                <p className="text-sm text-slate-500 mt-1">ช่วยจัดโครงสร้างข้อความและแก้คำผิดให้แม่นยำขึ้น</p>
              </div>
              <button
                type="button" role="switch" aria-checked={useLLM} disabled={isProcessing}
                onClick={() => setUseLLM(!useLLM)}
                className={`relative inline-flex h-7 w-14 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-300 ease-in-out focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2 ${
                  useLLM ? "bg-blue-600" : "bg-slate-300"
                } ${isProcessing ? "opacity-50 cursor-not-allowed" : ""}`}
              >
                <span className={`pointer-events-none inline-block h-6 w-6 transform rounded-full bg-white shadow-md ring-0 transition duration-300 ease-in-out ${useLLM ? "translate-x-7" : "translate-x-0"}`} />
              </button>
            </div>

            <AnimatePresence mode="wait">{statusBanner}</AnimatePresence>

            <div className="flex gap-3 pt-2">
              <button
                type="button" onClick={() => selectedFile && handleUpload(selectedFile)} disabled={!selectedFile || isProcessing}
                className="flex-1 inline-flex items-center justify-center gap-2 rounded-xl bg-slate-900 hover:bg-slate-800 transition-colors px-5 py-3.5 text-white font-medium shadow-md shadow-slate-900/10 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isProcessing ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4 text-blue-400" />}
                {isProcessing ? "กำลังวิเคราะห์..." : "ประมวลผลข้อมูล"}
              </button>
              {(selectedFile || result || error) && (
                <button
                  type="button" onClick={resetState} disabled={isProcessing}
                  className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 px-5 py-3.5 text-slate-700 font-medium transition-colors disabled:opacity-50"
                >
                  <RefreshCw className="h-4 w-4" /> เริ่มใหม่
                </button>
              )}
            </div>
          </div>
        </motion.div>

        {/* Right Column - Results */}
        <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2 }} className="space-y-6 flex flex-col items-center lg:items-start">
          <ResultCard result={result} />

          <AnimatePresence>
            {result && (
              <motion.div 
                initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
                className="w-full max-w-md bg-white border border-slate-200 shadow-sm rounded-2xl p-6"
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2 text-slate-800 font-semibold">
                    <FileJson className="w-5 h-5 text-blue-500" />
                    <h3>ข้อมูล Raw & JSON</h3>
                  </div>
                  <div className="flex gap-2">
                    <button onClick={() => setRawExpanded(!rawExpanded)} className="px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-100 text-slate-600 hover:bg-slate-200 transition-colors">
                      {rawExpanded ? "ซ่อน" : "ดู Raw Text"}
                    </button>
                    <button onClick={handleDownload} className="px-3 py-1.5 rounded-lg text-xs font-medium bg-blue-50 text-blue-700 hover:bg-blue-100 transition-colors flex items-center gap-1">
                      <Download className="w-3.5 h-3.5" /> โหลด JSON
                    </button>
                  </div>
                </div>
                {rawExpanded && (
                  <motion.pre 
                    initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }}
                    className="max-h-60 overflow-y-auto rounded-xl bg-slate-900 text-green-400 font-mono text-xs p-4 leading-relaxed custom-scrollbar"
                  >
                    {result.debug.raw_text.join("\n")}
                  </motion.pre>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </div>
    </main>
  );
}