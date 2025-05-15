#!/usr/bin/env python3
"""
Skrypt tworzący prosty obraz PNG bez dodatkowych zależności.
Używa tylko bibliotek standardowych Python.

Użycie:
    python create_simple_image.py --output ścieżka/do/obrazu.png --width 400 --height 300
"""

import struct
import zlib
import os
import argparse
import sys

def write_png(filename, width=400, height=300, pattern="grid"):
    """
    Tworzy prosty obraz PNG bez używania zewnętrznych bibliotek.
    
    Args:
        filename: Ścieżka do pliku wyjściowego
        width: Szerokość obrazu w pikselach
        height: Wysokość obrazu w pikselach
        pattern: Rodzaj wzoru ("grid", "cross", "frame")
    """
    # Utwórz katalog docelowy, jeśli nie istnieje
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    def chunk(chunk_type, data):
        """
        Tworzy fragment danych PNG.
        """
        return struct.pack(">I", len(data)) + chunk_type + data + struct.pack(">I", zlib.crc32(chunk_type + data) & 0xFFFFFFFF)

    # IDAT chunk (dane obrazu)
    raw_data = b''
    for y in range(height):
        raw_data += b'\x00'  # Typ filtra 0 (brak)
        for x in range(width):
            # Wybór wzoru w zależności od parametru
            if pattern == "grid":
                # Wzór siatki
                if x % 20 < 2 or y % 20 < 2:
                    raw_data += b'\x00\x00\x00'  # Czarny
                else:
                    raw_data += b'\xff\xff\xff'  # Biały
            elif pattern == "cross":
                # Wzór krzyża
                if (x == width//2 and y >= height//4 and y <= 3*height//4) or \
                   (y == height//2 and x >= width//4 and x <= 3*width//4):
                    raw_data += b'\x00\x00\x00'  # Czarny
                else:
                    raw_data += b'\xff\xff\xff'  # Biały
            elif pattern == "frame":
                # Wzór ramki i wypełnienia
                if (x < 10 or x > width-10 or y < 10 or y > height-10 or 
                    (x > width//3 and x < 2*width//3 and y > height//3 and y < 2*height//3)):
                    raw_data += b'\x00\x00\x00'  # Czarny
                else:
                    raw_data += b'\xff\xff\xff'  # Biały
            else:
                # Domyślny wzór - ramka
                if x == 0 or x == width-1 or y == 0 or y == height-1:
                    raw_data += b'\x00\x00\x00'  # Czarny
                else:
                    raw_data += b'\xff\xff\xff'  # Biały
    
    with open(filename, 'wb') as f:
        # Sygnatura PNG
        f.write(b'\x89PNG\r\n\x1a\n')
        
        # IHDR chunk (nagłówek obrazu)
        ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)  # 8-bit RGB
        f.write(chunk(b'IHDR', ihdr))
        
        # Kompresja danych
        compressed = zlib.compress(raw_data)
        f.write(chunk(b'IDAT', compressed))
        
        # IEND chunk (koniec obrazu)
        f.write(chunk(b'IEND', b''))

    print(f"Utworzono prosty obraz PNG: {filename}")

def main():
    parser = argparse.ArgumentParser(description="Tworzenie prostego obrazu PNG bez zewnętrznych zależności.")
    parser.add_argument("--output", default="pages/2/simple_image.png", 
                      help="Ścieżka wyjściowa dla obrazu")
    parser.add_argument("--width", type=int, default=400, 
                      help="Szerokość obrazu w pikselach")
    parser.add_argument("--height", type=int, default=300, 
                      help="Wysokość obrazu w pikselach")
    parser.add_argument("--pattern", default="grid", choices=["grid", "cross", "frame"],
                      help="Rodzaj wzoru: grid (siatka), cross (krzyż), frame (ramka)")
    
    args = parser.parse_args()
    
    try:
        write_png(args.output, args.width, args.height, args.pattern)
    except Exception as e:
        print(f"Błąd podczas tworzenia obrazu: {e}", file=sys.stderr)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())