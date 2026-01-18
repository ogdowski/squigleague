"""
Validate HTML file before deploying
"""
import sys
from pathlib import Path
from html.parser import HTMLParser

class HTMLValidator(HTMLParser):
    def __init__(self):
        super().__init__()
        self.errors = []
        self.tag_stack = []
        
    def handle_starttag(self, tag, attrs):
        if tag not in ['img', 'br', 'hr', 'input', 'meta', 'link']:
            self.tag_stack.append(tag)
    
    def handle_endtag(self, tag):
        if tag not in ['img', 'br', 'hr', 'input', 'meta', 'link']:
            if not self.tag_stack:
                self.errors.append(f"Closing tag </{tag}> without opening")
            elif self.tag_stack[-1] != tag:
                self.errors.append(f"Mismatched tag: expected </{self.tag_stack[-1]}>, got </{tag}>")
            else:
                self.tag_stack.pop()
    
    def validate(self):
        if self.tag_stack:
            self.errors.append(f"Unclosed tags: {', '.join(self.tag_stack)}")
        return len(self.errors) == 0

def validate_html(filepath):
    """Validate HTML file structure."""
    content = Path(filepath).read_text(encoding='utf-8')
    
    # CRITICAL: Check for emoji icons (FORBIDDEN)
    emoji_ranges = [
        (0x1F600, 0x1F64F),  # Emoticons
        (0x1F300, 0x1F5FF),  # Misc Symbols
        (0x1F680, 0x1F6FF),  # Transport
        (0x2600, 0x26FF),    # Misc symbols
        (0x2700, 0x27BF),    # Dingbats
        (0x2694, 0x2697),    # Swords, etc
    ]
    for char in content:
        code = ord(char)
        if any(start <= code <= end for start, end in emoji_ranges):
            print(f"FORBIDDEN EMOJI DETECTED: {char} (U+{code:04X})")
            return False
    
    # Basic checks
    if '<html' not in content:
        print(f"❌ Missing <html> tag")
        return False
    
    if '<head>' not in content or '</head>' not in content:
        print(f"❌ Missing or malformed <head> section")
        return False
    
    if '<body>' not in content or '</body>' not in content:
        print(f"❌ Missing or malformed <body> section")
        return False
    
    # Parse HTML
    parser = HTMLValidator()
    try:
        parser.feed(content)
    except Exception as e:
        print(f"❌ HTML parsing error: {e}")
        return False
    
    if not parser.validate():
        print(f"❌ HTML validation errors:")
        for error in parser.errors:
            print(f"  - {error}")
        return False
    
    # Check file size
    size_kb = len(content) / 1024
    if size_kb < 10:
        print(f"ERROR File suspiciously small: {size_kb:.1f}KB")
        return False
    
    print(f"OK HTML valid ({size_kb:.1f}KB)")
    print(f"OK All tags properly closed")
    return True

if __name__ == "__main__":
    filepath = sys.argv[1] if len(sys.argv) > 1 else "battle-plans-demo.html"
    
    if not Path(filepath).exists():
        print(f"ERROR File not found: {filepath}")
        sys.exit(1)
    
    if validate_html(filepath):
        print("OK Validation passed")
        sys.exit(0)
    else:
        print("ERROR Validation FAILED")
        sys.exit(1)
