#!/usr/bin/env python3
"""
Skrypt tworzący przykładowy obraz dla projektu thesis_builder.
Obraz przedstawia schemat przepływu pracy (workflow) w systemie.

Użycie:
    python create_sample_image.py --output ścieżka/do/obrazu.png --width 800 --height 600
"""

from PIL import Image, ImageDraw, ImageFont
import os
import argparse
import sys

def create_sample_image(output_path, width=400, height=300, title="Thesis Builder Workflow"):
    """
    Tworzy przykładowy obraz przedstawiający schemat przepływu pracy.
    
    Args:
        output_path: Ścieżka do pliku wyjściowego
        width: Szerokość obrazu w pikselach
        height: Wysokość obrazu w pikselach
        title: Tytuł umieszczony na obrazie
    """
    # Utwórz katalog docelowy, jeśli nie istnieje
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Utwórz nowy biały obraz
    img = Image.new('RGB', (width, height), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    
    # Dodaj obramowanie
    d.rectangle([(0, 0), (width-1, height-1)], outline=(0, 0, 0))
    
    # Proporcjonalne rozmieszczenie elementów
    box_width = width // 5
    box_height = height // 5
    y_center = height // 3
    
    # Oblicz współrzędne dla trzech bloków
    box1_x = width // 6
    box2_x = width // 2
    box3_x = 5 * width // 6
    
    # Blok 1 - JSON
    d.rectangle([(box1_x - box_width//2, y_center - box_height//2), 
                 (box1_x + box_width//2, y_center + box_height//2)], 
                outline=(0, 0, 0), width=2)
    d.text((box1_x, y_center), "JSON", fill=(0, 0, 0), anchor="mm")
    
    # Blok 2 - LaTeX
    d.rectangle([(box2_x - box_width//2, y_center - box_height//2), 
                 (box2_x + box_width//2, y_center + box_height//2)], 
                outline=(0, 0, 0), width=2)
    d.text((box2_x, y_center), "LaTeX", fill=(0, 0, 0), anchor="mm")
    
    # Blok 3 - PDF
    d.rectangle([(box3_x - box_width//2, y_center - box_height//2), 
                 (box3_x + box_width//2, y_center + box_height//2)], 
                outline=(0, 0, 0), width=2)
    d.text((box3_x, y_center), "PDF", fill=(0, 0, 0), anchor="mm")
    
    # Strzałki
    arrow_length = (box2_x - box1_x) - box_width
    
    # Strzałka 1
    d.line([(box1_x + box_width//2, y_center), 
            (box2_x - box_width//2, y_center)], 
           fill=(0, 0, 0), width=2)
    
    # Strzałka 2
    d.line([(box2_x + box_width//2, y_center), 
            (box3_x - box_width//2, y_center)], 
           fill=(0, 0, 0), width=2)
    
    # Tytuł
    d.text((width//2, 2*height//3), title, fill=(0, 0, 0), anchor="mm")
    
    # Dodatkowy opis
    d.text((width//2, 2*height//3 + 40), "Content → Assembly → Compilation", 
           fill=(0, 0, 0), anchor="mm")
    
    # Zapisz obraz
    img.save(output_path)
    print(f"Obraz został utworzony: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Tworzenie przykładowego obrazu dla thesis_builder.")
    parser.add_argument("--output", default="pages/1/sample_image.png", 
                      help="Ścieżka wyjściowa dla obrazu")
    parser.add_argument("--width", type=int, default=400, 
                      help="Szerokość obrazu w pikselach")
    parser.add_argument("--height", type=int, default=300, 
                      help="Wysokość obrazu w pikselach")
    parser.add_argument("--title", default="Thesis Builder Workflow", 
                      help="Tytuł umieszczony na obrazie")
    
    args = parser.parse_args()
    
    try:
        create_sample_image(args.output, args.width, args.height, args.title)
    except Exception as e:
        print(f"Błąd podczas tworzenia obrazu: {e}", file=sys.stderr)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())