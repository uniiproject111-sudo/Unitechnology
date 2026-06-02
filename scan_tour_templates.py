import re
from pathlib import Path
root = Path('templates')
old = []
for path in sorted(root.glob('*.html')):
    text = path.read_text(encoding='utf-8')
    if 'function showStep' in text:
        m = re.search(r'function showStep\s*\(\)\s*\{([\s\S]*?)\n\}', text)
        if m:
            body = m.group(1)
            if 'while (currentStepIdx' not in body and 'if (!step || !step.element) return' in body:
                old.append(path.name)
print('old pages:', len(old))
for name in old:
    print(name)
