#!/usr/bin/env python3
import os
import glob
import logging
import sys
import re
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("ascii-thesis-creator")

def fix_page_file(page_number):
    """Fix encoding in a single page file."""
    source_file = f"build/tex/page_{page_number}.tex"
    output_file = f"build/tex/page_{page_number}_ascii.tex"
    
    logger.info(f"Converting {source_file} to ASCII encoding")
    
    try:
        # Read file in binary mode to avoid encoding errors
        with open(source_file, 'rb') as f:
            content = f.read()
        
        # Convert to ASCII with LaTeX conventions for special characters
        result = b""
        i = 0
        while i < len(content):
            byte = content[i]
            
            if byte < 128:  # ASCII character
                result += bytes([byte])
            else:
                # Handle multi-byte UTF-8 sequences for Polish characters
                if i + 1 < len(content):
                    if byte == 0xc4:  # First byte of some Polish characters
                        if content[i+1] == 0x85:  # ą
                            result += b"\\k{a}"
                            i += 1
                        elif content[i+1] == 0x84:  # Ą
                            result += b"\\k{A}"
                            i += 1
                        elif content[i+1] == 0x87:  # ć
                            result += b"\\'c"
                            i += 1
                        elif content[i+1] == 0x86:  # Ć
                            result += b"\\'C"
                            i += 1
                        elif content[i+1] == 0x99:  # ę
                            result += b"\\k{e}"
                            i += 1
                        elif content[i+1] == 0x98:  # Ę
                            result += b"\\k{E}"
                            i += 1
                        else:
                            result += b"?"
                            i += 1
                    elif byte == 0xc5:  # First byte of other Polish characters
                        if content[i+1] == 0x82:  # ł
                            result += b"\\l{}"
                            i += 1
                        elif content[i+1] == 0x81:  # Ł
                            result += b"\\L{}"
                            i += 1
                        elif content[i+1] == 0x84:  # ń
                            result += b"\\'n"
                            i += 1
                        elif content[i+1] == 0x83:  # Ń
                            result += b"\\'N"
                            i += 1
                        elif content[i+1] == 0xb3:  # ó
                            result += b"\\'o"
                            i += 1
                        elif content[i+1] == 0x93:  # Ó
                            result += b"\\'O"
                            i += 1
                        elif content[i+1] == 0x9b:  # ś
                            result += b"\\'s"
                            i += 1
                        elif content[i+1] == 0x9a:  # Ś
                            result += b"\\'S"
                            i += 1
                        elif content[i+1] == 0xba:  # ź
                            result += b"\\'z"
                            i += 1
                        elif content[i+1] == 0xb9:  # Ź
                            result += b"\\'Z"
                            i += 1
                        elif content[i+1] == 0xbc:  # ż
                            result += b"\\.z"
                            i += 1
                        elif content[i+1] == 0xbb:  # Ż
                            result += b"\\.Z"
                            i += 1
                        else:
                            result += b"?"
                            i += 1
                    else:
                        # Handle other non-ASCII characters with LaTeX escape
                        result += b"\\textbf{?}"
                else:
                    # Incomplete UTF-8 sequence at end of file
                    result += b"?"
            i += 1
        
        # Write ASCII version
        with open(output_file, 'wb') as f:
            f.write(result)
        
        logger.info(f"Successfully created ASCII version in {output_file}")
        return True
    
    except Exception as e:
        logger.error(f"Error processing file {source_file}: {e}")
        return False

def create_main_tex_ascii():
    """Create a main.tex file in ASCII encoding that includes the ASCII versions of pages."""
    try:
        logger.info("Creating ASCII version of main.tex")
        
        # Get all page files
        page_files = sorted(glob.glob("build/tex/page_[0-9].tex"), 
                         key=lambda x: int(re.search(r'page_(\d+)\.tex', x).group(1)))
        
        if not page_files:
            logger.error("No page files found!")
            return False
        
        main_ascii_path = "build/tex/main_ascii.tex"
        
        with open(main_ascii_path, 'w', encoding='ascii', errors='backslashreplace') as f:
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
            f.write("\\usepackage{textcomp}\n")
            f.write("\\usepackage[sorting=none]{biblatex}\n")
            f.write("\\usepackage{polski}\n")
            f.write("\\usepackage[polish]{babel}\n")
            f.write("\\usepackage{lipsum}  % For sample text\n\n")
            
            # Set graphics path
            f.write("\\graphicspath{{../}}\n\n")
            
            # Document metadata
            f.write("\\title{Rewolucja w medycynie: Inteligentne sterowanie polami Tesli do ukladania nanorurek in vivo}\n")
            f.write("\\author{Magister Thesis}\n")
            f.write("\\date{\\today}\n\n")
            
            # Begin document
            f.write("\\begin{document}\n\n")
            
            # Title page
            f.write("\\maketitle\n")
            f.write("\\tableofcontents\n")
            f.write("\\newpage\n\n")
            
            # Include pages
            for page_file in page_files:
                page_num = re.search(r'page_(\d+)\.tex', page_file).group(1)
                # Create ASCII version of this page
                if fix_page_file(page_num):
                    f.write(f"\\include{{page_{page_num}_ascii}}\n")
            
            # End document
            f.write("\\end{document}\n")
        
        logger.info(f"Successfully created {main_ascii_path}")
        return True
    
    except Exception as e:
        logger.error(f"Error creating ASCII main.tex: {e}")
        return False

def compile_ascii_thesis():
    """Compile the ASCII version of the thesis."""
    try:
        logger.info("Compiling ASCII version of thesis")
        
        # Change to build/tex directory
        os.chdir("build/tex")
        
        # Compile with pdflatex
        command = ["pdflatex", "-shell-escape", "-interaction=nonstopmode", "main_ascii.tex"]
        logger.info(f"Running: {' '.join(command)}")
        
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Run biber
        subprocess.run(["biber", "main_ascii"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Run pdflatex again twice
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Check if PDF was created
        if os.path.exists("main_ascii.pdf"):
            # Copy to the pdf directory
            os.chdir("../..")  # Return to original directory
            os.makedirs("build/pdf", exist_ok=True)
            from shutil import copy
            copy("build/tex/main_ascii.pdf", "build/pdf/thesis_ascii.pdf")
            copy("build/tex/main_ascii.pdf", "build/pdf/latest.pdf")
            
            logger.info("Successfully compiled ASCII thesis")
            logger.info(f"PDF available at: {os.path.abspath('build/pdf/thesis_ascii.pdf')}")
            return True
        else:
            os.chdir("../..")  # Return to original directory
            logger.error("Failed to create PDF")
            return False
    
    except Exception as e:
        try:
            os.chdir("../..")  # Try to return to original directory
        except:
            pass
        
        logger.error(f"Error compiling ASCII thesis: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting ASCII thesis creation process")
    
    # Create ASCII versions of the page files
    if create_main_tex_ascii():
        # Compile the ASCII thesis
        if compile_ascii_thesis():
            logger.info("ASCII thesis creation completed successfully")
            sys.exit(0)
        else:
            logger.error("ASCII thesis compilation failed")
            sys.exit(1)
    else:
        logger.error("Failed to create ASCII main.tex")
        sys.exit(1)