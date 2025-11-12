"use client";

import type { NetworkStats as NetworkStatsType } from "./types";

interface NetworkStatsProps {
  stats: NetworkStatsType;
}

export default function NetworkStats({ stats }: NetworkStatsProps) {
  return (
    <div className="grid grid-cols-3 gap-4">
      {/* Total Nodes */}
      <div className="bg-white border border-gray-200 rounded-2xl p-5">
        <p className="text-sm text-gray-600 mb-1">Total Nodes</p>
        <p className="text-2xl font-semibold text-gray-900">{stats.totalNodes}</p>
      </div>

      {/* Connections */}
      <div className="bg-white border border-gray-200 rounded-2xl p-5">
        <p className="text-sm text-gray-600 mb-1">Connections</p>
        <p className="text-2xl font-semibold text-gray-900">{stats.connections}</p>
      </div>

      {/* Average Risk */}
      <div className="bg-white border border-gray-200 rounded-2xl p-5">
        <p className="text-sm text-gray-600 mb-1">Average Risk</p>
        <p className="text-2xl font-semibold text-gray-900">{stats.averageRisk}</p>
      </div>
    </div>
  );
}
