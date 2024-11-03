from ortools.linear_solver import pywraplp

def main():
    # Create the solver with the SCIP backend
    solver = pywraplp.Solver.CreateSolver('SCIP')

    # Define nodes by groups
    source = ['source']
    group1 = ['x1', 'x2', 'x3', 'x4']
    group2 = ['x5', 'x6']
    group3 = ['x7', 'x8', 'x9', 'x10', 'x11']
    group4 = ['x12', 'x13', 'x14']
    sink = ['sink']

    # Define edges and weights
    edges = []
    weights = {}

    # Connections with specific weights (inter-group)
    connections = {
        ('source', 'x1'): 6, ('source', 'x2'): 8, ('source', 'x3'): 7, ('source', 'x4'): 6,
        ('x1', 'x5'): 3, ('x1', 'x6'): 5, ('x2', 'x5'): 5, ('x2', 'x6'): 4,
        ('x3', 'x5'): 5, ('x3', 'x6'): 5, ('x4', 'x5'): 4, ('x4', 'x6'): 3,
        ('x5', 'x7'): 3, ('x5', 'x8'): 5, ('x5', 'x9'): 4, ('x5', 'x10'): 4, ('x5', 'x11'): 6,
        ('x6', 'x7'): 3, ('x6', 'x8'): 2, ('x6', 'x9'): 7, ('x6', 'x10'): 4, ('x6', 'x11'): 6,
        ('x7', 'x12'): 6, ('x7', 'x13'): 5, ('x7', 'x14'): 6, ('x8', 'x12'): 8, ('x8', 'x13'): 7,
        ('x8', 'x14'): 6, ('x9', 'x12'): 7, ('x9', 'x13'): 5, ('x9', 'x14'): 6, ('x10', 'x12'): 5,
        ('x10', 'x13'): 8, ('x10', 'x14'): 6, ('x11', 'x12'): 5, ('x11', 'x13'): 4, ('x11', 'x14'): 6,
        ('x12', 'sink'): 4, ('x13', 'sink'): 6, ('x14', 'sink'): 5
    }
    for (src, dest), w in connections.items():
        edges.append((src, dest))
        weights[(src, dest)] = w

    # Intra-group connections with specified weights
    intra_group_edges = {
        # Group 1
        ('x1', 'x2'): 2, ('x1', 'x3'): 1, ('x1', 'x4'): 2, ('x2', 'x3'): 3, ('x2', 'x4'): 3, ('x3', 'x4'): 1,
        # Group 2
        ('x5', 'x6'): 3,
        # Group 3
        ('x7', 'x8'): 2, ('x7', 'x9'): 1, ('x7', 'x10'): 3, ('x7', 'x11'): 3, ('x8', 'x9'): 2, ('x8', 'x10'): 1,
        ('x8', 'x11'): 4, ('x9', 'x10'): 2, ('x9', 'x11'): 3, ('x10', 'x11'): 2,
        # Group 4
        ('x12', 'x13'): 3, ('x12', 'x14'): 2, ('x13', 'x14'): 2
    }
    for (src, dest), w in intra_group_edges.items():
        edges.append((src, dest))
        edges.append((dest, src))  # Since it's undirected, add reverse direction
        weights[(src, dest)] = w
        weights[(dest, src)] = w  # Same weight for reverse direction

    # Create variables for each edge
    x = {}
    for edge in edges:
        x[edge] = solver.BoolVar('x[%s,%s]' % (edge[0], edge[1]))

    # Objective: Minimize the sum of the weights of the edges in the path
    objective = solver.Objective()
    for edge, weight in weights.items():
        objective.SetCoefficient(x[edge], weight)
    objective.SetMinimization()

    # Flow conservation for intermediate nodes
    all_nodes = group1 + group2 + group3 + group4
    for node in all_nodes:
        in_flow = sum(x[(i, node)] for i, j in edges if j == node)
        out_flow = sum(x[(node, j)] for i, j in edges if i == node)
        solver.Add(in_flow == out_flow)

    # Source should have exactly one outgoing flow
    solver.Add(sum(x[('source', j)] for _, j in edges if 'source' == _) == 1)

    # Sink should have exactly one incoming flow and no outgoing flow
    solver.Add(sum(x[(i, 'sink')] for i, _ in edges if _ == 'sink') == 1)
    solver.Add(sum(x[('sink', j)] for _, j in edges if 'sink' == _) == 0)  # Ensure no outgoing flow from sink

    # Force inclusion of specified nodes by requiring at least one incoming and one outgoing flow
    must_include_nodes = ['x4', 'x6', 'x7', 'x9', 'x10', 'x12', 'x13', 'x14']
    for node in must_include_nodes:
        solver.Add(sum(x[(i, node)] for i, j in edges if j == node) >= 1)  # At least one incoming flow
        solver.Add(sum(x[(node, j)] for i, j in edges if i == node) >= 1)  # At least one outgoing flow

    # Solve the problem
    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        print('Solution:')
        print('Objective value =', solver.Objective().Value())
        for edge in edges:
            if x[edge].solution_value() > 0:
                print('%s -> %s' % edge)
    else:
        print('The problem does not have an optimal solution.')

if __name__ == '__main__':
    main()
