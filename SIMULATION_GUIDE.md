# Village to Town: Bangladesh Development Simulation Guide

## 🏘️ Overview

This project simulates the transformation of a Bangladeshi village into a thriving town using agent-based modeling with Mesa. The simulation captures realistic development dynamics including:

- **Household decisions**: Education, health, migration, and sector transitions
- **Business dynamics**: Growth, employment, and productivity changes  
- **Infrastructure development**: Roads, schools, clinics, markets, and utilities
- **Policy interventions**: Government budget allocation and development programs

## 🚀 Quick Start

### Installation
```powershell
# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Run Web Visualization
```powershell
python -m vtown server
```
Open http://127.0.0.1:8521 to see the interactive simulation.

### Run Headless Simulation
```powershell
# Single simulation (100 steps)
python -m vtown run --steps 100 --output results/

# Batch runs for research
python -m vtown run --runs 10 --steps 200 --output batch_results/
```

## 🎯 What You'll See

### Visual Elements
- **🟢 Green circles**: Agricultural households  
- **🔵 Blue circles**: Manufacturing workers
- **🟡 Gold circles**: Service sector workers
- **🟩 Green squares**: Agricultural businesses
- **🟥 Red squares**: Manufacturing businesses  
- **🟧 Orange squares**: Service businesses
- **🛤️ Gray**: Roads
- **🏫 Gold**: Schools
- **🏥 Red**: Health clinics
- **🏪 Purple**: Markets
- **⚡ Teal**: Utilities

### Key Metrics Tracked
- **GDP per capita**: Economic development indicator
- **Gini coefficient**: Income inequality (0=equal, 1=unequal)
- **Urbanization rate**: % population in town center
- **Infrastructure coverage**: Access to services
- **Sector employment**: Agricultural → manufacturing → services transition

## 📊 Understanding the Development Process

### Phase 1: Agricultural Village (Steps 0-50)
- Most households work in agriculture
- Low income but low inequality
- Limited infrastructure
- Rural settlement pattern

### Phase 2: Early Development (Steps 50-100)
- Infrastructure investments begin
- Some migration to town center
- Manufacturing businesses emerge
- Income starts to grow

### Phase 3: Town Formation (Steps 100-200)
- Significant urbanization
- Service sector development
- Education and health improvements
- Infrastructure network formation

### Phase 4: Mature Town (Steps 200+)
- Balanced economic structure
- High service access rates
- Reduced agricultural dependency
- Potential inequality concerns

## 🛠️ Model Components

### Agents

**Households (200 initial)**
- Make education/health investment decisions
- Migrate based on economic opportunities
- Switch between economic sectors
- Accumulate savings and improve living standards

**Businesses (30 initial)**
- Operate in agriculture, manufacturing, or services
- Hire workers and generate economic activity
- Expand based on profitability
- Benefit from infrastructure access

**Infrastructure**
- **Roads**: Improve connectivity and reduce transport costs
- **Schools**: Boost education levels and productivity
- **Clinics**: Improve health outcomes and workforce quality
- **Markets**: Facilitate trade and business development
- **Utilities**: Enable modern economic activities

### Policy Engine
Automatically allocates annual budget (100,000 Taka default) across:
- Infrastructure development (50%)
- Education programs (15%)
- Health programs (15%) 
- Economic development (10%)
- Direct grants and microfinance (10%)

Policy priorities adapt based on development needs assessment.

## 📈 Analyzing Results

### Model Metrics (`model_metrics.csv`)
Time series data including:
- Population and business counts
- Economic indicators (GDP, Gini)
- Human development (education, health)
- Infrastructure coverage by type
- Sector employment distribution

### Agent Data (`agent_data.csv`)
Individual agent snapshots showing:
- Household income, education, health
- Business revenue, size, employees
- Infrastructure quality and coverage
- Spatial positions over time

## 🔧 Configuration

Edit `vtown/config/default.yaml` to adjust:

```yaml
# Population and economy
initial_population: 200
initial_businesses: 30
policy_budget: 100000

# Spatial setup  
grid_width: 50
grid_height: 50

# Development parameters
base_wages:
  agriculture: 2500
  manufacturing: 4000
  services: 5000

# Infrastructure costs
infrastructure_costs:
  road: 10000
  school: 50000
  clinic: 30000
  market: 20000
  utility: 40000
```

## 🔬 Research Applications

### Parameter Studies
- Vary policy budgets to test development strategies
- Adjust infrastructure costs to model different contexts
- Change initial conditions to explore path dependency

### Policy Experiments
- Infrastructure prioritization strategies
- Education vs. health investment trade-offs
- Direct transfers vs. infrastructure spending
- Rural development vs. urbanization policies

### Sensitivity Analysis
- Run multiple simulations with different random seeds
- Test model robustness to parameter changes
- Identify key leverage points for development

## 🎓 Educational Use

### Concepts Demonstrated
- **Agent-based modeling**: Emergent phenomena from individual decisions
- **Development economics**: Infrastructure-growth relationships
- **Spatial economics**: Agglomeration and urbanization
- **Policy analysis**: Budget allocation and intervention design

### Learning Exercises
1. **Experiment with policies**: Change budget allocations and observe outcomes
2. **Compare scenarios**: Run with/without specific infrastructure types
3. **Analyze inequality**: Track how development affects income distribution
4. **Study migration**: Observe spatial patterns of development

## 🐛 Troubleshooting

### Common Issues

**Warning messages about agent placement**
- Normal Mesa behavior when multiple agents occupy same cell
- Does not affect simulation functionality

**Negative Gini coefficients**
- Can occur with small populations or unusual income distributions
- Consider increasing population or adjusting income parameters

**Slow performance**
- Reduce grid size or population for faster runs
- Use headless mode for large batch experiments

### Getting Help
- Check configuration file for parameter explanations
- Review agent behavior in `vtown/agents.py`
- Examine policy logic in `vtown/policy.py`

## 📚 Extensions

### Potential Enhancements
- **Climate effects**: Add environmental constraints and shocks
- **Trade networks**: Model connections between multiple villages
- **Financial systems**: Include banks, credit, and investment
- **Demographics**: Add age structure and lifecycle effects
- **Technology**: Include innovation diffusion and productivity growth

### Data Integration
- Use real Bangladeshi village data for initialization
- Calibrate parameters to match empirical development patterns
- Validate outputs against historical development trajectories

## 🤝 Contributing

This simulation provides a foundation for exploring development dynamics. Feel free to:
- Add new agent types or behaviors
- Implement additional infrastructure types
- Create new policy interventions
- Develop alternative spatial arrangements
- Add economic complexity or social dynamics

The modular design makes it easy to extend while maintaining the core simulation engine.

---

**Happy Simulating!** 🎉

This tool can help researchers, policymakers, and students better understand the complex dynamics of rural-urban transformation and development policy impacts.
