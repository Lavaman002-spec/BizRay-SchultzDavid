'use client';

import { useEffect, useRef, useState } from 'react';
import CytoscapeComponent from 'react-cytoscapejs';
import cytoscape from 'cytoscape';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useAuth } from '@/context/AuthContext';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface NetworkGraphProps {
  companyId: number;
}

type TooltipState = {
  visible: boolean;
  label: string;
  type: string;
  position: { x: number; y: number };
};

export default function NetworkGraph({ companyId }: NetworkGraphProps) {
  const { session } = useAuth();
  const [elements, setElements] = useState<object[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tooltip, setTooltip] = useState<TooltipState>({
    visible: false,
    label: '',
    type: '',
    position: { x: 0, y: 0 },
  });
  const containerRef = useRef<HTMLDivElement | null>(null);
  const cyRef = useRef<cytoscape.Core | null>(null);

  useEffect(() => {
    const fetchGraph = async () => {
      if (!session?.access_token) {
        setError('Login required to view network data');
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const res = await fetch(`${API_URL}/api/graph/${companyId}?depth=1`, {
          headers: {
            Authorization: `Bearer ${session.access_token}`,
          },
        });

        if (!res.ok) throw new Error('Failed to fetch graph data');

        const data = await res.json();
        setElements(data.elements);
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : 'Unknown error';
        setError(message);
      } finally {
        setLoading(false);
      }
    };

    fetchGraph();
  }, [companyId, session]);

  const layout = {
    name: 'cose',
    animate: false,
    nodeDimensionsIncludeLabels: true,
  };

  const style = [
    {
      selector: 'node',
      style: {
        'background-color': 'data(color)',
        label: 'data(label)',
        'text-valign': 'bottom',
        'text-halign': 'center',
        'font-size': '12px',
        width: 40,
        height: 40,
      },
    },
    {
      selector: 'edge',
      style: {
        width: 2,
        'line-color': '#ccc',
        'target-arrow-color': '#ccc',
        'target-arrow-shape': 'triangle',
        'curve-style': 'bezier',
        label: 'data(label)',
        'font-size': '10px',
        'text-rotation': 'autorotate',
        'text-background-opacity': 1,
        'text-background-color': '#fff',
      },
    },
    {
      selector: 'edge[edge_type = "management"]',
      style: {
        'line-color': '#2563eb',
        'target-arrow-color': '#2563eb',
      },
    },
    {
      selector: 'edge[edge_type = "affiliation"]',
      style: {
        'line-color': '#f97316',
        'target-arrow-color': '#f97316',
        'line-style': 'dashed',
      },
    },
  ];

  if (loading)
    return (
      <div className="h-[400px] flex items-center justify-center">
        Loading graph...
      </div>
    );
  if (error)
    return (
      <div className="h-[400px] flex items-center justify-center text-red-500">
        Error: {error}
      </div>
    );
  if (elements.length === 0)
    return (
      <div className="h-[400px] flex items-center justify-center">
        No graph data available
      </div>
    );

  return (
    <Card className="w-full h-[500px]">
      <CardHeader>
        <CardTitle>Network Visualization</CardTitle>
      </CardHeader>
      <CardContent className="h-[420px]">
        <div ref={containerRef} className="relative w-full h-full">
          <CytoscapeComponent
            elements={elements}
            style={{ width: '100%', height: '100%' }}
            layout={layout}
            stylesheet={style}
            cy={(cy: cytoscape.Core) => {
              if (cyRef.current === cy) return;
              cyRef.current = cy;

              cy.on('tap', 'node', (event: cytoscape.EventObject) => {
                const data = event.target.data();
                const position = event.renderedPosition;
                setTooltip({
                  visible: true,
                  label: data.label ?? 'Unknown',
                  type: data.type ?? 'node',
                  position: { x: position.x, y: position.y },
                });
              });

              cy.on('tap', (event: cytoscape.EventObject) => {
                if (event.target === cy) {
                  setTooltip((prev) => ({ ...prev, visible: false }));
                }
              });
            }}
          />
          {tooltip.visible && (
            <div
              className="absolute bg-white shadow-lg rounded px-3 py-2 text-xs text-gray-800 pointer-events-none"
              style={{
                left: tooltip.position.x,
                top: tooltip.position.y - 30,
                transform: 'translate(-50%, -100%)',
              }}
            >
              <p className="font-semibold">{tooltip.label}</p>
              <p className="text-gray-500 capitalize">{tooltip.type}</p>
            </div>
          )}
        </div>
        <div className="flex flex-wrap gap-4 mt-2 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#2563eb]" />
            <span>Company</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#16a34a]" />
            <span>Person</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-8 border-t-2 border-[#2563eb]" />
            <span>Management Link</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-8 border-t-2 border-dashed border-[#f97316]" />
            <span>Shared Officer Link</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
