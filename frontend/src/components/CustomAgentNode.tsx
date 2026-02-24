import React from 'react';
import { Handle, Position, NodeProps } from '@xyflow/react';
import { Users, Bot } from 'lucide-react';
import Image from 'next/image';
import { AgentNode } from '@/types/agent';

// Define the shape of the data prop passed to the custom node
export type CustomAgentNodeData = AgentNode & {
  label?: string; // Optional for compatibility if needed
};

const CustomAgentNode = ({ data }: NodeProps<CustomAgentNodeData>) => {
  const isManager = data.id === "Manager";
  const isTeamLead = data.parent === "Manager";

  let containerClassName = "";
  let iconElement = null;
  let borderColor = "";

  if (isManager) {
    borderColor = "var(--accent-2)";
    containerClassName = "bg-accent-2/10 border border-accent-2 text-accent-2 shadow-[0_0_30px_color-mix(in_srgb,var(--accent-2),transparent_80%)] rounded-xl p-4 w-[240px] text-center font-orbitron text-sm font-bold backdrop-blur-md uppercase tracking-wider";
    iconElement = <Image src="/logo.svg" width={32} height={32} className="w-8 h-8 drop-shadow-[0_0_10px_var(--accent-2)]" alt="" />;
  } else if (isTeamLead) {
    borderColor = "var(--accent-1)";
    containerClassName = "bg-accent-1/10 border border-accent-1 text-accent-1 shadow-[0_0_20px_color-mix(in_srgb,var(--accent-1),transparent_80%)] rounded-xl p-3.5 w-[220px] text-center font-orbitron text-xs font-bold backdrop-blur-sm uppercase tracking-wide";
    iconElement = <Users className="w-6 h-6 text-accent-1 drop-shadow-[0_0_8px_var(--accent-1)]" />;
  } else {
    // Worker
    borderColor = "var(--accent-3)";
    containerClassName = "bg-accent-3/10 border border-accent-3 text-accent-3 shadow-[0_0_15px_color-mix(in_srgb,var(--accent-3),transparent_85%)] rounded-lg p-3 w-[200px] text-center font-mono text-xs font-normal backdrop-blur-sm";
    iconElement = <Bot className="w-5 h-5 text-accent-3 drop-shadow-[0_0_5px_var(--accent-3)]" />;
  }

  return (
    <div className={containerClassName}>
      {/* Hierarchy Handles (Vertical) */}
      <Handle type="target" position={Position.Top} id="top" style={{ background: 'transparent', border: 'none' }} />
      <Handle type="source" position={Position.Bottom} id="bottom" style={{ background: 'transparent', border: 'none' }} />

      {/* Sibling Handles (Horizontal) */}
      <Handle type="target" position={Position.Left} id="left" style={{ background: 'transparent', border: 'none' }} />
      <Handle type="source" position={Position.Right} id="right" style={{ background: 'transparent', border: 'none' }} />

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
              borderColor: `${borderColor}`,
              color: 'currentColor'
            }}
          >
            {data.last_thought}
          </div>
        )}
      </div>
    </div>
  );
};

export default CustomAgentNode;
