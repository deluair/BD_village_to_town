"""
Main entry point for the vtown package.

This allows running the package as a module using python -m vtown
"""

import sys
import argparse

def main():
    """Main entry point with subcommands."""
    
    parser = argparse.ArgumentParser(
        description="Village to Town Development Simulation",
        prog="python -m vtown"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Server command
    server_parser = subparsers.add_parser('server', help='Launch web visualization server')
    server_parser.add_argument('--port', type=int, default=8521, help='Server port')
    
    # Run command  
    run_parser = subparsers.add_parser('run', help='Run headless simulation')
    run_parser.add_argument('--config', type=str, default='vtown/config/default.yaml', 
                           help='Configuration file path')
    run_parser.add_argument('--steps', type=int, default=100, help='Number of steps')
    run_parser.add_argument('--output', type=str, default='outputs', help='Output directory')
    run_parser.add_argument('--seed', type=int, help='Random seed')
    run_parser.add_argument('--runs', type=int, default=1, help='Number of runs')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze simulation results')
    analyze_parser.add_argument('results_dir', help='Directory with simulation results')
    
    args = parser.parse_args()
    
    if args.command == 'server':
        from .server import server
        server.port = args.port
        print(f"Starting server on port {args.port}")
        server.launch()
        
    elif args.command == 'run':
        from .run_headless import main as run_main
        # Override sys.argv to pass arguments to run_main
        sys.argv = ['run_headless.py']
        if args.config:
            sys.argv.extend(['--config', args.config])
        if args.steps:
            sys.argv.extend(['--steps', str(args.steps)])
        if args.output:
            sys.argv.extend(['--output', args.output])
        if args.seed:
            sys.argv.extend(['--seed', str(args.seed)])
        if args.runs > 1:
            sys.argv.extend(['--runs', str(args.runs), '--batch'])
        
        run_main()
        
    elif args.command == 'analyze':
        from .utils import load_and_analyze_results
        import json
        
        print(f"Analyzing results in {args.results_dir}")
        analysis = load_and_analyze_results(args.results_dir)
        
        # Pretty print analysis
        print("\nAnalysis Results:")
        print(json.dumps(analysis, indent=2, default=str))
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
