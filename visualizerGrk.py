# -*- coding: utf-8 -*-
"""
MIL-STD-2525E Symbol Visualizer + STANAG 5516 Ed. 9 ID Extractor
----------------------------------------------------------------
Uses the user's original SIDC generator/decoder as the data source,
milsymbol-py for SVG rendering, and extracts STANAG 5516 Ed. 9 tactical IDs.

Link 16 teşhis kodundan SIDC üretme (ters dönüşüm) dahildir.

Kurulum:
  sudo apt install python3-tk libcairo2
  pip install -r requirements.txt

Çalıştırma:
  python3 visualizerGrk.py
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from collections import OrderedDict
from io import BytesIO
from pathlib import Path

from milstd2525e_sidc import MilStd2525EApp as BaseApp
from link16_ed9 import Link16Ed9Extractor

try:
    from milsymbol import Symbol
except Exception:
    Symbol = None

try:
    from PIL import Image, ImageTk
except Exception:
    Image = ImageTk = None

try:
    import cairosvg
except (ImportError, OSError, Exception):
    cairosvg = None


PREVIEW_PX = 450      # önizleme görüntüsü boyutu
RENDER_DELAY_MS = 80  # hızlı değişimlerde render'ı birleştirme süresi
CACHE_SIZE = 256      # SIDC başına tutulacak SVG/PNG sayısı


# =====================================================================
# GÖRSELLEŞTİRİCİ ARAYÜZ SINIFI
# =====================================================================
class MilStd2525EVisualizer(BaseApp):
    """Visual browser built on top of the supplied SIDC generator."""

    def __init__(self, root):
        self.symbol_photo = None
        self.render_after_id = None
        self._last_svg = None
        self._last_used_sidc = ""
        # SIDC -> (svg, kullanılan_sidc, png_bytes | None); LRU önbellek
        self._render_cache = OrderedDict()
        super().__init__(root)
        self.root.minsize(1150, 840)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        if self.render_after_id is not None:
            try:
                self.root.after_cancel(self.render_after_id)
            except Exception:
                pass
        self.root.destroy()

    def build_ui(self):
        self.root.title("MIL-STD-2525E Sembol Görselleştirici & STANAG 5516 Ed.9 Teşhis")
        self.root.geometry("1300x920")

        main = ttk.Frame(self.root, padding=10)
        main.pack(fill=tk.BOTH, expand=True)

        # ---------------- SOL PANEL: SIDC KONTROLLERİ ----------------
        left = ttk.Frame(main)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        fa = ttk.LabelFrame(left, text="SET A — Pozisyon 1–10", padding=7)
        fa.pack(fill=tk.X, pady=3)

        self.cb_ver = self.mk_cb(
            fa, "Poz 1-2 (Version):",
            self.versions, "13 - MIL-STD-2525E", 0
        )
        self.cb_ctx = self.mk_cb(
            fa, "Poz 3 (Context):",
            self.contexts, "0 - Reality", 1
        )
        self.cb_id = self.mk_cb(
            fa, "Poz 4 (Identity):",
            self.identities, "3 - Friend", 2
        )
        self.cb_ss = self.mk_cb(
            fa, "Poz 5-6 (Symbol Set):",
            self.symbol_sets, "01 - Air", 3
        )
        self.cb_ss.bind(
            "<<ComboboxSelected>>",
            lambda e: self.on_symset_change()
        )
        self.cb_st = self.mk_cb(
            fa, "Poz 7 (Status):",
            self.statuses, "0 - Present", 4
        )
        self.cb_hq = self.mk_cb(
            fa, "Poz 8 (HQ/TF/Dummy):",
            self.hq_tf, "0 - Unknown (No Statement)", 5
        )
        self.cb_amp = self.mk_cb(
            fa, "Poz 9-10 (Amplifier):",
            self.amplifiers, "00 - Unknown (No Statement)", 6
        )

        fb = ttk.LabelFrame(
            left,
            text="SET B — Pozisyon 11–20 & Set/Common Modifiers",
            padding=7
        )
        fb.pack(fill=tk.X, pady=3)

        ttk.Label(fb, text="Entity Arama:", width=34).grid(
            row=0, column=0, sticky=tk.W, pady=2
        )
        self.ent_q = ttk.Entry(fb, width=42)
        self.ent_q.grid(row=0, column=1, sticky=tk.W, padx=10, pady=2)
        self.ent_q.bind("<KeyRelease>", self.filter_ent)

        self.cb_ent = self.mk_cb(
            fb, "Poz 11-16 (Entity/Type/Subtype):", {}, "", 1
        )
        self.cb_s1 = self.mk_cb(
            fb, "Poz 17-18 (Set Sector 1 Mod):", {}, "", 2
        )
        self.cb_s2 = self.mk_cb(
            fb, "Poz 19-20 (Set Sector 2 Mod):", {}, "", 3
        )
        self.cb_c1 = self.mk_cb(
            fb, "Tablo A-IX (Common Sector 1):",
            self.common_s1,
            "000 - Yok (Set Özel Mod. Kullan)", 4
        )
        self.cb_c2 = self.mk_cb(
            fb, "Tablo A-X (Common Sector 2):",
            self.common_s2,
            "000 - Yok (Set Özel Mod. Kullan)", 5
        )

        fc = ttk.LabelFrame(left, text="SET C — Pozisyon 21–30", padding=7)
        fc.pack(fill=tk.X, pady=3)

        ttk.Label(
            fc, text="Poz 21-22 (Common Mod ID 1 & 2):", width=34
        ).grid(row=0, column=0, sticky=tk.W, pady=2)
        self.lbl_cid = ttk.Label(
            fc, text="00", font=("DejaVu Sans Mono", 10, "bold")
        )
        self.lbl_cid.grid(row=0, column=1, sticky=tk.W, padx=10, pady=2)

        self.cb_frm = self.mk_cb(
            fc, "Poz 23 (Frame Shape - A-LX):",
            self.frames, "0 - Unknown", 1
        )

        ttk.Label(fc, text="Poz 24-27 (Reserved):").grid(
            row=2, column=0, sticky=tk.W, pady=2
        )
        ttk.Label(fc, text="0000 (Sabit)").grid(
            row=2, column=1, sticky=tk.W, padx=10, pady=2
        )

        ttk.Label(fc, text="Poz 28-30 (Country Code):").grid(
            row=3, column=0, sticky=tk.W, pady=2
        )
        self.ent_cnt = ttk.Entry(fc, width=12)
        self.ent_cnt.insert(0, "000")
        self.ent_cnt.grid(row=3, column=1, sticky=tk.W, padx=10, pady=2)
        self.ent_cnt.bind("<KeyRelease>", lambda e: self.update_sidc())

        # SIDC / Decoder
        fo = ttk.LabelFrame(left, text="SIDC — 30 Hane", padding=8)
        fo.pack(fill=tk.X, pady=5)

        self.sidc_var = tk.StringVar()
        ttk.Entry(
            fo, textvariable=self.sidc_var,
            font=("DejaVu Sans Mono", 14, "bold"),
            justify="center", state="readonly"
        ).pack(fill=tk.X, pady=3)

        self.brk_var = tk.StringVar()
        ttk.Label(
            fo, textvariable=self.brk_var,
            font=("DejaVu Sans Mono", 9)
        ).pack(pady=2)

        row = ttk.Frame(fo)
        row.pack(fill=tk.X, pady=4)

        ttk.Button(
            row, text="Panoya Kopyala", command=self.copy_sidc
        ).pack(side=tk.LEFT, padx=3)
        ttk.Button(
            row, text="SVG Kaydet", command=self.save_svg
        ).pack(side=tk.LEFT, padx=3)
        ttk.Button(
            row, text="PNG Kaydet", command=self.save_png
        ).pack(side=tk.LEFT, padx=3)

        ttk.Label(row, text="  SIDC Çözümle:").pack(side=tk.LEFT)
        self.ent_dec = ttk.Entry(row, width=32, font=("DejaVu Sans Mono", 10))
        self.ent_dec.insert(0, "130310000012000000000200000000")
        self.ent_dec.pack(side=tk.LEFT, padx=4)
        ttk.Button(
            row, text="Çözümle", command=self.decode_sidc
        ).pack(side=tk.LEFT, padx=3)

        # Hızlı Sembol Tarama Listesi
        quick = ttk.LabelFrame(left, text="Hızlı Sembol Tarama", padding=7)
        quick.pack(fill=tk.BOTH, expand=True, pady=3)

        ttk.Label(
            quick,
            text="Aşağıdaki listeden Entity seçerek doğrudan görselleştirebilirsin."
        ).pack(anchor=tk.W)

        list_frame = ttk.Frame(quick)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.entity_list = tk.Listbox(
            list_frame, height=8, exportselection=False
        )
        scroll = ttk.Scrollbar(
            list_frame, orient=tk.VERTICAL,
            command=self.entity_list.yview
        )
        self.entity_list.configure(yscrollcommand=scroll.set)
        self.entity_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.entity_list.bind("<<ListboxSelect>>", self.on_entity_list_select)

        # ---------------- SAĞ PANEL: SEMBOL ÖNİZLEME & LINK 16 ID ----------------
        right = ttk.LabelFrame(main, text="2525E SEMBOL ÖNİZLEME", padding=10)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        self.preview_canvas = tk.Canvas(
            right, bg="#f4f4f4",
            highlightthickness=1,
            highlightbackground="#b0b0b0"
        )
        self.preview_canvas.pack(fill=tk.BOTH, expand=True)
        self.preview_canvas.bind("<Configure>", self._on_canvas_resize)

        # STANAG 5516 ED.9 TEŞHİS GÖSTERGE PANELİ (SIDC → Link16)
        l16_frame = ttk.LabelFrame(
            right, text="STANAG 5516 Ed.9 — Link 16 Teşhis Çıktısı (SIDC → Teşhis)", padding=8
        )
        l16_frame.pack(fill=tk.X, pady=(8, 4))

        top_l16 = ttk.Frame(l16_frame)
        top_l16.pack(fill=tk.X)

        ttk.Label(
            top_l16, text="Link 16 Teşhis Kodu:",
            font=("TkDefaultFont", 10, "bold")
        ).pack(side=tk.LEFT)

        self.l16_code_var = tk.StringVar(value="-----")
        ttk.Label(
            top_l16, textvariable=self.l16_code_var,
            font=("DejaVu Sans Mono", 16, "bold"),
            foreground="#0055aa"
        ).pack(side=tk.LEFT, padx=10)

        ttk.Button(
            top_l16, text="Kodu Kopyala",
            command=self.copy_l16_code
        ).pack(side=tk.RIGHT)

        self.l16_brk_var = tk.StringVar()
        ttk.Label(
            l16_frame, textvariable=self.l16_brk_var,
            font=("DejaVu Sans Mono", 9, "bold")
        ).pack(anchor=tk.W, pady=(2, 4))

        self.l16_det_var = tk.StringVar()
        ttk.Label(
            l16_frame, textvariable=self.l16_det_var,
            font=("DejaVu Sans Mono", 9),
            justify=tk.LEFT
        ).pack(anchor=tk.W)

        # ========== YENİ: Link 16 Teşhis → SIDC TERS DÖNÜŞÜM ==========
        rev_frame = ttk.LabelFrame(
            right, text="Link 16 Teşhis → SIDC (Ters Dönüşüm)", padding=8
        )
        rev_frame.pack(fill=tk.X, pady=(6, 4))

        rev_row = ttk.Frame(rev_frame)
        rev_row.pack(fill=tk.X)

        ttk.Label(rev_row, text="5 Karakter Teşhis:", width=18).pack(side=tk.LEFT)
        self.ent_l16_in = ttk.Entry(rev_row, width=10, font=("DejaVu Sans Mono", 12, "bold"))
        self.ent_l16_in.pack(side=tk.LEFT, padx=4)
        self.ent_l16_in.insert(0, "FFTCP")
        self.ent_l16_in.bind("<Return>", lambda e: self.reverse_l16_to_sidc())

        ttk.Button(
            rev_row, text="SIDC'ye Dönüştür",
            command=self.reverse_l16_to_sidc
        ).pack(side=tk.LEFT, padx=6)

        self.rev_status_var = tk.StringVar(value="Örnek: FFTCP, FBMBM, KFTIN, HSSPT …")
        ttk.Label(
            rev_frame, textvariable=self.rev_status_var,
            font=("TkDefaultFont", 9), foreground="#333"
        ).pack(anchor=tk.W, pady=(4, 0))

        # Sembol Render Durumu
        info = ttk.Frame(right)
        info.pack(fill=tk.X, pady=(6, 0))

        self.render_status = tk.StringVar(value="Sembol oluşturuluyor...")
        ttk.Label(
            info, textvariable=self.render_status,
            font=("TkDefaultFont", 9, "bold")
        ).pack(anchor=tk.W)

        self.meta_var = tk.StringVar()
        ttk.Label(
            info, textvariable=self.meta_var,
            justify=tk.LEFT
        ).pack(anchor=tk.W, pady=(3, 0))

    # ------------------------------------------------------------------
    # Pano / bildirim yardımcıları
    # ------------------------------------------------------------------
    def _notify(self, msg):
        """Kısa bilgi mesajını modal pencere açmadan durum satırında gösterir."""
        if hasattr(self, "render_status"):
            self.render_status.set(msg)

    def _copy(self, text, label):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self._notify(f"✓ {label} panoya kopyalandı: {text}")

    def copy_sidc(self):
        self._copy(self.sidc_var.get(), "SIDC")

    def copy_l16_code(self):
        self._copy(self.l16_code_var.get().strip(), "Link 16 teşhis kodu")

    def reverse_l16_to_sidc(self):
        """Link 16 5 karakterlik teşhis kodundan SIDC üret ve arayüzü güncelle."""
        code = self.ent_l16_in.get().strip().upper()
        result = Link16Ed9Extractor.reverse(code)

        if not result["success"]:
            self.rev_status_var.set(result["message"])
            messagebox.showwarning("Geçersiz Kod", result["message"])
            return

        suggested = result["suggested_sidc"]
        self.rev_status_var.set(f"✓ {code} → {suggested}\n{result['message']}")

        # Ana SIDC alanına yaz ve decode et (sol paneldeki alanlar ve sembol güncellenir)
        self.ent_dec.delete(0, tk.END)
        self.ent_dec.insert(0, suggested)
        self.decode_sidc()

    def _on_canvas_resize(self, event):
        if self.preview_canvas.find_withtag("center_item"):
            self.preview_canvas.coords(
                "center_item", event.width // 2, event.height // 2
            )

    # ------------------------------------------------------------------
    # Entity listesi
    # ------------------------------------------------------------------
    def _fill_entity_list(self, keys=None):
        if not hasattr(self, "entity_list"):
            return
        self.entity_list.delete(0, tk.END)
        self.entity_list.insert(tk.END, *(self.cur_e.keys() if keys is None else keys))

    def on_symset_change(self, init_mode=False):
        super().on_symset_change(init_mode=init_mode)
        self._fill_entity_list()

    def decode_sidc(self):
        super().decode_sidc()
        # Çözümleme tabloda olmayan bir entity eklemiş olabilir; listeyi yenile
        self._fill_entity_list()

    def filter_ent(self, event=None):
        super().filter_ent(event)
        # Listeyi de aramaya göre daralt; boş aramada tam liste
        q = self.ent_q.get().strip().lower()
        self._fill_entity_list([k for k in self.cur_e if q in k.lower()] if q else None)
        if q and self.entity_list.size():
            self.entity_list.selection_set(0)
            self.entity_list.see(0)

    def on_entity_list_select(self, event=None):
        sel = self.entity_list.curselection()
        if not sel:
            return
        key = self.entity_list.get(sel[0])
        self.cb_ent.set(key)
        self.update_sidc()

    def update_sidc(self):
        super().update_sidc()
        if not hasattr(self, "preview_canvas"):
            return
        if self.render_after_id is not None:
            try:
                self.root.after_cancel(self.render_after_id)
            except Exception:
                pass
        self.render_after_id = self.root.after(RENDER_DELAY_MS, self.render_symbol)

    # ------------------------------------------------------------------
    # Render (SVG/PNG önbellekli)
    # ------------------------------------------------------------------
    @staticmethod
    def _extract_svg_from_symbol(sym):
        if hasattr(sym, "as_svg"):
            return sym.as_svg()
        if hasattr(sym, "asSVG"):
            return sym.asSVG()
        raise RuntimeError("milsymbol Symbol nesnesinde SVG metodu bulunamadı.")

    def _cache_get(self, sidc):
        entry = self._render_cache.get(sidc)
        if entry is not None:
            self._render_cache.move_to_end(sidc)
        return entry

    def _cache_put(self, sidc, entry):
        self._render_cache[sidc] = entry
        self._render_cache.move_to_end(sidc)
        while len(self._render_cache) > CACHE_SIZE:
            self._render_cache.popitem(last=False)

    def _build_svg(self, raw_sidc):
        """(svg, kullanılan_sidc) döndürür; 2525E başarısızsa 2525D'ye düşer."""
        if Symbol is None:
            raise RuntimeError(
                "milsymbol bulunamadı. Paketleri kurun:\n"
                "pip install -r requirements.txt"
            )

        candidates = [raw_sidc]
        if len(raw_sidc) >= 20:
            candidates.append(raw_sidc[:20])
            candidates.append("10" + raw_sidc[2:20])

        last_err = None
        for candidate in candidates:
            try:
                sym = Symbol(candidate, size=180)
                if hasattr(sym, "is_valid") and not sym.is_valid():
                    continue
                svg = self._extract_svg_from_symbol(sym)
                if svg and "<svg" in svg:
                    return svg, candidate
            except Exception as exc:
                last_err = exc

        try:
            sym = Symbol(candidates[-1], size=180)
            return self._extract_svg_from_symbol(sym), candidates[-1]
        except Exception as exc:
            raise ValueError(
                f"Bu SIDC için sembol üretilemedi ({last_err or exc})."
            )

    def _get_svg(self):
        raw_sidc = self.sidc_var.get().strip()
        entry = self._cache_get(raw_sidc)
        if entry is None:
            svg, used = self._build_svg(raw_sidc)
            entry = [svg, used, None]
            self._cache_put(raw_sidc, entry)
        self._last_svg, self._last_used_sidc = entry[0], entry[1]
        return entry[0]

    def _get_preview_png(self):
        """Önizleme PNG'sini (önbellekten veya yeni) döndürür."""
        svg = self._get_svg()
        entry = self._render_cache[self.sidc_var.get().strip()]
        if entry[2] is None:
            entry[2] = cairosvg.svg2png(
                bytestring=svg.encode("utf-8"),
                output_width=PREVIEW_PX,
                output_height=PREVIEW_PX,
            )
        return entry[2]

    def render_symbol(self):
        self.render_after_id = None
        if not hasattr(self, "preview_canvas"):
            return

        full_sidc = self.sidc_var.get().strip()

        # HER SIDC DEĞİŞİMİNDE LINK 16 KODUNU HESAPLA VE GÖSTER
        if hasattr(self, "l16_code_var"):
            l16_res = Link16Ed9Extractor.extract(full_sidc)
            self.l16_code_var.set(l16_res["code_5char"])
            self.l16_brk_var.set(l16_res["breakdown"])
            self.l16_det_var.set(l16_res["details"])

        w = max(self.preview_canvas.winfo_width(), 500)
        h = max(self.preview_canvas.winfo_height(), 420)

        try:
            if cairosvg is None or Image is None or ImageTk is None:
                self._get_svg()
                self.render_status.set(
                    "SVG üretildi. Görsel önizleme için cairosvg + pillow kurulmalı."
                )
                self.preview_canvas.delete("all")
                self.preview_canvas.create_text(
                    w // 2, h // 2,
                    text="SVG hazır (Önizleme için cairosvg + Pillow gerekli)\n\n"
                         "pip install cairosvg Pillow",
                    justify=tk.CENTER,
                    font=("TkDefaultFont", 12),
                    tags="center_item"
                )
                return

            png = self._get_preview_png()
            image = Image.open(BytesIO(png)).convert("RGBA")
            self.symbol_photo = ImageTk.PhotoImage(image)

            self.preview_canvas.delete("all")
            self.preview_canvas.create_image(
                w // 2, h // 2,
                image=self.symbol_photo,
                anchor=tk.CENTER,
                tags="center_item"
            )

            mode_note = (
                "2525E (30 Hane)"
                if self._last_used_sidc == full_sidc
                else f"2525D Uyumluluk ({self._last_used_sidc})"
            )
            self.render_status.set(f"Renderer: milsymbol [{mode_note}]")
            self.meta_var.set(
                f"Symbol Set: {self.cb_ss.get()}  |  Entity: {self.cb_ent.get()}"
            )

        except Exception as exc:
            self.preview_canvas.delete("all")
            self.preview_canvas.create_text(
                w // 2, h // 2,
                text=f"Sembol render edilemedi.\n\n{exc}",
                justify=tk.CENTER,
                font=("TkDefaultFont", 11),
                tags="center_item"
            )
            self.render_status.set("Render hatası (Link 16 teşhisi yukarıda hesaplandı)")
            self.meta_var.set("")

    # ------------------------------------------------------------------
    # Dışa aktarma
    # ------------------------------------------------------------------
    def _default_filename(self, ext):
        return f"{self.sidc_var.get().strip()}_{self.l16_code_var.get()}.{ext}"

    def save_svg(self):
        try:
            svg = self._get_svg()
        except Exception as exc:
            messagebox.showerror("SVG Hatası", str(exc))
            return

        path = filedialog.asksaveasfilename(
            title="2525E SVG Kaydet",
            defaultextension=".svg",
            initialfile=self._default_filename("svg"),
            filetypes=[("SVG", "*.svg"), ("All files", "*.*")]
        )
        if not path:
            return

        try:
            Path(path).write_text(svg, encoding="utf-8")
        except OSError as exc:
            messagebox.showerror("SVG Hatası", str(exc))
            return
        self._notify(f"✓ SVG kaydedildi: {path}")

    def save_png(self):
        if cairosvg is None:
            messagebox.showerror(
                "Eksik paket",
                "PNG dışa aktarmak için cairosvg gerekli.\n\n"
                "pip install cairosvg"
            )
            return

        try:
            svg = self._get_svg()
            path = filedialog.asksaveasfilename(
                title="2525E PNG Kaydet",
                defaultextension=".png",
                initialfile=self._default_filename("png"),
                filetypes=[("PNG", "*.png"), ("All files", "*.*")]
            )
            if not path:
                return

            cairosvg.svg2png(
                bytestring=svg.encode("utf-8"),
                write_to=path,
                output_width=1000,
                output_height=1000
            )
            self._notify(f"✓ PNG kaydedildi: {path}")
        except Exception as exc:
            messagebox.showerror("PNG Hatası", str(exc))


def main():
    root = tk.Tk()

    if Symbol is None:
        root.after(
            300,
            lambda: messagebox.showwarning(
                "milsymbol eksik",
                "2525E sembollerini çizmek için önce:\n\n"
                "pip install -r requirements.txt\n\n"
                "komutunu çalıştır."
            )
        )

    MilStd2525EVisualizer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
