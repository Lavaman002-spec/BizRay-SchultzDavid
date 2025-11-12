export type NodeType = 'company' | 'person';
export type EdgeType = 'ownership' | 'management';
export type RiskLevel = 'low' | 'medium' | 'high';

export interface NetworkNode {
  id: string;
  label: string;
  type: NodeType;
  x: number;
  y: number;
  riskScore?: number;
}

export interface NetworkEdge {
  id: string;
  source: string;
  target: string;
  type: EdgeType;
  percentage?: string;
}

export interface NetworkFilters {
  connectionTypes: {
    ownership: boolean;
    management: boolean;
  };
  hopDistance: number;
  riskLevels: {
    low: boolean;
    medium: boolean;
    high: boolean;
  };
}

export interface NetworkStats {
  totalNodes: number;
  connections: number;
  averageRisk: number;
}

export interface NetworkData {
  nodes: NetworkNode[];
  edges: NetworkEdge[];
  stats: NetworkStats;
}
