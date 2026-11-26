from collections import deque
from pathlib import Path

import yaml


YAML_FILE = Path("repo_map.yaml")
OUTPUT_FILE = Path("repos.mmd")


def load_config():
    with YAML_FILE.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def connected_components(repos, edges):
    adjacency = {repo["id"]: set() for repo in repos}
    for source, target in edges:
        adjacency[source].add(target)
        adjacency[target].add(source)

    visited = set()
    components = []
    for repo in repos:
        repo_id = repo["id"]
        if repo_id in visited:
            continue
        component = []
        queue = deque([repo_id])
        visited.add(repo_id)
        while queue:
            current = queue.popleft()
            component.append(current)
            for neighbor in adjacency[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        components.append(component)
    return components


def generate_mermaid(config):
    repos = config.get("repos", [])
    repos_by_id = {repo["id"]: repo for repo in repos}

    edges = []
    for repo in repos:
        for dependency in repo.get("depends_on", []):
            source = repo["id"]
            target = dependency["repo"]
            dependency_type = dependency.get("type", "depends on")
            edges.append((source, target, dependency_type))

    components = connected_components(repos, [(s, t) for s, t, _ in edges])

    lines = ["flowchart LR"]

    cluster_ids = []
    for index, component in enumerate(components):
        subgraph_id = f"cluster_{index}"
        cluster_ids.append(subgraph_id)
        lines.append(f"    subgraph {subgraph_id}")
        for repo_id in component:
            name = repos_by_id[repo_id]["name"]
            lines.append(f'        {repo_id}["{name}"]')
        lines.append("    end")

    lines.append("")
    lines.append("    classDef plain fill:none,stroke:none;")
    lines.append(f"    class {','.join(cluster_ids)} plain;")
    lines.append("")

    for source, target, dep_type in edges:
        lines.append(f"    {source} -->|{dep_type}| {target}")

    return "\n".join(lines)


def main():
    config = load_config()
    mermaid = generate_mermaid(config)

    OUTPUT_FILE.write_text(
        mermaid + "\n",
        encoding="utf-8",
    )

    print(f"Generated: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()