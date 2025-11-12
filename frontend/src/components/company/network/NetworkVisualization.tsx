"use client";

import { useState, useMemo } from "react";
import { Filter, Maximize2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import NetworkCanvas from "./NetworkCanvas";
import NetworkFilters from "./NetworkFilters";
import NetworkStats from "./NetworkStats";
import NetworkLegend from "./NetworkLegend";
import NetworkControls from "./NetworkControls";
import type { CompanyWithDetails } from "@/types/company";
import type { NetworkFilters as NetworkFiltersType, NetworkData, NetworkNode, NetworkEdge } from "./types";

interface NetworkVisualizationProps {
  company: CompanyWithDetails;
}

// Generate sample network data from company details
function generateNetworkData(company: CompanyWithDetails): NetworkData {
  const nodes: NetworkNode[] = [];
  const edges: NetworkEdge[] = [];

  // Center node (the company)
  nodes.push({
    id: 'center',
    label: company.name,
    type: 'company',
    x: 450,
    y: 300,
    riskScore: 31
  });

  // Add officers as person nodes in a circle
  const officers = company.officers || [];
  const radius = 180;
  officers.slice(0, 5).forEach((officer, index) => {
    const angle = (index / Math.min(officers.length, 5)) * 2 * Math.PI - Math.PI / 2;
    const x = 450 + radius * Math.cos(angle);
    const y = 300 + radius * Math.sin(angle);

    const nodeId = `officer-${officer.id}`;
    nodes.push({
      id: nodeId,
      label: officer.full_name || `${officer.first_name || ''} ${officer.last_name || ''}`.trim() || 'Officer',
      type: 'person',
      x,
      y,
      riskScore: 25 + Math.random() * 50
    });

    // Add edge from person to company (management)
    edges.push({
      id: `edge-${nodeId}`,
      source: nodeId,
      target: 'center',
      type: 'management'
    });
  });

  // Add a related company if there are officers
  if (officers.length > 0) {
    const relatedId = 'related-1';
    nodes.push({
      id: relatedId,
      label: 'Beta Ventures GmbH',
      type: 'company',
      x: 200,
      y: 150,
      riskScore: 45
    });

    edges.push({
      id: `edge-${relatedId}`,
      source: relatedId,
      target: 'center',
      type: 'ownership',
      percentage: '30%'
    });

    // Connect a person to the related company
    if (nodes.length > 2) {
      edges.push({
        id: `edge-${relatedId}-person`,
        source: nodes[1].id,
        target: relatedId,
        type: 'management'
      });
    }
  }

  const stats = {
    totalNodes: nodes.length,
    connections: edges.length,
    averageRisk: Math.round(
      nodes.reduce((sum, node) => sum + (node.riskScore || 0), 0) / nodes.length
    )
  };

  return { nodes, edges, stats };
}

export default function NetworkVisualization({ company }: NetworkVisualizationProps) {
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<NetworkFiltersType>({
    connectionTypes: {
      ownership: true,
      management: true
    },
    hopDistance: 2,
    riskLevels: {
      low: true,
      medium: true,
      high: true
    }
  });

  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Generate network data
  const networkData = useMemo(() => generateNetworkData(company), [company]);

  // Filter nodes and edges based on filters
  const filteredData = useMemo(() => {
    let nodes = networkData.nodes;
    let edges = networkData.edges;

    // Filter by connection type
    edges = edges.filter((edge) => {
      if (edge.type === 'ownership' && !filters.connectionTypes.ownership) return false;
      if (edge.type === 'management' && !filters.connectionTypes.management) return false;
      return true;
    });

    // Filter by risk level
    nodes = nodes.filter((node) => {
      if (!node.riskScore) return true;
      const score = node.riskScore;
      if (score < 30 && !filters.riskLevels.low) return false;
      if (score >= 30 && score < 70 && !filters.riskLevels.medium) return false;
      if (score >= 70 && !filters.riskLevels.high) return false;
      return true;
    });

    // Filter edges to only include those with both nodes visible
    const nodeIds = new Set(nodes.map((n) => n.id));
    edges = edges.filter((e) => nodeIds.has(e.source) && nodeIds.has(e.target));

    return { nodes, edges };
  }, [networkData, filters]);

  const handleZoomIn = () => setZoom((z) => Math.min(z + 0.2, 2));
  const handleZoomOut = () => setZoom((z) => Math.max(z - 0.2, 0.5));
  const handleResetZoom = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };

  return (
    <div className="space-y-6">
      {/* Main visualization card */}
      <div className="bg-white border border-gray-200 rounded-2xl overflow-hidden">
        {/* Header */}
        <div className="border-b border-gray-200 px-4 py-4 flex items-center justify-between">
          <h3 className="text-base font-semibold text-gray-900">Network Visualization</h3>

          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowFilters(!showFilters)}
              className="text-sm"
            >
              <Filter className="w-4 h-4 mr-2" />
              Filters
            </Button>

            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsFullscreen(!isFullscreen)}
              className="text-sm"
            >
              <Maximize2 className="w-4 h-4 mr-2" />
              Fullscreen
            </Button>
          </div>
        </div>

        {/* Canvas with overlay */}
        <div className="relative">
          {showFilters && (
            <div className="absolute right-3 top-3 z-20">
              <NetworkFilters filters={filters} onChange={setFilters} />
            </div>
          )}

          <NetworkCanvas
            nodes={filteredData.nodes}
            edges={filteredData.edges}
            zoom={zoom}
            panX={pan.x}
            panY={pan.y}
          />

          <NetworkLegend />

          <NetworkControls
            onZoomIn={handleZoomIn}
            onZoomOut={handleZoomOut}
            onResetZoom={handleResetZoom}
            onToggleFullscreen={() => setIsFullscreen(!isFullscreen)}
            isFullscreen={isFullscreen}
          />
        </div>
      </div>

      {/* Stats */}
      <NetworkStats stats={networkData.stats} />
    </div>
  );
}
