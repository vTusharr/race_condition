
import os
import subprocess
import sys


def main():
    print("=" * 60)
    print("  Race Condition Visualizer")
    print("  Graph-Theoretic Modeling with NetworkX + Matplotlib")
    print("=" * 60)
    print()

    # Get project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    c_examples_dir = os.path.join(project_root, "c_examples")
    animations_dir = os.path.join(project_root, "animations")

    # Create directories if needed
    os.makedirs(animations_dir, exist_ok=True)

    
    race_c = os.path.join(c_examples_dir, "race_condition_example.c")
    peterson_c = os.path.join(c_examples_dir, "peterson_algorithm.c")

    if os.path.exists(race_c) and os.path.exists(peterson_c):
        print("C example files found")
        compile_c_examples(c_examples_dir)
    else:
        print("Warning: C example files not found in", c_examples_dir)

    print()
    print("=" * 60)
    print("Visualization Options:")
    print("=" * 60)
    print("1. Race Condition State Graph")
    print("2. Race Condition Timeline Diagram")
    print("3. Peterson's Algorithm State Graph")
    print("4. Peterson's Algorithm Timeline Diagram")
    print("5. Run C Race Condition Example")
    print("6. Run C Peterson's Algorithm Example")
    print("7. Generate ALL Visualizations")
    print("0. Exit")
    print("=" * 60)

    choice = input("\nEnter your choice: ").strip()
    
    # Import graph visualizer
    sys.path.insert(0, os.path.join(project_root, "src"))
    from visualizations.graph_visualizer import (
        visualize_race_condition_graph,
        visualize_race_condition_timeline,
        visualize_peterson_graph,
        visualize_peterson_timeline
    )
    
    if choice == "1":
        print("\nGenerating race condition state graph...")
        visualize_race_condition_graph(os.path.join(animations_dir, "race_condition_graph.png"))
    elif choice == "2":
        print("\nGenerating race condition timeline...")
        visualize_race_condition_timeline(os.path.join(animations_dir, "race_condition_timeline.png"))
    elif choice == "3":
        print("\nGenerating Peterson's algorithm state graph...")
        visualize_peterson_graph(os.path.join(animations_dir, "peterson_graph.png"))
    elif choice == "4":
        print("\nGenerating Peterson's algorithm timeline...")
        visualize_peterson_timeline(os.path.join(animations_dir, "peterson_timeline.png"))
    elif choice == "5":
        run_c_example(c_examples_dir, "race_condition")
    elif choice == "6":
        run_c_example(c_examples_dir, "peterson")
    elif choice == "7":
        print("\nGenerating all visualizations...")
        visualize_race_condition_graph(os.path.join(animations_dir, "race_condition_graph.png"))
        visualize_race_condition_timeline(os.path.join(animations_dir, "race_condition_timeline.png"))
        visualize_peterson_graph(os.path.join(animations_dir, "peterson_graph.png"))
        visualize_peterson_timeline(os.path.join(animations_dir, "peterson_timeline.png"))
        print("\nAll visualizations complete! Check the animations/ directory")
    elif choice == "0":
        print("Goodbye!")
        sys.exit(0)
    else:
        print("Invalid choice")
def compile_c_examples(c_dir):
    """Compile C examples and generate assembly"""
    print("\nCompiling C examples...")

    examples = [
        ("race_condition_example.c", "race_condition"),
        ("peterson_algorithm.c", "peterson"),
    ]

    for src, out in examples:
        src_path = os.path.join(c_dir, src)
        if not os.path.exists(src_path):
            continue

        try:
            # Generate 
            asm_path = os.path.join(c_dir, f"{out}.s")
            subprocess.run(
                ["gcc", "-O0", "-g", "-S", src_path, "-o", asm_path],
                check=True,
                capture_output=True,
            )

            # Compile 
            exe_path = os.path.join(c_dir, f"{out}.exe")
            subprocess.run(
                ["gcc", "-O0", "-g", src_path, "-o", exe_path, "-lpthread"],
                check=True,
                capture_output=True,
            )

            print(f"  Compiled {src}")
        except subprocess.CalledProcessError as e:
            print(f"  Error compiling {src}")
            if e.stderr:
                print(f"    {e.stderr.decode()}")
        except FileNotFoundError:
            print("  Error: gcc not found. Install MinGW-w64 for Windows")
            print("    Download: https://www.mingw-w64.org/")
            break


def run_c_example(c_dir, example_name):
    """Run a compiled C example"""
    exe_path = os.path.join(c_dir, f"{example_name}.exe")

    if not os.path.exists(exe_path):
        print(f"Error: Executable not found: {exe_path}")
        print("   Please compile the C examples first (they should auto-compile)")
        return

    print(f"\n Running {example_name}...")
    print("=" * 60)
    try:
        result = subprocess.run([exe_path], capture_output=True, timeout=10, encoding='utf-8', errors='replace')
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
    except subprocess.TimeoutExpired:
        print("Error: Program timed out (possible infinite loop)")
    except Exception as e:
        print(f"Error running example: {e}")
    print("=" * 60)


if __name__ == "__main__":
    main()
