"use client";

import { useState, useEffect, useCallback } from "react";

const LS_KEY = "meshy_ab_variant";

type Variant = "experiment" | "control";

const TITLES: Record<Variant, string> = {
  experiment: "Write like a pro with AI",
  control: "AI helps you write better",
};

const SUBTITLES: Record<Variant, string> = {
  experiment:
    "Unlock AI-powered writing that adapts to your unique voice and style.",
  control:
    "Discover how AI can help you craft clearer, more compelling content.",
};

const API_BASE = "http://localhost:8080";

async function trackEvent(name: string, payload?: Record<string, unknown>) {
  console.log("[Event]", name, payload);
  try {
    await fetch(`${API_BASE}/api/track`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ event: name, ...payload }),
    });
  } catch (err) {
    console.warn("[Event] failed to send", err);
  }
}

export default function Home() {
  const [variant, setVariant] = useState<Variant | null>(null);

  useEffect(() => {
    const stored = localStorage.getItem(LS_KEY);
    if (stored === "experiment" || stored === "control") {
      setVariant(stored);
    } else {
      const assigned: Variant = Math.random() < 0.5 ? "experiment" : "control";
      localStorage.setItem(LS_KEY, assigned);
      setVariant(assigned);
    }
  }, []);

  const handleCtaClick = useCallback(() => {
    trackEvent("cta_clicked", { variant });
  }, [variant]);

  return (
    <div className="flex min-h-screen flex-col bg-gradient-to-br from-slate-50 via-white to-blue-50">
      <header className="flex items-center justify-between px-6 py-5 sm:px-12 lg:px-24">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600 text-sm font-bold text-white">
            M
          </div>
          <span className="text-lg font-semibold text-slate-900">
            Meshy Copy
          </span>
        </div>
      </header>

      <main className="flex flex-1 flex-col items-center justify-center px-6 text-center sm:px-12 lg:px-24">
        <div className="mx-auto max-w-3xl">
          <h1 className="text-4xl font-bold leading-tight tracking-tight text-slate-900 sm:text-5xl lg:text-6xl">
            {variant ? TITLES[variant] : ""}
          </h1>

          <p className="mt-6 text-lg leading-relaxed text-slate-600 sm:text-xl">
            {variant ? SUBTITLES[variant] : ""}
          </p>

          <div className="mt-10 flex items-center justify-center gap-4">
            <button
              onClick={handleCtaClick}
              className="rounded-xl bg-blue-600 px-8 py-4 text-base font-semibold text-white shadow-lg shadow-blue-200 transition-all hover:bg-blue-700 hover:shadow-xl hover:shadow-blue-300 active:scale-[0.97]"
            >
              Start for Free
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
