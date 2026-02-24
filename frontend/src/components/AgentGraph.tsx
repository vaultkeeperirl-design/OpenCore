"use client";

import { useEffect } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  useNodesState,
  useEdgesState,
  MarkerType,
  Node,
  Edge,
  Position
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { AgentGraphData, AgentNode } from "@/types/agent";
import { Users, Bot } from "lucide-react";

// Helper to create a node object
const createNode = (data: AgentNode, x: number, y: number): Node => {
    const isManager = data.id === "Manager";
    const isTeamLead = data.parent === "Manager";

    // Define styles based on role
    let nodeStyle = {};
    let iconElement = null;
    let borderColor = "";
    let textColor = "";

    if (isManager) {
        borderColor = "#bc13fe";
        textColor = "#bc13fe";
        nodeStyle = {
            background: 'rgba(188, 19, 254, 0.08)',
            color: textColor,
            border: `1px solid ${borderColor}`,
            boxShadow: `0 0 30px rgba(188, 19, 254, 0.2)`,
            borderRadius: '12px',
            padding: '16px',
            width: 240,
            textAlign: 'center' as const,
            fontFamily: 'var(--font-orbitron)',
            fontSize: '14px',
            fontWeight: 'bold',
            backdropFilter: 'blur(10px)',
            textTransform: 'uppercase' as const,
            letterSpacing: '1px'
        };
        iconElement = <img src="/logo.svg" className="w-8 h-8 drop-shadow-[0_0_10px_#ff00ff]" alt="" />;
    } else if (isTeamLead) {
        borderColor = "#00f3ff"; // Cyan for Team Lead
        textColor = "#00f3ff";
        nodeStyle = {
            background: 'rgba(0, 243, 255, 0.08)',
            color: textColor,
            border: `1px solid ${borderColor}`,
            boxShadow: `0 0 20px rgba(0, 243, 255, 0.2)`,
            borderRadius: '12px',
            padding: '14px',
            width: 220,
            textAlign: 'center' as const,
            fontFamily: 'var(--font-orbitron)',
            fontSize: '12px',
            fontWeight: 'bold',
            backdropFilter: 'blur(8px)',
            textTransform: 'uppercase' as const,
            letterSpacing: '0.5px'
        };
        iconElement = <Users className="w-6 h-6 text-cyan-400 drop-shadow-[0_0_8px_rgba(0,243,255,0.8)]" />;
    } else {
        // Worker
        borderColor = "#22c55e"; // Green for Worker
        textColor = "#4ade80";
        nodeStyle = {
            background: 'rgba(34, 197, 94, 0.08)',
            color: textColor,
            border: `1px solid ${borderColor}`,
            boxShadow: `0 0 15px rgba(34, 197, 94, 0.15)`,
            borderRadius: '10px',
            padding: '12px',
            width: 200,
            textAlign: 'center' as const,
            fontFamily: 'var(--font-share-tech-mono)',
            fontSize: '12px',
            fontWeight: 'normal',
            backdropFilter: 'blur(5px)',
            textTransform: 'none' as const
        };
        iconElement = <Bot className="w-5 h-5 text-green-400 drop-shadow-[0_0_5px_rgba(34,197,94,0.8)]" />;
    }

    return {
        id: data.id,
        position: { x, y },
        data: {
            label: (
                <div className="flex flex-col items-center justify-center gap-2 pointer-events-none w-full h-full">
                    <div className="flex items-center justify-center gap-2 w-full">
                        {iconElement}
                        <span className="truncate max-w-[150px]" title={data.name}>
                            {data.name.replace(/_/g, ' ')}
                        </span>
                    </div>
                    {data.last_thought && data.last_thought !== "Idle" && (
                        <div
                            className="text-[10px] font-mono mt-1 w-full truncate px-2 border-t pt-2 opacity-80"
                            style={{
                                borderColor: `${borderColor}40`,
                                color: isManager ? '#f5d0fe' : (isTeamLead ? '#cffafe' : '#dcfce7')
                            }}
                        >
                            {data.last_thought}
                        </div>
                    )}
                </div>
            )
        },
        style: nodeStyle,
        type: 'default',
        sourcePosition: Position.Bottom,
        targetPosition: Position.Top,
    };
};

// Helper to calculate tree layout
const getLayout = (nodesData: AgentNode[]): Node[] => {
    if (!nodesData.length) return [];

    const parentMap: Record<string, string[]> = {};
    const roots: string[] = [];

    // Build hierarchy map
    nodesData.forEach(node => {
        if (!node.parent || !nodesData.find(n => n.id === node.parent)) {
            // Check if node is Manager, force it to be root if present
            if (node.id === "Manager" || !node.parent) {
                if (!roots.includes(node.id)) roots.push(node.id);
            }
        } else {
            if (!parentMap[node.parent]) parentMap[node.parent] = [];
            parentMap[node.parent].push(node.id);
        }
    });

    // Sort roots: Manager first
    roots.sort((a, b) => (a === "Manager" ? -1 : b === "Manager" ? 1 : a.localeCompare(b)));

    const layoutNodes: Node[] = [];
    const LEVEL_HEIGHT = 150;
    const SIBLING_SPACING = 240; // Increased spacing for larger nodes

    // Assign Levels
    const levels: Record<string, number> = {};
    const assignLevel = (id: string, lvl: number) => {
        levels[id] = lvl;
        (parentMap[id] || []).forEach(child => assignLevel(child, lvl + 1));
    };
    roots.forEach(root => assignLevel(root, 0));

    // Group by Level
    const nodesByLevel: Record<number, string[]> = {};
    nodesData.forEach(n => {
        const lvl = levels[n.id] ?? 0;
        if (!nodesByLevel[lvl]) nodesByLevel[lvl] = [];
        nodesByLevel[lvl].push(n.id);
    });

    Object.keys(nodesByLevel).forEach(lvlStr => {
        const lvl = parseInt(lvlStr);
        const nodesInLevel = nodesByLevel[lvl];
        // Sort nodes in level
        nodesInLevel.sort((a, b) => {
             const pA = nodesData.find(n => n.id === a)?.parent || "";
             const pB = nodesData.find(n => n.id === b)?.parent || "";
             return pA.localeCompare(pB) || a.localeCompare(b);
        });

        const totalWidth = nodesInLevel.length * SIBLING_SPACING;
        const startX = 400 - (totalWidth / 2) + (SIBLING_SPACING / 2); // Center around 400

        nodesInLevel.forEach((nodeId, index) => {
             const x = startX + (index * SIBLING_SPACING);
             const y = 50 + (lvl * LEVEL_HEIGHT);
             layoutNodes.push(createNode(nodesData.find(n => n.id === nodeId)!, x, y));
        });
    });

    return layoutNodes;
};

export default function AgentGraph({ graphData }: { graphData: AgentGraphData }) {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  useEffect(() => {
    if (!graphData?.nodes) return;

    // 1. Generate Nodes
    const newNodes = getLayout(graphData.nodes);
    setNodes(newNodes);

    // 2. Generate Edges
    const newEdges: Edge[] = [];

    // Structural Edges
    graphData.nodes.forEach(node => {
        if (node.parent && graphData.nodes.find(n => n.id === node.parent)) {
            newEdges.push({
                id: `struct-${node.parent}-${node.id}`,
                source: node.parent,
                target: node.id,
                animated: false,
                style: { stroke: '#333', strokeWidth: 1, strokeDasharray: '5,5' },
                type: 'straight', // Straight or smoothstep
                markerEnd: { type: MarkerType.ArrowClosed, color: '#333' },
            });
        }
    });

    // Interaction Edges
    if (graphData.edges) {
        graphData.edges.forEach((edge, i) => {
             newEdges.push({
                id: `interact-${edge.source}-${edge.target}-${i}`,
                source: edge.source,
                target: edge.target,
                animated: true,
                label: edge.label,
                labelStyle: { fill: '#00ffff', fontSize: 10, fontFamily: 'monospace', fontWeight: 'bold' },
                labelBgStyle: { fill: '#000', fillOpacity: 0.8, rx: 4, ry: 4 },
                labelBgPadding: [4, 2],
                style: { stroke: '#00ffff', strokeWidth: 2 },
                type: 'default',
                markerEnd: { type: MarkerType.ArrowClosed, color: '#00ffff' },
             });
        });
    }

    setEdges(newEdges);

  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [JSON.stringify(graphData), setNodes, setEdges]);

  return (
    <div className="w-full h-full bg-[#050510] relative overflow-hidden">
      {/* Grid Overlay */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(0,243,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(0,243,255,0.03)_1px,transparent_1px)] bg-[size:40px_40px] pointer-events-none" />

      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
        attributionPosition="bottom-right"
        className="transition-opacity duration-500"
      >
        <Background color="#1a1a2e" gap={40} size={1} />
        <Controls className="bg-black/50 border border-white/10 text-white fill-white" />
      </ReactFlow>

      <div className="absolute top-4 left-4 pointer-events-none z-10">
         <h3 className="text-xs font-orbitron text-cyan-500/50 tracking-[0.2em] uppercase border-b border-cyan-500/20 pb-1">Neural Network Topology</h3>
      </div>
    </div>
  );
}
