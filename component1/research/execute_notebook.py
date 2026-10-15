"""Notebook Execution Helper using nbclient and nbformat
IT22089236 | D T D Perera | R26-IT-148
"""
from pathlib import Path
import nbformat
from nbclient import NotebookClient

def execute_weight_analysis_notebook():
    research_dir = Path(__file__).resolve().parent
    nb_path = research_dir / "weight_analysis.ipynb"
    
    print(f"Reading notebook from: {nb_path}...")
    nb = nbformat.read(str(nb_path), as_version=4)
    
    print("Executing notebook cells with NotebookClient...")
    client = NotebookClient(nb, timeout=600, kernel_name="python3")
    client.execute(cwd=str(research_dir))
    
    print(f"Writing executed outputs back to: {nb_path}...")
    nbformat.write(nb, str(nb_path))
    print("[SUCCESS] Notebook executed successfully with all tables and outputs saved!")

if __name__ == "__main__":
    execute_weight_analysis_notebook()
