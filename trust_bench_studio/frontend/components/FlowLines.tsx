import React, { useEffect, useState } from 'react';
import { Status } from '../types';

interface Point {
  x: number;
  y: number;
}

interface FlowLinesProps {
  orchestratorStatus: Status;
  agentStatuses: Status[];
}

const FlowLines: React.FC<FlowLinesProps> = ({ orchestratorStatus, agentStatuses }) => {
  const [startPos, setStartPos] = useState<Point>({ x: 0, y: 0 });
  const [orchestratorPos, setOrchestratorPos] = useState<Point>({ x: 0, y: 0 });
  const [agentPositions, setAgentPositions] = useState<Point[]>([]);

  useEffect(() => {
    const updatePositions = () => {
      const flowContainer = document.getElementById('flow-container');
      if (!flowContainer) return;
      const containerRect = flowContainer.getBoundingClientRect();

      const getElementCenter = (element: HTMLElement | null): Point => {
        if (!element) return { x: 0, y: 0 };
        const rect = element.getBoundingClientRect();
        return {
          x: rect.left + rect.width / 2 - containerRect.left,
          y: rect.top + rect.height / 2 - containerRect.top,
        };
      };

      const taskInputEl = document.getElementById('task-input-field');
      const orchestratorEl = document.getElementById('orchestrator');
      const agentEls = [
        document.getElementById('agent-1'),
        document.getElementById('agent-2'),
        document.getElementById('agent-3'),
        document.getElementById('agent-4'),
      ];
      setStartPos(getElementCenter(taskInputEl));
      setOrchestratorPos(getElementCenter(orchestratorEl));
      setAgentPositions(agentEls.map(getElementCenter));
    };
    
    updatePositions();
    const timeoutId = setTimeout(updatePositions, 100);

    const resizeObserver = new ResizeObserver(updatePositions);
    const container = document.getElementById('flow-container');
    if (container) {
      resizeObserver.observe(container);
    }
    window.addEventListener('resize', updatePositions);

    return () => {
      clearTimeout(timeoutId);
      if (container) {
        resizeObserver.unobserve(container);
      }
      window.removeEventListener('resize', updatePositions);
    };
  }, []);

  const isAnalysisActive = orchestratorStatus !== Status.IDLE;
  const isAnalysisRunning = orchestratorStatus === Status.RUNNING;
  const inputToOrchestratorPath = `M ${startPos.x} ${startPos.y} C ${startPos.x} ${startPos.y + 80}, ${orchestratorPos.x} ${orchestratorPos.y - 80}, ${orchestratorPos.x} ${orchestratorPos.y}`;

  return (
    <svg className="absolute top-0 left-0 w-full h-full pointer-events-none z-0">
      <defs>
        <linearGradient id="line-gradient" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" className="text-brand-logos/80" stopColor="currentColor" />
          <stop offset="100%" className="text-brand-athena/50" stopColor="currentColor" />
        </linearGradient>
         <linearGradient id="return-line-gradient" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" className="text-brand-athena/50" stopColor="currentColor" />
          <stop offset="100%" className="text-brand-logos/80" stopColor="currentColor" />
        </linearGradient>
        <marker id="dot" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="5" markerHeight="5">
          <circle cx="5" cy="5" r="5" fill="currentColor" className="text-brand-logos"/>
        </marker>
      </defs>

      {/* Line from User Input to Orchestrator */}
      {startPos.x > 0 && orchestratorPos.x > 0 && (
        <g>
            <path
              d={inputToOrchestratorPath}
              stroke="url(#line-gradient)"
              strokeWidth="2"
              fill="none"
              className={`transition-opacity duration-500 ${isAnalysisActive ? 'opacity-100' : 'opacity-20'}`}
              markerEnd="url(#dot)"
            />
            {isAnalysisRunning && (
              <path
                d={inputToOrchestratorPath}
                stroke="white"
                strokeWidth="2"
                fill="none"
                className="opacity-50 animate-glow"
                style={{
                  strokeDasharray: 10,
                  strokeDashoffset: 1000,
                  animation: 'dash 2s linear infinite',
                }}
              />
            )}
        </g>
      )}

      {/* Lines from Orchestrator to Agents */}
      {agentPositions.map((pos, index) => {
        const agentStatus = agentStatuses[index];
        if (pos.x === 0 && pos.y === 0) return null;
        
        const isAgentActive = agentStatus !== Status.IDLE;
        const pathData = `M ${orchestratorPos.x} ${orchestratorPos.y} C ${orchestratorPos.x} ${orchestratorPos.y + 70}, ${pos.x} ${pos.y - 70}, ${pos.x} ${pos.y}`;
        
        return (
          <g key={index}>
            <path
              d={pathData}
              stroke="url(#line-gradient)"
              strokeWidth="2"
              fill="none"
              className={`transition-opacity duration-500 ${isAgentActive ? 'opacity-100' : 'opacity-20'}`}
              markerStart="url(#dot)"
              markerEnd="url(#dot)"
            />
            {agentStatus === Status.RUNNING && (
              <path
                d={pathData}
                stroke="white"
                strokeWidth="2"
                fill="none"
                className="opacity-50 animate-glow"
                style={{
                  strokeDasharray: 10,
                  strokeDashoffset: 1000,
                  animation: 'dash 2s linear infinite',
                }}
              />
            )}
          </g>
        );
      })}

      {/* Lines from Agents back to Orchestrator */}
      {agentPositions.map((pos, index) => {
        const agentStatus = agentStatuses[index];
        if (pos.x === 0 && pos.y === 0) return null;
        
        const isAgentFinished = agentStatus === Status.COMPLETE || agentStatus === Status.FAILED;
        if (!isAgentFinished) return null;

        const pathData = `M ${pos.x} ${pos.y} C ${pos.x} ${pos.y - 70}, ${orchestratorPos.x} ${orchestratorPos.y + 70}, ${orchestratorPos.x} ${orchestratorPos.y}`;
        
        return (
          <g key={`return-${index}`}>
            <path
              d={pathData}
              stroke="url(#return-line-gradient)"
              strokeWidth="2"
              fill="none"
              className="opacity-70"
              markerEnd="url(#dot)"
            />
             <path
                d={pathData}
                stroke="white"
                strokeWidth="1"
                fill="none"
                className="opacity-60"
                style={{
                  strokeDasharray: 4,
                  strokeDashoffset: 1000,
                  animation: 'dash-reverse 1.5s ease-out forwards',
                }}
              />
          </g>
        );
      })}

      <style>{`
        @keyframes dash {
          to {
            stroke-dashoffset: 0;
          }
        }
        @keyframes dash-reverse {
          from {
            stroke-dashoffset: 1000;
          }
          to {
            stroke-dashoffset: 0;
          }
        }
      `}</style>
    </svg>
  );
};

export default FlowLines;