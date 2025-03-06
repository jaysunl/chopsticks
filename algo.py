def generate_tap_states(attacker, defender, turn, k):
    """Generates possible states resulting from attacker taps defender with one of his hands"""
    next_states = []
    for i in range(2):
        for j in range(2):
            if attacker[i] == 0 or defender[j] == 0:
                continue

            new_value = attacker[i] + defender[j]
            if new_value >= k:
                new_value = 0

            new_defender = defender.copy()
            new_defender[j] = new_value

            if turn == 0:
                next_states.append(tuple(attacker[:] + new_defender[:] + [1]))
            else:
                next_states.append(tuple(new_defender[:] + attacker[:] + [0]))
    return list(set(next_states))


def generate_split_states(attacker, defender, turn, k):
    """Generates the possible states resulting from attacker splitting his fingers"""
    next_states = []
    total_fingers = attacker[0] + attacker[1]
    for left_fingers in range(0, total_fingers + 1):
        right_fingers = total_fingers - left_fingers

        # Mkae sure that left and right stay legal
        if left_fingers >= k or right_fingers >= k:
            continue

        # Make sure the new states are not identical.
        if list(sorted([left_fingers, right_fingers])) == list(sorted(attacker)):
            continue

        # Otherwise, we can append the state
        if turn == 0:
            next_states.append(tuple([left_fingers, right_fingers] + defender + [1]))
        else:
            next_states.append(tuple(defender + [left_fingers, right_fingers] + [0]))
    return list(set(next_states))


def generate_graph(k=5):
    """Graph for chopsticks. Nodes are the game states, a 5-tuple of (l1, l2, r1, r2, player). Edges
    represent the actions that can be taken in order to move from one state to the next.
    """
    initial_state = (1, 1, 1, 1, 0)
    graph = {}
    stack = [initial_state]
    while stack:
        state = stack.pop()
        p1_left, p1_right, p2_left, p2_right, turn = state

        # This is a terminal node, no further processing
        if p1_left == 0 and p1_right == 0:
            continue
        elif p2_left == 0 and p2_right == 0:
            continue

        # Attacker and defender depends on turn
        if turn == 0:
            attacker = [p1_left, p1_right]
            defender = [p2_left, p2_right]
        else:
            attacker = [p2_left, p2_right]
            defender = [p1_left, p1_right]

        next_states = []
        next_states += generate_tap_states(attacker, defender, turn, k)
        next_states += generate_split_states(attacker, defender, turn, k)

        graph[state] = next_states
        for next_state in next_states:
            if next_state not in graph:
                graph[next_state] = []
                stack.append(next_state)
    return graph


def reverse_graph(g):
    g_reverse = {state: [] for state in g.keys()}
    for state, children in g.items():
        for child in children:
            g_reverse[child].append(state)
    return g_reverse


def find_path(graph, start, end):
    """
    This part is written by an llm
    Find a path from start to end in a directed graph.

    Args:
        graph: A dictionary representing the graph where keys are vertices and
               values are lists of adjacent vertices
        start: The starting vertex
        end: The ending vertex

    Returns:
        A list representing the path from start to end, or None if no path exists
    """
    if start not in graph or end not in graph:
        return None

    if start == end:
        return [start]
    queue = [(start, [start])]
    visited = set([start])

    while queue:
        vertex, path = queue.pop(0)
        for neighbor in graph.get(vertex, []):
            if neighbor == end:
                return path + [neighbor]
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    return None


def solve_graph(k=5):
    """
    The state lookup table is expressed in terms of the CURRENT PLAYER'S
    ability to win/lose/draw from this
    position given player 2 makes optimal moves. The state +1 means that the player will win from this state,
    -1 means thy will lose, and 0 means a draw.

    The algorithm works with a backwards topological sort, starting from the terminal nodes. The
    graph is directed with states as nodes and actions as edges.

    We can propagate the win/loss/draw upwards with the following:
    1) if a node has ANY child has any such that the next player is losing, current node is winning
    2) if the node has ALL children such that the next player is winning, the current node is losing

    All other nodes are draws. Simply propagate upward with a topological sort, keeping track of
    each node's winningness with a dictionary
    """

    # Generate graph and lookup table for the states. The state for all nodes starts as a draw, but
    # these states are updated as the algorithm runs.
    g = generate_graph(k)
    parents = reverse_graph(g)
    state_lookup = {state: 0 for state in g.keys()}
    winning_children = {state: 0 for state in g.keys()}

    # Terminal states
    terminal_states = []
    for state, children in g.items():
        if len(children) == 0:
            terminal_states.append(state)
            state_lookup[state] = -1

    # Work backward with a topological sort
    visited = set()
    stack = terminal_states.copy()
    while stack:
        state = stack.pop()
        if state in visited:
            continue
        visited.add(state)

        # if loss, all parent nodes can force a win.
        # if win, increment the winning_children counter for all parents
        if state_lookup[state] == -1:
            for p in parents[state]:
                state_lookup[p] = 1
                if p not in visited:
                    stack.append(p)
        elif state_lookup[state] == 1:
            for p in parents[state]:
                winning_children[p] += 1
                if winning_children[p] == len(g[p]):
                    state_lookup[p] = -1
                    if p not in visited:
                        stack.append(p)
        else:
            print("Error, we shouldn't be exploring a draw node!")
    return state_lookup


if __name__ == "__main__":
    for k in range(2, 15):
        g = generate_graph(k)
        lookup = solve_graph(k)
        state = (1, 1, 1, 1, 0)

        if lookup[state] == 0:
            print(f"For k = {k}: draw")
            continue

        winner = ""
        if lookup[state] == -1:
            winner = "player 2"
        elif lookup[state] == 1:
            winner = "player 1"

        print(f"For k = {k}, the winner is {winner}")
