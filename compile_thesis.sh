#!/bin/bash

# Script for directly compiling the full thesis without using build_thesis.py
# This script avoids Python's encoding issues by using direct LaTeX commands
# Usage: ./compile_thesis.sh

# Set variables
BUILD_DIR="build/tex"
OUTPUT_DIR="build/pdf"
MAIN_TEX="main.tex"
OUTPUT_PDF="thesis_$(date +%Y%m%d_%H%M%S).pdf"
LATEST_PDF="latest.pdf"

# Create output directories if they don't exist
mkdir -p $BUILD_DIR $OUTPUT_DIR

# Display instructions
echo "=========================="
echo "Thesis Compilation Script"
echo "=========================="
echo "This script directly compiles the entire thesis using LaTeX commands"
echo "to avoid Python's encoding issues with Polish characters."
echo ""

# Run the assembler to generate page fragments and bibliography
echo "Generating LaTeX fragments with assembler.py..."
python3 assembler.py

# Run the compiler to generate main.tex with bibliography
echo "Generating main.tex with bibliography..."
python3 compiler.py

# Navigate to the build directory
cd $BUILD_DIR

# First pass of pdflatex
echo "Running first pdflatex pass..."
pdflatex -shell-escape -interaction=nonstopmode $MAIN_TEX

# Run biber for bibliography
echo "Running biber..."
biber main

# Second pass of pdflatex
echo "Running second pdflatex pass..."
pdflatex -shell-escape -interaction=nonstopmode $MAIN_TEX

# Final pass of pdflatex
echo "Running final pdflatex pass..."
pdflatex -shell-escape -interaction=nonstopmode $MAIN_TEX

# Check if compilation was successful
if [ -f "main.pdf" ]; then
    # Copy output to the PDF directory
    cp main.pdf "../pdf/$OUTPUT_PDF"
    cp main.pdf "../pdf/$LATEST_PDF"
    
    # Clean up temporary LaTeX files
    echo "Cleaning up temporary LaTeX files..."
    rm -f *.aux *.bbl *.bcf *.blg *.log *.out *.run.xml *.toc *.lof *.lot *.idx *.ilg *.ind *.fls *.fdb_latexmk
    
    # Return to original directory
    cd ../..
    
    echo ""
    echo "=========================="
    echo "Compilation successful!"
    echo "Output files:"
    echo " - $OUTPUT_DIR/$OUTPUT_PDF"
    echo " - $OUTPUT_DIR/$LATEST_PDF"
    echo "=========================="
else
    # Return to original directory
    cd ../..
    
    echo ""
    echo "=========================="
    echo "Compilation failed!"
    echo "Check the log files in $BUILD_DIR for errors."
    echo "=========================="
    exit 1
fi

exit 0