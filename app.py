import os
import javalang
import mgclient
from datetime import datetime
import json  # Import the json module for serialization

# Function to create an indented tree-like format (for printing)
def print_tree(node, indent=''):
    print(indent + str(node))
    indent += '  '
    if isinstance(node, dict):
        for key, value in node.items():
            print(f'{indent}{key}:')
            print_tree(value, indent + '  ')
    elif isinstance(node, list):
        for item in node:
            print_tree(item, indent)
    else:
        print(indent + str(node))

# Function to describe what a statement does and track method calls
def describe_statement(statement):
    if isinstance(statement, javalang.tree.StatementExpression):
        expression = statement.expression
        if isinstance(expression, javalang.tree.MethodInvocation):
            invoked_method = expression.member
            return f"Calls method: {invoked_method}", invoked_method
        elif isinstance(expression, javalang.tree.Assignment):
            return f"Assigns value {expression.value} to {expression.expression}", None
    elif isinstance(statement, javalang.tree.LocalVariableDeclaration):
        return f"Declares variable {statement.declarators[0].name} of type {statement.type.name}", None
    return "Unknown action", None

# Function to parse Java code and represent it as a tree with behavior and relationships
def java_code_to_tree(java_code, filename):
    tree = {}
    method_calls = {}
    parsed = javalang.parse.parse(java_code)

    # Extract class information
    for _, node in parsed.filter(javalang.tree.ClassDeclaration):
        class_info = {
            'name': node.name,
            'extends': node.extends.name if node.extends else None,
            'methods': [],
            'fields': []
        }

        # Extract fields (variables)
        for field in node.fields:
            for declarator in field.declarators:
                field_info = {
                    'name': declarator.name,
                    'type': field.type.name
                }
                class_info['fields'].append(field_info)

        # Extract method information and behavior
        for method in node.methods:
            method_info = {
                'name': method.name,
                'parameters': [(param.type.name, param.name) for param in method.parameters],
                'behavior': [],
                'called_methods': []  # Track called methods
            }

            if method.body:
                for statement in method.body:
                    behavior, called_method = describe_statement(statement)
                    method_info['behavior'].append(behavior)

                    if called_method:
                        # Store the qualified called method name for relationships
                        qualified_called_method = f"{filename}.{called_method}"
                        method_info['called_methods'].append(qualified_called_method)

            # Add method name with filename to method calls
            qualified_method_name = f"{filename}.{method.name}"
            method_calls[qualified_method_name] = method_info  # Store the method info
            
            class_info['methods'].append(method_info)

        # Add the class information to the tree
        tree[class_info['name']] = class_info

    return tree, method_calls

# Function to create a graph in Memgraph based on method relationships and class inheritance
def create_graph_in_memgraph(method_calls, class_info, filename):
    # Connect to Memgraph
    conn = mgclient.connect(host='127.0.0.1', port=7687)  # Adjust if needed
    cursor = conn.cursor()

    # Create nodes for each class (avoid duplicates with MERGE)
    for class_name, info in class_info.items():
        # Create a node for the class with additional properties
        creation_time = datetime.now().isoformat()  # Get current time as ISO format

        # Convert fields to JSON format
        fields_json = json.dumps(info['fields'])

        cursor.execute("""
            MERGE (c:Class {name: $class_name})
            ON CREATE SET c.extends = $extends, c.file = $filename, c.created_at = $created_at, c.fields = $fields
        """, {
            'class_name': class_name,
            'extends': info['extends'],
            'filename': filename,
            'created_at': creation_time,
            'fields': fields_json
        })

        # Create nodes for each method in the class (avoid duplicates with MERGE)
        for method in info['methods']:
            method_name = f"{filename}.{method['name']}"
            # Convert parameters and behavior to JSON format
            parameters_json = json.dumps(method['parameters'])
            behavior_json = json.dumps(method['behavior'])

            cursor.execute("""
                MERGE (m:Method {name: $method_name})
                ON CREATE SET m.file = $filename, m.created_at = $created_at, m.parameters = $parameters, m.behavior = $behavior
            """, {
                'method_name': method_name,
                'filename': filename,
                'created_at': creation_time,
                'parameters': parameters_json,
                'behavior': behavior_json
            })

    # Create relationships based on method calls (avoid duplicate relationships with MERGE)
    for method, info in method_calls.items():
        for called_method in info['called_methods']:
            # Create a relationship from the calling method to the called method
            cursor.execute("""
            MATCH (a:Method {name: $method}), (b:Method {name: $called_method})
            MERGE (a)-[:CALLS]->(b)
            """, {
                'method': method,
                'called_method': called_method
            })

    # Create inheritance relationships (avoid duplicate relationships with MERGE)
    for class_name, info in class_info.items():
        if info['extends']:
            cursor.execute("""
            MATCH (a:Class {name: $class_name}), (b:Class {name: $extends})
            MERGE (a)-[:EXTENDS]->(b)
            """, {
                'class_name': class_name,
                'extends': info['extends']
            })

    # Commit the changes and close the connection
    conn.commit()
    cursor.close()
    conn.close()

# Function to process all Java files in a directory
def process_java_files_in_directory(directory):
    class_info = {}
    for filename in os.listdir(directory):
        if filename.endswith('.java'):
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r') as file:
                java_code = file.read()
                print(f"Processing file: {filename}")
                
                # Parse and generate tree structure with behavior descriptions
                code_tree, method_calls = java_code_to_tree(java_code, filename)
                print_tree(code_tree)  # Print the tree structure

                # Store class info for graph creation
                class_info.update(code_tree)  # Add class info to the main class_info dictionary

                # Create the graph in Memgraph
                create_graph_in_memgraph(method_calls, class_info, filename)

# Example directory containing Java files
java_directory = '/Users/kaaustaaubshankar/Documents/Coding/ParseRag/medava'  # Adjust this path to your directory

# Clear the graph before processing
def drop_all_in_memgraph():
    conn = mgclient.connect(host='127.0.0.1', port=7687)  # Adjust if needed
    cursor = conn.cursor()
    cursor.execute("MATCH (n) DETACH DELETE n;")  # Clear all nodes and relationships
    conn.commit()
    cursor.close()
    conn.close()

# Drop all nodes and relationships in Memgraph
drop_all_in_memgraph()

# Process Java files in the specified directory
process_java_files_in_directory(java_directory)

print("All Java files have been processed and graphs created in Memgraph.")
