from pathlib import Path

import yaml


YAML_FILE = Path("repo_map.yaml")
OUTPUT_FILE = Path("repos.mmd")


def load_config():
    with YAML_FILE.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def generate_mermaid(config):
    repos = config.get("repos", [])

    lines = [
        "flowchart LR",
    ]

    # Repositories toevoegen als nodes
    for repo in repos:
        repo_id = repo["id"]
        name = repo["name"]

        lines.append(f'    {repo_id}["{name}"]')

    lines.append("")

    # Dependencies toevoegen
    for repo in repos:
        for dependency in repo.get("depends_on", []):
            source = repo["id"]
            target = dependency["repo"]
            dependency_type = dependency.get("type", "depends on")

            lines.append(
                f"    {source} -->|{dependency_type}| {target}"
            )

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