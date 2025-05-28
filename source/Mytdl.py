import tkinter as tk
from tkcalendar import DateEntry
from datetime import datetime
import os
from playsound import playsound

DOSYA_ADI = "mytodo.txt"

pencere = tk.Tk()
pencere.title("To-Do List (Developer by Alperen Kaymak)")
pencere.geometry("400x550")
pencere.config(bg="#fff9c4")

FONT_GOREV = ("Segoe UI", 11)
FONT_BUTON = ("Segoe UI", 10, "bold")
FONT_BASLIK = ("Segoe UI", 13, "bold")

gorevler = []
gorev_vars = []
cb_widgets = []

frame_giris = tk.Frame(pencere, bg="#fff9c4")
frame_giris.pack(pady=10)

entry_gorev = tk.Entry(frame_giris, width=25, font=FONT_GOREV)
entry_gorev.grid(row=0, column=0, padx=5)

date_giris = DateEntry(frame_giris, date_pattern="dd.mm.yyyy", font=FONT_GOREV, width=10)
date_giris.grid(row=0, column=1, padx=5)

entry_saat = tk.Entry(frame_giris, width=5, font=FONT_GOREV)
entry_saat.insert(0, "12:00")
entry_saat.grid(row=0, column=2, padx=5)

etiket_baslik = tk.Label(pencere, text="📒 Görev Listesi", font=FONT_BASLIK, fg="black", bg="#fff9c4")
etiket_baslik.pack()

frame_gorevler = tk.Frame(pencere, bg="#fff9c4")
frame_gorevler.pack(pady=5, fill=tk.BOTH, expand=True)

canvas = tk.Canvas(frame_gorevler, bg="#fff9c4", highlightthickness=0)
scrollbar_y = tk.Scrollbar(frame_gorevler, orient="vertical", command=canvas.yview)
scrollbar_x = tk.Scrollbar(frame_gorevler, orient="horizontal", command=canvas.xview)

canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
scrollable_frame = tk.Frame(canvas, bg="#fff9c4")

def draw_lines(event=None):
    canvas.delete("lines")
    height = canvas.winfo_height()
    line_spacing = 28
    for i in range(0, height, line_spacing):
        canvas.create_line(0, i, canvas.winfo_width(), i, fill="#ccddee", tags="lines")

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.bind("<Configure>", draw_lines)
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.pack(side="left", fill="both", expand=True)
scrollbar_y.pack(side="right", fill="y")
scrollbar_x.pack(side="bottom", fill="x")


def gorev_stil_guncelle(cb, var):
    if var.get():
        cb.config(fg="gray", font=(FONT_GOREV[0], FONT_GOREV[1], "overstrike"))
    else:
        cb.config(fg="black", font=FONT_GOREV)

def gorev_ekle(metin=None, tamamlandi=False):
    if metin is None:
        text_input = entry_gorev.get().strip()
        tarih = date_giris.get()
        saat = entry_saat.get().strip()
        if text_input == "":
            return
        metin = f"{text_input} [{tarih} {saat}]"
        entry_gorev.delete(0, tk.END)
    

    var = tk.BooleanVar(value=tamamlandi)
    gorev_vars.append(var)
    gorevler.append(metin)

    cb = tk.Checkbutton(scrollable_frame, text=metin, variable=var,
                        onvalue=True, offvalue=False,
                        command=lambda: [gorevleri_kaydet(), gorev_stil_guncelle(cb, var)],
                        font=FONT_GOREV, bg="#fff9c4", activebackground="#f6f09f",
                        anchor="w", padx=10, fg="black")
    cb.pack(fill="x", pady=3)
    cb_widgets.append(cb)
    gorev_stil_guncelle(cb, var)

    
    cb.bind("<Button-1>", drag_start)
    cb.bind("<B1-Motion>", drag_motion)
    cb.bind("<ButtonRelease-1>", drag_stop)


drag_data = {"widget": None, "y": 0, "index": None}

def drag_start(event):
    widget = event.widget
    drag_data["widget"] = widget
    drag_data["y"] = event.y_root
    drag_data["index"] = cb_widgets.index(widget)

def drag_motion(event):
    widget = drag_data["widget"]
    if widget is None:
        return
    dy = event.y_root - drag_data["y"]
    widget.place_configure(y=widget.winfo_y() + dy)
    drag_data["y"] = event.y_root

def drag_stop(event):
    widget = drag_data["widget"]
    if widget is None:
        return

    
    y = event.y_root - scrollable_frame.winfo_rooty()
    new_index = y // (widget.winfo_height() + 6)  

    old_index = drag_data["index"]
    new_index = max(0, min(new_index, len(cb_widgets)-1))

    if new_index != old_index:
       
        cb_widgets.insert(new_index, cb_widgets.pop(old_index))
        gorev_vars.insert(new_index, gorev_vars.pop(old_index))
        gorevler.insert(new_index, gorevler.pop(old_index))

        for w in cb_widgets:
            w.pack_forget()
        for w in cb_widgets:
            w.pack(fill="x", pady=3)

        gorevleri_kaydet()

    drag_data["widget"] = None
    drag_data["index"] = None

def gorevleri_yukle():
    if os.path.exists(DOSYA_ADI):
        with open(DOSYA_ADI, "r", encoding="utf-8") as dosya:
            for satir in dosya:
                tamamlandi = False
                metin = satir.strip()
                if metin.startswith("✓ "):
                    tamamlandi = True
                    metin = metin[2:]
                gorev_ekle(metin, tamamlandi)

def gorevleri_kaydet():
    with open(DOSYA_ADI, "w", encoding="utf-8") as dosya:
        for var, metin in zip(gorev_vars, gorevler):
            satir = metin
            if var.get():
                satir = "✓ " + satir
            dosya.write(satir + "\n")

def gorev_sil():
    silinecek_indeksler = [i for i, var in enumerate(gorev_vars) if var.get()]
    if not silinecek_indeksler:
        return
    for i in reversed(silinecek_indeksler):
        gorev_vars.pop(i)
        gorevler.pop(i)
        cb_widgets[i].destroy()
        cb_widgets.pop(i)
    gorevleri_kaydet()

frame_butonlar = tk.Frame(pencere, bg="#fff9c4")
frame_butonlar.pack(pady=10)

btn_ekle = tk.Button(frame_butonlar, text="Görev Ekle", command=gorev_ekle,
                     font=FONT_BUTON, bg="#4caf50", fg="white", activebackground="#45a049", width=12)
btn_ekle.pack(side="left", padx=5)

btn_sil = tk.Button(frame_butonlar, text="Seçili Görevleri Sil", command=gorev_sil,
                    font=FONT_BUTON, bg="#f44336", fg="white", activebackground="#d32f2f", width=16)
btn_sil.pack(side="left", padx=5)

gorevleri_yukle()

pencere.protocol("WM_DELETE_WINDOW", lambda: [gorevleri_kaydet(), pencere.destroy()])
pencere.mainloop()
