"use client";

import { Building2, User } from "lucide-react";

export default function NetworkLegend() {
  return (
    <div className="absolute left-4 bottom-4 bg-white rounded-lg shadow-lg p-4 w-[136px]">
      <p className="text-sm font-semibold text-gray-900 mb-3">Legend</p>

      <div className="space-y-2.5">
        {/* Company */}
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded-full bg-emerald-500 flex items-center justify-center">
            <Building2 className="w-2.5 h-2.5 text-white" />
          </div>
          <span className="text-sm text-gray-700">Company</span>
        </div>

        {/* Person */}
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded-full bg-blue-500 flex items-center justify-center">
            <User className="w-2.5 h-2.5 text-white" />
          </div>
          <span className="text-sm text-gray-700">Person</span>
        </div>

        {/* Ownership */}
        <div className="flex items-center gap-2">
          <div className="w-3 h-0.5 bg-blue-600" />
          <span className="text-sm text-gray-700">Ownership</span>
        </div>

        {/* Management */}
        <div className="flex items-center gap-2">
          <div className="w-3 h-0.5 bg-gray-400" />
          <span className="text-sm text-gray-700">Management</span>
        </div>
      </div>
    </div>
  );
}
