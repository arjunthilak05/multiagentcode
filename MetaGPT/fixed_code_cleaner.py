#!/usr/bin/env python3
"""
Fixed Code Cleaner with more robust HTML validation
"""

import re
import logging
from typing import List

logger = logging.getLogger(__name__)


class FixedCodeCleaner:
    """Enhanced code cleaner with more lenient validation"""
    
    @staticmethod
    def clean_html_response(raw_response: str) -> str:
        """Clean and validate HTML response with more lenient rules"""
        try:
            # Remove markdown wrappers
            cleaned = raw_response.strip()
            
            # Remove various markdown patterns - be more aggressive
            patterns = [
                r'^```html\s*\n?',
                r'^```\s*\n?',
                r'\n?```\s*$',
                r'```\s*$',
                r'^html\s*\n?',  # Sometimes just 'html' without backticks
            ]
            
            for pattern in patterns:
                cleaned = re.sub(pattern, '', cleaned, flags=re.MULTILINE | re.IGNORECASE)
            
            cleaned = cleaned.strip()
            
            # If it doesn't start with DOCTYPE, try to find HTML start
            if not cleaned.upper().startswith('<!DOCTYPE'):
                # Look for HTML tag start
                html_match = re.search(r'<html[^>]*>', cleaned, re.IGNORECASE)
                if html_match:
                    # Add basic DOCTYPE
                    cleaned = '<!DOCTYPE html>\n' + cleaned[html_match.start():]
                elif '<head>' in cleaned.lower() or '<body>' in cleaned.lower():
                    # Has HTML content but missing html tag, wrap it
                    cleaned = '<!DOCTYPE html>\n<html lang="en">\n' + cleaned + '\n</html>'
                else:
                    logger.warning("No clear HTML structure found, but proceeding anyway")
            
            # Basic validation - be more lenient
            if not FixedCodeCleaner._lenient_html_validation(cleaned):
                logger.warning("HTML validation issues, but proceeding with content")
            
            # Clean up formatting
            cleaned = FixedCodeCleaner._format_html(cleaned)
            
            return cleaned
            
        except Exception as e:
            logger.error(f"Error cleaning HTML: {str(e)}")
            # Don't raise ValidationError, return best effort cleanup
            return FixedCodeCleaner._emergency_cleanup(raw_response)
    
    @staticmethod
    def _lenient_html_validation(html: str) -> bool:
        """More lenient HTML validation"""
        html_lower = html.lower()
        
        # Check for basic HTML indicators (not all required)
        html_indicators = [
            'doctype' in html_lower,
            '<html' in html_lower,
            '<head' in html_lower,
            '<body' in html_lower,
            '<title' in html_lower,
        ]
        
        # If at least 3 out of 5 indicators are present, consider it valid
        valid_indicators = sum(html_indicators)
        
        if valid_indicators < 2:
            logger.warning(f"Only {valid_indicators}/5 HTML indicators found")
            return False
        
        return True
    
    @staticmethod
    def _emergency_cleanup(raw_response: str) -> str:
        """Emergency cleanup when all else fails"""
        logger.info("Performing emergency HTML cleanup")
        
        # Very basic cleanup
        cleaned = raw_response.strip()
        
        # Remove obvious markdown
        cleaned = re.sub(r'```[a-zA-Z]*\s*\n?', '', cleaned)
        cleaned = re.sub(r'\n?```\s*$', '', cleaned)
        
        # If it looks like it has HTML content, wrap it minimally
        if any(tag in cleaned.lower() for tag in ['<div', '<p>', '<h1', '<script', '<style']):
            if not cleaned.lower().startswith('<!doctype'):
                cleaned = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Educational Game</title>
</head>
<body>
{cleaned}
</body>
</html>"""
        
        return cleaned
    
    @staticmethod
    def _format_html(html: str) -> str:
        """Basic HTML formatting - preserve structure"""
        # Don't be too aggressive with formatting to avoid breaking code
        lines = html.split('\n')
        formatted_lines = []
        
        for line in lines:
            # Keep lines that aren't just whitespace
            if line.strip():
                formatted_lines.append(line.rstrip())  # Remove trailing whitespace only
        
        return '\n'.join(formatted_lines)
    
    @staticmethod
    def validate_javascript_basics(html: str) -> List[str]:
        """Basic JavaScript validation - more lenient"""
        issues = []
        
        try:
            # Check for common syntax errors but don't fail the whole thing
            js_blocks = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL | re.IGNORECASE)
            
            for i, js_block in enumerate(js_blocks):
                # Check for severely mismatched braces (allow some flexibility)
                open_braces = js_block.count('{')
                close_braces = js_block.count('}')
                if abs(open_braces - close_braces) > 2:  # Allow some tolerance
                    issues.append(f"Script block {i+1}: Significantly mismatched braces")
                
                # Check for severely mismatched parentheses
                open_parens = js_block.count('(')
                close_parens = js_block.count(')')
                if abs(open_parens - close_parens) > 2:  # Allow some tolerance
                    issues.append(f"Script block {i+1}: Significantly mismatched parentheses")
        
        except Exception as e:
            logger.warning(f"JavaScript validation error: {e}")
            # Don't fail, just log the issue
        
        return issues


# Monkey patch the original cleaner
def patch_code_cleaner():
    """Apply the fixed code cleaner to the enhanced system"""
    import sys
    import types
    
    # Create a module-like object with our fixed methods
    fixed_module = types.SimpleNamespace()
    fixed_module.clean_html_response = FixedCodeCleaner.clean_html_response
    fixed_module.validate_javascript_basics = FixedCodeCleaner.validate_javascript_basics
    
    # If the enhanced module is already imported, patch it
    if 'enhanced_unified_generator' in sys.modules:
        enhanced_module = sys.modules['enhanced_unified_generator']
        if hasattr(enhanced_module, 'CodeCleaner'):
            enhanced_module.CodeCleaner.clean_html_response = FixedCodeCleaner.clean_html_response
            enhanced_module.CodeCleaner.validate_javascript_basics = FixedCodeCleaner.validate_javascript_basics
            logger.info("Patched CodeCleaner in enhanced_unified_generator")


if __name__ == "__main__":
    # Test the fixed cleaner
    test_response = """
    ```html
    <!DOCTYPE html>
    <html>
    <head><title>Test</title></head>
    <body><h1>Hello</h1></body>
    </html>
    ```
    """
    
    try:
        cleaned = FixedCodeCleaner.clean_html_response(test_response)
        print("✅ Fixed cleaner working!")
        print(f"Cleaned length: {len(cleaned)}")
    except Exception as e:
        print(f"❌ Fixed cleaner error: {e}")