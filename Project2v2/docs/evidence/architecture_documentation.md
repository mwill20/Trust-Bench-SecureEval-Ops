Trust Bench v3.0 Architecture Documentation
============================================

## Overview
The Trust Bench SecureEval + Ops v3.0 architecture represents a comprehensive security evaluation platform with integrated operational capabilities and observability features.

## Architecture Files
- `architecture_v3.png` - High-resolution architecture diagram (PNG format)
- `architecture_v3.svg` - Vector-based architecture diagram (SVG format, scalable)

## Architecture Components

### Ops & Observability Layer
**Structured JSON Logs**
- Run ID correlation for traceability
- JSON-formatted logging via `Project2v2/app/logging.py`
- Centralized log aggregation capabilities

**Health Probes**
- `/healthz` endpoint for liveness checks
- `/readyz` endpoint for readiness verification
- Real-time system status monitoring

**CI Pipeline**
- Automated testing with pytest coverage
- Repository validation and scoring
- Security scanning with pip-audit
- GitHub Actions integration

### SecureEval Envelope
**Input Validation**
- Pydantic-based schema validation
- Repository URL sanitization
- Malicious input detection and blocking

**Output Clamping**
- 10K character limits for safety
- Content sanitization and escaping
- Sensitive data redaction policies

**Sandbox Execution**
- Allow-list based command filtering  
- Restricted execution environment
- Safe subprocess management

**Resilience Patterns**
- Retry mechanisms with exponential backoff
- Configurable timeout protection
- Graceful failure handling

### LangGraph Multi-Agent Orchestrator
**Specialized Agents**
- Security Agent: Vulnerability detection and analysis
- Code Quality Agent: Static analysis and best practices
- Documentation Agent: Completeness and clarity assessment
- Manager/Orchestrator: Coordination and decision routing

**Collaborative Evaluation Flow**
- Dynamic agent selection based on query complexity
- Cross-agent consultation for comprehensive analysis
- Consensus-building and conflict resolution
- Deterministic report generation

### Output Generation
**Deterministic Reports**
- JSON structured data with metrics and scores
- Markdown human-readable summaries  
- Bundle packages with complete evidence
- Audit trails and traceability information

## Technical Stack
- **Framework**: LangGraph for agent orchestration
- **Security**: Pydantic validation, sandboxed execution
- **Observability**: Structured logging, health endpoints
- **CI/CD**: GitHub Actions, automated testing
- **Documentation**: Comprehensive evidence generation

## Version History
- v1.0: Basic multi-agent evaluation
- v2.0: Enhanced UI and routing capabilities  
- v3.0: SecureEval + Ops integration with full observability

## Usage
This architecture supports enterprise-grade security evaluation with:
- Production-ready operational capabilities
- Comprehensive audit trails and evidence generation
- Scalable multi-agent processing
- Complete CI/CD integration
- SOC 2-lite compliance controls

Created: October 27, 2025
Version: Trust Bench v3.0 SecureEval + Ops