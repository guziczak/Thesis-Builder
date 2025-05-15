#!/usr/bin/env python3
"""
Skrypt walidacyjny do sprawdzania formatu plików tekstowych i poprawności JSON
w projekcie thesis_builder.
"""

import os
import re
import json
import argparse
from jsonschema import validate, ValidationError


def validate_json_schema(json_file, schema_file):
    """Waliduje strukture JSON względem schematu."""
    try:
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        
        with open(json_file, 'r', encoding='utf-8') as f:
            content = json.load(f)
            
        validate(instance=content, schema=schema)
        return True, "JSON zgodny ze schematem"
    except ValidationError as e:
        return False, f"Błąd walidacji JSON: {e}"
    except Exception as e:
        return False, f"Błąd podczas walidacji: {e}"


def has_markdown_formatting(file_path):
    """Sprawdza czy plik zawiera formatowanie markdown."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Typowe markery formatowania markdown
    markdown_patterns = [
        r'^#{1,6}\s',  # Nagłówki
        r'^\*\s',      # Lista nienumerowana
        r'^\d+\.\s',   # Lista numerowana 
        r'^>\s',       # Cytaty
        r'`{3}',       # Bloki kodu
        r'\[.*?\]\(.*?\)',  # Linki
        r'!\[.*?\]\(.*?\)',  # Obrazy
        r'^---+$',     # Linie poziome
        r'^\|\s',      # Tabele
        r'\*\*.+?\*\*',  # Pogrubienie
        r'_.+?_',      # Kursywa
        r'==[^=].+?==',  # Podkreślenie
    ]
    
    for pattern in markdown_patterns:
        if re.search(pattern, content, re.MULTILINE):
            return True, f"Znaleziono formatowanie markdown pasujące do wzoru: {pattern}"
    
    return False, "Brak formatowania markdown"


def check_text_files_in_json(json_file):
    """Sprawdza, czy wszystkie referencje do plików tekstowych mają rozszerzenie .txt"""
    errors = []
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            content = json.load(f)
        
        # Szukaj bloków tekstowych z referencjami do plików
        for block in content.get('content', []):
            if block.get('type') == 'text':
                data = block.get('data', {})
                if 'textPath' in data:
                    path = data['textPath']
                    if not path.endswith('.txt'):
                        errors.append(f"Nieprawidłowe rozszerzenie pliku tekstowego: {path} - musi kończyć się na .txt")
                    
                    # Sprawdź czy plik istnieje
                    full_path = os.path.join(os.path.dirname(json_file), path)
                    if not os.path.exists(full_path):
                        errors.append(f"Plik tekstowy nie istnieje: {full_path}")
                    else:
                        # Sprawdź formatowanie markdown
                        has_md, md_error = has_markdown_formatting(full_path)
                        if has_md:
                            errors.append(f"Plik {path} zawiera formatowanie markdown: {md_error}")
        
        if errors:
            return False, errors
        return True, ["Wszystkie pliki tekstowe są poprawne"]
        
    except Exception as e:
        return False, [f"Błąd podczas sprawdzania plików tekstowych: {e}"]


def validate_page_directory(page_dir, schema_file):
    """Waliduje katalog strony."""
    results = {}
    content_file = os.path.join(page_dir, 'content.json')
    
    if not os.path.exists(content_file):
        results['content.json'] = {"status": "ERROR", "messages": ["Plik content.json nie istnieje"]}
        return results
    
    # Walidacja schematu JSON
    schema_valid, schema_msg = validate_json_schema(content_file, schema_file)
    if not schema_valid:
        results['schema'] = {"status": "ERROR", "messages": [schema_msg]}
    else:
        results['schema'] = {"status": "OK", "messages": [schema_msg]}
    
    # Sprawdzenie plików tekstowych
    text_valid, text_msgs = check_text_files_in_json(content_file)
    if not text_valid:
        results['text_files'] = {"status": "ERROR", "messages": text_msgs}
    else:
        results['text_files'] = {"status": "OK", "messages": text_msgs}
    
    return results


def validate_project(thesis_dir):
    """Waliduje cały projekt thesis_builder."""
    schema_file = os.path.join(thesis_dir, 'schema', 'page_schema.json')
    pages_dir = os.path.join(thesis_dir, 'pages')
    
    if not os.path.exists(schema_file):
        print(f"BŁĄD: Nie znaleziono pliku schematu: {schema_file}")
        return False
    
    if not os.path.exists(pages_dir):
        print(f"BŁĄD: Nie znaleziono katalogu stron: {pages_dir}")
        return False
    
    all_valid = True
    results = {}
    
    # Znajdź wszystkie katalogi stron
    for item in os.listdir(pages_dir):
        page_dir = os.path.join(pages_dir, item)
        if os.path.isdir(page_dir) and not item.startswith('.'):
            page_result = validate_page_directory(page_dir, schema_file)
            results[item] = page_result
            
            # Sprawdź, czy są jakieś błędy
            if any(r["status"] == "ERROR" for r in page_result.values()):
                all_valid = False
    
    return all_valid, results


def print_results(results):
    """Wypisuje wyniki walidacji w czytelnym formacie."""
    print("\n=== WYNIKI WALIDACJI ===\n")
    
    for page, sections in results.items():
        print(f"Strona: {page}")
        print("=" * (8 + len(page)))
        
        for section, result in sections.items():
            status = result["status"]
            status_color = "\033[92m" if status == "OK" else "\033[91m"  # Zielony lub czerwony
            reset_color = "\033[0m"
            
            print(f"  {section}: {status_color}{status}{reset_color}")
            for msg in result["messages"]:
                prefix = "    ✓ " if status == "OK" else "    ✗ "
                print(f"{prefix}{msg}")
        
        print("")


def main():
    parser = argparse.ArgumentParser(description='Waliduj formatowanie plików tekstowych i strukturę JSON w projekcie thesis_builder.')
    parser.add_argument('-d', '--directory', default='.', help='Katalog główny projektu thesis_builder')
    parser.add_argument('-p', '--page', help='Waliduj tylko konkretną stronę/rozdział')
    
    args = parser.parse_args()
    thesis_dir = os.path.abspath(args.directory)
    
    if args.page:
        page_dir = os.path.join(thesis_dir, 'pages', args.page)
        schema_file = os.path.join(thesis_dir, 'schema', 'page_schema.json')
        
        if not os.path.exists(page_dir):
            print(f"BŁĄD: Nie znaleziono katalogu strony: {page_dir}")
            return 1
            
        results = {args.page: validate_page_directory(page_dir, schema_file)}
        valid = not any(r["status"] == "ERROR" for r in results[args.page].values())
    else:
        valid, results = validate_project(thesis_dir)
    
    print_results(results)
    
    if valid:
        print("\033[92mWALIDACJA ZAKOŃCZONA SUKCESEM: Wszystkie pliki są zgodne z wymaganiami.\033[0m")
        return 0
    else:
        print("\033[91mWALIDACJA ZAKOŃCZONA NIEPOWODZENIEM: Znaleziono błędy formatowania.\033[0m")
        return 1


if __name__ == "__main__":
    exit(main())