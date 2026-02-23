"use client";

import { useCallback, useId, useState, useEffect } from "react";
import { UploadCloud, FileImage, Loader2, X } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface UploadZoneProps {
  onUpload: (file: File) => void;
  isLoading: boolean;
  maxSizeMB?: number;
}

export default function UploadZone({ onUpload, isLoading, maxSizeMB }: UploadZoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [previewFile, setPreviewFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const inputId = useId();

  useEffect(() => {
    if (previewFile) {
      const url = URL.createObjectURL(previewFile);
      setPreviewUrl(url);
      return () => URL.revokeObjectURL(url);
    }
    setPreviewUrl(null);
  }, [previewFile]);

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      setIsDragging(false);
      if (isLoading) return;
      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        const file = e.dataTransfer.files[0];
        setPreviewFile(file);
        onUpload(file);
      }
    },
    [isLoading, onUpload]
  );

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (isLoading) return;
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      setPreviewFile(file);
      onUpload(file);
    }
  };

  const clearFile = (e: React.MouseEvent) => {
    e.preventDefault();
    setPreviewFile(null);
    setPreviewUrl(null);
  };

  return (
    <div className="w-full flex flex-col items-center gap-4">
      <motion.div
        whileHover={!isLoading && !previewFile ? { scale: 1.02 } : {}}
        whileTap={!isLoading && !previewFile ? { scale: 0.98 } : {}}
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        className={`relative w-full max-w-md p-8 flex flex-col items-center justify-center border-2 border-dashed rounded-3xl transition-all duration-300 overflow-hidden ${
          isDragging
            ? "border-blue-500 bg-blue-50/50 shadow-[0_0_40px_rgba(59,130,246,0.15)]"
            : previewFile 
            ? "border-slate-200 bg-white shadow-sm"
            : "border-slate-300 hover:border-blue-400 bg-slate-50/50 hover:bg-blue-50/30"
        } ${isLoading ? "opacity-70 pointer-events-none" : "cursor-pointer"}`}
      >
        <input
          type="file"
          accept="image/jpeg,image/png"
          className="hidden"
          id={inputId}
          onChange={handleChange}
        />
        <label htmlFor={inputId} className="flex flex-col items-center w-full h-full cursor-pointer z-10">
          <AnimatePresence mode="wait">
            {isLoading ? (
              <motion.div key="loading" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="flex flex-col items-center">
                <Loader2 className="w-14 h-14 text-blue-600 animate-spin mb-4 drop-shadow-md" />
                <p className="text-lg font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">กำลังให้ AI วิเคราะห์ข้อมูล...</p>
              </motion.div>
            ) : previewUrl && previewFile ? (
              <motion.div key="preview" initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="flex flex-col items-center w-full">
                <div className="relative w-full aspect-[1.6/1] mb-4 rounded-xl overflow-hidden border border-slate-200 shadow-inner">
                  <img src={previewUrl} alt="Preview" className="w-full h-full object-cover" />
                  <div className="absolute inset-0 bg-black/40 opacity-0 hover:opacity-100 transition-opacity flex items-center justify-center">
                    <p className="text-white font-medium text-sm flex items-center gap-2"><UploadCloud className="w-4 h-4" /> เปลี่ยนรูปภาพ</p>
                  </div>
                </div>
                <p className="text-sm font-medium text-slate-700 truncate max-w-[250px]">{previewFile.name}</p>
                <button onClick={clearFile} className="absolute top-4 right-4 p-2 bg-white/80 hover:bg-red-50 text-slate-500 hover:text-red-500 rounded-full backdrop-blur-sm transition-colors shadow-sm">
                  <X className="w-4 h-4" />
                </button>
              </motion.div>
            ) : (
              <motion.div key="idle" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="flex flex-col items-center">
                <div className="w-20 h-20 mb-6 rounded-full bg-blue-50 flex items-center justify-center shadow-inner">
                  <UploadCloud className="w-10 h-10 text-blue-500" />
                </div>
                <p className="text-xl font-semibold text-slate-800 text-center mb-2">ลากรูปบัตรมาวางที่นี่</p>
                <p className="text-sm text-slate-500 text-center">หรือคลิกเพื่อเลือกไฟล์ (PNG, JPG)</p>
              </motion.div>
            )}
          </AnimatePresence>
        </label>
      </motion.div>
      {!previewFile && maxSizeMB && (
        <p className="text-xs font-medium text-slate-400 bg-slate-100 px-3 py-1.5 rounded-full">
          รองรับขนาดไฟล์สูงสุด {maxSizeMB}MB
        </p>
      )}
    </div>
  );
}