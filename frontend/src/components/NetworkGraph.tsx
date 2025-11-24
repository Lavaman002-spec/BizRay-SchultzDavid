'use client';

import { useEffect, useState } from 'react';
import CytoscapeComponent from 'react-cytoscapejs';
import cytoscape from 'cytoscape';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useAuth } from '@/context/AuthContext';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface NetworkGraphProps {
    companyId: number;
}

export default function NetworkGraph({ companyId }: NetworkGraphProps) {
    const { session } = useAuth();
    const [elements, setElements] = useState<object[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchGraph = async () => {
            if (!session?.access_token) return;

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
    ];

    if (loading) return <div className="h-[400px] flex items-center justify-center">Loading graph...</div>;
    if (error) return <div className="h-[400px] flex items-center justify-center text-red-500">Error: {error}</div>;
    if (elements.length === 0) return <div className="h-[400px] flex items-center justify-center">No graph data available</div>;

    return (
        <Card className="w-full h-[500px]">
            <CardHeader>
                <CardTitle>Network Visualization</CardTitle>
            </CardHeader>
            <CardContent className="h-[450px]">
                <CytoscapeComponent
                    elements={elements}
                    style={{ width: '100%', height: '100%' }}
                    layout={layout}
                    stylesheet={style}
                    cy={(cy: cytoscape.Core) => {
                        cy.on('tap', 'node', (event: cytoscape.EventObject) => {
                            console.log(event.target.data());
                        });
                    }}
                />
                <div className="flex gap-4 mt-2 text-sm">
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-[#2563eb]" />
                        <span>Company</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-[#16a34a]" />
                        <span>Person</span>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
