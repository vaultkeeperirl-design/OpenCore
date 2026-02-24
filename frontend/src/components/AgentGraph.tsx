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

// Helper to create a node object
const createNode = (data: AgentNode, x: number, y: number): Node => {
    const isManager = data.id === "Manager";
    return {
        id: data.id,
        position: { x, y },
        data: {
            label: isManager ? (
                <div className="flex flex-col items-center justify-center gap-2 pointer-events-none w-full h-full">
                    <div className="flex items-center justify-center gap-2">
                        <img src="/logo.svg" className="w-8 h-8 drop-shadow-[0_0_10px_#ff00ff]" alt="" />
                        <span>MANAGER</span>
                    </div>
                    {data.last_thought && data.last_thought !== "Idle" && (
                        <div className="text-[10px] text-fuchsia-200/70 font-mono mt-1 w-full truncate px-2 border-t border-fuchsia-500/30 pt-1">
                            {data.last_thought}
                        </div>
                    )}
                </div>
            ) : (
                <div className="flex flex-col items-center w-full h-full">
                    <div className="font-bold mb-1">{data.name}</div>
                    {data.last_thought && data.last_thought !== "Idle" && (
                         <div className="text-[10px] text-cyan-200/70 font-mono w-full truncate border-t border-cyan-500/30 pt-1 px-1">
                            {data.last_thought}
                        </div>
                    )}
                </div>
            )
        },
        style: isManager ? {
            background: 'rgba(188, 19, 254, 0.1)',
            color: '#bc13fe',
            border: '1px solid #bc13fe',
            boxShadow: '0 0 30px rgba(188, 19, 254, 0.2)',
            borderRadius: '12px',
            padding: '16px',
            width: 220,
            textAlign: 'center',
            fontFamily: 'var(--font-orbitron)',
            fontSize: '14px',
            fontWeight: 'bold',
            backdropFilter: 'blur(10px)',
            textTransform: 'uppercase',
            letterSpacing: '1px'
        } : {
            background: 'rgba(5, 5, 16, 0.8)',
            color: '#00f3ff',
            border: '1px solid #00f3ff',
            boxShadow: '0 0 15px rgba(0, 243, 255, 0.15)',
            borderRadius: '8px',
            padding: '12px',
            width: 180,
            textAlign: 'center',
            fontFamily: 'var(--font-share-tech-mono)',
            fontSize: '12px',
            backdropFilter: 'blur(5px)'
        },
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

    // Ensure Manager is treated as root if it exists
    const manager = nodesData.find(n => n.id === "Manager");
    if (manager && !roots.includes("Manager")) {
         // If manager is somewhere in the list but not detected as root (e.g. if parent is null)
         // But logic above handles null parent.
         // What if Manager has a parent? Unlikely.
    }

    // Sort roots: Manager first
    roots.sort((a, b) => (a === "Manager" ? -1 : b === "Manager" ? 1 : a.localeCompare(b)));

    const layoutNodes: Node[] = [];
    const LEVEL_HEIGHT = 150;
    const SIBLING_SPACING = 220; // Increased for wider nodes

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

    // Calculate Positions
    // For a better tree look, we should center children under parents.
    // But simple level-based is safer for arbitrary graph changes.
    // Let's stick to level-based centering for now.

    Object.keys(nodesByLevel).forEach(lvlStr => {
        const lvl = parseInt(lvlStr);
        const nodesInLevel = nodesByLevel[lvl];
        // Sort nodes in level to keep siblings together if possible?
        // Sorting by parent ID helps
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

    // Maintain node positions if they exist? No, we force layout updates on data change.
    // React Flow might animate if we just update the props.
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
