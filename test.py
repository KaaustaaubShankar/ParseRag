import javalang
import mgclient

# Function to create an indented tree-like format
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
def java_code_to_tree(java_code):
    tree = {}
    method_calls = {}
    parsed = javalang.parse.parse(java_code)

    # Extract class information
    for _, node in parsed.filter(javalang.tree.ClassDeclaration):
        tree['Class'] = node.name
        tree['Methods'] = []
        tree['Fields'] = []

        # Extract fields (variables)
        for field in node.fields:
            for declarator in field.declarators:
                field_info = {
                    'name': declarator.name,
                    'type': field.type.name
                }
                tree['Fields'].append(field_info)

        # Extract method information and behavior
        for method in node.methods:
            method_info = {
                'name': method.name,
                'parameters': [(param.type.name, param.name) for param in method.parameters],
                'behavior': []
            }

            if method.body:
                for statement in method.body:
                    behavior, called_method = describe_statement(statement)
                    method_info['behavior'].append(behavior)

                    if called_method:
                        # Add to method_calls for tracking relationships
                        if method.name not in method_calls:
                            method_calls[method.name] = []
                        method_calls[method.name].append(called_method)

            tree['Methods'].append(method_info)

    return tree, method_calls

# Function to create a graph in Memgraph based on method relationships
def create_graph_in_memgraph(method_calls):
    # Connect to Memgraph
    conn = mgclient.connect(host='127.0.0.1', port=7687)  # Adjust if needed
    cursor = conn.cursor()

    # Create nodes and relationships
    for method, calls in method_calls.items():
        # Create a node for the method
        cursor.execute(f"CREATE (:Method {{name: '{method}'}})")
        
        for called_method in calls:
            # Create a node for the called method if it doesn't exist
            cursor.execute(f"CREATE (:Method {{name: '{called_method}'}})")
            # Create a relationship from the calling method to the called method
            cursor.execute(f"""
            MATCH (a:Method {{name: '{method}'}}), (b:Method {{name: '{called_method}'}})
            CREATE (a)-[:CALLS]->(b)
            """)

    # Commit the changes and close the connection
    conn.commit()
    cursor.close()
    conn.close()

# Example Java code to parse
java_code = """
public class HelloWorld {
    private String message;

    public HelloWorld(String message) {
        this.message = message;
    }

    public void sayHello() {
        System.out.println("Hello, " + message);
        anotherMethod();
    }

    public void anotherMethod() {
        System.out.println("This is another method.");
    }
}
"""

# Parse and generate tree structure with behavior descriptions
code_tree, method_calls = java_code_to_tree(java_code)
print_tree(code_tree)

# Create the graph in Memgraph
create_graph_in_memgraph(method_calls)

print("\nGraph created in Memgraph based on method calls.")
