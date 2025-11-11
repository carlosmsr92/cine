
import os
import sys
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from pathlib import Path
import asyncio
if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

NOTEBOOKS_DIR = Path(__file__).resolve().parents[1] / 'notebooks'


def run_all_notebooks():
    notebooks = sorted(NOTEBOOKS_DIR.glob('*.ipynb'))
    if not notebooks:
        print(f'No notebooks found in {NOTEBOOKS_DIR}')
        sys.exit(1)
    for nb_path in notebooks:
        print(f'Running {nb_path.name}...')
        with open(nb_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
        try:
            ep.preprocess(nb, {'metadata': {'path': NOTEBOOKS_DIR}})
            with open(nb_path, 'w', encoding='utf-8') as f:
                nbformat.write(nb, f)
            print(f'✅ {nb_path.name} executed and saved.')
        except Exception as e:
            print(f'❌ Error running {nb_path.name}: {e}')
            sys.exit(2)

if __name__ == '__main__':
    run_all_notebooks()
