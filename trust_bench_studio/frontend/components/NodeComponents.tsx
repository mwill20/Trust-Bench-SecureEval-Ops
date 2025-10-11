import React, { useState } from 'react';
import { Agent, Status } from '../types';
import { AGENT_COLORS, STATUS_STYLES } from '../constants';
import { AgentIcon, LogosIcon } from './icons/AgentIcons';

const StatusIndicator: React.FC<{ status: Status }> = ({ status }) => (
  <div className="flex items-center">
    <span className={`relative flex h-3 w-3`}>
      <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${STATUS_STYLES[status].color} opacity-75 ${status !== Status.RUNNING ? 'hidden' : ''}`}></span>
      <span className={`relative inline-flex rounded-full h-3 w-3 ${STATUS_STYLES[status].color}`}></span>
    </span>
    <span className={`ml-2 text-sm capitalize font-medium ${STATUS_STYLES[status].text}`}>{status}</span>
  </div>
);

const Dropdown: React.FC<{ skills: string[]; tools: string[]; position?: string }> = ({ skills, tools, position = 'top-full mt-2' }) => (
  <div className={`absolute w-56 bg-gray-900 border border-gray-700 rounded-lg shadow-xl z-20 p-3 text-sm animate-fade-in-up ${position}`}>
    <div className="mb-2">
      <h5 className="font-bold text-gray-300 mb-1 tracking-wide">Skills</h5>
      <ul className="list-disc list-inside text-gray-400 space-y-1">
        {skills.map(skill => <li key={skill}>{skill}</li>)}
      </ul>
    </div>
    <div>
      <h5 className="font-bold text-gray-300 mb-1 tracking-wide">Tools</h5>
      <ul className="list-disc list-inside text-gray-400 space-y-1">
        {tools.map(tool => <li key={tool}>{tool}</li>)}
      </ul>
    </div>
  </div>
);

export const OrchestratorNode: React.FC<{ status: Status; data: { skills: string[]; tools: string[] } }> = ({ status, data }) => {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  return (
    <div 
      id="orchestrator" 
      className="relative z-10 flex flex-col items-center p-4 bg-gray-800/60 backdrop-blur-md rounded-xl border border-gray-700 shadow-lg w-64"
    >
      <div className={`p-3 rounded-full bg-brand-logos/20 ring-2 ${STATUS_STYLES[status].ring} transition-all`}>
        <LogosIcon className="w-10 h-10 text-brand-logos" />
      </div>
      <h3 className="mt-3 text-lg font-bold text-gray-100">Logos Orchestrator</h3>
      <p className="text-sm text-gray-400">Composite Analysis</p>
      <div className="mt-3">
        <StatusIndicator status={status} />
      </div>
      <button 
        onClick={(e) => { e.stopPropagation(); setIsDropdownOpen(prev => !prev); }} 
        className="absolute bottom-3 right-3 p-1 rounded-full text-gray-500 hover:text-gray-300 transition-colors"
        aria-label="Toggle details"
      >
        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
        </svg>
      </button>

      {isDropdownOpen && <Dropdown skills={data.skills} tools={data.tools} position="top-0 left-full ml-4" />}
    </div>
  );
};

export const AgentNode: React.FC<{ agent: Agent; onSelect: (agent: Agent) => void }> = ({ agent, onSelect }) => {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const color = AGENT_COLORS[agent.name];
  const colorClass = `text-${color}`;

  return (
    <div
      id={`agent-${agent.id}`}
      className={`relative z-10 w-56 bg-gray-800/60 backdrop-blur-md rounded-xl border border-gray-700 shadow-md flex flex-col items-center p-4 transition-all`}
    >
      <div className={`p-2 rounded-full bg-${color}/20 ring-2 ${STATUS_STYLES[agent.status].ring} transition-all`}>
        <AgentIcon name={agent.name} className={`w-8 h-8 ${colorClass}`} />
      </div>
      <h4 className={`mt-2 font-bold ${colorClass}`}>{agent.name}</h4>
      <p className="text-xs text-gray-400 mb-2">{agent.description}</p>
      <StatusIndicator status={agent.status} />
      
      {[Status.COMPLETE, Status.FAILED].includes(agent.status) && (
         <button
            onClick={(e) => { e.stopPropagation(); onSelect(agent); }}
            className="mt-3 px-4 py-1.5 text-xs font-semibold bg-blue-600/80 text-white rounded-md hover:bg-blue-500 transition-colors animate-glow"
            aria-label={`Open chat with ${agent.name}`}
        >
            Chat with Agent
        </button>
      )}

      <button 
        onClick={(e) => { 
          e.stopPropagation(); 
          setIsDropdownOpen(prev => !prev); 
        }} 
        className="absolute bottom-3 right-3 p-1 rounded-full text-gray-500 hover:text-gray-300 transition-colors"
        aria-label={`Toggle details for ${agent.name}`}
      >
        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
        </svg>
      </button>
      {isDropdownOpen && <Dropdown skills={agent.skills} tools={agent.tools || []} />}
    </div>
  );
};