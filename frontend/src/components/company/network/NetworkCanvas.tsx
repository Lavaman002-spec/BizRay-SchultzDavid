"use client";

import { useRef, useEffect, useState } from "react";
import { Building2, User } from "lucide-react";
import type { NetworkNode, NetworkEdge } from "./types";

interface NetworkCanvasProps {
  nodes: NetworkNode[];
  edges: NetworkEdge[];
  width?: number;
  height?: number;
  zoom?: number;
  panX?: number;
  panY?: number;
}

export default function NetworkCanvas({
  nodes,
  edges,
  width = 900,
  height = 600,
  zoom = 1,
  panX = 0,
  panY = 0
}: NetworkCanvasProps) {
  const canvasRef = useRef<HTMLDivElement>(null);
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);

  // Get node color based on type
  const getNodeColor = (node: NetworkNode) => {
    if (node.type === 'company') {
      return {
        bg: 'bg-emerald-500',
        border: 'border-emerald-600',
        icon: Building2
      };
    }
    return {
      bg: 'bg-blue-500',
      border: 'border-blue-600',
      icon: User
    };
  };

  // Get edge color based on type
  const getEdgeColor = (edge: NetworkEdge) => {
    return edge.type === 'ownership' ? '#375dfb' : '#9ca3af';
  };

  return (
    <div
      ref={canvasRef}
      className="relative bg-gray-50 rounded-2xl overflow-hidden"
      style={{ width, height }}
    >
      {/* SVG for edges */}
      <svg
        className="absolute inset-0 pointer-events-none"
        width={width}
        height={height}
        style={{
          transform: `translate(${panX}px, ${panY}px) scale(${zoom})`,
          transformOrigin: 'center'
        }}
      >
        <defs>
          <marker
            id="arrowhead"
            markerWidth="10"
            markerHeight="10"
            refX="9"
            refY="3"
            orient="auto"
          >
            <polygon points="0 0, 10 3, 0 6" fill="#375dfb" />
          </marker>
        </defs>
        {edges.map((edge) => {
          const sourceNode = nodes.find((n) => n.id === edge.source);
          const targetNode = nodes.find((n) => n.id === edge.target);
          if (!sourceNode || !targetNode) return null;

          return (
            <g key={edge.id}>
              <line
                x1={sourceNode.x}
                y1={sourceNode.y}
                x2={targetNode.x}
                y2={targetNode.y}
                stroke={getEdgeColor(edge)}
                strokeWidth="2"
                markerEnd={edge.type === 'ownership' ? "url(#arrowhead)" : undefined}
              />
              {edge.percentage && (
                <text
                  x={(sourceNode.x + targetNode.x) / 2}
                  y={(sourceNode.y + targetNode.y) / 2 - 10}
                  fill="#374151"
                  fontSize="12"
                  textAnchor="middle"
                  className="pointer-events-none"
                >
                  {edge.percentage}
                </text>
              )}
            </g>
          );
        })}
      </svg>

      {/* Nodes */}
      <div className="absolute inset-0">
        {nodes.map((node) => {
          const { bg, border, icon: Icon } = getNodeColor(node);
          const isHovered = hoveredNode === node.id;
          const isCenterNode = node.type === 'company' && node.id === 'center';

          return (
            <div
              key={node.id}
              className={`absolute cursor-pointer transition-all ${
                isHovered ? 'z-10' : 'z-0'
              }`}
              style={{
                left: node.x,
                top: node.y,
                transform: `translate(-50%, -50%) translate(${panX}px, ${panY}px) scale(${zoom})`,
                transformOrigin: 'center'
              }}
              onMouseEnter={() => setHoveredNode(node.id)}
              onMouseLeave={() => setHoveredNode(null)}
              title={node.label}
            >
              <div
                className={`rounded-full ${bg} ${border} border-2 flex items-center justify-center shadow-md ${
                  isHovered ? 'scale-110' : ''
                } transition-transform`}
                style={{
                  width: isCenterNode ? 56 : 44,
                  height: isCenterNode ? 56 : 44
                }}
              >
                <Icon className={`text-white ${isCenterNode ? 'w-7 h-7' : 'w-5 h-5'}`} />
              </div>

              {/* Label */}
              {(isHovered || isCenterNode) && (
                <div className="absolute top-full mt-2 left-1/2 -translate-x-1/2 bg-white px-2 py-1 rounded shadow-lg text-xs whitespace-nowrap">
                  {node.label}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
