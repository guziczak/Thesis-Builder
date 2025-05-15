#!/usr/bin/env python3
import os
import subprocess
import logging
import sys
import re
import shutil
from pathlib import Path
import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("build/logs/compiler.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("thesis-compiler")

def fix_fragment_encoding(fragment_path):
    """
    Fix encoding issues in a LaTeX file.
    Read the file as binary and write a new ASCII version with proper LaTeX commands.
    """
    logger.info(f"Fixing encoding in {fragment_path}")
    
    output_path = fragment_path.replace('.tex', '_fixed.tex')
    
    try:
        # Read the file as binary to avoid encoding errors
        with open(fragment_path, 'rb') as f:
            content = f.read()
        
        # Directly prepare content to include in main document
        content_ascii = ""
        i = 0
        while i < len(content):
            if content[i] < 128:  # ASCII character
                content_ascii += chr(content[i])
            else:
                # Multi-byte sequence handling
                if i + 1 < len(content):
                    # Handling Polish characters in UTF-8
                    if content[i] == 0xc4:  # First byte of some Polish chars
                        second_byte = content[i+1]
                        if second_byte == 0x85:  # ą
                            content_ascii += "\\k{a}"
                        elif second_byte == 0x84:  # Ą
                            content_ascii += "\\k{A}"
                        elif second_byte == 0x87:  # ć
                            content_ascii += "\\'c"
                        elif second_byte == 0x86:  # Ć
                            content_ascii += "\\'C"
                        elif second_byte == 0x99:  # ę
                            content_ascii += "\\k{e}"
                        elif second_byte == 0x98:  # Ę
                            content_ascii += "\\k{E}"
                        else:
                            content_ascii += "?"
                        i += 1  # Skip next byte
                    elif content[i] == 0xc5:  # First byte of other Polish chars
                        second_byte = content[i+1]
                        if second_byte == 0x82:  # ł
                            content_ascii += "\\l{}"
                        elif second_byte == 0x81:  # Ł
                            content_ascii += "\\L{}"
                        elif second_byte == 0x84:  # ń
                            content_ascii += "\\'n"
                        elif second_byte == 0x83:  # Ń
                            content_ascii += "\\'N"
                        elif second_byte == 0xb3:  # ó
                            content_ascii += "\\'o"
                        elif second_byte == 0x93:  # Ó
                            content_ascii += "\\'O"
                        elif second_byte == 0x9b:  # ś
                            content_ascii += "\\'s"
                        elif second_byte == 0x9a:  # Ś
                            content_ascii += "\\'S"
                        elif second_byte == 0xba:  # ź
                            content_ascii += "\\'z"
                        elif second_byte == 0xb9:  # Ź
                            content_ascii += "\\'Z"
                        elif second_byte == 0xbc:  # ż
                            content_ascii += "\\.z"
                        elif second_byte == 0xbb:  # Ż
                            content_ascii += "\\.Z"
                        else:
                            content_ascii += "?"
                        i += 1  # Skip next byte
                    else:
                        # Other UTF-8 sequences
                        content_ascii += "?"
                else:
                    # Incomplete UTF-8 sequence
                    content_ascii += "?"
            i += 1
        
        # Write fixed content to new file
        with open(output_path, 'w', encoding='ascii', errors='replace') as f:
            f.write(content_ascii)
        
        logger.info(f"Successfully created fixed encoding file: {output_path}")
        return output_path
    
    except Exception as e:
        logger.error(f"Error fixing encoding: {e}")
        return None

def create_main_tex():
    """Create the main LaTeX document that imports all page fragments."""
    logger.info("Creating main LaTeX document")
    
    # Get all LaTeX fragments - tylko oryginalne pliki (bez _fixed i _ascii)
    fragments = sorted([f for f in os.listdir("build/tex") if f.startswith("page_") and f.endswith(".tex") 
                    and not (f.endswith("_fixed.tex") or f.endswith("_ascii.tex"))],
                    key=lambda x: int(re.findall(r'page_(\d+)', x)[0]))
    
    if not fragments:
        logger.error("No page fragments found")
        return False
    
    # Napraw kodowanie we wszystkich fragmentach
    fixed_fragments = []
    for fragment in fragments:
        fragment_path = os.path.join("build/tex", fragment)
        fixed_path = fix_fragment_encoding(fragment_path)
        if fixed_path:
            fixed_fragments.append(os.path.basename(fixed_path))
    
    # Create main.tex file
    with open("build/tex/main.tex", 'w', encoding='ascii', errors='replace') as f:
        # Write LaTeX preamble
        f.write("\\documentclass[a4paper, 12pt]{report}\n\n")
        
        # Required packages
        f.write("\\usepackage[utf8]{inputenc}\n")
        f.write("\\usepackage[T1]{fontenc}\n")
        f.write("\\usepackage{graphicx}\n")
        f.write("\\usepackage{hyperref}\n")
        f.write("\\usepackage{float}\n")
        f.write("\\usepackage{amsmath}\n")
        f.write("\\usepackage{amssymb}\n")
        f.write("\\usepackage{minted}\n")
        f.write("\\usepackage{textcomp}\n")  # Dodatkowy pakiet dla znaków specjalnych
        f.write("\\usepackage{csquotes}\n")  # Package for handling quotes and special chars
        f.write("\\usepackage[backend=biber, sorting=none, style=numeric]{biblatex}\n")
        f.write("\\usepackage{polski}\n")
        f.write("\\usepackage[polish]{babel}\n")
        f.write("\\usepackage{lipsum}  % For sample text\n")
        
        # Set graphics path
        f.write("\\graphicspath{{../}}\n\n")
        
        # Check if bibliography file exists
        if os.path.exists("build/tex/references.bib"):
            f.write("\\addbibresource{references.bib}\n\n")
        
        # Document metadata - tutaj już używamy ASCII, więc nie ma potrzeby konwersji
        f.write("\\title{Rewolucja w medycynie: Inteligentne sterowanie polami Tesli do uk\\l{}adania nanorurek in vivo}\n")
        f.write("\\author{Magister Thesis}\n")
        f.write("\\date{\\today}\n\n")
        
        # Begin document
        f.write("\\begin{document}\n\n")
        
        # Title page
        f.write("\\maketitle\n")
        f.write("\\tableofcontents\n")
        f.write("\\newpage\n\n")
        
        # Dołączamy poprawione pliki
        for fragment in fixed_fragments:
            fragment_name = fragment.replace('.tex', '')
            f.write(f"\\include{{{fragment_name}}}\n")
        
        # Add bibliography section
        f.write("\n% Print the bibliography\n")
        f.write("\\printbibliography[heading=bibintoc, title=Bibliografia]\n\n")
        
        # End document
        f.write("\\end{document}\n")
    
    logger.info("Successfully created main LaTeX document")
    return True

def compile_document():
    """Compile the LaTeX document using pdflatex with detailed error logging."""
    logger.info("Starting LaTeX compilation")
    
    # Change to the build/tex directory
    os.chdir("build/tex")
    
    # Run pdflatex to compile the document
    compile_command = ["pdflatex", "-shell-escape", "-interaction=nonstopmode", "main.tex"]
    
    # Track compilation status
    compilation_success = True
    error_log = []
    
    # Run pdflatex and capture output
    try:
        logger.info(f"Running command: {' '.join(compile_command)}")
        result = subprocess.run(compile_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Parse output for errors and warnings
        for line in result.stdout.split('\n'):
            if "Error:" in line or "Fatal error" in line:
                compilation_success = False
                error_log.append(line)
                logger.error(f"LaTeX error: {line}")
            elif "Warning:" in line:
                error_log.append(line)
                logger.warning(f"LaTeX warning: {line}")
            elif "Output written on" in line:
                logger.info(line)
        
        # Run biber for bibliography
        logger.info("Running biber for bibliography")
        biber_result = subprocess.run(["biber", "main"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Run pdflatex again (twice) to resolve references
        logger.info("Running pdflatex second time")
        subprocess.run(compile_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        logger.info("Running pdflatex third time")
        final_result = subprocess.run(compile_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Copy PDF to the pdf directory
        if os.path.exists("main.pdf"):
            # Return to original directory
            os.chdir("../..")
            
            # Create timestamp string
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Copy PDF to output directory with timestamp
            pdf_path = f"build/pdf/thesis_{timestamp}.pdf"
            shutil.copy("build/tex/main.pdf", pdf_path)
            
            logger.info(f"PDF generated successfully: {pdf_path}")
            
            # Also keep a latest.pdf copy
            shutil.copy("build/tex/main.pdf", "build/pdf/latest.pdf")
        else:
            os.chdir("../..")
            compilation_success = False
            logger.error("PDF file not generated")
    
    except Exception as e:
        compilation_success = False
        logger.error(f"Compilation failed with error: {e}")
    
    # Write detailed error log
    if error_log:
        with open("build/logs/latex_errors.log", 'w') as f:
            f.write("\n".join(error_log))
    
    return compilation_success

def compile_single_page(page_number):
    """Compile a single LaTeX page fragment for testing."""
    logger.info(f"Compiling single page {page_number}")
    
    # Check if the fragment exists
    fragment_path = f"build/tex/page_{page_number}.tex"
    if not os.path.exists(fragment_path):
        logger.error(f"Page fragment not found: {fragment_path}")
        return False
    
    # Nie próbujemy już naprawiać kodowania, ponieważ poprawiliśmy mechanizm generowania plików LaTeX
    # Tutaj możemy dodać inne operacje przygotowawcze w przyszłości, jeśli będzie to potrzebne
    logger.info(f"Using file {fragment_path} directly")
    
    # Create a temporary main document that includes just this page
    temp_main = f"build/tex/temp_page_{page_number}.tex"
    with open(temp_main, 'w', encoding='ascii', errors='backslashreplace') as f:
        # Write LaTeX preamble
        f.write("\\documentclass[a4paper, 12pt]{report}\n\n")
        
        # Required packages
        f.write("\\usepackage[utf8]{inputenc}\n")
        f.write("\\usepackage[T1]{fontenc}\n")
        f.write("\\usepackage{graphicx}\n")
        f.write("\\usepackage{hyperref}\n")
        f.write("\\usepackage{float}\n")
        f.write("\\usepackage{amsmath}\n")
        f.write("\\usepackage{amssymb}\n")
        f.write("\\usepackage{minted}\n")
        f.write("\\usepackage{textcomp}\n")  # Dodatkowy pakiet dla znaków specjalnych
        f.write("\\usepackage{polski}\n")
        f.write("\\usepackage[polish]{babel}\n")
        
        # Set graphics path
        f.write("\\graphicspath{{../}}\n\n")
        
        # Begin document
        f.write("\\begin{document}\n\n")
        
        # Include the specific page content from the fixed file
        try:
            # Czytamy plik w ASCII, ponieważ został zapisany w ASCII z backslashreplace
            with open(fragment_path, 'r', encoding='ascii') as page_file:
                page_content = page_file.read()
                f.write(page_content)
        except Exception as e:
            logger.error(f"Failed to read page content: {e}")
            return False
        
        # End document
        f.write("\\end{document}\n")
    
    # Compile the temporary document
    os.chdir("build/tex")
    compile_command = ["pdflatex", "-shell-escape", "-interaction=nonstopmode", f"temp_page_{page_number}.tex"]
    
    try:
        logger.info(f"Running command: {' '.join(compile_command)}")
        result = subprocess.run(compile_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Sprawdź, czy PDF został wygenerowany - to jest najważniejszy wskaźnik sukcesu
        success = os.path.exists(f"temp_page_{page_number}.pdf")
        
        # Zapisz log kompilacji, niezależnie od wyniku
        os.makedirs("../../build/logs", exist_ok=True)  # Upewnij się, że katalog istnieje
        log_path = f"../../build/logs/page_{page_number}_compile.log"
        with open(log_path, 'w') as f:
            f.write(result.stdout)
        
        # Return to original directory
        os.chdir("../..")
        
        if success:
            # Sprawdź rozmiar pliku PDF, aby upewnić się, że nie jest pusty
            pdf_size = os.path.getsize(f"build/tex/temp_page_{page_number}.pdf")
            
            # Jeśli PDF istnieje, uważamy kompilację za udaną, nawet jeśli były ostrzeżenia
            pdf_path = f"build/pdf/page_{page_number}.pdf"
            shutil.copy(f"build/tex/temp_page_{page_number}.pdf", pdf_path)
            
            # Sprawdź, czy były jakieś ostrzeżenia lub nieblokujące błędy
            warnings_found = False
            with open(log_path, 'r', errors='replace') as log_file:
                log_content = log_file.read()
                if "Warning:" in log_content or "Overfull" in log_content or "Underfull" in log_content:
                    warnings_found = True
            
            if warnings_found:
                logger.info(f"Page {page_number} compiled with warnings, PDF generated: {pdf_path}")
                logger.info(f"See {log_path} for details")
            else:
                logger.info(f"Page {page_number} compiled successfully: {pdf_path}")
                
            return True
        else:
            # Jeśli PDF nie został wygenerowany, to faktycznie mamy błąd
            logger.error(f"Failed to compile page {page_number} - PDF was not generated")
            logger.error(f"See {log_path} for details")
            return False
        
    except Exception as e:
        os.chdir("../..")
        
        # Sprawdź, czy mimo zgłoszonego wyjątku PDF został wygenerowany
        if os.path.exists(f"build/tex/temp_page_{page_number}.pdf"):
            # Jeśli PDF istnieje mimo błędu, to traktujemy to jako ostrzeżenie
            pdf_size = os.path.getsize(f"build/tex/temp_page_{page_number}.pdf")
            if pdf_size > 1000:  # Plik większy niż 1KB jest prawidłowym PDF
                logger.info(f"Despite error '{str(e)}', PDF was successfully generated")
                
                # Kopiujemy PDF do katalogu docelowego
                pdf_path = f"build/pdf/page_{page_number}.pdf"
                shutil.copy(f"build/tex/temp_page_{page_number}.pdf", pdf_path)
                logger.info(f"Page {page_number} compiled with warnings: {pdf_path}")
                return True
        
        # Jeśli PDF nie istnieje lub jest zbyt mały, to faktycznie mamy błąd
        logger.error(f"Compilation process failed with exception: {e}")
        return False

def compile_all():
    """Create main document and compile it."""
    logger.info("Starting full thesis compilation")
    
    # Create main LaTeX document
    if not create_main_tex():
        logger.error("Failed to create main LaTeX document")
        return False
    
    # Compile document
    if compile_document():
        logger.info("Thesis compiled successfully")
        return True
    else:
        logger.error("Thesis compilation failed")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # If a page number is provided, compile just that page
        try:
            page_number = int(sys.argv[1])
            result = compile_single_page(page_number)
            sys.exit(0 if result else 1)
        except ValueError:
            logger.error(f"Invalid page number: {sys.argv[1]}")
            sys.exit(1)
    else:
        # Compile the entire thesis
        result = compile_all()
        sys.exit(0 if result else 1)