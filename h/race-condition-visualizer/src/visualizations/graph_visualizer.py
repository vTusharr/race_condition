"""
Graph visualizations using NetworkX and Matplotlib.
Creates state transition graphs and timeline diagrams for race conditions and Peterson's algorithm.
"""

import networkx as nx
import matplotlib.pyplot as plt
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.state_machine import RaceConditionStateMachine, PetersonStateMachine, ProcessState


def visualize_race_condition_graph(output_path=None):
    """
    Create a directed graph showing race condition state transitions.
    Highlights the problematic paths where lost updates occur.
    """
    sm = RaceConditionStateMachine()
    
    # Create directed graph
    G = nx.DiGraph()
    
    # Add nodes with state information
    for idx, state in enumerate(sm.states):
        label = f"S{idx}\nP1:{state.p1_state.value[:3]}\nP2:{state.p2_state.value[:3]}\nC={state.counter}"
        G.add_node(idx, label=label, state=state)
    
    # Add edges from transitions
    for trans in sm.transitions:
        from_idx = sm.states.index(trans.from_state)
        to_idx = sm.states.index(trans.to_state)
        G.add_edge(from_idx, to_idx, action=trans.action, process=trans.process)
    
    # Create figure
    plt.figure(figsize=(16, 12))
    
    # Use spring layout for better visualization
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    
    # Color nodes based on state type
    node_colors = []
    for idx in G.nodes():
        state = sm.states[idx]
        if state.is_race_condition():
            node_colors.append('#FF6B6B')  # Red for race condition
        elif state.p1_state == ProcessState.IDLE and state.p2_state == ProcessState.IDLE:
            if state.counter == 0:
                node_colors.append('#4ECDC4')  # Cyan for initial
            else:
                node_colors.append('#95E1D3')  # Light green for final
        else:
            node_colors.append('#FFE66D')  # Yellow for normal states
    
    # Draw the graph
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                          node_size=3000, alpha=0.9, edgecolors='black', linewidths=2)
    
    # Draw labels
    labels = nx.get_node_attributes(G, 'label')
    nx.draw_networkx_labels(G, pos, labels, font_size=9, font_weight='bold')
    
    # Draw edges with arrows
    nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True,
                          arrowsize=20, arrowstyle='->', width=2,
                          connectionstyle='arc3,rad=0.1')
    
    # Add edge labels (process actions)
    edge_labels = {}
    for u, v, data in G.edges(data=True):
        action = data['action']
        if len(action) > 20:
            action = action[:17] + "..."
        edge_labels[(u, v)] = action
    
    nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=7)
    
    # Add title and legend
    plt.title("Race Condition State Transition Graph\n" + 
             "Red = Race Condition States | Yellow = Normal | Cyan/Green = Initial/Final",
             fontsize=16, fontweight='bold', pad=20)
    
    plt.axis('off')
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved race condition graph to {output_path}")
    else:
        plt.show()
    
    plt.close()


def visualize_race_condition_timeline(output_path=None):
    """
    Create a timeline visualization showing the race condition scenario.
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Scenario 1: Safe execution (sequential)
    ax1.set_title("Safe Execution: Sequential Access", fontsize=14, fontweight='bold')
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 3)
    ax1.set_yticks([1, 2])
    ax1.set_yticklabels(['Process 2', 'Process 1'])
    ax1.set_xlabel('Time →', fontsize=12)
    
    # P1 executes first
    ax1.barh(2, 2, left=1, height=0.6, color='#4ECDC4', edgecolor='black', linewidth=2)
    ax1.text(2, 2, 'READ\nC=0', ha='center', va='center', fontweight='bold')
    
    ax1.barh(2, 2, left=3, height=0.6, color='#4ECDC4', edgecolor='black', linewidth=2)
    ax1.text(4, 2, 'WRITE\nC=1', ha='center', va='center', fontweight='bold')
    
    # P2 executes second
    ax1.barh(1, 2, left=5, height=0.6, color='#FFE66D', edgecolor='black', linewidth=2)
    ax1.text(6, 1, 'READ\nC=1', ha='center', va='center', fontweight='bold')
    
    ax1.barh(1, 2, left=7, height=0.6, color='#FFE66D', edgecolor='black', linewidth=2)
    ax1.text(8, 1, 'WRITE\nC=2', ha='center', va='center', fontweight='bold')
    
    ax1.text(9.5, 2.7, 'Result: C=2 (Correct)', fontsize=12, 
            color='green', fontweight='bold', bbox=dict(boxstyle='round', facecolor='lightgreen'))
    
    # Scenario 2: Race condition (concurrent)
    ax2.set_title("Race Condition: Concurrent Access (Lost Update)", fontsize=14, fontweight='bold')
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 3)
    ax2.set_yticks([1, 2])
    ax2.set_yticklabels(['Process 2', 'Process 1'])
    ax2.set_xlabel('Time →', fontsize=12)
    
    # Both processes read simultaneously
    ax2.barh(2, 2, left=1, height=0.6, color='#FF6B6B', edgecolor='black', linewidth=2)
    ax2.text(2, 2, 'READ\nC=0', ha='center', va='center', fontweight='bold')
    
    ax2.barh(1, 2, left=1, height=0.6, color='#FF6B6B', edgecolor='black', linewidth=2)
    ax2.text(2, 1, 'READ\nC=0', ha='center', va='center', fontweight='bold')
    
    ax2.text(3.5, 1.5, 'WARNING: BOTH READ\nSAME VALUE', ha='center', va='center',
            fontsize=11, color='red', fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='#FFE6E6', edgecolor='red', linewidth=2))
    
    # Both write
    ax2.barh(2, 2, left=5, height=0.6, color='#FF6B6B', edgecolor='black', linewidth=2)
    ax2.text(6, 2, 'WRITE\nC=1', ha='center', va='center', fontweight='bold')
    
    ax2.barh(1, 2, left=7, height=0.6, color='#FF6B6B', edgecolor='black', linewidth=2)
    ax2.text(8, 1, 'WRITE\nC=1', ha='center', va='center', fontweight='bold')
    
    ax2.text(9.5, 2.7, 'ERROR: Result: C=1 (Wrong)', fontsize=12, 
            color='red', fontweight='bold', bbox=dict(boxstyle='round', facecolor='#FFE6E6'))
    
    ax2.text(5, 0.3, 'Lost Update: Expected C=2, but got C=1', fontsize=11,
            style='italic', ha='center')
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved race condition timeline to {output_path}")
    else:
        plt.show()
    
    plt.close()


def visualize_peterson_graph(output_path=None):
    """
    Create a directed graph showing Peterson's algorithm state transitions.
    Demonstrates that mutual exclusion is preserved.
    """
    sm = PetersonStateMachine()
    
    # Verify mutual exclusion
    is_safe = sm.verify_mutual_exclusion()
    
    # Create directed graph
    G = nx.DiGraph()
    
    # Add nodes
    for idx, state in enumerate(sm.states):
        label = f"S{idx}\nP1:{state.p1_state.value[:4]}\nP2:{state.p2_state.value[:4]}"
        label += f"\nf1={int(state.flag1)} f2={int(state.flag2)}\nturn={state.turn}"
        G.add_node(idx, label=label, state=state)
    
    # Add edges
    for trans in sm.transitions:
        from_idx = sm.states.index(trans.from_state)
        to_idx = sm.states.index(trans.to_state)
        G.add_edge(from_idx, to_idx, action=trans.action, process=trans.process)
    
    # Create figure
    plt.figure(figsize=(16, 12))
    
    # Use spring layout
    pos = nx.spring_layout(G, k=2.5, iterations=50, seed=43)
    
    # Color nodes based on state
    node_colors = []
    for idx in G.nodes():
        state = sm.states[idx]
        if state.p1_state == ProcessState.CRITICAL or state.p2_state == ProcessState.CRITICAL:
            node_colors.append('#95E1D3')  # Green for critical section
        elif state.p1_state == ProcessState.WAITING or state.p2_state == ProcessState.WAITING:
            node_colors.append('#FFE66D')  # Yellow for waiting
        else:
            node_colors.append('#4ECDC4')  # Cyan for idle
    
    # Draw the graph
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                          node_size=3500, alpha=0.9, edgecolors='black', linewidths=2)
    
    # Draw labels
    labels = nx.get_node_attributes(G, 'label')
    nx.draw_networkx_labels(G, pos, labels, font_size=8, font_weight='bold')
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True,
                          arrowsize=20, arrowstyle='->', width=2,
                          connectionstyle='arc3,rad=0.1')
    
    # Add edge labels
    edge_labels = {}
    for u, v, data in G.edges(data=True):
        action = data['action']
        if len(action) > 25:
            action = action[:22] + "..."
        edge_labels[(u, v)] = action
    
    nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=6)
    
    # Add title
    status = "MUTUAL EXCLUSION VERIFIED" if is_safe else "VIOLATION DETECTED"
    color = 'green' if is_safe else 'red'
    plt.title(f"Peterson's Algorithm State Transition Graph\n{status}\n" + 
             "Green = Critical Section | Yellow = Waiting | Cyan = Idle",
             fontsize=16, fontweight='bold', pad=20, color=color)
    
    plt.axis('off')
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved Peterson's algorithm graph to {output_path}")
    else:
        plt.show()
    
    plt.close()


def visualize_peterson_timeline(output_path=None):
    """
    Create a timeline visualization showing Peterson's algorithm in action.
    """
    fig, ax = plt.subplots(figsize=(14, 8))
    
    ax.set_title("Peterson's Algorithm: Mutual Exclusion Guaranteed", fontsize=14, fontweight='bold')
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 3)
    ax.set_yticks([1, 2])
    ax.set_yticklabels(['Process 2', 'Process 1'])
    ax.set_xlabel('Time →', fontsize=12)
    
    # P1 wants to enter
    ax.barh(2, 1.5, left=1, height=0.5, color='#FFE66D', edgecolor='black', linewidth=2)
    ax.text(1.75, 2, 'flag[1]=T\nturn=2', ha='center', va='center', fontsize=9, fontweight='bold')
    
    # P1 enters critical section
    ax.barh(2, 3, left=2.5, height=0.5, color='#95E1D3', edgecolor='black', linewidth=2)
    ax.text(4, 2, 'CRITICAL\nSECTION', ha='center', va='center', fontsize=10, fontweight='bold')
    
    # P1 exits
    ax.barh(2, 1, left=5.5, height=0.5, color='#4ECDC4', edgecolor='black', linewidth=2)
    ax.text(6, 2, 'flag[1]=F', ha='center', va='center', fontsize=9, fontweight='bold')
    
    # P2 wants to enter while P1 is in CS
    ax.barh(1, 1.5, left=3, height=0.5, color='#FFD93D', edgecolor='black', linewidth=2)
    ax.text(3.75, 1, 'flag[2]=T\nturn=1', ha='center', va='center', fontsize=9, fontweight='bold')
    
    # P2 waits (blocked by Peterson's algorithm)
    ax.barh(1, 2, left=4.5, height=0.5, color='#FF6B6B', edgecolor='black', linewidth=3)
    ax.text(5.5, 1, 'WAITING\n(blocked)', ha='center', va='center', fontsize=10, fontweight='bold', color='white')
    
    # P2 enters after P1 exits
    ax.barh(1, 3, left=6.5, height=0.5, color='#95E1D3', edgecolor='black', linewidth=2)
    ax.text(8, 1, 'CRITICAL\nSECTION', ha='center', va='center', fontsize=10, fontweight='bold')
    
    # P2 exits
    ax.barh(1, 1, left=9.5, height=0.5, color='#4ECDC4', edgecolor='black', linewidth=2)
    ax.text(10, 1, 'flag[2]=F', ha='center', va='center', fontsize=9, fontweight='bold')
    
    # Add annotations
    ax.annotate('Only ONE process\nin critical section', xy=(4, 1.5), xytext=(12, 1.5),
               fontsize=11, color='green', fontweight='bold',
               bbox=dict(boxstyle='round', facecolor='lightgreen'),
               arrowprops=dict(arrowstyle='->', color='green', lw=2))
    
    ax.text(10, 2.7, 'Mutual Exclusion Guaranteed\nNo race conditions possible', 
           fontsize=12, color='green', fontweight='bold', ha='center',
           bbox=dict(boxstyle='round', facecolor='lightgreen', edgecolor='green', linewidth=2))
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved Peterson's algorithm timeline to {output_path}")
    else:
        plt.show()
    
    plt.close()


if __name__ == "__main__":
    print("Generating visualizations...")
    os.makedirs("animations", exist_ok=True)
    
    print("\n1. Race Condition Visualizations")
    visualize_race_condition_graph("animations/race_condition_graph.png")
    visualize_race_condition_timeline("animations/race_condition_timeline.png")
    
    print("\n2. Peterson's Algorithm Visualizations")
    visualize_peterson_graph("animations/peterson_graph.png")
    visualize_peterson_timeline("animations/peterson_timeline.png")
    
    print("\nAll visualizations generated successfully!")
