export interface AgentNode {
    id: string;
    name: string;
    parent: string | null;
    last_thought?: string;
    status?: "active" | "inactive";
}

export interface AgentEdge {
    source: string;
    target: string;
    label: string;
    timestamp?: string;
}

export interface AgentGraphData {
    nodes: AgentNode[];
    edges: AgentEdge[];
}
