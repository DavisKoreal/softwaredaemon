import os
from treelib import Tree, Node as TreeLibNode



# Your Node and NaryTree classes (included for completeness)
class Node:
    def __init__(self, task: str, level: int = 99999) -> None:
        self.task: str = task
        self.parent: bool = False
        self.leaf: bool = False
        self.level: int = level
        self.subTasks: list = []

    def addSubTask(self, subTaskName: str):
        """Add a child node with the given task"""
        child_node = Node(subTaskName, level=(self.level + 1))
        self.subTasks.append(child_node)
        self.parent = True
        return child_node

    def addListOfSubtasks(self, listofsubtasks):
        if not listofsubtasks:
            return
        for task in listofsubtasks:
            self.subTasks.append(Node(task, level=(self.level + 1)))
        self.parent = True

    def fillTreeWithTasks(self):
        # Placeholder: assuming this interacts with getSubTaskList
        pass

    def __str__(self):
        return str(self.task)

class NaryTree:
    def __init__(self, root_task=None, startlevel=0):
        self.root = Node(root_task, level=startlevel) if root_task is not None else None

    def postorder_traversal(self, node=None):
        """Post-order traversal: subTasks from left to right, then root"""
        if node is None and self.root is None:
            return []

        if node is None:
            node = self.root

        result = []
        if node.parent:
            for child in node.subTasks:
                result.extend(self.postorder_traversal(child))

        if not node.parent:
            result.append(node.task)

        return result

# Function to visualize NaryTree using treelib
def visualize_nary_tree(nary_tree):
    if nary_tree.root is None:
        print("Tree is empty")
        return

    # Create a new treelib Tree
    tree = Tree()

    # Create root node
    root_id = nary_tree.root.task + "_0"  # Unique ID for root
    tree.create_node(nary_tree.root.task, root_id, data=nary_tree.root)

    # Recursive function to add nodes to treelib Tree
    def add_nodes_to_tree(current_node, parent_id, tree):
        for subtask in current_node.subTasks:
            # Create a unique ID for the node (task + level to avoid duplicates)
            node_id = f"{subtask.task}_{subtask.level}"
            tree.create_node(subtask.task, node_id, parent=parent_id, data=subtask)
            # Recursively add subtasks
            add_nodes_to_tree(subtask, node_id, tree)

    # Add all nodes starting from root
    add_nodes_to_tree(nary_tree.root, root_id, tree)

    # Display the tree
    print("\nN-ary Tree Structure:")
    tree.show(line_type="ascii-em")

# Create a sample NaryTree
def create_sample_nary_tree():
    # Initialize tree with root task
    tree = NaryTree(root_task="Main Task", startlevel=0)

    # Add subtasks manually
    root = tree.root
    subtask1 = root.addSubTask("Subtask 1")
    subtask2 = root.addSubTask("Subtask 2")
    subtask3 = root.addSubTask("Subtask 3")

    # Add subtasks to Subtask 1
    subtask1.addListOfSubtasks(["Subtask 1.1", "Subtask 1.2"])
    # Add a subtask to Subtask 1.1
    subtask1.subTasks[0].addSubTask("Subtask 1.1.1")

    # Add subtasks to Subtask 2
    subtask2.addSubTask("Subtask 2.1")

    # Mark leaf nodes (for visualization clarity)
    for node in subtask1.subTasks:
        if not node.subTasks:
            node.leaf = True
    for node in subtask2.subTasks:
        if not node.subTasks:
            node.leaf = True
    if not subtask3.subTasks:
        subtask3.leaf = True

    return tree

# Main execution
if __name__ == "__main__":
    # Create and visualize sample NaryTree
    sample_tree = create_sample_nary_tree()
    visualize_nary_tree(sample_tree)

    # Optional: Print postorder traversal to verify
    print("\nPostorder Traversal:")
    print(sample_tree.postorder_traversal())