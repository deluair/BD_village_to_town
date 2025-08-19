# Village to Town: Bangladesh Development Simulation

This project simulates the transformation of a Bangladeshi village into a thriving town using an agent-based model built with Mesa. It captures households, businesses, and infrastructure interacting under policy interventions to track outcomes like GDP per capita, service access, urbanization, and inequality.

Developed with authentic Bangladesh rural context including flood risks, remittances, cooperative membership, microfinance access, and rural-urban wage differentials based on real-world development patterns from the Comilla Model, BRAC programs, and Bangladesh's rural transformation experience.

## Features

- **Realistic Bangladesh Context**: 
  - Flood risks (15% annual probability) affecting income and savings
  - Remittances (25% of households receive external income)
  - Cooperative membership (35% participation with income benefits)  
  - Microfinance access (45% coverage for health/education investments)
  - Landless households (40% rate) with lower agricultural incomes
  - Off-grid solar electricity (12% coverage)
  - Rural-urban wage gaps (1.8x premium for urban manufacturing/services)

- **Detailed Agent Behaviors**: 
  - Households make education/health investments, migrate, change sectors
  - Flood-driven sector transitions and recovery patterns
  - Cooperative benefits for education/training access
  - Microfinance-enabled health investments

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
- Migration from rural areas to developing town center with rural-urban wage premiums
- Flood-driven sector transitions and agricultural household vulnerability
- Landless agricultural workers switching to manufacturing/services
- Cooperative membership providing education/health program access
- Remittance flows supplementing household incomes
- Microfinance enabling health investments and small business development
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
- **Population & Demographics**: Household sizes (3-7), sector distribution (70% agriculture)
- **Economic Parameters**: Bangladesh wages (Agri: 10k, Mfg: 15k, Services: 18k Taka/month)
- **Bangladesh-Specific Factors**: 
  - Flood risk probability (15%)
  - Remittance receiving rate (25%)
  - Cooperative membership (35%)
  - Microfinance access (45%)
  - Landless household rate (40%)
  - Off-grid electricity coverage (12%)
  - Rural-urban wage multiplier (1.8x)
- **Infrastructure**: Costs, coverage areas, and productivity effects
- **Policy Budgets**: Infrastructure development, microfinance, education/health programs

## Outputs

- `model_metrics.csv`: Time series of aggregate indicators (GDP, Gini, urbanization, etc.)
- `agent_data.csv`: Individual agent states over time (income, education, sector, flood status, etc.)

## Bangladesh Development Context

This simulation incorporates real-world Bangladesh rural development patterns:

- **Comilla Model**: Cooperative-based rural development with infrastructure and training
- **BRAC Programs**: Microfinance, non-formal education, and health services
- **Grameen Bank**: Collateral-free microcredit for rural women
- **Solar Home Systems**: Off-grid electrification reaching 12% of rural households
- **Flood Resilience**: Annual monsoon flooding affecting livelihoods and recovery
- **Remittance Economy**: Overseas workers supporting rural families
- **Landless Agricultural Labor**: Sharecropping and daily wage patterns

## Research Applications

- **Policy Analysis**: Test infrastructure vs. social program investments
- **Resilience Studies**: Examine flood recovery and adaptation strategies  
- **Development Economics**: Model rural transformation and inequality dynamics
- **Cooperative Impact**: Assess collective action benefits on development outcomes

## License

MIT License - See LICENSE file for details
