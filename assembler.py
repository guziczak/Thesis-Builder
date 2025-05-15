#!/usr/bin/env python3
import os
import json
import glob
import logging
from pathlib import Path
import jsonschema
import re
import sys

# Configure logging
os.makedirs("build/logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("build/logs/assembler.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("thesis-assembler")

def validate_json(json_path, schema_path):
    """Validate a JSON file against a schema."""
    try:
        with open(schema_path, 'r') as schema_file:
            schema = json.load(schema_file)
        
        with open(json_path, 'r') as json_file:
            data = json.load(json_file)
        
        jsonschema.validate(instance=data, schema=schema)
        logger.info(f"JSON validation successful for {json_path}")
        return data
    except jsonschema.exceptions.ValidationError as e:
        logger.error(f"JSON validation failed for {json_path}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error reading or parsing JSON file {json_path}: {e}")
        return None

def create_latex_text(text):
    """Process text for LaTeX, preserving math expressions and references."""
    # Step 1: Identify and extract math and reference sections to protect them
    pattern_ref = r'\\ref\{[^}]+\}'
    pattern_math = r'\$[^$]+?\$'
    
    # Find all references and math expressions
    ref_matches = list(re.finditer(pattern_ref, text))
    math_matches = list(re.finditer(pattern_math, text))
    
    # Combine all matches and sort by position
    all_matches = []
    for match in ref_matches:
        all_matches.append(('ref', match.start(), match.end(), match.group()))
    for match in math_matches:
        all_matches.append(('math', match.start(), match.end(), match.group()))
    
    all_matches.sort(key=lambda x: x[1])  # Sort by start position
    
    # Step 2: Build segments of text to process separately
    segments = []
    last_end = 0
    
    for match_type, start, end, content in all_matches:
        # Add text before this match
        if start > last_end:
            segments.append(('text', text[last_end:start]))
        
        # Add the match itself (to be preserved)
        segments.append((match_type, content))
        last_end = end
    
    # Add remaining text after last match
    if last_end < len(text):
        segments.append(('text', text[last_end:]))
    
    # Step 3: Process each segment according to its type
    processed_segments = []
    
    for segment_type, content in segments:
        if segment_type == 'text':
            # Process regular text with LaTeX escaping
            processed = process_plain_text(content)
            processed_segments.append(processed)
        else:
            # Preserve math and reference segments exactly as they are
            processed_segments.append(content)
    
    # Step 4: Join all processed segments
    result = ''.join(processed_segments)
    
    # Step 5: Handle line breaks and other final formatting
    result = result.replace("\n\n", "\n\\par\n")
    
    return result

def process_plain_text(text):
    """Process plain text (non-math, non-reference) for LaTeX."""
    # Replace special LaTeX characters
    replacements = {
        '&': r'\&',
        '%': r'\%',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
        '\\': r'\textbackslash{}',
        '$': r'\$'  # Escape $ that aren't part of math expressions
    }
    
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    
    # Process Polish characters
    polish_chars = {
        'ą': r'\k{a}',
        'ć': r"\'c",
        'ę': r'\k{e}',
        'ł': r'\l{}',
        'ń': r"\'n",
        'ó': r"\'o",
        'ś': r"\'s",
        'ź': r"\'z",
        'ż': r'\.z',
        'Ą': r'\k{A}',
        'Ć': r"\'C",
        'Ę': r'\k{E}',
        'Ł': r'\L{}',
        'Ń': r"\'N",
        'Ó': r"\'O",
        'Ś': r"\'S",
        'Ź': r"\'Z",
        'Ż': r'\.Z'
    }
    
    for char, replacement in polish_chars.items():
        text = text.replace(char, replacement)
    
    # Process special scientific characters
    special_chars = {
        'μ': r'$\mu$',
        '±': r'$\pm$',
        '°': r'$^{\circ}$',
        '≈': r'$\approx$',
        '≥': r'$\geq$',
        '≤': r'$\leq$',
        '⁻': r'$^{-}$',
        '¹': r'$^{1}$',
        '²': r'$^{2}$',
        '³': r'$^{3}$',
        '⁴': r'$^{4}$',
        '⁵': r'$^{5}$',
        '⁶': r'$^{6}$',
        '⁷': r'$^{7}$',
        '⁸': r'$^{8}$',
        '⁹': r'$^{9}$',
        '⁰': r'$^{0}$',
        '₁': r'$_{1}$',
        '₂': r'$_{2}$',
        '₃': r'$_{3}$',
        '₄': r'$_{4}$'
    }
    
    for char, replacement in special_chars.items():
        text = text.replace(char, replacement)
    
    # Process citations
    text = re.sub(r'\[(\w+)\]', r'\\cite{\1}', text)
    
    # Process Markdown-like formatting
    text = re.sub(r'^# (.+)$', r'\\chapter{\1}', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'\\section{\1}', text, flags=re.MULTILINE)
    text = re.sub(r'^### (.+)$', r'\\subsection{\1}', text, flags=re.MULTILINE)
    text = re.sub(r'^#### (.+)$', r'\\subsubsection{\1}', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', text)
    text = re.sub(r'\*(.+?)\*', r'\\textit{\1}', text)
    
    # Handle special numeric patterns
    text = re.sub(r'(\d+)%', r'\1\\%', text)
    text = text.replace("~70%", "\\textasciitilde{}70\\%")
    text = re.sub(r'(\d+)\s*([µμ])[mM]', r'\1 $\\mu$m', text)
    text = re.sub(r'(\d+)\s*([µμ])[Aa]', r'\1 $\\mu$A', text)
    
    return text

def load_external_text(text_path, page_dir):
    """Load text from an external file."""
    # Convert relative path to absolute
    if not os.path.isabs(text_path):
        text_path = os.path.join(page_dir, text_path)
    
    try:
        with open(text_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # Próba z innym kodowaniem, jeśli UTF-8 zawiedzie
        try:
            with open(text_path, 'r', encoding='iso-8859-2') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error loading external text file {text_path} with ISO-8859-2 encoding: {e}")
            return ""
    except Exception as e:
        logger.error(f"Error loading external text file {text_path}: {e}")
        return ""

def process_image(content_block, page_dir):
    """Process an image block and return LaTeX code."""
    data = content_block['data']
    image_path = data.get('imagePath', '')
    
    # Convert relative path to absolute
    if not os.path.isabs(image_path):
        image_path = os.path.join(page_dir, image_path)
    
    # Make sure the path is relative to the build directory for LaTeX
    relative_path = os.path.relpath(image_path, 'build/tex')
    
    caption = data.get('caption', '')
    label = data.get('label', '')
    
    # Create image LaTeX code
    latex = "\\begin{figure}[htbp]\n\\centering\n"
    latex += f"\\includegraphics[width=0.8\\textwidth]{{{relative_path}}}\n"
    
    if caption:
        latex += f"\\caption{{{create_latex_text(caption)}}}\n"
    
    if label:
        latex += f"\\label{{{label}}}\n"
    
    latex += "\\end{figure}\n"
    
    return latex

def process_table(content_block):
    """Process a table block and return LaTeX code."""
    data = content_block['data']
    table_data = data.get('tableData', [])
    caption = data.get('caption', '')
    label = data.get('label', '')
    
    if not table_data:
        return ""
    
    # Determine the number of columns
    num_cols = len(table_data[0]) if table_data else 0
    
    # Create table LaTeX code
    latex = "\\begin{table}[htbp]\n\\centering\n"
    latex += f"\\begin{{tabular}}{{{'|'.join(['c'] * num_cols)}}}\n\\hline\n"
    
    # Add table rows
    for i, row in enumerate(table_data):
        latex += " & ".join([create_latex_text(cell) for cell in row]) + " \\\\ \\hline\n"
    
    latex += "\\end{tabular}\n"
    
    if caption:
        latex += f"\\caption{{{create_latex_text(caption)}}}\n"
    
    if label:
        latex += f"\\label{{{label}}}\n"
    
    latex += "\\end{table}\n"
    
    return latex

def process_code(content_block):
    """Process a code block and return LaTeX code."""
    data = content_block['data']
    code = data.get('code', '')
    language = data.get('language', 'text')
    caption = data.get('caption', '')
    label = data.get('label', '')
    
    # Create code listing LaTeX code
    latex = f"\\begin{{listing}}[H]\n"
    latex += f"\\begin{{minted}}[breaklines, linenos]{{{language}}}\n"
    latex += code + "\n"
    latex += "\\end{minted}\n"
    
    if caption:
        latex += f"\\caption{{{create_latex_text(caption)}}}\n"
    
    if label:
        latex += f"\\label{{{label}}}\n"
    
    latex += "\\end{listing}\n"
    
    return latex

def process_equation(content_block):
    """Process an equation block and return LaTeX code."""
    data = content_block['data']
    equation = data.get('equation', '')
    label = data.get('label', '')
    
    # Create equation LaTeX code
    latex = "\\begin{equation}\n"
    
    if label:
        latex += f"\\label{{{label}}}\n"
    
    latex += equation + "\n"
    latex += "\\end{equation}\n"
    
    return latex

def process_content_block(content_block, page_dir):
    """Process a content block and return LaTeX code."""
    block_type = content_block['type']
    
    if block_type == 'text':
        # Check if text is provided directly or via a file path
        if 'text' in content_block['data']:
            text = content_block['data'].get('text', '')
            # Usuń nagłówki Markdown, które są przetwarzane jako LaTeX verbatim
            if text.startswith('#'):
                # Znajdź poziom nagłówka i treść
                heading_level = 0
                for char in text:
                    if char == '#':
                        heading_level += 1
                    else:
                        break
                
                text_content = text[heading_level:].strip()  # Treść nagłówka bez znaków #
                
                # Utwórz odpowiednią komendę LaTeX
                if heading_level == 1:
                    return f"\\chapter{{{create_latex_text(text_content)}}}\n\n"
                elif heading_level == 2:
                    return f"\\section{{{create_latex_text(text_content)}}}\n\n"
                elif heading_level == 3:
                    return f"\\subsection{{{create_latex_text(text_content)}}}\n\n"
                elif heading_level == 4:
                    return f"\\subsubsection{{{create_latex_text(text_content)}}}\n\n"
                else:
                    return f"\\paragraph{{{create_latex_text(text_content)}}}\n\n"
            else:
                return create_latex_text(text) + "\n\n"
        elif 'textPath' in content_block['data']:
            text_path = content_block['data'].get('textPath', '')
            external_text = load_external_text(text_path, page_dir)
            
            # Przetwarzamy tekst, zachowując markdown nagłówki dla konwersji do LaTeX
            lines = external_text.split('\n')
            processed_lines = []
            
            for line in lines:
                # Sprawdzamy, czy linia jest nagłówkiem Markdown
                if line.strip().startswith('#'):
                    # Liczymy poziom nagłówka
                    heading_level = 0
                    for char in line.strip():
                        if char == '#':
                            heading_level += 1
                        else:
                            break
                    
                    text_content = line.strip()[heading_level:].strip()  # Treść nagłówka bez znaków #
                    
                    # Przetwarzamy treść nagłówka (bez znaków #)
                    safe_text_content = create_latex_text(text_content)
                    
                    # Tworzymy odpowiednią komendę LaTeX
                    if heading_level == 1:
                        processed_lines.append(f"\\chapter{{{safe_text_content}}}")
                    elif heading_level == 2:
                        processed_lines.append(f"\\section{{{safe_text_content}}}")
                    elif heading_level == 3:
                        processed_lines.append(f"\\subsection{{{safe_text_content}}}")
                    elif heading_level == 4:
                        processed_lines.append(f"\\subsubsection{{{safe_text_content}}}")
                    else:
                        processed_lines.append(f"\\paragraph{{{safe_text_content}}}")
                else:
                    processed_lines.append(line)
            
            # Łączymy linie po przetworzeniu nagłówków
            processed_text = '\n'.join(processed_lines)
            
            # Przetwarzamy cały tekst z zachowaniem równań
            result = create_latex_text(processed_text)
            
            # Przetwarzamy listy (wszystkie elementy zaczynające się od "-")
            lines = result.split('\n')
            final_result = []
            i = 0
            
            while i < len(lines):
                current_line = lines[i]
                
                # Jeśli znaleźliśmy element listy
                if current_line.strip().startswith('- '):
                    # Dodajemy otwarcie środowiska itemize
                    final_result.append("\\begin{itemize}")
                    
                    # Przetwarzamy wszystkie kolejne elementy listy
                    while i < len(lines) and lines[i].strip().startswith('- '):
                        item_content = lines[i].strip()[2:]  # Usuwamy "- " z początku linii
                        final_result.append(f"\\item {item_content}")
                        i += 1
                    
                    # Zamykamy środowisko itemize
                    final_result.append("\\end{itemize}")
                else:
                    # To nie jest element listy, dodajemy normalnie
                    final_result.append(current_line)
                    i += 1
            
            # Łączymy wszystkie linie wynikowe
            return '\n'.join(final_result)
        else:
            logger.warning("Text block is missing both 'text' and 'textPath'")
            return ""
    elif block_type == 'image':
        return process_image(content_block, page_dir) + "\n"
    elif block_type == 'table':
        return process_table(content_block) + "\n"
    elif block_type == 'code':
        return process_code(content_block) + "\n"
    elif block_type == 'equation':
        return process_equation(content_block) + "\n"
    elif block_type == 'listing':
        return process_code(content_block) + "\n"  # Use same processor for listings
    else:
        logger.warning(f"Unknown content block type: {block_type}")
        return ""

def process_page(page_number):
    """Process a page directory and generate a LaTeX fragment."""
    logger.info(f"Processing page {page_number}")
    
    page_dir = f"pages/{page_number}"
    
    # Find content JSON files in the page directory
    json_files = glob.glob(f"{page_dir}/*.json")
    
    if not json_files:
        logger.warning(f"No JSON files found in {page_dir}")
        return False
    
    # Process each JSON file in the page
    for json_file in json_files:
        logger.info(f"Processing JSON file: {json_file}")
        
        # Validate JSON against schema
        page_data = validate_json(json_file, "schema/page_schema.json")
        
        if page_data is None:
            logger.error(f"Failed to validate {json_file}")
            return False
        
        # Create output directories if they don't exist
        os.makedirs("build/tex", exist_ok=True)
        os.makedirs("build/pdf", exist_ok=True)
        
        # Create LaTeX fragment for this page
        output_file = f"build/tex/page_{page_number}.tex"
        # Używamy kodowania ASCII z backslashreplace dla poprawnej obsługi przez LaTeX
        with open(output_file, 'w', encoding='ascii', errors='backslashreplace') as f:
            # Write section header
            section_level = page_data.get('sectionLevel', 1)
            title = page_data.get('title', f"Page {page_number}")
            
            # Zapis z poprawnym kodowaniem - używamy create_latex_text dla tytułu
            title_safe = create_latex_text(title)
            
            if section_level == 1:
                f.write(f"\\chapter{{{title_safe}}}\n\n")
            elif section_level == 2:
                f.write(f"\\section{{{title_safe}}}\n\n")
            elif section_level == 3:
                f.write(f"\\subsection{{{title_safe}}}\n\n")
            elif section_level == 4:
                f.write(f"\\subsubsection{{{title_safe}}}\n\n")
            else:
                f.write(f"\\paragraph{{{title_safe}}}\n\n")
            
            # Process content blocks
            for content_block in page_data.get('content', []):
                try:
                    latex_content = process_content_block(content_block, page_dir)
                    
                    # Bezpośrednio zapisujemy zawartość LaTeX-a, która już jest odpowiednio przetworzona
                    # przez funkcję create_latex_text
                    f.write(latex_content)
                except Exception as e:
                    logger.error(f"Error processing content block: {e}")
                    return False
            
            # Process references if any
            references = page_data.get('references', [])
            if references:
                f.write("% References used in this page:\n")
                f.write("% These will be collected into the main bibliography file\n")
                for ref in references:
                    f.write(f"% {ref['id']}: {ref['citation']}\n")
        
        logger.info(f"Successfully generated LaTeX fragment: {output_file}")
        return True

def collect_bibliography():
    """Collect all bibliography entries from all pages and create a .bib file."""
    logger.info("Collecting bibliography entries from all pages")
    
    all_references = {}
    
    # Get all page directories
    page_dirs = sorted([d for d in os.listdir("pages") if os.path.isdir(os.path.join("pages", d)) and d.isdigit()],
                      key=lambda x: int(x))
    
    for page_dir in page_dirs:
        page_number = int(page_dir)
        page_json_files = glob.glob(f"pages/{page_number}/*.json")
        
        for json_file in page_json_files:
            try:
                with open(json_file, 'r') as f:
                    page_data = json.load(f)
                
                # Extract references
                references = page_data.get('references', [])
                
                for ref in references:
                    ref_id = ref.get('id')
                    citation = ref.get('citation')
                    
                    if ref_id and citation:
                        all_references[ref_id] = citation
            except Exception as e:
                logger.error(f"Error collecting references from {json_file}: {e}")
    
    # Create bibliography file
    if all_references:
        os.makedirs("build/tex", exist_ok=True)
        bib_file_path = "build/tex/references.bib"
        
        with open(bib_file_path, 'w', encoding='utf-8') as bib_file:
            for ref_id, citation in all_references.items():
                # Remove any leading @article or similar to ensure proper formatting
                if citation.startswith('@'):
                    bib_file.write(f"{citation}\n\n")
                else:
                    bib_file.write(f"@misc{{{ref_id},\n  title={{{ref_id}}},\n  author={{Unknown}}\n}}\n\n")
        
        logger.info(f"Successfully created bibliography file with {len(all_references)} entries: {bib_file_path}")
        return True
    else:
        logger.warning("No bibliography entries found across all pages")
        return False

def assemble_all_pages():
    """Process all pages in the pages directory."""
    success_count = 0
    failure_count = 0
    
    # Get all page directories
    page_dirs = sorted([d for d in os.listdir("pages") if os.path.isdir(os.path.join("pages", d)) and d.isdigit()],
                      key=lambda x: int(x))
    
    for page_dir in page_dirs:
        page_number = int(page_dir)
        if process_page(page_number):
            success_count += 1
        else:
            failure_count += 1
    
    # Collect bibliography after processing all pages
    collect_bibliography()
    
    logger.info(f"Assembly complete. Success: {success_count}, Failures: {failure_count}")
    return success_count, failure_count

if __name__ == "__main__":
    logger.info("Starting thesis content assembly")
    
    if len(sys.argv) > 1:
        # If a page number is provided, process just that page
        try:
            page_number = int(sys.argv[1])
            success = process_page(page_number)
            sys.exit(0 if success else 1)
        except ValueError:
            logger.error(f"Invalid page number: {sys.argv[1]}")
            sys.exit(1)
    else:
        # Process all pages
        success, failures = assemble_all_pages()
        
        if failures == 0:
            logger.info("All pages assembled successfully")
            sys.exit(0)
        else:
            logger.warning(f"{failures} pages failed to assemble")
            sys.exit(1)