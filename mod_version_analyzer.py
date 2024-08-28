import json
from collections import defaultdict, Counter


def load_config(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)


def get_closest_versions(target_versions, mod_versions):
    mod_versions.sort(key=lambda x: [int(i) for i in x.split('.')])
    closest_versions = []
    for target in target_versions:
        for version in mod_versions:
            if version.startswith(target):
                closest_versions.append(version)
                break
    return closest_versions[:3]


def analyze_mods(config):
    target_versions = config["target_versions"]
    mod_data = config["mods"]

    compatibility = defaultdict(list)

    for version in target_versions:
        for mod in mod_data:
            mod_name = mod["name"]
            mod_versions = mod["versions"]
            mod_importance = mod["importance"]

            # If the target version is not in the mod's available versions, it's incompatible
            if not any(version.startswith(v) for v in mod_versions):
                compatibility[version].append((mod_name, mod_importance))

    return compatibility


def prioritize_versions(compatibility, top_n=5):
    # Calculate score based on mod importance
    scores = Counter()
    importance_weights = {"high": 3, "medium": 2, "low": 1}

    for version, mods in compatibility.items():
        for mod_name, importance in mods:
            scores[version] += importance_weights.get(importance, 1)

    # Sort versions by compatibility score (lower score means more compatible)
    prioritized_versions = sorted(scores.items(), key=lambda x: x[1])
    return prioritized_versions[:top_n]


def main():
    config = load_config('config.json')
    compatibility = analyze_mods(config)
    prioritized_versions = prioritize_versions(compatibility)

    print(f"Top {len(prioritized_versions)} versions to update:")
    for version, score in prioritized_versions:
        incompatible_mods = compatibility[version]
        print(f"\nVersion: {version}, Compatibility Score: {score}")
        if incompatible_mods:
            print(f"The following mods are not compatible:")
            for mod_name, importance in incompatible_mods:
                print(f"- {mod_name} (Importance: {importance})")
        else:
            print("All mods are compatible.")


if __name__ == "__main__":
    main()
