import re
import num2words
from pathlib import Path
from typing import Optional, Union

def convert_numerals_to_words(markdown_file_path: Union[str, Path], output_file_path: Optional[Union[str, Path]] = None) -> str:
    """
    Read a markdown file, convert all numerals to their word representation,
    and save the result to a new file or overwrite the original.
    
    Args:
        markdown_file_path (str): Path to the markdown file to process
        output_file_path (str, optional): Path where to save the processed markdown.
            If None, the original file will be overwritten. Defaults to None.
    
    Returns:
        str: The processed markdown content
    """
    # Read the markdown file
    md_path = Path(markdown_file_path)
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Function to convert found numerals to words
    def replace_numeral(match: re.Match) -> str:
        numeral_str = match.group(1) # The digits
        original_match = match.group(0) # The full match (could include boundaries)
        start_index = match.start(1)
        end_index = match.end(1)
        full_string = match.string

        # --- Context Checks --- 

        # Check character BEFORE the number
        if start_index > 0:
            char_before = full_string[start_index - 1]
            # If preceded by '.' or '-', likely part of version/date/negative number
            if char_before == '.' or char_before == '-': 
                return original_match

        # Check character AFTER the number
        if end_index < len(full_string):
            char_after = full_string[end_index]
            if char_after == '.':
                # Check if it's a version (3.2) or list marker (1. )
                if end_index + 1 < len(full_string):
                    char_after_dot = full_string[end_index + 1]
                    if char_after_dot.isdigit(): # Version: 3.2
                        return original_match
                    # Prevent conversion for space after dot (list), BUT ALLOW newline
                    if char_after_dot.isspace() and char_after_dot != '\n': # List marker: 1. 
                        return original_match
                # Otherwise, allow conversion attempt (covers 42. at sentence end, or 42.\n)
            elif char_after == '-':
                # Check if it's a date (e.g., 2023-11)
                if end_index + 1 < len(full_string):
                    char_after_hyphen = full_string[end_index + 1]
                    if char_after_hyphen.isdigit(): # Date: 2023-11
                        return original_match
            # Add other context checks if needed (e.g., currency $42)
            # Currently, $42 gets converted, which might be desired.
            
        # --- Conversion Attempt --- 
        try:
            num_int = int(numeral_str)
            # Skip conversion for very large numbers
            if num_int > 9999:
                return original_match
            
            # Perform the conversion
            return num2words.num2words(num_int)
        except ValueError:
            # If conversion fails, return the original
            return original_match
    
    # First, let's identify code blocks to protect them
    code_blocks = []
    code_pattern = re.compile(r'```.*?```', re.DOTALL)
    
    def save_code_block(match: re.Match) -> str:
        block = match.group(0)
        code_blocks.append(block)
        return f"CODE_BLOCK_{len(code_blocks)-1}"
    
    # Replace code blocks with placeholders
    protected_content = re.sub(code_pattern, save_code_block, content)
    
    # Convert numbers to words in the protected content
    # Use simple pattern, context checks are now in replace_numeral
    number_pattern = re.compile(r'\b(\d+)\b')
    processed_content = re.sub(number_pattern, replace_numeral, protected_content)
    
    # Restore code blocks
    for i, block in enumerate(code_blocks):
        processed_content = processed_content.replace(f"CODE_BLOCK_{i}", block)
    
    # Write the processed content to the output file
    if output_file_path:
        output_path = Path(output_file_path)
    else:
        output_path = md_path
        
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(processed_content)
    
    return processed_content

# Example usage
if __name__ == "__main__":
    # Example with a markdown file
    input_file = "example.md"
    output_file = "example_processed.md"
    
    # Create example file if it doesn't exist
    if not Path(input_file).exists():
        with open(input_file, 'w', encoding='utf-8') as f:
            f.write("""# Sample Markdown with Numbers

- There are 5 apples in the basket
- Room temperature is 21 degrees
- Cost: $42 per item
- Version 3.2.1 should not change
- Date 2023-11-15 should not change
- A list:
  1. First item
  2. Second item
  3. Third item

```python
# This code should not change
x = 123
for i in range(10):
    print(i)
```

The year is 2024 and the answer is 42.
""")
    
    # Process the file
    convert_numerals_to_words(input_file, output_file)
    
    print(f"Processed file saved to {output_file}")
    
    # Show the result
    with open(output_file, 'r', encoding='utf-8') as f:
        print("\nProcessed content:")
        print(f.read())