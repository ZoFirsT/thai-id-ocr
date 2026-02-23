import { OcrResponse } from "@/types";
import { User, CreditCard, Calendar, MapPin, Heart, Shield, Copy, Check } from "lucide-react";
import { motion } from "framer-motion";
import { useState } from "react";

interface ResultCardProps {
  result: OcrResponse | null;
}

export default function ResultCard({ result }: ResultCardProps) {
  const [copiedField, setCopiedField] = useState<string | null>(null);

  if (!result) return null;
  const { data, debug, timestamp } = result;

  const handleCopy = (text: string | null, fieldId: string) => {
    if (!text) return;
    navigator.clipboard.writeText(text);
    setCopiedField(fieldId);
    setTimeout(() => setCopiedField(null), 2000);
  };

  const InfoRow = ({ icon: Icon, label, value, id }: { icon: any; label: string; value: string | null, id: string }) => (
    <motion.div 
      initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}
      className="group flex items-start gap-4 p-3.5 hover:bg-slate-50 rounded-xl transition-all border border-transparent hover:border-slate-100"
    >
      <div className="p-2.5 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl text-blue-600 shadow-sm border border-blue-100/50">
        <Icon className="w-5 h-5" />
      </div>
      <div className="flex-1">
        <p className="text-xs text-slate-500 font-medium tracking-wide uppercase">{label}</p>
        <p className="text-slate-900 font-semibold text-[15px] mt-1">{value || "-"}</p>
      </div>
      {value && (
        <button 
          onClick={() => handleCopy(value, id)}
          className="p-2 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors opacity-0 group-hover:opacity-100"
          title="คัดลอกข้อมูล"
        >
          {copiedField === id ? <Check className="w-4 h-4 text-emerald-500" /> : <Copy className="w-4 h-4" />}
        </button>
      )}
    </motion.div>
  );

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}
      className="w-full max-w-md bg-white/80 backdrop-blur-xl border border-white/40 shadow-[0_8px_30px_rgb(0,0,0,0.04)] rounded-[2rem] p-7 overflow-hidden relative"
    >
      {/* Decorative background element */}
      <div className="absolute top-0 right-0 -mt-10 -mr-10 w-40 h-40 bg-blue-500/5 rounded-full blur-3xl"></div>

      <div className="flex items-center justify-between mb-6 pb-5 border-b border-slate-100 relative z-10">
        <div className="flex items-center gap-3">
          <div className="w-2.5 h-8 bg-gradient-to-b from-blue-500 to-indigo-600 rounded-full shadow-sm"></div>
          <h2 className="text-xl font-bold text-slate-800 tracking-tight">ข้อมูลบัตรประชาชน</h2>
        </div>
      </div>

      <div className="flex flex-wrap gap-2.5 mb-6 text-xs relative z-10">
        <span className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 font-semibold border ${data.metadata.is_masked ? 'bg-indigo-50 text-indigo-700 border-indigo-100' : 'bg-slate-50 text-slate-600 border-slate-200'}`}>
          <Shield className="w-3.5 h-3.5" />
          {data.metadata.is_masked ? "Masking: ON" : "Masking: OFF"}
        </span>
        <span className="inline-flex items-center gap-1.5 rounded-full bg-slate-50 text-slate-700 px-3 py-1.5 font-semibold border border-slate-200">
          {debug.llm_model === "disabled" ? "LLM: Off" : `LLM: ${debug.llm_model}`}
        </span>
        <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 text-emerald-700 px-3 py-1.5 font-semibold border border-emerald-100">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          {data.metadata.process_time_ms} ms
        </span>
      </div>

      <div className="space-y-1 relative z-10">
        <InfoRow id="id" icon={CreditCard} label="เลขประจำตัวประชาชน" value={data.id_number} />
        <InfoRow id="th" icon={User} label="ชื่อ - นามสกุล (TH)" value={data.name_th} />
        <InfoRow id="en" icon={User} label="Name - Surname (EN)" value={data.name_en} />
        <InfoRow id="dob" icon={Calendar} label="วันเกิด" value={data.dob} />
        <InfoRow id="rel" icon={Heart} label="ศาสนา" value={data.religion} />
        <InfoRow id="addr" icon={MapPin} label="ที่อยู่" value={data.address} />
      </div>
      
      <div className="mt-8 pt-5 border-t border-slate-100 text-[11px] font-medium text-slate-400 flex justify-between relative z-10 uppercase tracking-wider">
        <span>Req: {result.request_id?.slice(0, 8) || "N/A"}</span>
        <span>{timestamp ? new Date(timestamp).toLocaleTimeString() : ""}</span>
      </div>
    </motion.div>
  );
}