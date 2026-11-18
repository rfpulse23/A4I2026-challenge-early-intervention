from pathlib import Path

p = Path("/config/A4I2026-challenge-early-intervention/ui/static/js/components/GoogleCloudAssist.js")
content = p.read_text(encoding="utf-8")

# Completely remove the quick-questions-section from the scroll content
import re
pattern = r'<!-- Demo Questions.*?</div>\s*</div>\s*</div>'
if re.search(pattern, content, re.DOTALL):
    content = re.sub(pattern, '</div>', content, flags=re.DOTALL)
    p.write_text(content, encoding="utf-8")
    print("Successfully removed Curated Demo Questions section completely!")
else:
    # Try alternate pattern if comment differs
    pattern2 = r'<div class="quick-questions-section">.*?</div>\s*</div>\s*</div>'
    if re.search(pattern2, content, re.DOTALL):
        content = re.sub(pattern2, '</div>', content, flags=re.DOTALL)
        p.write_text(content, encoding="utf-8")
        print("Removed using pattern2!")
    else:
        print("Could not match pattern, please inspect file.")
