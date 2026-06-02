"""
Script to clean up all templates by removing the problematic inline onclick handlers.
"""

import re
from pathlib import Path

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

def clean_template(file_path):
    """Remove inline onclick handler from quiz button."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Remove the onclick attribute that contains the Jinja template syntax
        # Pattern matches: onclick="{% if exam_url %}window.open(\'{{ exam_url }}\', \'_blank\'){% endif %}"
        content = re.sub(
            r' onclick="[^"]*window\.open[^"]*"',
            '',
            content
        )
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Cleaned: {file_path.name}")
            return True
        else:
            print(f"- No change: {file_path.name}")
            return False
        
    except Exception as e:
        print(f"✗ Error cleaning {file_path.name}: {e}")
        return False

def main():
    print("Removing problematic inline onclick handlers...\n")
    
    template_files = list(TEMPLATES_DIR.glob("*.html"))
    updated_count = 0
    
    for template_path in sorted(template_files):
        if clean_template(template_path):
            updated_count += 1
    
    print(f"\n✓ Total cleaned: {updated_count} files")

if __name__ == "__main__":
    main()
