# Village to Town: Bangladesh Development Simulation

This project simulates the transformation of a Bangladeshi village into a thriving town using an agent-based model built with Mesa. It captures households, businesses, and infrastructure interacting under policy interventions to track outcomes like GDP per capita, service access, urbanization, and inequality.

## Features

- **Detailed Agents**: Households with education/health decisions, businesses across sectors, infrastructure development
- **Bangladeshi Context**: Rural-urban migration patterns, agricultural economy, traditional social structures
- **Policy Interventions**: Roads, schools, clinics, markets, utilities, microfinance programs
- **Real-time Visualization**: Web-based interface showing spatial development
- **Data Export**: CSV outputs for analysis and research

## Quick Start (Windows)

1. Create and activate virtual environment:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:
```powershell
pip install -r requirements.txt
```

3. Run web visualization:
```powershell
python -m vtown.server
```
Open http://127.0.0.1:8521

4. Run headless simulation:
```powershell
python -m vtown.run_headless --config vtown/config/default.yaml --steps 200 --output outputs/
```

## Model Overview

### Agents
- **Households**: Make education/health investments, migrate, change occupations
- **Businesses**: Operate in agriculture, manufacturing, services sectors
- **Infrastructure**: Roads, schools, clinics, markets, utilities with coverage areas

### Dynamics
- Migration from rural areas to developing town center
- Sector transitions from agriculture to manufacturing/services
- Infrastructure development improving access and productivity
- Policy interventions affecting development trajectories

### Metrics
- GDP per capita, Gini coefficient (inequality)
- Infrastructure coverage, service access rates
- Urbanization rate, average education/health levels
- Population distribution and economic activity

## Project Structure

```
vtown/
├── agents.py          # Agent definitions
├── model.py           # Main simulation model
├── policy.py          # Policy engine
├── server.py          # Web visualization
├── run_headless.py    # Batch runner
├── config/
│   └── default.yaml   # Default parameters
└── utils.py           # Helper functions
```

## Configuration

Parameters can be adjusted in `vtown/config/default.yaml`:
- Population size and composition
- Economic parameters (wages, productivity)
- Infrastructure costs and effects
- Policy intervention budgets
- Spatial parameters

## Outputs

- `model_metrics.csv`: Time series of aggregate indicators
- `agent_data.csv`: Individual agent states over time
- `infrastructure_log.csv`: Infrastructure development history

## License

MIT License - See LICENSE file for details
