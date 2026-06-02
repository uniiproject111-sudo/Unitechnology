"""
Script to add quiz button event listener to all templates that have const examUrl
"""

import re
from pathlib import Path

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

LISTENER_CODE = """    // Quiz button handler
    const quizBtn = document.getElementById('quizBtn');
    if (quizBtn) {
      quizBtn.addEventListener('click', function() {
        if (examUrl && examUrl.trim()) {
          window.open(examUrl, '_blank');
        } else {
          showToast('❌ رابط الامتحان غير متوفر حالياً', 'error');
        }
      });
    }
    """

def add_quiz_listener(file_path):
    """Add quiz button event listener if not present."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if it already has the listener
        if "quizBtn.addEventListener('click'" in content:
            print(f"✓ Already has listener: {file_path.name}")
            return True
        
        # Check if it has const examUrl
        if 'const examUrl = "{{ exam_url }}"' not in content:
            print(f"- No examUrl variable: {file_path.name}")
            return False
        
        # Find the showToast function and add listener after it
        # Pattern: function showToast(...) { ... }
        pattern = r'(function showToast\([^)]*\)\s*\{[^}]*\})'
        match = re.search(pattern, content)
        
        if match:
            insertion_point = match.end()
            new_content = content[:insertion_point] + "\n" + LISTENER_CODE + content[insertion_point:]
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✓ Added listener: {file_path.name}")
            return True
        else:
            print(f"✗ Could not find insertion point: {file_path.name}")
            return False
        
    except Exception as e:
        print(f"✗ Error processing {file_path.name}: {e}")
        return False

def main():
    print("Adding quiz button event listeners...\n")
    
    template_files = list(TEMPLATES_DIR.glob("*.html"))
    added_count = 0
    
    for template_path in sorted(template_files):
        if add_quiz_listener(template_path):
            added_count += 1
    
    print(f"\n✓ Total listeners added: {added_count}")

if __name__ == "__main__":
    main()
