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
  Edge
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

const initialNodes: Node[] = [];
const initialEdges: Edge[] = [];

export default function AgentGraph({ agents }: { agents: string[] }) {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  useEffect(() => {
    if (!agents.length) return;

    const centerX = 400;
    const centerY = 300;
    const radius = 250;

    // Sort agents so Manager is first
    const sortedAgents = [...agents].sort((a, b) => {
        if (a === "Manager") return -1;
        if (b === "Manager") return 1;
        return a.localeCompare(b);
    });

    const newNodes: Node[] = sortedAgents.map((agent, index) => {
      // If Manager, put in center
      if (agent === "Manager") {
          return {
            id: agent,
            position: { x: centerX, y: centerY },
            data: { label: agent },
            style: {
                background: 'rgba(188, 19, 254, 0.1)',
                color: '#bc13fe',
                border: '1px solid #bc13fe',
                boxShadow: '0 0 30px rgba(188, 19, 254, 0.2)',
                borderRadius: '12px',
                padding: '16px',
                width: 180,
                textAlign: 'center',
                fontFamily: 'var(--font-orbitron)',
                fontSize: '16px',
                fontWeight: 'bold',
                backdropFilter: 'blur(10px)',
                textTransform: 'uppercase',
                letterSpacing: '1px'
            },
            type: 'default',
          };
      }

      // Others in circle
      const circleIndex = sortedAgents.indexOf("Manager") === -1 ? index : index - 1;
      const totalCircleNodes = sortedAgents.indexOf("Manager") === -1 ? sortedAgents.length : sortedAgents.length - 1;

      const angle = (circleIndex / (totalCircleNodes || 1)) * 2 * Math.PI;
      const x = centerX + radius * Math.cos(angle);
      const y = centerY + radius * Math.sin(angle);

      return {
        id: agent,
        position: { x, y },
        data: { label: agent },
        style: {
          background: 'rgba(5, 5, 16, 0.8)',
          color: '#00f3ff',
          border: '1px solid #00f3ff',
          boxShadow: '0 0 15px rgba(0, 243, 255, 0.15)',
          borderRadius: '8px',
          padding: '12px',
          width: 150,
          textAlign: 'center',
          fontFamily: 'var(--font-share-tech-mono)',
          fontSize: '14px',
          backdropFilter: 'blur(5px)'
        },
        type: 'default',
      };
    });

    setNodes(newNodes);

    // Create edges - Connect Manager to everyone else
    if (agents.includes("Manager")) {
      const newEdges: Edge[] = newNodes
        .filter(n => n.id !== "Manager")
        .map(n => ({
          id: `e-Manager-${n.id}`,
          source: "Manager",
          target: n.id,
          animated: true,
          style: { stroke: '#bc13fe', strokeWidth: 1, opacity: 0.5 },
          markerEnd: { type: MarkerType.ArrowClosed, color: '#bc13fe' },
        }));
      setEdges(newEdges);
    } else {
        setEdges([]);
    }

  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [JSON.stringify(agents), setNodes, setEdges]);

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
