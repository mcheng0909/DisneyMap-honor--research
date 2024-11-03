from ortools.linear_solver import pywraplp

def solve_knapsack_or_tools():
    weights = [25, 36, 78, 26, 33, 44, 89, 65, 73, 54, 60, 40, 30, 64]
    values = [1.2, 4.5, 6.7, 5.7, 4.4, 12.1, 11.5, 7.8, 9.4, 7.7, 8.5, 10.6, 11.2, 8.9]
    max_weight = 480  # Maximum adjusted weight (sum of item weights and a fixed multiplier per item)

    # Create the solver using CBC as the backend solver.
    solver = pywraplp.Solver.CreateSolver('CBC')

    # Define decision variables
    x = [solver.BoolVar(f'x[{i}]') for i in range(14)]

    # Set specified items to be selected
    required_items = [0, 5, 7, 9, 11]  # Indices for x1, x6, x8, x10, x12
    for i in required_items:
        solver.Add(x[i] == 1)

    # Objective: Minimize the total value of the selected items
    objective = solver.Objective()
    for i in range(14):
        objective.SetCoefficient(x[i], values[i])
    objective.SetMaximization()

    # Constraint: Total adjusted weight of selected items
    weight_constraint = solver.Constraint(-solver.infinity(), max_weight)
    for i in range(14):
        weight_constraint.SetCoefficient(x[i], weights[i] + 7)  # Including fixed weight of 7 per selected item

    # Bin constraints
    solver.Add(solver.Sum([x[i] for i in range(4)]) >= 1)  # Bin 1: x1 to x4
    solver.Add(solver.Sum([x[i] for i in range(4, 6)]) >= 1)  # Bin 2: x5 to x6
    solver.Add(solver.Sum([x[i] for i in range(6, 11)]) >= 1)  # Bin 3: x7 to x11
    solver.Add(solver.Sum([x[i] for i in range(11, 14)]) >= 1)  # Bin 4: x12 to x14

    # Solve the problem
    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        print('Solution:')
        print('Objective value =', objective.Value())
        total_weight_selected = 0
        for i in range(14):
            if x[i].solution_value() > 0.5:  # Check if the variable is practically 1
                item_weight = weights[i] * x[i].solution_value()
                total_weight_selected += item_weight
                bin_id = "Bin 1" if i < 4 else ("Bin 2" if i < 6 else ("Bin 3" if i < 11 else "Bin 4"))
                print(f'Item {i+1} from {bin_id} - selected: {x[i].solution_value()}, Weight: {item_weight}')
        print(f'Total selected weight: {total_weight_selected}')
    else:
        print('No feasible solution found.')

# Solve the problem
solve_knapsack_or_tools()
