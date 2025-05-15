#!/usr/bin/env python3
import os
import sys
import logging
import argparse
import subprocess
import json
import glob
import shutil
from pathlib import Path
import time
import datetime

# Configure logging
os.makedirs("build/logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("build/logs/build.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("thesis-builder")

def ensure_directory_structure():
    """Ensure the required directory structure exists."""
    logger.info("Checking directory structure")
    
    # Create required directories if they don't exist
    required_dirs = [
        "pages",
        "build",
        "build/tex",
        "build/pdf",
        "build/logs",
        "schema"
    ]
    
    for directory in required_dirs:
        if not os.path.exists(directory):
            logger.info(f"Creating directory: {directory}")
            os.makedirs(directory, exist_ok=True)
    
    # Check for the schema file
    if not os.path.exists("schema/page_schema.json"):
        logger.error("Schema file not found: schema/page_schema.json")
        return False
    
    return True

def validate_page_json(page_number):
    """Validate JSON files for a specific page."""
    logger.info(f"Validating JSON for page {page_number}")
    
    page_dir = f"pages/{page_number}"
    if not os.path.exists(page_dir):
        logger.error(f"Page directory not found: {page_dir}")
        return False
    
    # Find all JSON files in the page directory
    json_files = glob.glob(f"{page_dir}/*.json")
    
    if not json_files:
        logger.warning(f"No JSON files found in {page_dir}")
        return False
    
    valid_count = 0
    
    for json_file in json_files:
        try:
            # Load the JSON schema
            with open("schema/page_schema.json", 'r') as schema_file:
                from jsonschema import validate
                schema = json.load(schema_file)
            
            # Load and validate the JSON file
            with open(json_file, 'r') as f:
                data = json.load(f)
                validate(instance=data, schema=schema)
                valid_count += 1
                logger.info(f"Successfully validated {json_file}")
        
        except Exception as e:
            logger.error(f"Validation failed for {json_file}: {e}")
            return False
    
    return valid_count > 0

def assemble_page(page_number):
    """Assemble LaTeX fragments for a specific page."""
    logger.info(f"Assembling page {page_number}")
    
    try:
        # Run the assembler script for this page
        result = subprocess.run(
            [sys.executable, "assembler.py", str(page_number)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Check if the output file was created
        output_file = f"build/tex/page_{page_number}.tex"
        if os.path.exists(output_file):
            logger.info(f"Successfully assembled {output_file}")
            return True
        else:
            logger.error(f"Failed to create {output_file}")
            logger.error(f"Assembler output: {result.stdout}")
            logger.error(f"Assembler errors: {result.stderr}")
            return False
    
    except Exception as e:
        logger.error(f"Error assembling page {page_number}: {e}")
        return False

def compile_page(page_number):
    """Compile a single page to PDF for testing."""
    logger.info(f"Compiling page {page_number}")
    
    try:
        # Run the compiler script for this page
        result = subprocess.run(
            [sys.executable, "compiler.py", str(page_number)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Check if the output file was created
        output_file = f"build/pdf/page_{page_number}.pdf"
        if os.path.exists(output_file):
            logger.info(f"Successfully compiled {output_file}")
            return True
        else:
            logger.error(f"Failed to create {output_file}")
            logger.error(f"Compiler output: {result.stdout}")
            logger.error(f"Compiler errors: {result.stderr}")
            return False
    
    except Exception as e:
        logger.error(f"Error compiling page {page_number}: {e}")
        return False

def compile_thesis():
    """Compile the entire thesis."""
    logger.info("Compiling entire thesis")
    
    try:
        # Assemble all pages first
        subprocess.run(
            [sys.executable, "assembler.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wykonaj bezpośrednią kompilację poprzez uruchomienie poleceń LaTeX
        logger.info("Compiling thesis directly with pdflatex")
        
        current_dir = os.getcwd()
        
        # Przejdź do katalogu z plikami źródłowymi
        os.chdir("build/tex")
        
        try:
            # Uruchom kolejno komendy pdflatex i biber, żeby wygenerować dokument
            logger.info("Running pdflatex first pass")
            pdflatex1 = subprocess.run(
                ["pdflatex", "-shell-escape", "-interaction=nonstopmode", "main.tex"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            logger.info("Running biber")
            biber = subprocess.run(
                ["biber", "main"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            logger.info("Running pdflatex second pass")
            pdflatex2 = subprocess.run(
                ["pdflatex", "-shell-escape", "-interaction=nonstopmode", "main.tex"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            logger.info("Running pdflatex final pass")
            pdflatex3 = subprocess.run(
                ["pdflatex", "-shell-escape", "-interaction=nonstopmode", "main.tex"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Sprawdź czy PDF został wygenerowany
            if os.path.exists("main.pdf"):
                # Kopiuj do odpowiedniego katalogu wyjściowego
                os.makedirs("../pdf", exist_ok=True)
                shutil.copy("main.pdf", "../pdf/latest.pdf")
                
                # Utwórz kopię z datownikiem
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                shutil.copy("main.pdf", f"../pdf/thesis_{timestamp}.pdf")
                
                # Wróć do oryginalnego katalogu
                os.chdir(current_dir)
                logger.info(f"Thesis compiled successfully to build/pdf/latest.pdf")
                return True
            else:
                # Wróć do oryginalnego katalogu
                os.chdir(current_dir)
                logger.error("Failed to generate PDF")
                return False
                
        except Exception as e:
            # Wróć do oryginalnego katalogu w przypadku błędu
            os.chdir(current_dir)
            logger.error(f"Error during LaTeX compilation: {e}")
            return False
    
    except Exception as e:
        logger.error(f"Error compiling thesis: {e}")
        return False

def build_page(page_number):
    """Build a single page (validate, assemble, compile)."""
    logger.info(f"Building page {page_number}")
    
    # Track step status
    steps_status = {
        "validate": False,
        "assemble": False,
        "compile": False
    }
    
    # Step 1: Validate JSON
    logger.info(f"[STEP 1/3] Validating page {page_number}")
    steps_status["validate"] = validate_page_json(page_number)
    
    if not steps_status["validate"]:
        logger.error(f"Validation failed for page {page_number}")
        return False
    
    # Step 2: Assemble LaTeX
    logger.info(f"[STEP 2/3] Assembling page {page_number}")
    steps_status["assemble"] = assemble_page(page_number)
    
    if not steps_status["assemble"]:
        logger.error(f"Assembly failed for page {page_number}")
        return False
    
    # Step 3: Compile to PDF
    logger.info(f"[STEP 3/3] Compiling page {page_number}")
    steps_status["compile"] = compile_page(page_number)
    
    if not steps_status["compile"]:
        logger.error(f"Compilation failed for page {page_number}")
        return False
    
    # All steps passed
    logger.info(f"Successfully built page {page_number}")
    return True

def clean_log_files():
    """Clean log files to avoid line ending issues."""
    log_dir = "build/logs"
    if os.path.exists(log_dir):
        for log_file in os.listdir(log_dir):
            file_path = os.path.join(log_dir, log_file)
            if os.path.isfile(file_path):
                try:
                    # Czyszczenie pliku
                    with open(file_path, 'w') as f:
                        f.write("")
                except Exception as e:
                    logger.error(f"Error cleaning log file {file_path}: {e}")

def build_all():
    """Build the entire thesis."""
    logger.info("Building entire thesis")
    
    # Get all page directories
    page_dirs = sorted([d for d in os.listdir("pages") if os.path.isdir(os.path.join("pages", d)) and d.isdigit()],
                      key=lambda x: int(x))
    
    if not page_dirs:
        logger.error("No page directories found")
        return False
    
    # Track build status for each page
    build_status = {}
    
    # First, build each page individually
    for page_dir in page_dirs:
        page_number = int(page_dir)
        logger.info(f"Building individual page {page_number}")
        
        success = build_page(page_number)
        build_status[page_number] = success
        
        if not success:
            logger.error(f"Failed to build page {page_number}")
    
    # Report individual page build status
    logger.info("Individual page build status:")
    for page_number, success in build_status.items():
        status_str = "SUCCESS" if success else "FAILED"
        logger.info(f"Page {page_number}: {status_str}")
    
    # Check if we can proceed with full thesis build
    if not all(build_status.values()):
        logger.warning("Some pages failed to build individually")
        proceed = input("Continue with full thesis build anyway? (y/n): ").lower()
        if proceed != 'y':
            logger.info("Build aborted by user")
            return False
    
    # Compile the full thesis
    logger.info("Building full thesis document")
    thesis_success = compile_thesis()
    
    if thesis_success:
        logger.info("Thesis built successfully")
        print(f"Thesis PDF available at: {os.path.abspath('build/pdf/latest.pdf')}")
    else:
        logger.error("Failed to build thesis")
    
    # Clean log files to avoid line ending issues
    clean_log_files()
    
    return thesis_success

def clean_build():
    """Clean build artifacts."""
    logger.info("Cleaning build artifacts")
    
    # List of directories to clean
    to_clean = [
        "build/tex",
        "build/pdf",
        "build/logs"
    ]
    
    for directory in to_clean:
        if os.path.exists(directory):
            logger.info(f"Cleaning {directory}")
            # Remove all files in the directory
            for file in os.listdir(directory):
                file_path = os.path.join(directory, file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    logger.error(f"Error removing {file_path}: {e}")
    
    # Recreate empty log directory
    os.makedirs("build/logs", exist_ok=True)
    
    logger.info("Build artifacts cleaned")
    return True

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Thesis Builder")
    parser.add_argument("command", choices=["build", "validate", "assemble", "compile", "clean"],
                        help="Command to execute")
    parser.add_argument("--page", type=int, help="Page number to process (optional)")
    
    args = parser.parse_args()
    
    # Ensure directory structure
    if not ensure_directory_structure():
        logger.error("Failed to ensure directory structure")
        return 1
    
    # Process the command
    if args.command == "build":
        if args.page:
            success = build_page(args.page)
        else:
            success = build_all()
        # Clean log files after build
        clean_log_files()
    
    elif args.command == "validate":
        if args.page:
            success = validate_page_json(args.page)
        else:
            # Validate all pages
            page_dirs = sorted([d for d in os.listdir("pages") if os.path.isdir(os.path.join("pages", d)) and d.isdigit()],
                              key=lambda x: int(x))
            success = True
            for page_dir in page_dirs:
                page_success = validate_page_json(int(page_dir))
                if not page_success:
                    success = False
        # Clean log files after validation
        clean_log_files()
    
    elif args.command == "assemble":
        if args.page:
            success = assemble_page(args.page)
        else:
            # Run the assembler for all pages
            subprocess_result = subprocess.run(
                [sys.executable, "assembler.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            success = subprocess_result.returncode == 0
        # Clean log files after assembly
        clean_log_files()
    
    elif args.command == "compile":
        if args.page:
            success = compile_page(args.page)
        else:
            success = compile_thesis()
        # Clean log files after compilation
        clean_log_files()
    
    elif args.command == "clean":
        success = clean_build()
    
    # Return exit code based on success
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())