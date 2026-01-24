import os
import re

def get_imports(file_path):
    imports = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                match = re.search(r'^(?:from|import)\s+([a-zA-Z0-9_.]+)', line)
                if match:
                    imports.append(match.group(1))
    except:
        pass
    return imports

workspace = r"c:\Users\diego\Desktop\Master_BigData_IA\forestGuardian\forestGuardianRL"
files = [f for f in os.listdir(workspace) if f.endswith('.py')]
graph = {}

for f in files:
    name = f[:-3]
    path = os.path.join(workspace, f)
    graph[name] = [imp for imp in get_imports(path) if imp in [file[:-3] for file in files]]

print("Dependency Graph:")
for k, v in graph.items():
    print(f"{k}: {v}")

def find_cycles(node, visited, stack):
    visited.add(node)
    stack.add(node)
    for neighbor in graph.get(node, []):
        if neighbor not in visited:
            if find_cycles(neighbor, visited, stack):
                return True
        elif neighbor in stack:
            print(f"Cycle detected: {node} -> {neighbor}")
            return True
    stack.remove(node)
    return False

visited = set()
for node in graph:
    if node not in visited:
        if find_cycles(node, visited, set()):
            print("Circular dependency found!")
            break
else:
    print("No circular dependencies found.")
