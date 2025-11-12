"use client";

import React from "react";

interface RiskScoreGaugeProps {
  score: number; // 0-100
  size?: number; // px
}

// Radial gauge using CSS conic-gradient
export default function RiskScoreGauge({ score, size = 120 }: RiskScoreGaugeProps) {
  const clamped = Math.max(0, Math.min(100, score));

  // Color from green -> amber -> red
  const hue = 120 - (clamped * 120) / 100; // 120 (green) to 0 (red)
  const color = `hsl(${hue} 70% 45%)`;

  const thickness = 12;
  const bgTrack = "#e5e7eb"; // gray-200

  return (
    <div
      className="relative"
      style={{ width: size, height: size }}
      aria-label={`Risk score ${clamped}`}
    >
      <div
        className="rounded-full"
        style={{
          width: size,
          height: size,
          background: `conic-gradient(${color} ${clamped * 3.6}deg, ${bgTrack} 0deg)`,
          mask: `radial-gradient(circle at center, transparent calc(50% - ${thickness}px), black calc(50% - ${thickness - 1}px))`,
          WebkitMask: `radial-gradient(circle at center, transparent calc(50% - ${thickness}px), black calc(50% - ${thickness - 1}px))`,
        }}
      />
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="text-center">
          <div className="text-2xl font-semibold text-gray-900">{clamped}</div>
          <div className="text-xs text-gray-500">Score</div>
        </div>
      </div>
    </div>
  );
}

