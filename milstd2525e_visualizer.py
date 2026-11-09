# -*- coding: utf-8 -*-
"""
Geriye dönük uyumluluk giriş noktası.

Görselleştirici artık tek bir yerde tutulur:
  - visualizerGrk.py  : Tkinter arayüzü (SIDC <-> Link 16, sembol önizleme)
  - link16_ed9.py     : STANAG 5516 Ed.9 teşhis motoru (GUI'den bağımsız)

Çalıştırma:
  python3 milstd2525e_visualizer.py   (veya python3 visualizerGrk.py)
"""

from link16_ed9 import Link16Ed9Extractor  # noqa: F401  (eski import yolları için)
from visualizerGrk import MilStd2525EVisualizer, main  # noqa: F401

if __name__ == "__main__":
    main()
