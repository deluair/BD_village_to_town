"""
Policy engine for the Village to Town development simulation.

This module implements various policy interventions including:
- Infrastructure development planning
- Education and health programs
- Microfinance and grant programs
- Urban planning policies
"""

import numpy as np
from typing import Dict, List, Tuple, Any
from .agents import InfrastructureAgent


class PolicyEngine:
    """
    Manages policy interventions and government decisions in the simulation.
    
    The policy engine allocates budget across different intervention types
    and implements development strategies to transform the village into a town.
    """
    
    def __init__(self, model, annual_budget: float, config: Dict[str, Any]):
        self.model = model
        self.annual_budget = annual_budget
        self.config = config
        
        # Policy state
        self.current_budget = annual_budget
        self.infrastructure_priorities = config.get('infrastructure_weights', {
            'road': 0.3, 'school': 0.2, 'clinic': 0.2, 'market': 0.15, 'utility': 0.15
        })
        
        # Program budgets
        self.grant_program_budget = config.get('grant_program_budget', 20000)
        self.microfinance_budget = config.get('microfinance_budget', 15000)
        
        # Policy history for adaptive strategies
        self.policy_history = []
        self.effectiveness_scores = {}
        
    def execute_annual_policies(self):
        """Execute annual policy interventions."""
        # Reset budget for the year
        self.current_budget = self.annual_budget
        
        # Assess current situation
        situation_assessment = self.assess_current_situation()
        
        # Allocate budget across policy areas
        budget_allocation = self.allocate_budget(situation_assessment)
        
        # Execute specific policies
        results = {}
        results['infrastructure'] = self.implement_infrastructure_development(
            budget_allocation['infrastructure']
        )
        results['education'] = self.implement_education_programs(
            budget_allocation['education']
        )
        results['health'] = self.implement_health_programs(
            budget_allocation['health']
        )
        results['economic'] = self.implement_economic_programs(
            budget_allocation['economic']
        )
        results['grants'] = self.implement_grant_programs(
            budget_allocation['grants']
        )
        
        # Record policy execution
        self.policy_history.append({
            'step': self.model.step_count,
            'budget_allocation': budget_allocation,
            'results': results,
            'situation': situation_assessment
        })
        
        # Update policy effectiveness
        self.update_policy_effectiveness()
        
    def assess_current_situation(self) -> Dict[str, float]:
        """Assess current development situation to guide policy priorities."""
        households = [agent for agent in self.model.schedule.agents 
                     if hasattr(agent, 'sector')]
        businesses = [agent for agent in self.model.schedule.agents 
                     if hasattr(agent, 'business_type')]
        infrastructure = [agent for agent in self.model.schedule.agents 
                         if hasattr(agent, 'infrastructure_type')]
        
        assessment = {}
        
        # Economic indicators
        if households:
            avg_income = sum(h.income for h in households) / len(households)
            assessment['economic_development'] = min(1.0, avg_income / 5000)
            
            # Sector distribution
            agriculture_pct = sum(1 for h in households if h.sector == 'agriculture') / len(households)
            assessment['agricultural_dependency'] = agriculture_pct
            
            # Education level
            avg_education = sum(h.education_level for h in households) / len(households)
            assessment['education_level'] = avg_education / 12
            
            # Health level
            avg_health = sum(h.health_index for h in households) / len(households)
            assessment['health_level'] = avg_health
        else:
            assessment.update({
                'economic_development': 0,
                'agricultural_dependency': 1,
                'education_level': 0,
                'health_level': 0.5
            })
        
        # Infrastructure coverage
        infrastructure_coverage = {}
        for infra_type in ['road', 'school', 'clinic', 'market', 'utility']:
            count = sum(1 for i in infrastructure if i.infrastructure_type == infra_type)
            infrastructure_coverage[infra_type] = count
            
        assessment['infrastructure_coverage'] = infrastructure_coverage
        
        # Urbanization level
        assessment['urbanization_rate'] = self.model.calculate_urbanization_rate()
        
        # Business development
        assessment['business_density'] = len(businesses) / max(1, len(households))
        
        return assessment
        
    def allocate_budget(self, situation: Dict[str, Any]) -> Dict[str, float]:
        """Allocate annual budget across policy areas based on current situation."""
        base_allocation = {
            'infrastructure': 0.5,
            'education': 0.15,
            'health': 0.15,
            'economic': 0.1,
            'grants': 0.1
        }
        
        # Adjust allocation based on situation
        adjustments = {}
        
        # If low education, increase education budget
        if situation['education_level'] < 0.3:
            adjustments['education'] = 0.05
            adjustments['infrastructure'] = -0.03
            adjustments['economic'] = -0.02
            
        # If low health, increase health budget  
        if situation['health_level'] < 0.6:
            adjustments['health'] = 0.05
            adjustments['infrastructure'] = -0.03
            adjustments['grants'] = -0.02
            
        # If high agricultural dependency, focus on economic diversification
        if situation['agricultural_dependency'] > 0.7:
            adjustments['economic'] = 0.08
            adjustments['infrastructure'] = -0.05
            adjustments['grants'] = -0.03
            
        # If low urbanization, focus on infrastructure
        if situation['urbanization_rate'] < 0.3:
            adjustments['infrastructure'] = 0.1
            adjustments['education'] = -0.03
            adjustments['health'] = -0.03
            adjustments['economic'] = -0.02
            adjustments['grants'] = -0.02
            
        # Apply adjustments
        final_allocation = {}
        for area, base_pct in base_allocation.items():
            adjustment = adjustments.get(area, 0)
            final_allocation[area] = max(0.05, base_pct + adjustment)
            
        # Normalize to ensure sum = 1
        total = sum(final_allocation.values())
        for area in final_allocation:
            final_allocation[area] = (final_allocation[area] / total) * self.annual_budget
            
        return final_allocation
        
    def implement_infrastructure_development(self, budget: float) -> Dict[str, Any]:
        """Implement infrastructure development projects."""
        results = {'projects_completed': 0, 'total_cost': 0, 'types_built': []}
        
        # Assess infrastructure needs
        infrastructure_needs = self.assess_infrastructure_needs()
        
        # Prioritize infrastructure types
        sorted_needs = sorted(infrastructure_needs.items(), 
                            key=lambda x: x[1], reverse=True)
        
        remaining_budget = budget
        
        for infra_type, priority_score in sorted_needs:
            if remaining_budget <= 0:
                break
                
            # Determine how many to build based on budget and priority
            construction_cost = {
                'road': 10000, 'school': 50000, 'clinic': 30000,
                'market': 20000, 'utility': 40000
            }[infra_type]
            
            max_buildable = int(remaining_budget // construction_cost)
            target_builds = min(max_buildable, max(1, int(priority_score * 3)))
            
            built_count = 0
            for _ in range(target_builds):
                if remaining_budget >= construction_cost:
                    location = self.find_optimal_infrastructure_location(infra_type)
                    if location and self.model.add_infrastructure(location, infra_type):
                        remaining_budget -= construction_cost
                        built_count += 1
                        results['types_built'].append(infra_type)
                        
            results['projects_completed'] += built_count
            
        results['total_cost'] = budget - remaining_budget
        
        return results
        
    def assess_infrastructure_needs(self) -> Dict[str, float]:
        """Assess relative need for different infrastructure types."""
        households = [agent for agent in self.model.schedule.agents 
                     if hasattr(agent, 'sector')]
        infrastructure = [agent for agent in self.model.schedule.agents 
                         if hasattr(agent, 'infrastructure_type')]
        
        needs = {}
        
        if not households:
            return {'road': 1.0, 'school': 1.0, 'clinic': 1.0, 'market': 1.0, 'utility': 1.0}
        
        population = len(households)
        
        # Calculate coverage ratios
        for infra_type in ['road', 'school', 'clinic', 'market', 'utility']:
            current_count = sum(1 for i in infrastructure if i.infrastructure_type == infra_type)
            
            # Target ratios (infrastructure per 100 people)
            target_ratios = {
                'road': 0.5,     # 1 road per 200 people
                'school': 0.25,  # 1 school per 400 people  
                'clinic': 0.2,   # 1 clinic per 500 people
                'market': 0.15,  # 1 market per 667 people
                'utility': 0.3   # 1 utility per 333 people
            }
            
            target_count = (population / 100) * target_ratios[infra_type]
            coverage_ratio = current_count / max(1, target_count)
            
            # Need is inverse of coverage (higher need = lower coverage)
            needs[infra_type] = max(0, 1 - coverage_ratio)
            
        return needs
        
    def find_optimal_infrastructure_location(self, infra_type: str) -> Tuple[int, int]:
        """Find optimal location for new infrastructure."""
        households = [agent for agent in self.model.schedule.agents 
                     if hasattr(agent, 'sector')]
        
        if not households:
            # Default to center if no households
            return (self.model.grid.width // 2, self.model.grid.height // 2)
            
        # Strategy depends on infrastructure type
        if infra_type == 'road':
            # Roads should connect population centers
            return self.find_road_connection_point()
        elif infra_type in ['school', 'clinic']:
            # Schools and clinics should be central to underserved areas
            return self.find_underserved_population_center(infra_type)
        elif infra_type == 'market':
            # Markets should be accessible to many households
            return self.find_high_accessibility_location()
        elif infra_type == 'utility':
            # Utilities should expand from existing infrastructure
            return self.find_utility_expansion_point()
            
        # Default fallback
        return self.find_population_weighted_center()
        
    def find_road_connection_point(self) -> Tuple[int, int]:
        """Find location that connects population clusters."""
        households = [agent for agent in self.model.schedule.agents 
                     if hasattr(agent, 'sector')]
        
        # Find population density clusters
        density_map = np.zeros((self.model.grid.width, self.model.grid.height))
        
        for h in households:
            x, y = h.pos
            # Add density in 3x3 area around household
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.model.grid.width and 0 <= ny < self.model.grid.height:
                        density_map[nx, ny] += 1
                        
        # Find location with good connectivity potential
        best_score = -1
        best_location = None
        
        for x in range(self.model.grid.width):
            for y in range(self.model.grid.height):
                # Check if location is available
                contents = self.model.grid.get_cell_list_contents([(x, y)])
                infrastructure_count = sum(1 for agent in contents 
                                         if hasattr(agent, 'infrastructure_type'))
                
                if infrastructure_count >= 2:
                    continue
                    
                # Score based on nearby population and connectivity
                score = 0
                for dx in range(-5, 6):
                    for dy in range(-5, 6):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.model.grid.width and 0 <= ny < self.model.grid.height:
                            distance = max(1, np.sqrt(dx*dx + dy*dy))
                            score += density_map[nx, ny] / distance
                            
                if score > best_score:
                    best_score = score
                    best_location = (x, y)
                    
        return best_location or (self.model.grid.width // 2, self.model.grid.height // 2)
        
    def find_underserved_population_center(self, infra_type: str) -> Tuple[int, int]:
        """Find center of population underserved by specific infrastructure."""
        households = [agent for agent in self.model.schedule.agents 
                     if hasattr(agent, 'sector')]
        infrastructure = [agent for agent in self.model.schedule.agents 
                         if hasattr(agent, 'infrastructure_type') and 
                         agent.infrastructure_type == infra_type]
        
        # Find households without access to this infrastructure type
        underserved = []
        for h in households:
            has_access = False
            for infra in infrastructure:
                distance = np.sqrt((h.pos[0] - infra.pos[0])**2 + (h.pos[1] - infra.pos[1])**2)
                if distance <= infra.coverage_radius:
                    has_access = True
                    break
            if not has_access:
                underserved.append(h)
                
        if not underserved:
            # If everyone has access, find general population center
            return self.find_population_weighted_center()
            
        # Find center of underserved population
        center_x = sum(h.pos[0] for h in underserved) / len(underserved)
        center_y = sum(h.pos[1] for h in underserved) / len(underserved)
        
        # Find nearest valid grid position
        x = int(round(center_x))
        y = int(round(center_y))
        x = max(0, min(x, self.model.grid.width - 1))
        y = max(0, min(y, self.model.grid.height - 1))
        
        return (x, y)
        
    def find_high_accessibility_location(self) -> Tuple[int, int]:
        """Find location with high accessibility to population."""
        households = [agent for agent in self.model.schedule.agents 
                     if hasattr(agent, 'sector')]
        
        best_score = -1
        best_location = None
        
        # Sample locations and find one with best accessibility
        for _ in range(50):  # Sample 50 random locations
            x = np.random.randint(0, self.model.grid.width)
            y = np.random.randint(0, self.model.grid.height)
            
            # Check if location is available
            contents = self.model.grid.get_cell_list_contents([(x, y)])
            infrastructure_count = sum(1 for agent in contents 
                                     if hasattr(agent, 'infrastructure_type'))
            
            if infrastructure_count >= 2:
                continue
                
            # Calculate accessibility score
            accessibility = 0
            for h in households:
                distance = np.sqrt((x - h.pos[0])**2 + (y - h.pos[1])**2)
                accessibility += 1 / max(1, distance)
                
            if accessibility > best_score:
                best_score = accessibility
                best_location = (x, y)
                
        return best_location or (self.model.grid.width // 2, self.model.grid.height // 2)
        
    def find_utility_expansion_point(self) -> Tuple[int, int]:
        """Find location to expand utility network."""
        existing_utilities = [agent for agent in self.model.schedule.agents 
                             if hasattr(agent, 'infrastructure_type') and 
                             agent.infrastructure_type == 'utility']
        
        if not existing_utilities:
            # If no existing utilities, place at population center
            return self.find_population_weighted_center()
            
        # Find location near existing utilities but serving new areas
        best_location = None
        best_score = -1
        
        for utility in existing_utilities:
            # Look for expansion points around existing utilities
            for dx in range(-3, 4):
                for dy in range(-3, 4):
                    if dx == 0 and dy == 0:
                        continue
                        
                    x = utility.pos[0] + dx
                    y = utility.pos[1] + dy
                    
                    if not (0 <= x < self.model.grid.width and 0 <= y < self.model.grid.height):
                        continue
                        
                    # Check availability
                    contents = self.model.grid.get_cell_list_contents([(x, y)])
                    infrastructure_count = sum(1 for agent in contents 
                                             if hasattr(agent, 'infrastructure_type'))
                    
                    if infrastructure_count >= 2:
                        continue
                        
                    # Score based on nearby underserved population
                    score = 0
                    households = [agent for agent in self.model.schedule.agents 
                                 if hasattr(agent, 'sector')]
                    
                    for h in households:
                        if not h.has_utility_access():
                            distance = np.sqrt((x - h.pos[0])**2 + (y - h.pos[1])**2)
                            if distance <= 3:  # Within utility coverage
                                score += 1
                                
                    if score > best_score:
                        best_score = score
                        best_location = (x, y)
                        
        return best_location or self.find_population_weighted_center()
        
    def find_population_weighted_center(self) -> Tuple[int, int]:
        """Find population-weighted center of the settlement."""
        households = [agent for agent in self.model.schedule.agents 
                     if hasattr(agent, 'sector')]
        
        if not households:
            return (self.model.grid.width // 2, self.model.grid.height // 2)
            
        center_x = sum(h.pos[0] for h in households) / len(households)
        center_y = sum(h.pos[1] for h in households) / len(households)
        
        x = int(round(center_x))
        y = int(round(center_y))
        x = max(0, min(x, self.model.grid.width - 1))
        y = max(0, min(y, self.model.grid.height - 1))
        
        return (x, y)
        
    def implement_education_programs(self, budget: float) -> Dict[str, Any]:
        """Implement education improvement programs."""
        results = {'beneficiaries': 0, 'total_cost': 0}
        
        households = [agent for agent in self.model.schedule.agents 
                     if hasattr(agent, 'sector')]
        
        # Target households with low education
        cost_per_beneficiary = 300
        max_beneficiaries = int(budget // cost_per_beneficiary)
        
        eligible_households = [h for h in households if h.education_level < 10]
        beneficiaries = min(max_beneficiaries, len(eligible_households))
        
        # Select beneficiaries (prioritize lowest education)
        eligible_households.sort(key=lambda h: h.education_level)
        selected = eligible_households[:beneficiaries]
        
        # Apply education boost
        for household in selected:
            household.education_level = min(12, household.education_level + 1)
            
        results['beneficiaries'] = beneficiaries
        results['total_cost'] = beneficiaries * cost_per_beneficiary
        
        return results
        
    def implement_health_programs(self, budget: float) -> Dict[str, Any]:
        """Implement health improvement programs."""
        results = {'beneficiaries': 0, 'total_cost': 0}
        
        households = [agent for agent in self.model.schedule.agents 
                     if hasattr(agent, 'sector')]
        
        # Target households with low health
        cost_per_beneficiary = 250
        max_beneficiaries = int(budget // cost_per_beneficiary)
        
        eligible_households = [h for h in households if h.health_index < 0.8]
        beneficiaries = min(max_beneficiaries, len(eligible_households))
        
        # Select beneficiaries (prioritize lowest health)
        eligible_households.sort(key=lambda h: h.health_index)
        selected = eligible_households[:beneficiaries]
        
        # Apply health boost
        for household in selected:
            household.health_index = min(1.0, household.health_index + 0.15)
            
        results['beneficiaries'] = beneficiaries
        results['total_cost'] = beneficiaries * cost_per_beneficiary
        
        return results
        
    def implement_economic_programs(self, budget: float) -> Dict[str, Any]:
        """Implement economic development programs."""
        results = {'businesses_supported': 0, 'training_provided': 0, 'total_cost': 0}
        
        businesses = [agent for agent in self.model.schedule.agents 
                     if hasattr(agent, 'business_type')]
        households = [agent for agent in self.model.schedule.agents 
                     if hasattr(agent, 'sector')]
        
        remaining_budget = budget
        
        # Business support grants
        business_grant = 5000
        max_business_grants = int(remaining_budget * 0.6 // business_grant)
        
        # Prioritize small businesses
        small_businesses = [b for b in businesses if b.size == 'small']
        grants_given = min(max_business_grants, len(small_businesses))
        
        for i in range(grants_given):
            small_businesses[i].capital += business_grant
            small_businesses[i].productivity += 0.1
            
        results['businesses_supported'] = grants_given
        remaining_budget -= grants_given * business_grant
        
        # Skills training
        training_cost = 500
        max_training = int(remaining_budget // training_cost)
        
        # Target agricultural workers for sector transition
        agricultural_workers = [h for h in households if h.sector == 'agriculture' and h.education_level >= 5]
        training_provided = min(max_training, len(agricultural_workers))
        
        for i in range(training_provided):
            # Increase chance of sector transition
            if np.random.random() < 0.3:
                agricultural_workers[i].sector = np.random.choice(['manufacturing', 'services'])
                
        results['training_provided'] = training_provided
        results['total_cost'] = (grants_given * business_grant) + (training_provided * training_cost)
        
        return results
        
    def implement_grant_programs(self, budget: float) -> Dict[str, Any]:
        """Implement direct grants and microfinance programs."""
        results = {'direct_grants': 0, 'microfinance_loans': 0, 'total_cost': 0}
        
        households = [agent for agent in self.model.schedule.agents 
                     if hasattr(agent, 'sector')]
        
        # Direct grants for poorest households
        grant_amount = 1000
        max_grants = int(budget * 0.4 // grant_amount)
        
        # Target lowest income households
        poor_households = [h for h in households if h.income < 2000]
        grants_given = min(max_grants, len(poor_households))
        
        poor_households.sort(key=lambda h: h.income)
        for i in range(grants_given):
            poor_households[i].savings += grant_amount
            
        results['direct_grants'] = grants_given
        
        # Microfinance loans
        remaining_budget = budget - (grants_given * grant_amount)
        loan_amount = 2000
        max_loans = int(remaining_budget // loan_amount)
        
        # Target households with some savings but limited capital
        eligible_for_loans = [h for h in households if 500 <= h.savings <= 3000]
        loans_given = min(max_loans, len(eligible_for_loans))
        
        for i in range(loans_given):
            eligible_for_loans[i].savings += loan_amount
            # Note: In a more complex model, we'd track loan repayment
            
        results['microfinance_loans'] = loans_given
        results['total_cost'] = (grants_given * grant_amount) + (loans_given * loan_amount)
        
        return results
        
    def update_policy_effectiveness(self):
        """Update policy effectiveness scores based on outcomes."""
        if len(self.policy_history) < 2:
            return
            
        # Compare current outcomes to previous step
        current_gdp = self.model.calculate_gdp_per_capita()
        current_education = self.model.calculate_average_education()
        current_health = self.model.calculate_average_health()
        
        # Store for future adaptive policy making
        self.effectiveness_scores[self.model.step_count] = {
            'gdp_per_capita': current_gdp,
            'education_level': current_education,
            'health_level': current_health,
            'infrastructure_coverage': self.model.calculate_infrastructure_coverage(),
            'urbanization_rate': self.model.calculate_urbanization_rate()
        }
