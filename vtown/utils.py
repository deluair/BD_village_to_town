"""
Utility functions for the Village to Town simulation.

This module provides helper functions for data analysis,
visualization, and common calculations used throughout the simulation.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional, Any
import os


def calculate_gini_coefficient(incomes: List[float]) -> float:
    """
    Calculate Gini coefficient for income inequality.
    
    Args:
        incomes: List of income values
        
    Returns:
        Gini coefficient (0 = perfect equality, 1 = perfect inequality)
    """
    if not incomes or len(incomes) < 2:
        return 0.0
        
    # Remove any negative or zero incomes
    incomes = [i for i in incomes if i > 0]
    
    if len(incomes) < 2:
        return 0.0
        
    incomes = sorted(incomes)
    n = len(incomes)
    cumsum = np.cumsum(incomes)
    
    return (n + 1 - 2 * sum((n + 1 - i) * income for i, income in enumerate(incomes, 1))) / (n * sum(incomes))


def calculate_spatial_statistics(agents, grid_width: int, grid_height: int) -> Dict[str, float]:
    """
    Calculate spatial distribution statistics for agents.
    
    Args:
        agents: List of agents with position attributes
        grid_width: Width of the simulation grid
        grid_height: Height of the simulation grid
        
    Returns:
        Dictionary of spatial statistics
    """
    if not agents:
        return {
            'center_of_mass_x': grid_width / 2,
            'center_of_mass_y': grid_height / 2,
            'spatial_dispersion': 0,
            'clustering_index': 0
        }
    
    positions = [agent.pos for agent in agents if hasattr(agent, 'pos')]
    
    if not positions:
        return {
            'center_of_mass_x': grid_width / 2,
            'center_of_mass_y': grid_height / 2,
            'spatial_dispersion': 0,
            'clustering_index': 0
        }
    
    # Center of mass
    center_x = sum(pos[0] for pos in positions) / len(positions)
    center_y = sum(pos[1] for pos in positions) / len(positions)
    
    # Spatial dispersion (average distance from center of mass)
    distances = [np.sqrt((pos[0] - center_x)**2 + (pos[1] - center_y)**2) for pos in positions]
    spatial_dispersion = sum(distances) / len(distances)
    
    # Clustering index (average distance to nearest neighbor)
    nearest_neighbor_distances = []
    for i, pos1 in enumerate(positions):
        min_distance = float('inf')
        for j, pos2 in enumerate(positions):
            if i != j:
                distance = np.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
                min_distance = min(min_distance, distance)
        if min_distance != float('inf'):
            nearest_neighbor_distances.append(min_distance)
    
    clustering_index = sum(nearest_neighbor_distances) / len(nearest_neighbor_distances) if nearest_neighbor_distances else 0
    
    return {
        'center_of_mass_x': center_x,
        'center_of_mass_y': center_y,
        'spatial_dispersion': spatial_dispersion,
        'clustering_index': clustering_index
    }


def analyze_development_trajectory(model_data: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze the development trajectory from simulation data.
    
    Args:
        model_data: DataFrame with model metrics over time
        
    Returns:
        Dictionary with trajectory analysis
    """
    if model_data.empty:
        return {}
    
    analysis = {}
    
    # Growth rates
    initial_gdp = model_data['GDP_Per_Capita'].iloc[0]
    final_gdp = model_data['GDP_Per_Capita'].iloc[-1]
    steps = len(model_data)
    
    if initial_gdp > 0:
        gdp_growth_rate = ((final_gdp / initial_gdp) ** (1/steps) - 1) * 100
        analysis['gdp_growth_rate_per_step'] = gdp_growth_rate
    
    # Development phases
    urbanization = model_data['Urbanization_Rate'].values
    analysis['urbanization_phases'] = identify_development_phases(urbanization)
    
    # Infrastructure development pattern
    infrastructure_cols = ['Road_Coverage', 'School_Coverage', 'Clinic_Coverage', 
                          'Market_Coverage', 'Utility_Coverage']
    
    infrastructure_data = model_data[infrastructure_cols]
    analysis['infrastructure_development'] = analyze_infrastructure_pattern(infrastructure_data)
    
    # Inequality trajectory
    gini_values = model_data['Gini_Coefficient'].values
    analysis['inequality_trend'] = analyze_inequality_trend(gini_values)
    
    # Sector transition
    sector_cols = ['Agricultural_Employment', 'Manufacturing_Employment', 'Services_Employment']
    if all(col in model_data.columns for col in sector_cols):
        sector_data = model_data[sector_cols]
        analysis['sector_transition'] = analyze_sector_transition(sector_data)
    
    return analysis


def identify_development_phases(urbanization: np.ndarray) -> List[Dict[str, Any]]:
    """Identify distinct phases of urban development."""
    phases = []
    
    if len(urbanization) < 10:
        return phases
    
    # Calculate growth rates
    growth_rates = np.diff(urbanization)
    
    # Identify phases based on growth rate changes
    current_phase = {'start': 0, 'type': 'initial'}
    
    for i in range(1, len(growth_rates)):
        if i > 5:  # Minimum phase length
            recent_growth = np.mean(growth_rates[max(0, i-5):i])
            
            if recent_growth > 0.01:  # High growth
                if current_phase['type'] != 'rapid_growth':
                    phases.append(current_phase)
                    current_phase = {'start': i, 'type': 'rapid_growth'}
            elif recent_growth > 0.005:  # Moderate growth
                if current_phase['type'] != 'steady_growth':
                    phases.append(current_phase)
                    current_phase = {'start': i, 'type': 'steady_growth'}
            else:  # Slow/no growth
                if current_phase['type'] != 'stagnation':
                    phases.append(current_phase)
                    current_phase = {'start': i, 'type': 'stagnation'}
    
    # Add final phase
    current_phase['end'] = len(urbanization) - 1
    phases.append(current_phase)
    
    return phases


def analyze_infrastructure_pattern(infrastructure_data: pd.DataFrame) -> Dict[str, Any]:
    """Analyze infrastructure development patterns."""
    analysis = {}
    
    # Total infrastructure development
    total_infrastructure = infrastructure_data.sum(axis=1)
    analysis['total_growth'] = total_infrastructure.iloc[-1] - total_infrastructure.iloc[0]
    
    # Infrastructure type priorities (which was built first/most)
    final_values = infrastructure_data.iloc[-1]
    analysis['infrastructure_ranking'] = final_values.sort_values(ascending=False).to_dict()
    
    # Development timing (when each type started growing)
    development_timing = {}
    for col in infrastructure_data.columns:
        values = infrastructure_data[col].values
        first_growth = np.where(np.diff(values) > 0)[0]
        if len(first_growth) > 0:
            development_timing[col] = first_growth[0]
        else:
            development_timing[col] = len(values)
    
    analysis['development_timing'] = development_timing
    
    return analysis


def analyze_inequality_trend(gini_values: np.ndarray) -> Dict[str, Any]:
    """Analyze inequality trends over time."""
    analysis = {}
    
    if len(gini_values) < 2:
        return analysis
    
    initial_gini = gini_values[0]
    final_gini = gini_values[-1]
    
    analysis['initial_inequality'] = initial_gini
    analysis['final_inequality'] = final_gini
    analysis['inequality_change'] = final_gini - initial_gini
    
    # Find peak inequality
    max_gini_idx = np.argmax(gini_values)
    analysis['peak_inequality'] = {
        'value': gini_values[max_gini_idx],
        'step': max_gini_idx
    }
    
    # Trend classification
    if final_gini < initial_gini - 0.05:
        analysis['trend'] = 'decreasing'
    elif final_gini > initial_gini + 0.05:
        analysis['trend'] = 'increasing'
    else:
        analysis['trend'] = 'stable'
    
    return analysis


def analyze_sector_transition(sector_data: pd.DataFrame) -> Dict[str, Any]:
    """Analyze sector transition patterns."""
    analysis = {}
    
    # Calculate sector shares over time
    total_employment = sector_data.sum(axis=1)
    sector_shares = sector_data.div(total_employment, axis=0)
    
    # Initial and final composition
    initial_shares = sector_shares.iloc[0].to_dict()
    final_shares = sector_shares.iloc[-1].to_dict()
    
    analysis['initial_composition'] = initial_shares
    analysis['final_composition'] = final_shares
    
    # Transition pattern
    changes = {}
    for sector in sector_shares.columns:
        changes[sector] = final_shares[sector] - initial_shares[sector]
    
    analysis['sector_changes'] = changes
    
    # Identify dominant transition
    max_increase = max(changes.values())
    max_decrease = min(changes.values())
    
    if abs(max_decrease) > max_increase:
        declining_sector = [k for k, v in changes.items() if v == max_decrease][0]
        analysis['primary_transition'] = f"decline_of_{declining_sector}"
    else:
        growing_sector = [k for k, v in changes.items() if v == max_increase][0]
        analysis['primary_transition'] = f"growth_of_{growing_sector}"
    
    return analysis


def create_development_plots(model_data: pd.DataFrame, output_dir: str = "plots"):
    """
    Create visualization plots for development analysis.
    
    Args:
        model_data: DataFrame with simulation results
        output_dir: Directory to save plots
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Set style
    plt.style.use('seaborn-v0_8')
    
    # 1. Economic development over time
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # GDP per capita
    axes[0, 0].plot(model_data['Step'], model_data['GDP_Per_Capita'])
    axes[0, 0].set_title('GDP per Capita Over Time')
    axes[0, 0].set_xlabel('Step')
    axes[0, 0].set_ylabel('GDP per Capita (Taka)')
    
    # Inequality
    axes[0, 1].plot(model_data['Step'], model_data['Gini_Coefficient'], color='red')
    axes[0, 1].set_title('Income Inequality (Gini Coefficient)')
    axes[0, 1].set_xlabel('Step')
    axes[0, 1].set_ylabel('Gini Coefficient')
    
    # Urbanization
    axes[1, 0].plot(model_data['Step'], model_data['Urbanization_Rate'], color='green')
    axes[1, 0].set_title('Urbanization Rate')
    axes[1, 0].set_xlabel('Step')
    axes[1, 0].set_ylabel('Urbanization Rate')
    
    # Human development
    axes[1, 1].plot(model_data['Step'], model_data['Average_Education'], label='Education', color='blue')
    axes[1, 1].plot(model_data['Step'], model_data['Average_Health'], label='Health', color='orange')
    axes[1, 1].set_title('Human Development Indicators')
    axes[1, 1].set_xlabel('Step')
    axes[1, 1].set_ylabel('Level')
    axes[1, 1].legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'economic_development.png'), dpi=300)
    plt.close()
    
    # 2. Sector composition over time
    plt.figure(figsize=(12, 8))
    
    sector_cols = ['Agricultural_Employment', 'Manufacturing_Employment', 'Services_Employment']
    if all(col in model_data.columns for col in sector_cols):
        total_employment = model_data[sector_cols].sum(axis=1)
        
        plt.stackplot(model_data['Step'],
                     model_data['Agricultural_Employment'] / total_employment,
                     model_data['Manufacturing_Employment'] / total_employment,
                     model_data['Services_Employment'] / total_employment,
                     labels=['Agriculture', 'Manufacturing', 'Services'],
                     alpha=0.7)
        
        plt.title('Employment Sector Composition Over Time')
        plt.xlabel('Step')
        plt.ylabel('Employment Share')
        plt.legend(loc='upper right')
        plt.ylim(0, 1)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'sector_composition.png'), dpi=300)
    plt.close()
    
    # 3. Infrastructure development
    plt.figure(figsize=(12, 8))
    
    infrastructure_cols = ['Road_Coverage', 'School_Coverage', 'Clinic_Coverage', 
                          'Market_Coverage', 'Utility_Coverage']
    
    for col in infrastructure_cols:
        if col in model_data.columns:
            plt.plot(model_data['Step'], model_data[col], 
                    label=col.replace('_Coverage', ''), linewidth=2)
    
    plt.title('Infrastructure Development Over Time')
    plt.xlabel('Step')
    plt.ylabel('Coverage (Number of Infrastructure)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'infrastructure_development.png'), dpi=300)
    plt.close()
    
    print(f"Plots saved to {output_dir}/")


def load_and_analyze_results(results_dir: str) -> Dict[str, Any]:
    """
    Load simulation results and perform comprehensive analysis.
    
    Args:
        results_dir: Directory containing CSV result files
        
    Returns:
        Dictionary with analysis results
    """
    model_data_path = os.path.join(results_dir, 'model_metrics.csv')
    agent_data_path = os.path.join(results_dir, 'agent_data.csv')
    
    analysis = {}
    
    # Load model data
    if os.path.exists(model_data_path):
        model_data = pd.read_csv(model_data_path)
        analysis['development_trajectory'] = analyze_development_trajectory(model_data)
        
        # Create plots
        create_development_plots(model_data, os.path.join(results_dir, 'plots'))
        
    # Load agent data for additional analysis
    if os.path.exists(agent_data_path):
        agent_data = pd.read_csv(agent_data_path)
        
        # Final step agent analysis
        final_step = agent_data['Step'].max()
        final_agents = agent_data[agent_data['Step'] == final_step]
        
        # Income distribution
        households = final_agents[final_agents['Agent_Type'] == 'HouseholdAgent']
        if not households.empty:
            incomes = households['Income'].dropna().values
            analysis['final_income_distribution'] = {
                'mean': np.mean(incomes),
                'median': np.median(incomes),
                'std': np.std(incomes),
                'gini': calculate_gini_coefficient(incomes.tolist())
            }
    
    return analysis
