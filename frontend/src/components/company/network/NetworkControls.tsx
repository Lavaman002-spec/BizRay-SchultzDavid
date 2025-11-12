"use client";

import { ZoomIn, ZoomOut, Maximize2, Minimize2 } from "lucide-react";
import { Button } from "@/components/ui/button";

interface NetworkControlsProps {
  onZoomIn: () => void;
  onZoomOut: () => void;
  onResetZoom: () => void;
  onToggleFullscreen: () => void;
  isFullscreen: boolean;
}

export default function NetworkControls({
  onZoomIn,
  onZoomOut,
  onResetZoom,
  onToggleFullscreen,
  isFullscreen
}: NetworkControlsProps) {
  return (
    <div className="absolute right-3 top-4 flex flex-col gap-2">
      <Button
        variant="outline"
        size="icon"
        onClick={onZoomIn}
        className="bg-white shadow-lg hover:bg-gray-50 w-9 h-9 rounded-lg"
        title="Zoom in"
      >
        <ZoomIn className="w-5 h-5" />
      </Button>

      <Button
        variant="outline"
        size="icon"
        onClick={onZoomOut}
        className="bg-white shadow-lg hover:bg-gray-50 w-9 h-9 rounded-lg"
        title="Zoom out"
      >
        <ZoomOut className="w-5 h-5" />
      </Button>

      <Button
        variant="outline"
        size="icon"
        onClick={onResetZoom}
        className="bg-white shadow-lg hover:bg-gray-50 w-9 h-9 rounded-lg"
        title="Reset zoom"
      >
        <Maximize2 className="w-4 h-4" />
      </Button>
    </div>
  );
}
