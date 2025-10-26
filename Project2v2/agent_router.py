"""
Orchestrator-based agent routing for Trust Bench multi-agent chat system.
Routes user questions to appropriate specialist agents with contextual responses.
"""

from __future__ import annotations

import re
from typing import Any, Dict, Optional, Tuple

try:
    from .llm_utils import chat_with_llm, LLMError
except ImportError:
    from llm_utils import chat_with_llm, LLMError


class OrchestrationRouter:
    """
    Orchestrator that routes user questions to appropriate specialist agents
    and generates contextual responses based on Trust Bench analysis results.
    """

    def __init__(self, report_data: Dict[str, Any]):
        """Initialize router with analysis report context."""
        self.report_data = report_data
        self.agents_data = report_data.get('agents', {})
        self.summary = report_data.get('summary', {})
        self.conversation_log = report_data.get('conversation', [])
        
        # Extract agent-specific contexts
        self.security_context = self._extract_security_context()
        self.quality_context = self._extract_quality_context()
        self.docs_context = self._extract_docs_context()
        self.orchestrator_context = self._extract_orchestrator_context()

    def route_and_respond(
        self, 
        question: str, 
        provider_override: Optional[str] = None,
        api_key_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Route question to appropriate agent(s) and generate response.
        
        Returns:
            dict with 'agent', 'response', 'routing_reason', 'confidence'
            For multi-agent: 'agents' list and 'multi_agent_response' 
        """
        # Check if this requires multiple agents
        required_agents = self.requires_multiple_agents(question)
        
        if len(required_agents) > 1:
            # Multi-agent consultation
            return self.consult_multiple_agents(
                question, required_agents, provider_override, api_key_override
            )
        else:
            # Single agent routing (existing logic)
            agent_type, confidence = self.classify_question(question)
            
            prompt = self._build_agent_prompt(agent_type, question)
            
            try:
                llm_response = chat_with_llm(
                    question=prompt,
                    provider_override=provider_override,
                    api_key_override=api_key_override
                )
                response = llm_response.get('answer', 'Unable to generate response.')
            except LLMError as e:
                response = f"Sorry, I'm having trouble accessing the AI service: {str(e)}"
                confidence = 0.0
            except Exception as e:
                response = f"An unexpected error occurred: {str(e)}"
                confidence = 0.0

            return {
                'agent': agent_type,
                'response': response,
                'routing_reason': self._get_routing_reason(question, agent_type),
                'confidence': confidence
            }

    def requires_multiple_agents(self, question: str) -> list[str]:
        """
        Determine if question requires consultation from multiple agents.
        
        Returns:
            list of agent types that should collaborate on the response
        """
        question_lower = question.lower()
        required_agents = []
        
        # Multi-agent trigger phrases
        comprehensive_phrases = [
            'comprehensive', 'complete', 'full', 'overall', 'entire', 
            'thorough', 'detailed analysis', 'end-to-end', 'holistic'
        ]
        
        multi_domain_phrases = [
            'security and quality', 'quality and security', 'security and documentation',
            'documentation and security', 'quality and documentation', 'documentation and quality',
            'security, quality, and documentation', 'all aspects', 'every area'
        ]
        
        # Check for explicit multi-domain requests
        for phrase in multi_domain_phrases:
            if phrase in question_lower:
                if 'security' in phrase:
                    required_agents.append('security')
                if 'quality' in phrase:
                    required_agents.append('quality')
                if 'documentation' in phrase:
                    required_agents.append('docs')
                break
        
        # Check for comprehensive analysis requests
        if any(phrase in question_lower for phrase in comprehensive_phrases):
            # Look for context clues to determine which agents
            if any(word in question_lower for word in ['vulnerability', 'security', 'risk']):
                required_agents.append('security')
            if any(word in question_lower for word in ['code', 'quality', 'architecture', 'testing']):
                required_agents.append('quality')  
            if any(word in question_lower for word in ['documentation', 'readme', 'guide']):
                required_agents.append('docs')
            
            # If comprehensive but no specific domains, include all
            if not required_agents:
                required_agents = ['security', 'quality', 'docs']
        
        # Remove duplicates and ensure we have at least one agent
        required_agents = list(set(required_agents))
        if not required_agents:
            # Fallback to single agent classification
            agent_type, _ = self.classify_question(question)
            required_agents = [agent_type]
        
        return required_agents

    def consult_multiple_agents(
        self,
        question: str,
        required_agents: list[str], 
        provider_override: Optional[str] = None,
        api_key_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Advanced multi-agent consultation with consensus building.
        
        Phase 3: Includes iterative refinement, conflict resolution, and consensus building.
        
        Returns:
            dict with 'agents', 'multi_agent_response', 'individual_responses', 
            'consensus_process', 'iterations', etc.
        """
        # Check if this requires advanced orchestration (Phase 3)
        needs_consensus = self._requires_consensus_building(question)
        
        if needs_consensus and len(required_agents) > 1:
            return self._advanced_orchestration_process(
                question, required_agents, provider_override, api_key_override
            )
        else:
            # Use Phase 2 multi-agent consultation
            return self._basic_multi_agent_consultation(
                question, required_agents, provider_override, api_key_override
            )

    def _basic_multi_agent_consultation(
        self,
        question: str,
        required_agents: list[str], 
        provider_override: Optional[str] = None,
        api_key_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Phase 2 multi-agent consultation (existing functionality).
        """
        individual_responses = {}
        
        # Get response from each required agent
        for agent_type in required_agents:
            try:
                prompt = self._build_agent_prompt(agent_type, question)
                llm_response = chat_with_llm(
                    question=prompt,
                    provider_override=provider_override,
                    api_key_override=api_key_override
                )
                individual_responses[agent_type] = llm_response.get('answer', f'No response from {agent_type} agent.')
            except Exception as e:
                individual_responses[agent_type] = f"Error from {agent_type} agent: {str(e)}"
        
        # Synthesize responses using orchestrator
        synthesis_prompt = self._build_synthesis_prompt(question, individual_responses)
        
        try:
            synthesis_response = chat_with_llm(
                question=synthesis_prompt,
                provider_override=provider_override,
                api_key_override=api_key_override
            )
            synthesized_answer = synthesis_response.get('answer', 'Unable to synthesize multi-agent response.')
        except Exception as e:
            synthesized_answer = f"Error synthesizing responses: {str(e)}"
        
        return {
            'agents': required_agents,
            'agent': 'multi-agent',
            'response': synthesized_answer,
            'individual_responses': individual_responses,
            'routing_reason': f"Multi-agent consultation required for comprehensive analysis involving: {', '.join(required_agents)}",
            'confidence': 0.85,  # High confidence for multi-agent responses
            'multi_agent': True,
            'orchestration_level': 'phase2'
        }

    def classify_question(self, question: str) -> Tuple[str, float]:
        """
        Classify question to determine which agent should respond.
        
        Returns:
            tuple of (agent_type, confidence_score)
        """
        question_lower = question.lower()
        
        # Security-related keywords and patterns
        security_keywords = [
            'security', 'vulnerability', 'vulnerabilities', 'secret', 'secrets',
            'password', 'token', 'key', 'credential', 'auth', 'authentication',
            'authorization', 'ssl', 'tls', 'encryption', 'crypto', 'hash',
            'injection', 'xss', 'csrf', 'sql injection', 'malware', 'breach',
            'attack', 'threat', 'risk', 'exploit', 'cve', 'owasp'
        ]
        
        # Quality-related keywords
        quality_keywords = [
            'code quality', 'quality', 'testing', 'test', 'coverage', 'tests',
            'architecture', 'structure', 'complexity', 'maintainability',
            'technical debt', 'refactor', 'refactoring', 'performance',
            'optimization', 'scalability', 'design pattern', 'clean code',
            'best practices', 'standards', 'linting', 'static analysis'
        ]
        
        # Documentation-related keywords  
        docs_keywords = [
            'documentation', 'docs', 'readme', 'guide', 'tutorial',
            'examples', 'usage', 'instructions', 'manual', 'help',
            'onboarding', 'getting started', 'installation', 'setup',
            'api docs', 'comments', 'docstring', 'changelog'
        ]
        
        # Executive/high-level keywords
        executive_keywords = [
            'overall', 'summary', 'recommendation', 'recommendations',
            'priority', 'priorities', 'business', 'executive', 'decision',
            'strategy', 'roadmap', 'investment', 'roi', 'cost', 'benefit',
            'timeline', 'resource', 'team', 'management'
        ]

        # Calculate keyword match scores
        security_score = self._calculate_keyword_score(question_lower, security_keywords)
        quality_score = self._calculate_keyword_score(question_lower, quality_keywords)
        docs_score = self._calculate_keyword_score(question_lower, docs_keywords)
        executive_score = self._calculate_keyword_score(question_lower, executive_keywords)

        # Determine best match
        scores = {
            'security': security_score,
            'quality': quality_score,
            'docs': docs_score,
            'orchestrator': executive_score
        }
        
        # Get highest scoring agent
        best_agent = max(scores, key=scores.get)
        best_score = scores[best_agent]
        
        # If no clear match, default to orchestrator
        if best_score == 0:
            return 'orchestrator', 0.5
        
        # Convert score to confidence (0.6 to 0.95 range)
        confidence = min(0.95, 0.6 + (best_score * 0.35))
        
        return best_agent, confidence

    def _calculate_keyword_score(self, text: str, keywords: list) -> float:
        """Calculate relevance score based on keyword matches."""
        matches = 0
        total_keywords = len(keywords)
        
        for keyword in keywords:
            if keyword in text:
                matches += 1
        
        return matches / total_keywords if total_keywords > 0 else 0

    def _build_agent_prompt(self, agent_type: str, question: str) -> str:
        """Build agent-specific prompt with contextual information."""
        
        if agent_type == 'security':
            return self._build_security_prompt(question)
        elif agent_type == 'quality':
            return self._build_quality_prompt(question)
        elif agent_type == 'docs':
            return self._build_docs_prompt(question)
        else:  # orchestrator
            return self._build_orchestrator_prompt(question)

    def _build_security_prompt(self, question: str) -> str:
        """Build Security Agent prompt with scan findings."""
        security_data = self.security_context
        
        prompt = f"""You are the Security Agent from Trust Bench, a specialist in vulnerability analysis and risk assessment.

SECURITY ANALYSIS CONTEXT:
- Security Score: {security_data.get('score', 'N/A')}/100
- Risk Level: {security_data.get('risk_level', 'Unknown')}
- Secrets Found: {security_data.get('secrets_count', 0)}
- Vulnerability Patterns: {security_data.get('vulnerability_patterns', 'None detected')}

KEY FINDINGS:
{security_data.get('summary', 'Security analysis completed with standard checks.')}

DETECTED ISSUES:
{self._format_security_findings(security_data.get('findings', []))}

USER QUESTION: {question}

As the Security Agent who performed this analysis, provide a detailed response focused on:
- Specific security vulnerabilities and risks
- Concrete mitigation recommendations  
- Risk prioritization and business impact
- Security best practices relevant to the findings

Use security terminology and reference the actual scan results where relevant."""

        return prompt

    def _build_quality_prompt(self, question: str) -> str:
        """Build Quality Agent prompt with code analysis."""
        quality_data = self.quality_context
        
        prompt = f"""You are the Quality Agent from Trust Bench, a specialist in code quality and software architecture.

CODE QUALITY ANALYSIS CONTEXT:
- Quality Score: {quality_data.get('score', 'N/A')}/100
- Code Complexity: {quality_data.get('complexity_level', 'Unknown')}
- Test Coverage: {quality_data.get('test_coverage', 'Unknown')}
- Technical Debt Level: {quality_data.get('tech_debt', 'Moderate')}

KEY FINDINGS:
{quality_data.get('summary', 'Code quality analysis completed with standard metrics.')}

ANALYSIS RESULTS:
{self._format_quality_findings(quality_data.get('findings', []))}

USER QUESTION: {question}

As the Quality Agent who performed this analysis, provide a detailed response focused on:
- Code quality metrics and patterns
- Testing strategies and coverage improvements
- Architecture and maintainability concerns
- Refactoring opportunities and technical debt reduction

Reference specific code analysis results and provide actionable recommendations."""

        return prompt

    def _build_docs_prompt(self, question: str) -> str:
        """Build Documentation Agent prompt with docs assessment."""
        docs_data = self.docs_context
        
        prompt = f"""You are the Documentation Agent from Trust Bench, a specialist in developer experience and documentation quality.

DOCUMENTATION ANALYSIS CONTEXT:
- Documentation Score: {docs_data.get('score', 'N/A')}/100
- Completeness Level: {docs_data.get('completeness', 'Unknown')}
- User Experience Rating: {docs_data.get('ux_rating', 'Unknown')}
- Coverage Areas: {docs_data.get('coverage_areas', 'Standard documentation')}

KEY FINDINGS:
{docs_data.get('summary', 'Documentation analysis completed with standard checks.')}

ASSESSMENT RESULTS:
{self._format_docs_findings(docs_data.get('findings', []))}

USER QUESTION: {question}

As the Documentation Agent who performed this analysis, provide a detailed response focused on:
- Documentation completeness and quality
- User onboarding and developer experience
- Missing guides and documentation gaps
- Recommendations for improving accessibility and clarity

Reference specific documentation assessment results and suggest concrete improvements."""

        return prompt

    def _build_orchestrator_prompt(self, question: str) -> str:
        """Build Orchestrator prompt with high-level system context."""
        
        prompt = f"""You are the Orchestrator from Trust Bench, coordinating the multi-agent security evaluation system with executive-level perspective.

OVERALL SYSTEM CONTEXT:
- Repository: {self.report_data.get('repo_root', 'Unknown')}
- Overall Score: {self.summary.get('overall_score', 'N/A')}/100
- Grade: {self.summary.get('grade', 'Unknown')}

AGENT SUMMARIES:
- Security Agent: {self.security_context.get('summary', 'Analysis completed')}
- Quality Agent: {self.quality_context.get('summary', 'Analysis completed')}  
- Documentation Agent: {self.docs_context.get('summary', 'Analysis completed')}

CROSS-AGENT COLLABORATION:
{len(self.conversation_log)} messages exchanged between agents during analysis.

KEY METRICS:
- System Latency: {self.report_data.get('metrics', {}).get('system_latency_seconds', 'N/A')} seconds
- Faithfulness: {self.report_data.get('metrics', {}).get('faithfulness', 'N/A')}

USER QUESTION: {question}

As the Orchestrator with complete system visibility, provide a strategic response that:
- Synthesizes insights from all specialist agents
- Provides executive-level recommendations and priorities
- Considers business impact and resource allocation
- Offers strategic guidance based on the complete analysis

Focus on high-level decision making and cross-functional coordination."""

        return prompt

    def _get_routing_reason(self, question: str, agent_type: str) -> str:
        """Generate explanation for routing decision."""
        reasons = {
            'security': 'Detected security-related keywords and vulnerability concerns',
            'quality': 'Identified code quality and software engineering topics',
            'docs': 'Recognized documentation and user experience questions',
            'orchestrator': 'Determined need for high-level strategic guidance'
        }
        
        return reasons.get(agent_type, 'Defaulted to orchestrator for general coordination')

    def _extract_security_context(self) -> Dict[str, Any]:
        """Extract security-specific context from report."""
        security_agent = self.agents_data.get('SecurityAgent', {})
        return {
            'score': security_agent.get('score', 0),
            'summary': security_agent.get('summary', ''),
            'findings': security_agent.get('findings', []),
            'risk_level': self._determine_risk_level(security_agent.get('score', 0)),
            'secrets_count': self._count_secrets(security_agent),
            'vulnerability_patterns': self._extract_vulnerability_patterns(security_agent)
        }

    def _extract_quality_context(self) -> Dict[str, Any]:
        """Extract quality-specific context from report."""
        quality_agent = self.agents_data.get('QualityAgent', {})
        return {
            'score': quality_agent.get('score', 0),
            'summary': quality_agent.get('summary', ''),
            'findings': quality_agent.get('findings', []),
            'complexity_level': self._determine_complexity_level(quality_agent.get('score', 0)),
            'test_coverage': self._extract_test_coverage(quality_agent),
            'tech_debt': self._assess_tech_debt(quality_agent)
        }

    def _extract_docs_context(self) -> Dict[str, Any]:
        """Extract documentation-specific context from report."""
        docs_agent = self.agents_data.get('DocumentationAgent', {})
        return {
            'score': docs_agent.get('score', 0),
            'summary': docs_agent.get('summary', ''),
            'findings': docs_agent.get('findings', []),
            'completeness': self._assess_docs_completeness(docs_agent.get('score', 0)),
            'ux_rating': self._rate_docs_ux(docs_agent),
            'coverage_areas': self._identify_coverage_areas(docs_agent)
        }

    def _extract_orchestrator_context(self) -> Dict[str, Any]:
        """Extract orchestrator-level context from report."""
        return {
            'overall_assessment': self.summary,
            'collaboration_metrics': len(self.conversation_log),
            'system_performance': self.report_data.get('metrics', {}),
            'strategic_recommendations': self._generate_strategic_recommendations()
        }

    # Helper methods for context extraction
    def _determine_risk_level(self, score: int) -> str:
        """Determine risk level based on security score."""
        if score >= 80:
            return 'Low'
        elif score >= 60:
            return 'Moderate'
        elif score >= 40:
            return 'High'
        else:
            return 'Critical'

    def _count_secrets(self, security_data: Dict) -> int:
        """Count detected secrets from security analysis."""
        # This would parse actual security findings to count secrets
        # For now, return a placeholder
        return len(security_data.get('findings', []))

    def _extract_vulnerability_patterns(self, security_data: Dict) -> str:
        """Extract vulnerability patterns from security analysis."""
        findings = security_data.get('findings', [])
        if findings:
            return f"{len(findings)} potential security issues identified"
        return "No significant vulnerability patterns detected"

    def _determine_complexity_level(self, score: int) -> str:
        """Determine complexity level based on quality score."""
        if score >= 80:
            return 'Low'
        elif score >= 60:
            return 'Moderate'  
        else:
            return 'High'

    def _extract_test_coverage(self, quality_data: Dict) -> str:
        """Extract test coverage information."""
        # Parse quality findings for test coverage info
        return "Test coverage analysis performed"

    def _assess_tech_debt(self, quality_data: Dict) -> str:
        """Assess technical debt level."""
        score = quality_data.get('score', 50)
        if score >= 80:
            return 'Low'
        elif score >= 60:
            return 'Moderate'
        else:
            return 'High'

    def _assess_docs_completeness(self, score: int) -> str:
        """Assess documentation completeness."""
        if score >= 80:
            return 'Comprehensive'
        elif score >= 60:
            return 'Adequate'
        else:
            return 'Incomplete'

    def _rate_docs_ux(self, docs_data: Dict) -> str:
        """Rate documentation user experience."""
        score = docs_data.get('score', 50)
        if score >= 80:
            return 'Excellent'
        elif score >= 60:
            return 'Good'
        else:
            return 'Needs Improvement'

    def _identify_coverage_areas(self, docs_data: Dict) -> str:
        """Identify documentation coverage areas."""
        return "Standard documentation areas assessed"

    def _generate_strategic_recommendations(self) -> str:
        """Generate strategic recommendations based on overall analysis."""
        overall_score = self.summary.get('overall_score', 0)
        
        if overall_score >= 80:
            return "Maintain current practices with minor optimizations"
        elif overall_score >= 60:
            return "Focus on targeted improvements in lower-scoring areas"
        else:
            return "Comprehensive improvement plan recommended across all areas"

    def _format_security_findings(self, findings: list) -> str:
        """Format security findings for display."""
        if not findings:
            return "No critical security issues detected in scan."
        
        formatted = []
        for i, finding in enumerate(findings[:3], 1):  # Limit to top 3
            if isinstance(finding, dict):
                formatted.append(f"{i}. {finding.get('title', 'Security Issue')}: {finding.get('description', 'Details available')}")
            else:
                formatted.append(f"{i}. {str(finding)}")
        
        return '\n'.join(formatted)

    def _format_quality_findings(self, findings: list) -> str:
        """Format quality findings for display."""
        if not findings:
            return "Code quality metrics within acceptable ranges."
        
        formatted = []
        for i, finding in enumerate(findings[:3], 1):
            if isinstance(finding, dict):
                formatted.append(f"{i}. {finding.get('metric', 'Quality Metric')}: {finding.get('value', 'Measured')}")
            else:
                formatted.append(f"{i}. {str(finding)}")
        
        return '\n'.join(formatted)

    def _format_docs_findings(self, findings: list) -> str:
        """Format documentation findings for display."""
        if not findings:
            return "Documentation structure and content reviewed."
        
        formatted = []
        for i, finding in enumerate(findings[:3], 1):
            if isinstance(finding, dict):
                formatted.append(f"{i}. {finding.get('area', 'Documentation Area')}: {finding.get('status', 'Assessed')}")
            else:
                formatted.append(f"{i}. {str(finding)}")
        
        return '\n'.join(formatted)

    def _requires_consensus_building(self, question: str) -> bool:
        """
        Determine if question requires Phase 3 advanced orchestration with consensus building.
        """
        question_lower = question.lower()
        
        # Consensus-requiring phrases
        consensus_phrases = [
            'consensus', 'agreement', 'conflicts', 'disagreements', 'contradictions',
            'priority', 'priorities', 'most important', 'critical issues',
            'trade-offs', 'balance', 'negotiate', 'decide between',
            'conflicting', 'different opinions', 'which should', 'what matters most',
            'reconcile', 'resolve differences', 'unified approach'
        ]
        
        # Advanced orchestration phrases  
        advanced_phrases = [
            'iterative', 'refine', 'improve', 'follow-up', 'deep dive',
            'comprehensive review', 'thorough analysis', 'detailed examination',
            'step-by-step', 'progressive', 'collaborative decision'
        ]
        
        return any(phrase in question_lower for phrase in consensus_phrases + advanced_phrases)
    
    def _advanced_orchestration_process(
        self,
        question: str,
        required_agents: list[str],
        provider_override: Optional[str] = None,
        api_key_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Phase 3: Advanced orchestration with consensus building and iterative refinement.
        """
        orchestration_log = []
        iterations = []
        
        orchestration_log.append("🎯 Phase 3 Advanced Orchestration initiated")
        orchestration_log.append(f"🤝 Consensus building required for: {', '.join(required_agents)}")
        
        # Step 1: Initial consultation
        orchestration_log.append("📋 Step 1: Initial agent consultation")
        initial_responses = self._get_initial_agent_responses(
            question, required_agents, provider_override, api_key_override
        )
        iterations.append({"step": "initial", "responses": initial_responses})
        
        # Step 2: Conflict detection and analysis
        orchestration_log.append("🔍 Step 2: Analyzing potential conflicts and overlaps")
        conflicts = self._detect_conflicts_and_overlaps(initial_responses)
        
        # Step 3: Consensus building if conflicts found
        final_responses = initial_responses
        if conflicts['has_conflicts']:
            orchestration_log.append("⚖️  Step 3: Resolving conflicts through consensus building")
            consensus_result = self._build_consensus(
                question, initial_responses, conflicts, 
                provider_override, api_key_override
            )
            final_responses.update(consensus_result['refined_responses'])
            iterations.append({"step": "consensus", "responses": consensus_result['refined_responses']})
            orchestration_log.extend(consensus_result['log'])
        else:
            orchestration_log.append("✅ Step 3: No significant conflicts detected")
        
        # Step 4: Advanced synthesis with priority negotiation
        orchestration_log.append("🎯 Step 4: Advanced synthesis with priority negotiation")
        synthesis_result = self._advanced_synthesis(
            question, final_responses, conflicts, 
            provider_override, api_key_override
        )
        
        orchestration_log.append("🏁 Phase 3 Advanced Orchestration completed")
        
        return {
            'agents': required_agents,
            'agent': 'advanced-orchestrator',
            'response': synthesis_result['synthesis'],
            'individual_responses': final_responses,
            'conflicts': conflicts,
            'iterations': iterations,
            'orchestration_log': orchestration_log,
            'routing_reason': f"Advanced orchestration with consensus building for: {', '.join(required_agents)}",
            'confidence': synthesis_result['confidence'],
            'multi_agent': True,
            'orchestration_level': 'phase3',
            'consensus_achieved': not conflicts['has_conflicts'] or len(iterations) > 1
        }

    def _build_synthesis_prompt(self, question: str, individual_responses: Dict[str, str]) -> str:
        """
        Build prompt for orchestrator to synthesize multi-agent responses.
        """
        prompt = f"""You are the Orchestrator Agent coordinating a multi-agent analysis.

ORIGINAL QUESTION: {question}

INDIVIDUAL AGENT RESPONSES:
"""
        
        agent_names = {
            'security': '🛡️ Security Agent', 
            'quality': '⚡ Quality Agent',
            'docs': '📚 Documentation Agent'
        }
        
        for agent_type, response in individual_responses.items():
            agent_name = agent_names.get(agent_type, f"{agent_type.title()} Agent")
            prompt += f"\n{agent_name}:\n{response}\n\n---\n"
        
        prompt += f"""
YOUR TASK as Orchestrator:
1. Synthesize these expert perspectives into a cohesive, comprehensive response
2. Identify overlapping concerns and complementary insights
3. Prioritize recommendations based on risk and impact
4. Present a unified action plan that addresses all aspects

SYNTHESIS GUIDELINES:
- Start with a brief executive summary
- Organize findings by priority/severity
- Show how different aspects (security/quality/docs) interconnect
- Provide clear, actionable next steps
- Maintain each agent's expertise while creating unity

FORMAT your response with:
## Executive Summary
## Key Findings (prioritized)
## Interconnected Issues  
## Recommended Action Plan

Repository Context: {self.report_data.get('repository', 'Unknown repository')}
Overall Assessment: {self.summary.get('overall_score', 'Not available')}/100

Provide a well-structured, professional synthesis that helps the user understand the complete picture and next steps.
"""
        
        return prompt
    
    def _get_initial_agent_responses(
        self, 
        question: str, 
        required_agents: list[str],
        provider_override: Optional[str] = None,
        api_key_override: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Get initial responses from all required agents.
        """
        responses = {}
        
        for agent_type in required_agents:
            try:
                print(f"DEBUG: Getting response from {agent_type} agent - provider: {provider_override}, api_key present: {api_key_override is not None}")
                prompt = self._build_agent_prompt(agent_type, question)
                llm_response = chat_with_llm(
                    question=prompt,
                    provider_override=provider_override,
                    api_key_override=api_key_override
                )
                responses[agent_type] = llm_response.get('answer', f'No response from {agent_type} agent.')
            except Exception as e:
                print(f"DEBUG: Error from {agent_type} agent: {str(e)}")
                responses[agent_type] = f"Error from {agent_type} agent: {str(e)}"
        
        return responses
    
    def _detect_conflicts_and_overlaps(self, responses: Dict[str, str]) -> Dict[str, Any]:
        """
        Analyze agent responses for conflicts, contradictions, and overlaps.
        """
        # Simple conflict detection based on keywords and sentiment
        conflicts = {
            'has_conflicts': False,
            'conflict_areas': [],
            'overlapping_concerns': [],
            'priority_disagreements': []
        }
        
        # Keywords that suggest conflicting priorities
        conflict_keywords = {
            'high_priority': ['critical', 'urgent', 'immediate', 'severe', 'high priority'],
            'low_priority': ['minor', 'low priority', 'not critical', 'optional', 'nice to have'],
            'positive_sentiment': ['good', 'excellent', 'well-done', 'appropriate', 'sufficient'],
            'negative_sentiment': ['poor', 'inadequate', 'missing', 'problematic', 'concerning']
        }
        
        # Detect overlapping concerns
        agent_topics = {}
        for agent, response in responses.items():
            response_lower = response.lower()
            topics = []
            if 'security' in response_lower or 'vulnerability' in response_lower:
                topics.append('security')
            if 'quality' in response_lower or 'code' in response_lower:
                topics.append('quality')
            if 'documentation' in response_lower or 'readme' in response_lower:
                topics.append('documentation')
            agent_topics[agent] = topics
        
        # Find overlapping areas
        all_topics = set()
        for topics in agent_topics.values():
            all_topics.update(topics)
        
        for topic in all_topics:
            agents_covering = [agent for agent, topics in agent_topics.items() if topic in topics]
            if len(agents_covering) > 1:
                conflicts['overlapping_concerns'].append({
                    'topic': topic,
                    'agents': agents_covering
                })
        
        # Detect priority conflicts (simplified)
        high_priority_agents = []
        low_priority_agents = []
        
        for agent, response in responses.items():
            response_lower = response.lower()
            if any(keyword in response_lower for keyword in conflict_keywords['high_priority']):
                high_priority_agents.append(agent)
            if any(keyword in response_lower for keyword in conflict_keywords['low_priority']):
                low_priority_agents.append(agent)
        
        if high_priority_agents and low_priority_agents:
            conflicts['has_conflicts'] = True
            conflicts['priority_disagreements'].append({
                'high_priority_agents': high_priority_agents,
                'low_priority_agents': low_priority_agents
            })
        
        return conflicts
    
    def _build_consensus(
        self,
        question: str,
        initial_responses: Dict[str, str],
        conflicts: Dict[str, Any],
        provider_override: Optional[str] = None,
        api_key_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Build consensus through iterative agent negotiation.
        """
        consensus_log = []
        refined_responses = {}
        
        consensus_log.append("🤝 Initiating consensus building process")
        
        # Create consensus building prompt for each agent
        for agent_type in initial_responses.keys():
            consensus_prompt = self._build_consensus_prompt(
                agent_type, question, initial_responses, conflicts
            )
            
            try:
                consensus_log.append(f"💭 Asking {agent_type} agent to consider other perspectives")
                consensus_response = chat_with_llm(
                    question=consensus_prompt,
                    provider_override=provider_override,
                    api_key_override=api_key_override
                )
                refined_responses[agent_type] = consensus_response.get('answer', initial_responses[agent_type])
                consensus_log.append(f"✅ {agent_type} agent provided refined perspective")
            except Exception as e:
                refined_responses[agent_type] = initial_responses[agent_type]
                consensus_log.append(f"⚠️ {agent_type} agent consensus failed: {str(e)}")
        
        return {
            'refined_responses': refined_responses,
            'log': consensus_log
        }
    
    def _build_consensus_prompt(
        self, 
        agent_type: str, 
        question: str, 
        all_responses: Dict[str, str], 
        conflicts: Dict[str, Any]
    ) -> str:
        """
        Build prompt for agent to reconsider their position given other agent perspectives.
        """
        agent_names = {
            'security': '🛡️ Security Agent', 
            'quality': '⚡ Quality Agent',
            'docs': '📚 Documentation Agent'
        }
        
        current_agent_name = agent_names.get(agent_type, f"{agent_type.title()} Agent")
        other_agents = {k: v for k, v in all_responses.items() if k != agent_type}
        
        prompt = f"""You are the {current_agent_name} participating in a consensus-building process.

ORIGINAL QUESTION: {question}

YOUR INITIAL RESPONSE:
{all_responses[agent_type]}

OTHER AGENT PERSPECTIVES:
"""
        
        for other_agent, response in other_agents.items():
            other_name = agent_names.get(other_agent, f"{other_agent.title()} Agent")
            prompt += f"\n{other_name}:\n{response}\n\n"
        
        if conflicts['has_conflicts']:
            prompt += f"""
IDENTIFIED CONFLICTS:
"""
            if conflicts['priority_disagreements']:
                prompt += "- Priority level disagreements detected\n"
            if conflicts['overlapping_concerns']:
                prompt += f"- Overlapping concerns: {', '.join([c['topic'] for c in conflicts['overlapping_concerns']])}\n"
        
        prompt += f"""
CONSENSUS BUILDING TASK:
1. Review other agents' perspectives carefully
2. Identify where you agree or disagree and why  
3. Consider if your initial assessment needs adjustment
4. Provide a refined response that:
   - Maintains your core expertise and concerns
   - Acknowledges valid points from other agents
   - Suggests how to address any conflicts or overlaps
   - Proposes collaborative solutions where possible

Please provide your refined perspective as the {current_agent_name}:
"""
        
        return prompt
    
    def _advanced_synthesis(
        self,
        question: str,
        final_responses: Dict[str, str],
        conflicts: Dict[str, Any],
        provider_override: Optional[str] = None,
        api_key_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Advanced synthesis with priority negotiation and conflict resolution.
        """
        synthesis_prompt = self._build_advanced_synthesis_prompt(question, final_responses, conflicts)
        
        try:
            # Add debug information
            print(f"DEBUG: Advanced synthesis - provider: {provider_override}, api_key present: {api_key_override is not None}")
            
            synthesis_response = chat_with_llm(
                question=synthesis_prompt,
                provider_override=provider_override,
                api_key_override=api_key_override
            )
            synthesized_answer = synthesis_response.get('answer', 'Unable to perform advanced synthesis.')
            confidence = 0.92  # Higher confidence due to consensus process
        except Exception as e:
            print(f"DEBUG: Advanced synthesis error: {str(e)}")
            synthesized_answer = f"Error in advanced synthesis: {str(e)}"
            confidence = 0.70
        
        return {
            'synthesis': synthesized_answer,
            'confidence': confidence
        }
    
    def _build_advanced_synthesis_prompt(
        self, 
        question: str, 
        responses: Dict[str, str], 
        conflicts: Dict[str, Any]
    ) -> str:
        """
        Build advanced synthesis prompt with conflict resolution guidance.
        """
        prompt = f"""You are the Advanced Orchestrator conducting Phase 3 synthesis with consensus building.

ORIGINAL QUESTION: {question}

AGENT RESPONSES (after consensus building):
"""
        
        agent_names = {
            'security': '🛡️ Security Agent', 
            'quality': '⚡ Quality Agent',
            'docs': '📚 Documentation Agent'
        }
        
        for agent_type, response in responses.items():
            agent_name = agent_names.get(agent_type, f"{agent_type.title()} Agent")
            prompt += f"\n{agent_name}:\n{response}\n\n---\n"
        
        if conflicts['has_conflicts']:
            prompt += f"""
CONFLICT ANALYSIS:
- Overlapping concerns: {len(conflicts['overlapping_concerns'])} areas
- Priority disagreements: {'Yes' if conflicts['priority_disagreements'] else 'No'}
- Consensus building applied: Agents have refined their perspectives

"""
        
        prompt += f"""
ADVANCED SYNTHESIS TASK:
You must create a sophisticated synthesis that:

1. **Executive Summary**: Clear overview acknowledging complexity and nuance
2. **Consensus Areas**: Highlight where agents agree and reinforce these points  
3. **Resolved Conflicts**: Show how apparent conflicts were resolved through consensus
4. **Prioritized Action Plan**: Create unified priorities balancing all perspectives
5. **Implementation Strategy**: Practical steps that address all agent concerns
6. **Success Metrics**: How to measure progress across all domains

ADVANCED SYNTHESIS GUIDELINES:
- Acknowledge the consensus-building process used
- Show how different expertise areas complement each other
- Present a unified strategy that optimizes across all concerns
- Include specific, actionable recommendations with clear ownership
- Address potential implementation challenges proactively
- Demonstrate sophisticated understanding of trade-offs and dependencies

FORMAT: Use clear headings and prioritized sections for maximum impact.

Begin your advanced synthesis:
"""
        
        return prompt