"""
Web visualization server for the Village to Town simulation.

This module provides a Mesa-based web interface for real-time visualization
of the simulation, allowing users to observe the development process
and interact with model parameters.
"""

import mesa
from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserActivatedAgent import UserActivatedAgent

from .model import TownDevelopmentModel
from .agents import HouseholdAgent, BusinessAgent, InfrastructureAgent


def agent_portrayal(agent):
    """
    Define how agents are displayed in the visualization.
    
    Returns a dictionary with visualization properties for each agent type.
    """
    if isinstance(agent, HouseholdAgent):
        portrayal = {
            "Shape": "circle",
            "Filled": "true",
            "Layer": 1,
            "r": 0.6,
        }
        
        # Color based on sector
        if agent.sector == "agriculture":
            portrayal["Color"] = "#8FBC8F"  # Light green
        elif agent.sector == "manufacturing":
            portrayal["Color"] = "#4682B4"  # Steel blue
        else:  # services
            portrayal["Color"] = "#DAA520"  # Golden rod
            
        # Size based on income level
        if agent.income > 6000:
            portrayal["r"] = 0.8
        elif agent.income < 3000:
            portrayal["r"] = 0.4
            
        # Add text showing household size
        portrayal["text"] = str(agent.household_size)
        portrayal["text_color"] = "white"
        
    elif isinstance(agent, BusinessAgent):
        portrayal = {
            "Shape": "rect",
            "Filled": "true",
            "Layer": 2,
            "w": 0.8,
            "h": 0.8,
        }
        
        # Color based on business type
        if agent.business_type == "agriculture":
            portrayal["Color"] = "#228B22"  # Forest green
        elif agent.business_type == "manufacturing":
            portrayal["Color"] = "#DC143C"  # Crimson
        else:  # services
            portrayal["Color"] = "#FF8C00"  # Dark orange
            
        # Size based on business size
        if agent.size == "large":
            portrayal["w"] = 1.0
            portrayal["h"] = 1.0
        elif agent.size == "small":
            portrayal["w"] = 0.6
            portrayal["h"] = 0.6
            
        # Add text showing employee count
        portrayal["text"] = str(agent.current_employees)
        portrayal["text_color"] = "white"
        
    elif isinstance(agent, InfrastructureAgent):
        portrayal = {
            "Shape": "rect",
            "Filled": "true",
            "Layer": 0,
            "w": 1.0,
            "h": 1.0,
        }
        
        # Color and symbol based on infrastructure type
        if agent.infrastructure_type == "road":
            portrayal["Color"] = "#696969"  # Dim gray
            portrayal["text"] = "🛤️"
        elif agent.infrastructure_type == "school":
            portrayal["Color"] = "#FFD700"  # Gold
            portrayal["text"] = "🏫"
        elif agent.infrastructure_type == "clinic":
            portrayal["Color"] = "#FF6347"  # Tomato
            portrayal["text"] = "🏥"
        elif agent.infrastructure_type == "market":
            portrayal["Color"] = "#9370DB"  # Medium purple
            portrayal["text"] = "🏪"
        elif agent.infrastructure_type == "utility":
            portrayal["Color"] = "#20B2AA"  # Light sea green
            portrayal["text"] = "⚡"
            
        # Opacity based on quality
        portrayal["opacity"] = max(0.3, agent.quality)
        
        portrayal["text_color"] = "white"
        
    return portrayal


def get_happy_agents(model):
    """Count agents with above-average income (happiness proxy)."""
    households = [agent for agent in model.schedule.agents 
                 if isinstance(agent, HouseholdAgent)]
    
    if not households:
        return 0
        
    avg_income = sum(h.income for h in households) / len(households)
    return sum(1 for h in households if h.income > avg_income)


# Define the grid visualization
grid = CanvasGrid(
    agent_portrayal, 
    50,  # Grid width
    50,  # Grid height  
    500, # Canvas width in pixels
    500  # Canvas height in pixels
)

# Define charts for tracking key metrics
gdp_chart = ChartModule([
    {"Label": "GDP_Per_Capita", "Color": "#3498db"},
], data_collector_name='datacollector')

population_chart = ChartModule([
    {"Label": "Population", "Color": "#e74c3c"},
    {"Label": "Total_Businesses", "Color": "#f39c12"},
], data_collector_name='datacollector')

development_chart = ChartModule([
    {"Label": "Average_Education", "Color": "#9b59b6"},
    {"Label": "Average_Health", "Color": "#1abc9c"},
    {"Label": "Urbanization_Rate", "Color": "#34495e"},
], data_collector_name='datacollector')

sector_chart = ChartModule([
    {"Label": "Agricultural_Employment", "Color": "#27ae60"},
    {"Label": "Manufacturing_Employment", "Color": "#2980b9"},
    {"Label": "Services_Employment", "Color": "#f1c40f"},
], data_collector_name='datacollector')

infrastructure_chart = ChartModule([
    {"Label": "Road_Coverage", "Color": "#95a5a6"},
    {"Label": "School_Coverage", "Color": "#f39c12"},
    {"Label": "Clinic_Coverage", "Color": "#e74c3c"},
    {"Label": "Market_Coverage", "Color": "#9b59b6"},
    {"Label": "Utility_Coverage", "Color": "#1abc9c"},
], data_collector_name='datacollector')

inequality_chart = ChartModule([
    {"Label": "Gini_Coefficient", "Color": "#e67e22"},
    {"Label": "Service_Access_Rate", "Color": "#16a085"},
], data_collector_name='datacollector')


# Model parameters that can be adjusted in the web interface
model_params = {
    "initial_population": mesa.visualization.Slider(
        "Initial Population",
        200,   # Default value
        50,    # Minimum
        500,   # Maximum
        25     # Step size
    ),
    "initial_businesses": mesa.visualization.Slider(
        "Initial Businesses",
        30,    # Default value
        10,    # Minimum
        100,   # Maximum
        5      # Step size
    ),
    "policy_budget": mesa.visualization.Slider(
        "Annual Policy Budget (Taka)",
        100000,  # Default value
        50000,   # Minimum
        500000,  # Maximum
        25000    # Step size
    ),
    "grid_width": mesa.visualization.Slider(
        "Grid Width",
        50,    # Default value
        30,    # Minimum
        100,   # Maximum
        10     # Step size
    ),
    "grid_height": mesa.visualization.Slider(
        "Grid Height", 
        50,    # Default value
        30,    # Minimum
        100,   # Maximum
        10     # Step size
    ),
}

# Create the modular server
server = ModularServer(
    TownDevelopmentModel,
    [
        grid,
        gdp_chart,
        population_chart,
        development_chart,
        sector_chart,
        infrastructure_chart,
        inequality_chart
    ],
    "Village to Town Development Simulation",
    model_params
)

# Set the port
server.port = 8521


def launch_server():
    """Launch the visualization server."""
    print("Starting Village to Town Development Simulation Server...")
    print("Open your browser to http://127.0.0.1:8521")
    print("\nVisualization Guide:")
    print("- Circles: Households (green=agriculture, blue=manufacturing, gold=services)")
    print("- Squares: Businesses (green=agriculture, red=manufacturing, orange=services)")
    print("- Infrastructure: Roads🛤️, Schools🏫, Clinics🏥, Markets🏪, Utilities⚡")
    print("- Size indicates economic level, opacity shows infrastructure quality")
    print("\nControls:")
    print("- Adjust parameters in the left panel")
    print("- Click 'Reset' to restart with new parameters")
    print("- Click 'Step' for single step or 'Start' for continuous simulation")
    print("\nPress Ctrl+C to stop the server")
    
    server.launch()


if __name__ == "__main__":
    launch_server()
