
import React, { useState, useEffect, useCallback, useRef } from 'react';
import { GoogleGenAI, Chat } from '@google/genai';
import Sidebar from './Sidebar';
import { OrchestratorNode, AgentNode } from './NodeComponents';
import FlowLines from './FlowLines';
import { Agent, Status, Verdict, LogEntry, AgentName, ChatMessage, Sender } from '../types';
import { INITIAL_AGENTS, VERDICT_STYLES, STATUS_STYLES, AGENT_COLORS, INITIAL_CHAT_HISTORY, ORCHESTRATOR_DATA } from '../constants';

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

const getFeedbackForAgent = (agentName: AgentName, status: Status): string => {
    if (status === Status.FAILED) {
        return `Your analysis failed. Please run diagnostics and report back on the cause of the error.`;
    }
    switch (agentName) {
        case 'Athena': return "Good work, Athena. The complexity analysis is thorough. Please prioritize the high-complexity functions in the final report.";
        case 'Aegis': return "Aegis, the XSS vulnerability is critical. Flag this as high priority. We need a patch plan ASAP.";
        case 'Helios': return "Helios, the memory leak is a significant finding. Can you provide a stack trace in your detailed report?";
        case 'Eidos': return "Eidos, the bias detection is noted. Include recommendations for data augmentation to mitigate this.";
        default: return "Feedback received and noted.";
    }
};

const getAcknowledgementForAgent = (agentName: AgentName, status: Status): string => {
    if (status === Status.FAILED) {
        return "Understood. Running diagnostics now. I will report my findings shortly.";
    }
    switch (agentName) {
        case 'Athena': return "Acknowledged, Logos. High-priority functions will be highlighted in the report.";
        case 'Aegis': return "Understood. The XSS vulnerability is now marked as critical. A patch plan is being drafted.";
        case 'Helios': return "Roger that. I will append the stack trace to the full report.";
        case 'Eidos': return "Acknowledged. Mitigation strategies and data augmentation recommendations will be included.";
        default: return "Acknowledgement sent.";
    }
};

interface ChatWindowProps {
    agent: Agent;
    chatHistory: ChatMessage[];
    onSendMessage: (agentName: AgentName, message: string) => void;
    onClose: (agentName: AgentName) => void;
    initialPosition: { x: number, y: number };
    isThinking: boolean;
}

const ChatWindow: React.FC<ChatWindowProps> = ({ agent, chatHistory, onSendMessage, onClose, initialPosition, isThinking }) => {
    const [message, setMessage] = useState('');
    const chatContainerRef = useRef<HTMLDivElement>(null);
    const [position, setPosition] = useState(initialPosition);
    const [isDragging, setIsDragging] = useState(false);
    const dragStartPos = useRef({ x: 0, y: 0 });
    const windowRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (chatContainerRef.current) {
            chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
        }
    }, [chatHistory]);
    
    const handleMouseDown = (e: React.MouseEvent<HTMLDivElement>) => {
        if (windowRef.current && e.target === e.currentTarget) { // Only drag on the header itself
            setIsDragging(true);
            dragStartPos.current = {
                x: e.clientX - windowRef.current.offsetLeft,
                y: e.clientY - windowRef.current.offsetTop,
            };
        }
    };
    
    const handleMouseMove = (e: MouseEvent) => {
        if (isDragging) {
            setPosition({
                x: e.clientX - dragStartPos.current.x,
                y: e.clientY - dragStartPos.current.y,
            });
        }
    };

    const handleMouseUp = () => {
        setIsDragging(false);
    };

    useEffect(() => {
        if (isDragging) {
            window.addEventListener('mousemove', handleMouseMove);
            window.addEventListener('mouseup', handleMouseUp);
        } else {
            window.removeEventListener('mousemove', handleMouseMove);
            window.removeEventListener('mouseup', handleMouseUp);
        }

        return () => {
            window.removeEventListener('mousemove', handleMouseMove);
            window.removeEventListener('mouseup', handleMouseUp);
        };
    }, [isDragging]);

    const handleFormSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!message.trim() || isThinking) return;
        onSendMessage(agent.name, message);
        setMessage('');
    };

    const getSenderStyles = (sender: Sender) => {
        const isUser = sender === 'User';
        const colorName = AGENT_COLORS[sender] || 'gray-400';
        const textColorClass = `text-${colorName}`;

        return {
            wrapper: isUser ? 'items-end' : 'items-start',
            bubble: isUser ? 'bg-blue-600' : 'bg-gray-700',
            text: isUser ? 'text-white' : 'text-gray-200',
            name: isUser ? `font-bold text-blue-300` : `font-bold ${textColorClass}`,
        }
    };

    return (
        <div
            ref={windowRef}
            className="fixed w-96 h-[32rem] bg-gray-800/80 backdrop-blur-md border border-gray-700/50 rounded-lg shadow-2xl flex flex-col z-30 pointer-events-auto"
            style={{ top: `${position.y}px`, left: `${position.x}px`, cursor: isDragging ? 'grabbing' : 'default' }}
        >
            <div
                className="p-3 border-b border-gray-700 flex justify-between items-center flex-shrink-0 cursor-grab"
                onMouseDown={handleMouseDown}
            >
                <h3 className={`font-bold text-base text-${AGENT_COLORS[agent.name]}`}>{agent.name} Chat</h3>
                <button onClick={() => onClose(agent.name)} className="p-1 rounded-full text-gray-400 hover:bg-gray-600 hover:text-white transition-colors">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" /></svg>
                </button>
            </div>
            <div ref={chatContainerRef} className="flex-grow p-4 space-y-4 overflow-y-auto">
                {chatHistory.map((chat, index) => {
                    const styles = getSenderStyles(chat.sender);
                    return (
                        <div key={index} className={`flex flex-col ${styles.wrapper}`}>
                            <span className={`text-xs mb-1 px-1 ${styles.name}`}>{chat.sender}</span>
                            <div className={`max-w-xs p-3 rounded-lg ${styles.bubble}`}>
                                <p className={`text-sm break-words ${styles.text} ${chat.isThinking ? 'italic animate-pulse' : ''}`}>{chat.text || '...'}</p>
                            </div>
                        </div>
                    )
                })}
            </div>
            <div className="p-4 border-t border-gray-700 mt-auto flex-shrink-0">
                <form onSubmit={handleFormSubmit} className="flex space-x-2">
                    <input
                        type="text"
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        placeholder={isThinking ? `${agent.name} is thinking...` : `Message ${agent.name}...`}
                        className="flex-1 w-full bg-gray-700/50 border border-gray-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:opacity-50"
                        disabled={isThinking}
                    />
                    <button type="submit" className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm font-semibold transition-colors disabled:bg-gray-500 disabled:cursor-not-allowed" disabled={isThinking}>Send</button>
                </form>
            </div>
        </div>
    );
};


const RightPanel: React.FC<{
  logs: LogEntry[];
  verdict: Verdict;
}> = ({ logs, verdict }) => {
  
  const renderLogs = () => (
    <div className="h-full flex flex-col">
        <div className="p-4 border-b border-gray-700 flex-shrink-0">
            <h3 className="font-bold text-lg text-gray-200">System Logs</h3>
        </div>
        <div className="flex-grow p-4 overflow-y-auto">
            <ul className="space-y-2 text-sm">
            {logs.slice().reverse().map(log => (
                <li key={log.id} className="flex items-start">
                    <span className="text-gray-500 mr-3 w-16 text-right tabular-nums">{log.timestamp}</span>
                    <span className={`w-3 h-3 rounded-full mt-1 mr-3 flex-shrink-0 ${STATUS_STYLES[log.status].color}`}></span>
                    <span className="text-gray-300">
                        <span className={`font-semibold text-${AGENT_COLORS[log.source] || 'gray-400'}`}>{log.source}: </span>
                        {log.message}
                    </span>
                </li>
            ))}
            </ul>
        </div>
    </div>
  );

  return (
    <div className="w-[28rem] h-full bg-gray-800/50 backdrop-blur-sm border-l border-gray-700/50 flex flex-col text-gray-200">
      <div className="flex-grow min-h-0">
        {renderLogs()}
      </div>
      <div className={`p-4 mt-auto border-t border-gray-700 flex-shrink-0 ${VERDICT_STYLES[verdict].bg}`}>
        <h3 className="font-bold text-lg mb-2">Composite Verdict</h3>
        <div className={`px-4 py-2 rounded-lg border-2 ${VERDICT_STYLES[verdict].border} flex items-center justify-center`}>
            <span className={`text-2xl font-black tracking-widest ${VERDICT_STYLES[verdict].text}`}>{verdict}</span>
        </div>
      </div>
    </div>
  );
};

export default function App() {
  const [isDarkMode, setIsDarkMode] = useState(true);
  const [agents, setAgents] = useState<Agent[]>(INITIAL_AGENTS);
  const [orchestratorStatus, setOrchestratorStatus] = useState<Status>(Status.IDLE);
  const [isProcessing, setIsProcessing] = useState(false);
  const [verdict, setVerdict] = useState<Verdict>(Verdict.PENDING);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [logCounter, setLogCounter] = useState(0);
  const [openChats, setOpenChats] = useState<AgentName[]>([]);
  const [chatHistories, setChatHistories] = useState(INITIAL_CHAT_HISTORY);
  const [thinkingAgents, setThinkingAgents] = useState<AgentName[]>([]);

  const ai = useRef<GoogleGenAI | null>(null);
  const chatSessions = useRef<Partial<Record<AgentName, Chat>>>({});

  useEffect(() => {
    document.documentElement.classList.toggle('dark', isDarkMode);
  }, [isDarkMode]);

  useEffect(() => {
    try {
      ai.current = new GoogleGenAI({ apiKey: process.env.API_KEY });
    } catch (e) {
      console.error("Failed to initialize GoogleGenAI", e);
      addLog('System', 'Error: Could not initialize AI services. Chat functionality will be disabled.', Status.FAILED);
    }
  }, []);

  const addLog = useCallback((source: string, message: string, status: Status) => {
    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    setLogs(prev => [...prev, { id: logCounter, timestamp, source, message, status }]);
    setLogCounter(prev => prev + 1);
  }, [logCounter]);

  const addChatMessage = useCallback((agentName: AgentName, message: ChatMessage) => {
    setChatHistories(prev => ({
      ...prev,
      [agentName]: [...prev[agentName], message]
    }));
  }, []);
  
  const replaceLastChatMessage = useCallback((agentName: AgentName, message: ChatMessage) => {
      setChatHistories(prev => {
          const newHistory = [...prev[agentName]];
          const lastIndex = newHistory.length - 1;
          if (lastIndex >= 0) {
              newHistory[lastIndex] = message;
          }
          return { ...prev, [agentName]: newHistory };
      });
  }, []);


  const handleStartAnalysis = async () => {
    if (isProcessing) return;

    setIsProcessing(true);
    setAgents(INITIAL_AGENTS);
    setOrchestratorStatus(Status.IDLE);
    setVerdict(Verdict.PENDING);
    setLogs([]);
    setLogCounter(0);
    setOpenChats([]);
    setChatHistories(INITIAL_CHAT_HISTORY);
    chatSessions.current = {}; // Reset chat sessions

    await sleep(200);
    addLog('System', 'Initializing analysis...', Status.RUNNING);
    
    await sleep(500);
    setOrchestratorStatus(Status.RUNNING);
    addLog('Logos', 'Orchestration started. Dispatching agents.', Status.RUNNING);

    await sleep(1000);
    setAgents(prev => prev.map(a => ({ ...a, status: Status.RUNNING })));
    addLog('Logos', 'All agents are now active.', Status.RUNNING);

    agents.forEach(agent => {
        addChatMessage(agent.name, { sender: 'Logos', text: `Agent ${agent.name}, begin your analysis. Report your findings here.` });
    });

    const agentPromises = agents.map((agent, i) => (
      sleep(1500 + i * 500).then(async () => {
        addChatMessage(agent.name, { sender: agent.name, text: 'Thinking...', isThinking: true });
        
        await sleep(2000 + Math.random() * 1500);

        const isFailure = Math.random() < 0.1;
        const newStatus = isFailure ? Status.FAILED : Status.COMPLETE;
        
        let agentResponseText = '';
        if (newStatus === Status.COMPLETE) {
            switch(agent.name) {
                case 'Athena': agentResponseText = 'Task analysis complete. Found 2 high-complexity functions and 5 outdated dependency calls. Full report available.'; break;
                case 'Aegis': agentResponseText = 'Security scan finished. Identified one cross-site scripting (XSS) vulnerability and a hardcoded API key. Recommending immediate remediation.'; break;
                case 'Helios': agentResponseText = 'System analysis complete. Detected a memory leak in the data processing module under high load. Performance is otherwise within acceptable parameters.'; break;
                case 'Eidos': agentResponseText = 'Ethics audit complete. The model exhibits a minor demographic bias in sentiment analysis. Mitigation strategies are outlined in the full report.'; break;
            }
        } else {
            agentResponseText = 'Analysis failed due to an unexpected error in the environment. Could not complete the scan.';
        }
        
        replaceLastChatMessage(agent.name, { sender: agent.name, text: agentResponseText });

        setAgents(prev => prev.map(a => a.id === agent.id ? { ...a, status: newStatus } : a));
        addLog(agent.name, `Analysis ${newStatus}.`, newStatus);
        
        await sleep(500);
        addChatMessage(agent.name, { sender: 'Logos', text: `Thank you, ${agent.name}. Your report is received.` });
        
        await sleep(1000);
        const feedbackText = getFeedbackForAgent(agent.name, newStatus);
        addChatMessage(agent.name, { sender: 'Logos', text: feedbackText });

        await sleep(800);
        addChatMessage(agent.name, { sender: agent.name, text: 'Acknowledging...', isThinking: true });
        
        await sleep(1500);
        const ackText = getAcknowledgementForAgent(agent.name, newStatus);
        replaceLastChatMessage(agent.name, { sender: agent.name, text: ackText });

        return newStatus;
      })
    ));

    const results = await Promise.all(agentPromises);

    await sleep(500);
    setOrchestratorStatus(Status.COMPLETE);
    addLog('Logos', 'All agents complete. Compiling final verdict.', Status.COMPLETE);
    
    if (results.includes(Status.FAILED)) {
      setVerdict(Verdict.FAIL);
    } else if (results.some(r => r === Status.COMPLETE)) {
        const hasFailures = results.includes(Status.FAILED);
        const successfulAgents = agents.filter((a,i) => results[i] === Status.COMPLETE).length;

        if(hasFailures || successfulAgents < 2) setVerdict(Verdict.FAIL);
        else if (successfulAgents <= 3) setVerdict(Verdict.WARN)
        else setVerdict(Verdict.PASS);

    } else {
        setVerdict(Verdict.FAIL);
    }

    setIsProcessing(false);
  };
  
  const handleOpenChat = (agent: Agent) => {
    setOpenChats(prev => [...new Set([...prev, agent.name])]);
  };
  
  const handleCloseChat = (agentNameToClose: AgentName) => {
    setOpenChats(prev => prev.filter(name => name !== agentNameToClose));
  };

  const getSystemInstruction = (agent: Agent): string => {
    return `You are ${agent.name}, a specialist AI agent. Your official description is: "${agent.description}".
You are an expert in the following skills: ${agent.skills.join(', ')}.
You have access to these tools: ${agent.tools.join(', ')}.
You have just completed a detailed analysis of a code repository. A user is now chatting with you to ask follow-up questions about your findings.
Be concise, act as your persona, and answer based on the context of the analysis. Do not repeat your identity in every response.`;
  };

  const handleSendMessage = async (agentName: AgentName, text: string) => {
    if (thinkingAgents.includes(agentName) || !ai.current) {
        return;
    }

    addChatMessage(agentName, { sender: 'User', text });
    setThinkingAgents(prev => [...prev, agentName]);

    addChatMessage(agentName, { sender: agentName, text: '', isThinking: true });

    try {
        if (!chatSessions.current[agentName]) {
            const agent = agents.find(a => a.name === agentName);
            if (!agent) throw new Error(`Agent configuration for ${agentName} not found.`);
            
            chatSessions.current[agentName] = ai.current.chats.create({
                model: 'gemini-2.5-flash',
                config: {
                    systemInstruction: getSystemInstruction(agent),
                },
            });
        }
        
        const chat = chatSessions.current[agentName]!;
        const stream = await chat.sendMessageStream({ message: text });

        let fullResponse = "";
        for await (const chunk of stream) {
            fullResponse += chunk.text;
            replaceLastChatMessage(agentName, { sender: agentName, text: fullResponse, isThinking: true });
        }
        
        replaceLastChatMessage(agentName, { sender: agentName, text: fullResponse, isThinking: false });

    } catch (error) {
        console.error(`Error with Gemini for agent ${agentName}:`, error);
        replaceLastChatMessage(agentName, { sender: agentName, text: "I'm having trouble connecting to my reasoning circuits. Please try again later.", isThinking: false });
    } finally {
        setThinkingAgents(prev => prev.filter(name => name !== agentName));
    }
  };


  return (
    <div className="dark">
      <div className="h-screen w-screen flex bg-gray-900 text-gray-100 font-sans overflow-hidden">
        <Sidebar />
        <main className="flex-1 flex flex-col min-w-0 relative">
          <header className="p-4 border-b border-gray-800 flex justify-between items-center flex-shrink-0 z-10">
             <div className="flex-1">
                <input
                    id="task-input-field"
                    type="text"
                    placeholder="Enter task instructions or repository URL..."
                    className="w-full max-w-lg bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
                    disabled={isProcessing}
                />
             </div>
             <button
              onClick={handleStartAnalysis}
              disabled={isProcessing}
              className="px-6 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg font-semibold text-white transition-colors disabled:bg-gray-600 disabled:cursor-not-allowed flex items-center"
            >
              {isProcessing && <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>}
              {isProcessing ? 'Analyzing...' : 'Start Analysis'}
            </button>
          </header>
          
          <div className="flex-1 flex overflow-hidden">
            <div id="flow-container" className="flex-1 relative p-8 flex flex-col items-center justify-start">
              <FlowLines orchestratorStatus={orchestratorStatus} agentStatuses={agents.map(a => a.status)} />
              <div className="mt-8">
                <OrchestratorNode status={orchestratorStatus} data={ORCHESTRATOR_DATA} />
              </div>
              <div className="flex justify-around w-full max-w-5xl mt-24">
                {agents.map(agent => (
                  <AgentNode key={agent.id} agent={agent} onSelect={handleOpenChat} />
                ))}
              </div>
              <div className="flex-grow"></div>
            </div>
            
            <RightPanel 
              logs={logs} 
              verdict={verdict} 
            />
          </div>
          
          <footer className="p-3 border-t border-gray-800 bg-gray-900/50 flex justify-end items-center space-x-4 flex-shrink-0 z-10">
            <button className="px-4 py-2 text-sm bg-gray-700 hover:bg-gray-600 rounded-md transition-colors">Promote to Baseline</button>
            <button className="px-4 py-2 text-sm bg-green-600 hover:bg-green-500 rounded-md transition-colors">Export Report</button>
          </footer>
           <div className="absolute top-0 left-0 w-full h-full pointer-events-none">
                {openChats.map((agentName, index) => {
                    const agent = agents.find(a => a.name === agentName);
                    if (!agent) return null;
                    const xPosition = (window.innerWidth / 2) - 400 + (index * 60) - (openChats.length * 30);
                    const yPosition = 100 + (index * 40);

                    return (
                        <ChatWindow 
                            key={agent.id}
                            agent={agent}
                            chatHistory={chatHistories[agent.name]}
                            onSendMessage={handleSendMessage}
                            onClose={handleCloseChat}
                            initialPosition={{ x: xPosition, y: yPosition }}
                            isThinking={thinkingAgents.includes(agent.name)}
                        />
                    );
                })}
            </div>
        </main>
      </div>
    </div>
  );
}
