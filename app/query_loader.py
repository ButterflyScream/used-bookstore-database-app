
# app/query_loader.py
# This file loads the SQL queries into the Python app logic (.py) files

def load_queries(path="db/queries.sql"):
    queries = {}
    with open(path, "r") as file:
        lines = file.readlines()

    current_name = None
    current_query = []

    for line in lines:
        stripped = line.strip()

        # Start of a named query
        if stripped.startswith("-- name:"):
            if current_name:
                queries[current_name] = "".join(current_query).strip()
                current_query = []
            current_name = stripped.split("-- name:")[1].strip()
        # Skip all other comments
        elif stripped.startswith("--"):
            continue
        # Otherwise, collect SQL lines
        elif current_name:
            current_query.append(line)

    # Add the final query if any
    if current_name:
        queries[current_name] = "".join(current_query).strip()

    return queries