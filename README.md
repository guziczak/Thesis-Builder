# Thesis Builder

A structured two-stage LaTeX thesis builder system that organizes content in JSON format and compiles it into a unified LaTeX document.

## Overview

This thesis builder system provides a structured approach to writing a thesis:

1. **First stage**: Content is organized in JSON files with a well-defined schema
2. **Second stage**: Content is automatically assembled and compiled into LaTeX documents with detailed logging

## Features

- Structured content organization with JSON schema validation
- Independent page compilation for incremental testing
- Detailed logging of compilation status for each component
- Clean separation of content and formatting
- Support for text, images, tables, code listings, and equations
- **External text files**: Text content can be stored in separate text files (.txt) and referenced from JSON (must be plain text without any Markdown formatting)

## Directory Structure

```
thesis_builder/
├── build/               # Build artifacts
│   ├── logs/            # Compilation logs
│   ├── pdf/             # Generated PDF files
│   └── tex/             # Generated LaTeX files
├── pages/               # Content organized by page number
│   ├── 1/               # Page 1 content
│   │   ├── content.json # Content definition
│   │   ├── text_*.txt   # External text files (MUST use .txt extension)
│   │   └── *.png        # Images used on this page
│   ├── 2/               # Page 2 content
│   └── ...
├── schema/              # JSON schemas
│   └── page_schema.json # Schema for page content
├── assembler.py         # Script to generate LaTeX from JSON
├── compiler.py          # Script to compile LaTeX to PDF
├── build_thesis.py      # Main build script
└── create_structure.sh  # Script to create initial directory structure
```

## Krok po kroku instrukcja użycia

### 1. Utworzenie struktury projektu

```bash
# Nadanie uprawnień wykonywania skryptowi
chmod +x create_structure.sh

# Utworzenie podstawowej struktury katalogów i pliku schematu JSON
./create_structure.sh
```

**Uwaga:** Skrypt `create_structure.sh` automatycznie tworzy katalogi dla stron (pages/1-5), katalogi dla plików wyjściowych (build/logs, build/pdf, build/tex) oraz plik schematu JSON (schema/page_schema.json).

### 2. Tworzenie zawartości

#### 2.1 Utworzenie strony/rozdziału

```bash
# Utworzenie katalogu dla strony (jeśli nie istnieje)
mkdir -p pages/1
```

#### 2.2 Dodanie tekstu (bez formatowania markdown!)

```bash
# Utworzenie tekstu dla strony
cat > pages/1/text_content.txt << EOF
To jest przykładowy tekst dla strony pracy. Należy używać zwykłego tekstu bez formatowania markdown.

Tekst może zawierać wiele akapitów, każdy akapit powinien być w jednej linii.

Ważne elementy takie jak tabele, kody czy równania, powinny być definiowane jako osobne bloki w pliku content.json, nie w pliku tekstowym.

UWAGA: Tekst musi być zwykłym tekstem bez formatowania markdown (bez nagłówków #, list numerowanych 1., 2., pogrubień **, kursywy *, bloków kodu itp.).
EOF
```

#### 2.3 Dodanie obrazów (opcjonalnie)

```bash
# Utworzenie lub skopiowanie obrazu do katalogu strony
./create_sample_image.py --output pages/1/sample_image.png --width 800 --height 600
```

#### 2.4 Utworzenie pliku content.json

```bash
# Utworzenie pliku content.json dla strony
cat > pages/1/content.json << EOF
{
  "title": "Rozdział pierwszy",
  "sectionLevel": 1,
  "pageNumber": 1,
  "content": [
    {
      "type": "text",
      "data": {
        "textPath": "text_content.txt"
      }
    },
    {
      "type": "image",
      "data": {
        "imagePath": "sample_image.png",
        "caption": "Przykładowy obraz wygenerowany przez skrypt",
        "label": "fig:sample1"
      }
    },
    {
      "type": "table",
      "data": {
        "tableData": [
          ["Kolumna 1", "Kolumna 2", "Kolumna 3"],
          ["Wartość 1", "Wartość 2", "Wartość 3"],
          ["Wartość 4", "Wartość 5", "Wartość 6"]
        ],
        "caption": "Przykładowa tabela",
        "label": "tab:przyklad1"
      }
    }
  ],
  "references": [
    {
      "id": "ref1",
      "citation": "@article{przykład2023, title={Przykładowy artykuł}, author={Kowalski, Jan}, journal={Journal of Examples}, year={2023}}"
    }
  ]
}
EOF
```

#### 2.5 Utworzenie strony z równaniem matematycznym (strona 2)

```bash
# Utworzenie katalogu dla strony 2
mkdir -p pages/2

# Utworzenie pliku content.json dla strony 2
cat > pages/2/content.json << 'EOF'
{
  "title": "Analiza matematyczna",
  "sectionLevel": 2,
  "pageNumber": 2,
  "content": [
    {
      "type": "text",
      "data": {
        "text": "Poniżej przedstawiamy fundamentalne równanie opisujące nasz model matematyczny:"
      }
    },
    {
      "type": "equation",
      "data": {
        "equation": "\\frac{\\partial u}{\\partial t} = \\alpha \\nabla^2 u",
        "label": "eq:diffusion"
      }
    },
    {
      "type": "text",
      "data": {
        "text": "Powyższe równanie (\\ref{eq:diffusion}) opisuje proces dyfuzji ciepła, gdzie $u$ oznacza temperaturę, a $\\alpha$ jest współczynnikiem dyfuzyjności termicznej. Ta formuła matematyczna stanowi podstawę do dalszych rozważań w naszej pracy."
      }
    }
  ]
}
EOF
```

### 3. Walidacja zawartości

```bash
# Walidacja wszystkich stron
./validate_format.py
```

```bash
# Walidacja tylko konkretnej strony
./validate_format.py --page 1
```

Skrypt walidacyjny sprawdza:
- Poprawność schematów JSON
- Istnienie wszystkich plików tekstowych
- Brak formatowania markdown w plikach tekstowych (zakazane są nagłówki #, listy 1., pogrubienia **, itp.)

### 4. Generowanie i kompilacja

#### 4.1 Konwersja JSON na LaTeX

```bash
# Konwersja zawartości JSON na fragmenty LaTeX (bez kompilacji PDF)
./build_thesis.py assemble
```

```bash
# Konwersja tylko konkretnej strony
./build_thesis.py assemble --page 1
```

#### 4.2 Kompilacja LaTeX do PDF

```bash
# Kompilacja fragmentów LaTeX do PDF
./build_thesis.py compile
```
```bash
./compile_thesis.sh
```

```bash
# Kompilacja tylko konkretnej strony
./build_thesis.py compile --page 1
```

#### 4.3 Pełny proces (walidacja + konwersja + kompilacja)

```bash
# Pełny proces dla wszystkich stron
./build_thesis.py build

# Pełny proces dla pojedynczej strony
./build_thesis.py build --page 1
```

```bash
# Alternatywna metoda kompilacji całej pracy
./compile_thesis.sh
```

### 5. Czyszczenie plików tymczasowych

```bash
# Usunięcie wszystkich plików tymczasowych (tex, pdf, logi)
./build_thesis.py clean
```

Komenda `clean` usuwa:
- Pliki LaTeX (build/tex/)
- Pliki PDF (build/pdf/)
- Pliki logów (build/logs/)

Warto używać tej komendy przed commitem do repozytorium, aby uniknąć śledzenia tymczasowych plików.

## Command Reference

The main build script offers several commands:

- `build`: Validate, assemble, and compile (full process)
- `validate`: Only validate JSON content
- `assemble`: Generate LaTeX fragments from JSON
- `compile`: Compile LaTeX to PDF
- `clean`: Remove build artifacts

Add `--page N` to any command to process only a specific page.

## Requirements

- Python 3.6+
- LaTeX distribution (e.g., TeX Live, MiKTeX)
- Python packages: `jsonschema`

## JSON Content Schema

Content is organized in JSON files that follow this structure:

```json
{
  "title": "Chapter Title",
  "sectionLevel": 1,
  "pageNumber": 1,
  "content": [
    {
      "type": "text",
      "data": {
        "text": "This is inline text content."
      }
    },
    {
      "type": "text",
      "data": {
        "textPath": "external_text_file.txt"
      }
    },
    {
      "type": "image",
      "data": {
        "imagePath": "image.png",
        "caption": "Image caption",
        "label": "fig:label"
      }
    }
  ],
  "references": [
    {
      "id": "ref1",
      "citation": "BibTeX citation"
    }
  ]
}
```

## Text Content Options

Text content can be specified in two ways:

1. **Inline text**: Directly included in the JSON file
   ```json
   {
     "type": "text",
     "data": {
       "text": "This is inline text content."
     }
   }
   ```

2. **External file**: Referenced from a separate text file (MUST use .txt extension)
   ```json
   {
     "type": "text",
     "data": {
       "textPath": "text_content.txt"
     }
   }
   ```

## Mathematical Equations

The system supports LaTeX mathematical equations with auto-numbering and referencing capabilities:

- Standard LaTeX math notation
- Auto-numbering in the final document
- Referencing via the label property
- Inline math expressions using $...$ syntax (even in external text files)
- References to equations using \ref{eq:label} syntax (even in external text files)
- Integration with the document's equation numbering system
- Full support for complex mathematical notation

### Math in Text Files

You can include inline math expressions and equation references directly in your text files:

1. **Inline Math**: Use standard LaTeX syntax with dollar signs: `$u$` for variable u or `$\alpha$` for the alpha symbol
2. **Equation References**: Use the standard LaTeX reference syntax: `\ref{eq:diffusion}` to reference an equation with label "eq:diffusion"

Example text file content:
```
Powyższe równanie (\ref{eq:diffusion}) opisuje proces dyfuzji ciepła, gdzie $u$ oznacza temperaturę, a $\alpha$ jest współczynnikiem dyfuzyjności termicznej. Ta formuła matematyczna stanowi podstawę do dalszych rozważań w naszej pracy.
```

### Important Rules for Text Files

External text files (.txt) must follow these requirements:

- Must contain ONLY plain text without any Markdown formatting
- NO headings (lines starting with #)
- NO numbered or bulleted lists (lines starting with numbers followed by periods or asterisks)
- NO formatting marks (**, *, __, ~~, etc.)
- NO code blocks (```), tables, or any other markdown syntax
- Text can contain paragraphs (blank lines are allowed)
- Each paragraph should be in a single line
- LaTeX inline math expressions using $...$ syntax ARE ALLOWED
- LaTeX equation references using \ref{label} syntax ARE ALLOWED
- Any formatting needed (italics, bold, etc.) should be applied at the LaTeX level

The validator script (validate_format.py) checks all text files to ensure they don't contain Markdown formatting. This ensures consistent rendering in the final LaTeX document.

This gives you flexibility to:
- Keep short text blocks in the JSON file for better context
- Move longer text sections to dedicated files for better editing
- Split content across multiple files for collaborative editing

For more details, see the `schema/page_schema.json` file.