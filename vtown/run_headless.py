"""
Headless runner for batch simulations of the Village to Town model.

This module allows running multiple simulations without the web interface,
collecting data for analysis and research purposes.
"""

import argparse
import os
import pandas as pd
import numpy as np
from pathlib import Path
import yaml
from typing import Dict, List, Optional
import time

from .model import TownDevelopmentModel


class BatchRunner:
    """
    Runs multiple simulations and collects aggregate data.
    
    Useful for parameter sweeps, sensitivity analysis,
    and generating datasets for research.
    """
    
    def __init__(self, model_class=TownDevelopmentModel):
        self.model_class = model_class
        self.results = []
        
    def run_batch(self, 
                  config_path: str,
                  num_runs: int = 1,
                  max_steps: int = 100,
                  output_dir: str = "outputs",
                  seed: Optional[int] = None,
                  parameter_sweep: Optional[Dict] = None):
        """
        Run multiple simulations and collect results.
        
        Args:
            config_path: Path to YAML configuration file
            num_runs: Number of simulation runs
            max_steps: Maximum steps per simulation
            output_dir: Directory to save outputs
            seed: Random seed for reproducibility
            parameter_sweep: Dictionary of parameters to vary
        """
        
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Load base configuration
        with open(config_path, 'r') as f:
            base_config = yaml.safe_load(f)
            
        print(f"Starting batch run: {num_runs} simulations, {max_steps} steps each")
        print(f"Output directory: {output_dir}")
        
        all_model_data = []
        all_agent_data = []
        
        for run_id in range(num_runs):
            print(f"Running simulation {run_id + 1}/{num_runs}...")
            
            # Set up configuration for this run
            run_config = base_config.copy()
            
            # Apply parameter sweep if specified
            if parameter_sweep:
                for param, values in parameter_sweep.items():
                    if isinstance(values, list):
                        run_config[param] = values[run_id % len(values)]
                    else:
                        run_config[param] = values
            
            # Set random seed
            if seed is not None:
                np.random.seed(seed + run_id)
                run_config['random_seed'] = seed + run_id
            
            # Create and run model
            model = self.model_class(**run_config)
            
            # Run simulation
            start_time = time.time()
            for step in range(max_steps):
                model.step()
                
                # Progress indicator
                if (step + 1) % 20 == 0:
                    print(f"  Step {step + 1}/{max_steps}")
            
            run_time = time.time() - start_time
            print(f"  Completed in {run_time:.2f} seconds")
            
            # Collect data
            model_data = model.get_model_data()
            agent_data = model.get_agent_data()
            
            # Add run identifier
            model_data['run_id'] = run_id
            agent_data['run_id'] = run_id
            
            all_model_data.append(model_data)
            all_agent_data.append(agent_data)
            
        # Combine all runs
        print("Combining results...")
        combined_model_data = pd.concat(all_model_data, ignore_index=True)
        combined_agent_data = pd.concat(all_agent_data, ignore_index=True)
        
        # Save results
        model_output_path = os.path.join(output_dir, "model_metrics.csv")
        agent_output_path = os.path.join(output_dir, "agent_data.csv")
        
        combined_model_data.to_csv(model_output_path, index=False)
        combined_agent_data.to_csv(agent_output_path, index=False)
        
        print(f"Results saved:")
        print(f"  Model metrics: {model_output_path}")
        print(f"  Agent data: {agent_output_path}")
        
        # Generate summary statistics
        self.generate_summary_report(combined_model_data, output_dir)
        
        return combined_model_data, combined_agent_data
        
    def generate_summary_report(self, model_data: pd.DataFrame, output_dir: str):
        """Generate a summary report of simulation results."""
        
        summary_path = os.path.join(output_dir, "summary_report.txt")
        
        with open(summary_path, 'w') as f:
            f.write("=== Village to Town Simulation Summary Report ===\n\n")
            
            # Basic statistics
            f.write("SIMULATION OVERVIEW\n")
            f.write(f"Number of runs: {model_data['run_id'].nunique()}\n")
            f.write(f"Steps per run: {model_data['Step'].max()}\n")
            f.write(f"Total simulation steps: {len(model_data)}\n\n")
            
            # Final outcomes (last step of each run)
            final_data = model_data.groupby('run_id').last()
            
            f.write("FINAL OUTCOMES (Average across runs)\n")
            f.write(f"Population: {final_data['Population'].mean():.1f} ± {final_data['Population'].std():.1f}\n")
            f.write(f"GDP per capita: {final_data['GDP_Per_Capita'].mean():.0f} ± {final_data['GDP_Per_Capita'].std():.0f} Taka\n")
            f.write(f"Gini coefficient: {final_data['Gini_Coefficient'].mean():.3f} ± {final_data['Gini_Coefficient'].std():.3f}\n")
            f.write(f"Average education: {final_data['Average_Education'].mean():.1f} ± {final_data['Average_Education'].std():.1f} years\n")
            f.write(f"Average health: {final_data['Average_Health'].mean():.3f} ± {final_data['Average_Health'].std():.3f}\n")
            f.write(f"Urbanization rate: {final_data['Urbanization_Rate'].mean():.1%} ± {final_data['Urbanization_Rate'].std():.1%}\n")
            f.write(f"Service access: {final_data['Service_Access_Rate'].mean():.1%} ± {final_data['Service_Access_Rate'].std():.1%}\n\n")
            
            # Sector distribution
            f.write("EMPLOYMENT DISTRIBUTION (Final)\n")
            f.write(f"Agriculture: {final_data['Agricultural_Employment'].mean():.1f} people\n")
            f.write(f"Manufacturing: {final_data['Manufacturing_Employment'].mean():.1f} people\n")
            f.write(f"Services: {final_data['Services_Employment'].mean():.1f} people\n\n")
            
            # Infrastructure
            f.write("INFRASTRUCTURE (Final)\n")
            f.write(f"Roads: {final_data['Road_Coverage'].mean():.1f}\n")
            f.write(f"Schools: {final_data['School_Coverage'].mean():.1f}\n")
            f.write(f"Clinics: {final_data['Clinic_Coverage'].mean():.1f}\n")
            f.write(f"Markets: {final_data['Market_Coverage'].mean():.1f}\n")
            f.write(f"Utilities: {final_data['Utility_Coverage'].mean():.1f}\n\n")
            
            # Development progress
            f.write("DEVELOPMENT PROGRESS\n")
            initial_data = model_data.groupby('run_id').first()
            
            gdp_growth = ((final_data['GDP_Per_Capita'].mean() - initial_data['GDP_Per_Capita'].mean()) / 
                         initial_data['GDP_Per_Capita'].mean()) * 100
            f.write(f"GDP per capita growth: {gdp_growth:.1f}%\n")
            
            education_improvement = final_data['Average_Education'].mean() - initial_data['Average_Education'].mean()
            f.write(f"Education improvement: +{education_improvement:.1f} years\n")
            
            health_improvement = final_data['Average_Health'].mean() - initial_data['Average_Health'].mean()
            f.write(f"Health improvement: +{health_improvement:.3f}\n")
            
            urbanization_change = final_data['Urbanization_Rate'].mean() - initial_data['Urbanization_Rate'].mean()
            f.write(f"Urbanization increase: +{urbanization_change:.1%}\n")
            
        print(f"Summary report saved: {summary_path}")


def run_single_simulation(config_path: str,
                         steps: int = 100,
                         output_dir: str = "outputs",
                         seed: Optional[int] = None,
                         verbose: bool = True) -> TownDevelopmentModel:
    """
    Run a single simulation and save results.
    
    Args:
        config_path: Path to configuration file
        steps: Number of simulation steps
        output_dir: Output directory
        seed: Random seed
        verbose: Print progress information
        
    Returns:
        Completed model instance
    """
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Load configuration
    if config_path and os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    else:
        config = {}
        if verbose:
            print("Using default configuration")
    
    # Set random seed
    if seed is not None:
        np.random.seed(seed)
        config['random_seed'] = seed
    
    if verbose:
        print(f"Starting simulation: {steps} steps")
        print(f"Output directory: {output_dir}")
    
    # Create and run model
    model = TownDevelopmentModel(**config)
    
    start_time = time.time()
    for step in range(steps):
        model.step()
        
        if verbose and (step + 1) % 20 == 0:
            print(f"Step {step + 1}/{steps}")
    
    run_time = time.time() - start_time
    
    if verbose:
        print(f"Simulation completed in {run_time:.2f} seconds")
    
    # Save results
    model_data = model.get_model_data()
    agent_data = model.get_agent_data()
    
    model_output_path = os.path.join(output_dir, "model_metrics.csv")
    agent_output_path = os.path.join(output_dir, "agent_data.csv")
    
    model_data.to_csv(model_output_path, index=False)
    agent_data.to_csv(agent_output_path, index=False)
    
    if verbose:
        print(f"Results saved:")
        print(f"  Model metrics: {model_output_path}")
        print(f"  Agent data: {agent_output_path}")
        
        # Print final statistics
        final_step = model_data.iloc[-1]
        print(f"\nFinal Outcomes:")
        print(f"  Population: {final_step['Population']}")
        print(f"  GDP per capita: {final_step['GDP_Per_Capita']:.0f} Taka")
        print(f"  Gini coefficient: {final_step['Gini_Coefficient']:.3f}")
        print(f"  Urbanization rate: {final_step['Urbanization_Rate']:.1%}")
        print(f"  Service access: {final_step['Service_Access_Rate']:.1%}")
    
    return model


def main():
    """Command line interface for headless simulation."""
    
    parser = argparse.ArgumentParser(
        description="Run Village to Town development simulation headlessly"
    )
    
    parser.add_argument(
        "--config", 
        type=str,
        default="vtown/config/default.yaml",
        help="Path to configuration YAML file"
    )
    
    parser.add_argument(
        "--steps",
        type=int,
        default=100,
        help="Number of simulation steps to run"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default="outputs",
        help="Output directory for results"
    )
    
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducible results"
    )
    
    parser.add_argument(
        "--runs",
        type=int,
        default=1,
        help="Number of simulation runs (for batch mode)"
    )
    
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Run in batch mode with multiple simulations"
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress output"
    )
    
    args = parser.parse_args()
    
    if args.batch or args.runs > 1:
        # Batch mode
        runner = BatchRunner()
        runner.run_batch(
            config_path=args.config,
            num_runs=args.runs,
            max_steps=args.steps,
            output_dir=args.output,
            seed=args.seed
        )
    else:
        # Single simulation
        run_single_simulation(
            config_path=args.config,
            steps=args.steps,
            output_dir=args.output,
            seed=args.seed,
            verbose=not args.quiet
        )


if __name__ == "__main__":
    main()
