"use client";

import { useEffect, useState } from "react";
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
import Image from "next/image";

// Helper to create a node object
const createNode = (data: AgentNode, x: number, y: number): Node => {
    const isManager = data.id === "Manager";
    const isTeamLead = data.parent === "Manager";

    let className = "";
    let iconElement = null;
    let borderColor = ""; // retained for last_thought inline style

    if (isManager) {
        borderColor = "var(--accent-2)";
        className = "bg-accent-2/10 border border-accent-2 text-accent-2 shadow-[0_0_30px_color-mix(in_srgb,var(--accent-2),transparent_80%)] rounded-xl p-4 w-[240px] text-center font-orbitron text-sm font-bold backdrop-blur-md uppercase tracking-wider";
        iconElement = <Image src="/logo.svg" width={32} height={32} className="w-8 h-8 drop-shadow-[0_0_10px_var(--accent-2)]" alt="" />;
    } else if (isTeamLead) {
        borderColor = "var(--accent-1)";
        className = "bg-accent-1/10 border border-accent-1 text-accent-1 shadow-[0_0_20px_color-mix(in_srgb,var(--accent-1),transparent_80%)] rounded-xl p-3.5 w-[220px] text-center font-orbitron text-xs font-bold backdrop-blur-sm uppercase tracking-wide";
        iconElement = <Users className="w-6 h-6 text-accent-1 drop-shadow-[0_0_8px_var(--accent-1)]" />;
    } else {
        // Worker
        borderColor = "var(--accent-3)";
        className = "bg-accent-3/10 border border-accent-3 text-accent-3 shadow-[0_0_15px_color-mix(in_srgb,var(--accent-3),transparent_85%)] rounded-lg p-3 w-[200px] text-center font-mono text-xs font-normal backdrop-blur-sm";
        iconElement = <Bot className="w-5 h-5 text-accent-3 drop-shadow-[0_0_5px_var(--accent-3)]" />;
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
                                borderColor: `${borderColor}`, // Ideally color-mix but simple var works for border color
                                // We need to match the text color slightly lighter.
                                // Since we are using vars, we can just inherit or use specific mix
                                color: 'currentColor'
                            }}
                        >
                            {data.last_thought}
                        </div>
                    )}
                </div>
            )
        },
        className: className,
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
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const [now, setNow] = useState(Date.now());

  // Update time every second to prune old interactions
  useEffect(() => {
    const interval = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (!graphData?.nodes) return;

    // 1. Generate Nodes
    const newNodes = getLayout(graphData.nodes);
    setNodes(newNodes);

    // 2. Generate Edges
    const newEdges: Edge[] = [];

    // Structural Edges (Parent -> Child)
    graphData.nodes.forEach(node => {
        if (node.parent && graphData.nodes.find(n => n.id === node.parent)) {
            newEdges.push({
                id: `struct-${node.parent}-${node.id}`,
                source: node.parent,
                target: node.id,
                animated: false,
                style: { stroke: '#333', strokeWidth: 1, strokeDasharray: '5,5' },
                type: 'straight',
                markerEnd: { type: MarkerType.ArrowClosed, color: '#333' },
            });
        }
    });

    // Sibling/Team Edges (Child <-> Child)
    const nodesByParent: Record<string, AgentNode[]> = {};
    graphData.nodes.forEach(node => {
        if (node.parent) {
             if (!nodesByParent[node.parent]) nodesByParent[node.parent] = [];
             nodesByParent[node.parent].push(node);
        }
    });

    Object.entries(nodesByParent).forEach(([parentId, children]) => {
         if (children.length > 1) {
             // Sort by ID to match layout order (alphabetical usually)
             children.sort((a, b) => a.id.localeCompare(b.id));

             for (let i = 0; i < children.length - 1; i++) {
                 const current = children[i];
                 const next = children[i+1];
                 newEdges.push({
                     id: `sibling-${current.id}-${next.id}`,
                     source: current.id,
                     target: next.id,
                     animated: false,
                     style: {
                         stroke: '#00f3ff',
                         strokeWidth: 2,
                         strokeOpacity: 0.3
                     },
                     type: 'straight',
                     zIndex: -1 // Behind nodes
                 });
             }
         }
    });

    // Interaction Edges (Ephemeral)
    if (graphData.edges) {
        graphData.edges.forEach((edge, i) => {
             // Filter by time: Only show if < 5 seconds old
             if (edge.timestamp) {
                 const edgeTime = new Date(edge.timestamp).getTime();
                 if (now - edgeTime > 5000) return; // Skip old edges
             } else {
                 // Backward compatibility or fallback: don't show if no timestamp?
                 // Or show briefly? Let's assume new backend always sends timestamp.
                 // If no timestamp, maybe it's very old or just created.
                 // Safe to hide to ensure "only when talking".
                 return;
             }

             const isResponse = edge.label.startsWith("Response: ");
             const color = isResponse ? 'var(--text-primary)' : 'var(--accent-1)';

             newEdges.push({
                id: `interact-${edge.source}-${edge.target}-${i}`,
                source: edge.source,
                target: edge.target,
                animated: true,
                label: edge.label,
                labelStyle: { fill: color, fontSize: 10, fontFamily: 'monospace', fontWeight: 'bold' },
                labelBgStyle: { fill: 'var(--bg-primary)', fillOpacity: 0.8, rx: 4, ry: 4 },
                labelBgPadding: [4, 2],
                style: {
                    stroke: color,
                    strokeWidth: 2,
                    strokeDasharray: isResponse ? '5,5' : undefined
                },
                type: 'default',
                markerEnd: { type: MarkerType.ArrowClosed, color: color },
             });
        });
    }

    setEdges(newEdges);

  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [JSON.stringify(graphData), now, setNodes, setEdges]);

  return (
    <div className="w-full h-full bg-bg-primary relative overflow-hidden transition-colors duration-300">
      {/* Grid Overlay */}
      <div className="absolute inset-0 bg-[linear-gradient(color-mix(in_srgb,var(--accent-1),transparent_97%)_1px,transparent_1px),linear-gradient(90deg,color-mix(in_srgb,var(--accent-1),transparent_97%)_1px,transparent_1px)] bg-[size:40px_40px] pointer-events-none" />

      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
        attributionPosition="bottom-right"
        className="transition-opacity duration-500"
      >
        <Background color="var(--border-primary)" gap={40} size={1} style={{ opacity: 0.2 }} />
        <Controls className="bg-bg-secondary/80 border border-border-primary text-text-primary fill-text-primary" />
      </ReactFlow>

      <div className="absolute top-4 left-4 pointer-events-none z-10">
         <h3 className="text-xs font-orbitron text-accent-1/50 tracking-[0.2em] uppercase border-b border-accent-1/20 pb-1">Neural Network Topology</h3>
      </div>
    </div>
  );
}
