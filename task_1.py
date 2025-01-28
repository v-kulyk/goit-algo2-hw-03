from collections import deque
from typing import Dict, List

class Edge:
    def __init__(self, to: str, capacity: int):
        self.to = to
        self.capacity = capacity
        self.flow = 0
        self.reverse = None

class FlowNetwork:
    def __init__(self):
        self.graph: Dict[str, List[Edge]] = {}
    
    def add_node(self, node: str):
        if node not in self.graph:
            self.graph[node] = []
    
    def add_edge(self, fr: str, to: str, capacity: int):
        self.add_node(fr)
        self.add_node(to)
        forward = Edge(to, capacity)
        backward = Edge(fr, 0)
        forward.reverse = backward
        backward.reverse = forward
        self.graph[fr].append(forward)
        self.graph[to].append(backward)
    
    def bfs(self, source: str, sink: str, parent: Dict[str, Edge]):
        visited = set()
        queue = deque([source])
        visited.add(source)
        while queue:
            u = queue.popleft()
            for edge in self.graph.get(u, []):
                if edge.to not in visited and edge.capacity > edge.flow:
                    visited.add(edge.to)
                    parent[edge.to] = edge
                    queue.append(edge.to)
                    if edge.to == sink:
                        return True
        return False
    
    def edmonds_karp(self, source: str, sink: str) -> int:
        max_flow = 0
        parent = {}
        while self.bfs(source, sink, parent):
            path_flow = float('inf')
            s = sink
            while s != source:
                edge = parent[s]
                path_flow = min(path_flow, edge.capacity - edge.flow)
                s = edge.reverse.to
            max_flow += path_flow
            v = sink
            while v != source:
                edge = parent[v]
                edge.flow += path_flow
                edge.reverse.flow -= path_flow
                v = edge.reverse.to
            parent = {}
        return max_flow

def build_network() -> FlowNetwork:
    network = FlowNetwork()
    terminals = ['Термінал 1', 'Термінал 2']
    sklads = ['Склад 1', 'Склад 2', 'Склад 3', 'Склад 4']
    magazins = [f'Магазин {i}' for i in range(1, 15)]
    
    # Add super source and super sink
    network.add_node('Джерело')
    network.add_node('Споживач')
    
    # Connect source to terminals with high capacity
    for terminal in terminals:
        network.add_edge('Джерело', terminal, 1_000_000)
    
    # Add edges from terminals to sklads
    terminal_edges = [
        ('Термінал 1', 'Склад 1', 25),
        ('Термінал 1', 'Склад 2', 20),
        ('Термінал 1', 'Склад 3', 15),
        ('Термінал 2', 'Склад 3', 15),
        ('Термінал 2', 'Склад 4', 30),
        ('Термінал 2', 'Склад 2', 10),
    ]
    for u, v, cap in terminal_edges:
        network.add_edge(u, v, cap)
    
    # Add edges from sklads to magazins
    sklad_magazin_edges = [
        ('Склад 1', 'Магазин 1', 15),
        ('Склад 1', 'Магазин 2', 10),
        ('Склад 1', 'Магазин 3', 20),
        ('Склад 2', 'Магазин 4', 15),
        ('Склад 2', 'Магазин 5', 10),
        ('Склад 2', 'Магазин 6', 25),
        ('Склад 3', 'Магазин 7', 20),
        ('Склад 3', 'Магазин 8', 15),
        ('Склад 3', 'Магазин 9', 10),
        ('Склад 4', 'Магазин 10', 20),
        ('Склад 4', 'Магазин 11', 10),
        ('Склад 4', 'Магазин 12', 15),
        ('Склад 4', 'Магазин 13', 5),
        ('Склад 4', 'Магазин 14', 10),
    ]
    for u, v, cap in sklad_magazin_edges:
        network.add_edge(u, v, cap)
    
    # Connect magazins to sink
    for magazin in magazins:
        network.add_edge(magazin, 'Споживач', 1_000_000)
    
    return network

def get_flows(network: FlowNetwork) -> Dict[str, Dict[str, int]]:
    terminal_to_sklad = {}
    sklad_magazin_flow = {}
    sklad_total_inflow = {}
    
    # Collect flows from terminals to sklads
    for node in network.graph:
        if node.startswith('Термінал'):
            for edge in network.graph[node]:
                if edge.to.startswith('Склад'):
                    key = (node, edge.to)
                    terminal_to_sklad[key] = edge.flow
    
    # Collect flows from sklads to magazins
    for node in network.graph:
        if node.startswith('Склад'):
            for edge in network.graph[node]:
                if edge.to.startswith('Магазин'):
                    key = (node, edge.to)
                    sklad_magazin_flow[key] = edge.flow
    
    # Calculate total inflow for each sklad
    for sklad in ['Склад 1', 'Склад 2', 'Склад 3', 'Склад 4']:
        total = 0
        for (term, s), flow in terminal_to_sklad.items():
            if s == sklad:
                total += flow
        sklad_total_inflow[sklad] = total
    
    return {
        'terminal_to_sklad': terminal_to_sklad,
        'sklad_magazin_flow': sklad_magazin_flow,
        'sklad_total_inflow': sklad_total_inflow
    }

def generate_flow_table(flows: Dict) -> List[Dict]:
    table = []
    for sklad in ['Склад 1', 'Склад 2', 'Склад 3', 'Склад 4']:
        # Calculate total input capacity
        total_input = sum(flows['terminal_to_sklad'].get((term, sklad), 0)
                         for term in ['Термінал 1', 'Термінал 2'])
        
        # Distribute flow proportionally to connected stores
        for (source, dest), flow in flows['sklad_magazin_flow'].items():
            if source == sklad and flow > 0:
                # Calculate proportional contribution from each terminal
                for term in ['Термінал 1', 'Термінал 2']:
                    term_flow = flows['terminal_to_sklad'].get((term, sklad), 0)
                    if term_flow > 0:
                        proportion = term_flow / total_input
                        table.append({
                            'Термінал': term,
                            'Магазин': dest,
                            'Потік': round(flow * proportion)
                        })
    return table

def main():
    network = build_network()
    max_flow = network.edmonds_karp('Джерело', 'Споживач')
    print(f"Максимальний потік: {max_flow}")
    flows = get_flows(network)
    table = generate_flow_table(flows)
    
    # Print the table
    print("\nТаблиця потоків:")
    print("{:<10} {:<10} {:<15}".format('Термінал', 'Магазин', 'Реальний потік'))
    for entry in table:
        print("{:<10} {:<10} {:<15}".format(entry['Термінал'], entry['Магазин'], entry['Потік']))
    
    # Answer analysis questions
    print("\nАналіз:")
    # 1. Which terminals provide the most flow?
    terminal_flows = {}
    for (term, sklad), flow in flows['terminal_to_sklad'].items():
        terminal_flows[term] = terminal_flows.get(term, 0) + flow
    max_term = max(terminal_flows, key=terminal_flows.get)
    print(f"1. Термінал з найбільшим потоком: {max_term} ({terminal_flows[max_term]} units)")
    
    # 2. Routes with least capacity and impact
    min_capacity = float('inf')
    min_edges = []
    for edge in network.graph:
        for e in network.graph[edge]:
            if e.capacity > 0 and e.capacity < min_capacity:
                min_capacity = e.capacity
                min_edges = [(edge, e.to)]
            elif e.capacity == min_capacity:
                min_edges.append((edge, e.to))
    print(f"2. Маршрути з найменшими ємностями ({min_capacity} одиниць): {min_edges}")
    
    # 3. Stores with least supply and improvement
    magazin_flows = {}
    for entry in table:
        mag = entry['Магазин']
        magazin_flows[mag] = magazin_flows.get(mag, 0) + entry['Потік']
    min_flow = min(magazin_flows.values())
    min_mags = [k for k, v in magazin_flows.items() if v == min_flow]
    print(f"3. Магазини з найменшим постачанням: {min_mags} ({min_flow} units)")
    
    # 4. Identify bottlenecks
    bottlenecks = []
    for edge in network.graph:
        for e in network.graph[edge]:
            if e.flow == e.capacity and e.capacity > 0:
                bottlenecks.append(f"{edge} -> {e.to}")
    print("4. Пляшкові горлишка (ребра з максимальним навантаженням):", bottlenecks[:5])  # Limiting output

if __name__ == "__main__":
    main()