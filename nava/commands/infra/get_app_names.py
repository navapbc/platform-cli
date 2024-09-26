import os
import sys


def get_app_names(dest="."):
    excluded_dirs = {
        "infra",
        "accounts",
        "modules",
        "networks",
        "project-config",
        "test",
    }
    infra_path = os.path.join(dest, "infra")

    if not os.path.exists(infra_path):
        print(f"The path {infra_path} does not exist.")
        return

    for root, dirs, _ in os.walk(infra_path):
        # Only consider directories at the maxdepth 1
        if root == infra_path:
            for dir_name in dirs:
                if dir_name not in excluded_dirs:
                    print(dir_name)
            break
