import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import barcode
from barcode.writer import ImageWriter
import tkinter as tk
from tkinter import font as tkFont

# Läs in CSV-filen (alltid produktdatabas.csv)
file_path = 'produktdatabas.csv'
data = pd.read_csv(file_path)

# Fokusera på de relevanta kolumnerna
relevant_columns = ['Variant SKU', 'Title', 'Option1 Value', 'Vendor']
filtered_data = data.loc[:, relevant_columns]

# Fyll i tomma titlar med Option1 Value för att skapa fullständiga produkttitlar
filtered_data.loc[:, 'Full Title'] = filtered_data['Title'].fillna('') + ' ' + filtered_data['Option1 Value'].fillna('')
filtered_data.loc[:, 'Full Title'] = filtered_data['Full Title'].str.strip()  # Rensa bort onödiga blanksteg

# Funktion för att skapa etikett baserat på data
def skapa_etikett(sku, ordernummer, antal):
    # Hitta produkten baserat på SKU
    produkt = filtered_data[filtered_data['Variant SKU'] == sku]

    if produkt.empty:
        print(f"SKU {sku} hittades inte i databasen.")
        return
    
    # Hämta relevant data
    title = produkt['Full Title'].values[0]
    vendor = produkt['Vendor'].values[0] if pd.notna(produkt['Vendor'].values[0]) else "-"

    # Etikettens dimensioner (bredd x höjd)
    bredd, höjd = 732, 342  # Öka bredden för att rymma streckkoden

    # Skapa en ny bild med vit bakgrund
    bild = Image.new('RGB', (bredd, höjd), 'white')
    ritare = ImageDraw.Draw(bild)

    # Ladda font
    try:
        bold_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 40)
        regular_font = ImageFont.truetype("DejaVuSans.ttf", 40)
        small_font = ImageFont.truetype("DejaVuSans.ttf", 30)
    except IOError:
        font = ImageFont.load_default()  # Standardfont om Arial inte finns

    # Lägg till logotyp (alltid logo.png)
    logopath = "logo.jpg"
    logotyp = Image.open(logopath)
    logotyp = logotyp.resize((int(2.5*100), int(2.5*36)), Image.Resampling.LANCZOS)
    bild.paste(logotyp, (470, 10), logotyp if logotyp.mode == 'RGBA' else None)

    title = title.replace("   Default Title", "")
    title = title.replace("Default Title", "")
    text_title = title
    textlengd = 40
    if len(title) > textlengd:
        
        if len(title) > textlengd*2:
            title = title[:textlengd*2] + '...'
        short_title = title[:textlengd] + "-\n" + title[textlengd:]
        text_title = short_title
        
    # Skriva ut SKU, Produkttitel, Vendor och Antal med bold för etiketterna
    ritare.text((20, 10), "ORDER\nANTAL\nTILLV.", fill="black", font=bold_font)
    ritare.text((200, 10), ': '+ordernummer+'\n'+': '+f'{antal}'+'\n'+': '+vendor, fill="black", font=regular_font)
    ritare.text((20, 135), text_title, fill="black", font=small_font)
    ritare.text((110, 290), 'SKU: ' + sku, fill="black", font=regular_font)

    # Generera CODE128-streckkod och spara som tmp_barcode
    streckkod_writer = ImageWriter()
    barcode.base.Barcode.default_writer_options['write_text'] = False
    streckkod_writer.set_options({
        'module_width': 0.4, 
        'module_height': 20, 
        'quiet_zone': 0
    })
    streckkod = barcode.get('code128', sku, writer=streckkod_writer)
    streckkod_filnamn = 'tmp_barcode'  # Spara som tmp_barcode utan .png
    streckkod.save(streckkod_filnamn)

    # Lägg till streckkoden på etiketten
    streckkod_bild = Image.open(f'{streckkod_filnamn}.png')  # Öppna filen med .png tillagd
    bild.paste(streckkod_bild.resize((732, 50)), (0, 245))  # Anpassa bredden till 700 pixlar och centrera med 16 pixlar marginal

    # Spara etiketten som bildfil
    bildfilnamn = 'label.png'
    bild.save(bildfilnamn)
    bild.show()
    print(f"Etikett skapad: {bildfilnamn}")

# Tkinter GUI
def start_gui():
    def skapa_etikett_gui():
        sku = sku_entry.get()
        ordernummer = ordernummer_entry.get()
        antal = antal_entry.get()
        skapa_etikett(sku, ordernummer, antal)

    root = tk.Tk()
    root.title("Skapa Etikett")

    # Definiera en större font
    large_font = tkFont.Font(size=20)  # Dubbelt så stor som standard

    # SKU
    tk.Label(root, text="SKU:", font=large_font).grid(row=0)
    sku_entry = tk.Entry(root, font=large_font)
    sku_entry.grid(row=0, column=1)

    # Ordernummer
    tk.Label(root, text="Ordernummer:", font=large_font).grid(row=1)
    ordernummer_entry = tk.Entry(root, font=large_font)
    ordernummer_entry.grid(row=1, column=1)

    # Antal
    tk.Label(root, text="Antal:", font=large_font).grid(row=2)
    antal_entry = tk.Entry(root, font=large_font)
    antal_entry.grid(row=2, column=1)

    # Skapa Etikett-knapp
    tk.Button(root, text="Skapa Etikett", font=large_font, command=skapa_etikett_gui).grid(row=3, column=1)

    root.mainloop()

# Starta GUI
start_gui()

