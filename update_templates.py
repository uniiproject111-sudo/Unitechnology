"""
Script to update all course HTML templates to support exam URLs.
"""

import re
from pathlib import Path

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

# List of course template files to update (excluding generic templates)
COURSE_TEMPLATES = [
    "Photoshop.html",
    "MicrosoftWord.html",
    "MicrosoftExcel.html",
    "powerpoint.html",
    "MicrosoftTeams.html",
    "MicrosoftOutlook.html",
    "MicrosoftOneNote.html",
    "MicrosoftAccess.html",
    "Ilustrator.html",
    "Canva.html",
    "InDesign.html",
    "premiere.html",
    "CapCut.html",
    "Filmora.html",
    "Lightroom.html",
    "PanoramaMaker.html",
    "Audacity.html",
    "Audition.html",
    "WordPress.html",
    "googleclassroom.html",
    "Googledrive.html",
    "GoogleForms.html",
    "GoogleSites.html",
    "claudeai.html",
    "KlingAI.html",
    "Openread.html",
    "NotebookLM.html",
    "FlowAI.html",
    "لهجاتي.html",
    "figma.html"
]

def update_course_template(file_path):
    """Update a course template to add proper quiz button handler."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Remove old onclick handler if it exists
        content = re.sub(
            r'onclick="{% if exam_url %}window\.open\(\'{{ exam_url }}\', \'_blank\'\){% endif %}"',
            '',
            content
        )
        
        # Check if quiz button script is already updated
        if 'const examUrl = "{{ exam_url }}"' in content:
            if content == original_content:
                print(f"✓ Already updated: {file_path.name}")
            else:
                print(f"✓ Fixed: {file_path.name}")
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            return True
        
        # Add event listener script after toast variable declaration
        script_to_add = '''    // Quiz button handler
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
    '''
        
        # Find where to insert - after "const toast" line
        pattern = r'(const toast = document\.getElementById\(\'toast\'\);.*?function showToast\(.*?\) \{.*?\})'
        
        if re.search(pattern, content, re.DOTALL):
            # Add exam URL variable at the beginning of the script
            new_content = re.sub(
                r'(  <div id="toast"></div>\n  <script>\n)',
                r'\1    const examUrl = "{{ exam_url }}";\n',
                content
            )
            
            # Add quiz button handler after showToast function
            new_content = re.sub(
                r'(function showToast\(msg, type=\'success\'\) \{ toast\.textContent = msg; toast\.className = \'show \' \+ type; setTimeout\(() => toast\.className = \'\', 3000\); \})',
                r'\1\n    \n' + script_to_add.replace("    ", "    "),
                new_content
            )
            
            if new_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"✓ Updated: {file_path.name}")
                return True
        
        print(f"✗ Could not update: {file_path.name}")
        return False
        
    except Exception as e:
        print(f"✗ Error updating {file_path.name}: {e}")
        return False

def main():
    print("Updating course templates with exam URL support...")
    print(f"Templates directory: {TEMPLATES_DIR}\n")
    
    updated_count = 0
    failed_count = 0
    
    for template_file in COURSE_TEMPLATES:
        template_path = TEMPLATES_DIR / template_file
        
        if not template_path.exists():
            print(f"✗ File not found: {template_file}")
            failed_count += 1
            continue
        
        if update_course_template(template_path):
            updated_count += 1
        else:
            failed_count += 1
    
    print(f"\n📊 Summary:")
    print(f"✓ Successfully updated: {updated_count}")
    print(f"✗ Failed/Skipped: {failed_count}")

if __name__ == "__main__":
    main()
