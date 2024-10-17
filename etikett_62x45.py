import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import barcode
from barcode.writer import ImageWriter

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
    bredd, höjd = 732, 531  # Öka bredden för att rymma streckkoden

    # Skapa en ny bild med vit bakgrund
    bild = Image.new('RGB', (bredd, höjd), 'white')
    ritare = ImageDraw.Draw(bild)

    # Ladda font
    try:
        bold_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 40)
        regular_font = ImageFont.truetype("DejaVuSans.ttf", 40)
        small_font = ImageFont.truetype("DejaVuSans.ttf", 50)
    except IOError:
        font = ImageFont.load_default()  # Standardfont om Arial inte finns

    # Lägg till logotyp (alltid logo.png)
    logopath = "logo.jpg"
    logotyp = Image.open(logopath)
    logotyp = logotyp.resize((int(2.5*100), int(2.5*36)), Image.Resampling.LANCZOS)
    bild.paste(logotyp, (470, 10), logotyp if logotyp.mode == 'RGBA' else None)
    print(title)
    title = title.replace("   Default Title", "")
    title = title.replace("Default Title", "")
    text_title = title
    
    if len(title) > 20:
    # Dela upp titeln i två delar, de första 20 tecknen och resten
        textlengd = 24
        if len(title) > textlengd*2:
            title = title[:textlengd*2] + '...'
        short_title = title[:textlengd] + "-\n" + title[textlengd:]
        text_title = short_title
        
        
    # Skriva ut SKU, Produkttitel, Vendor och Antal med bold för etiketterna
    ritare.text((20, 10), "ORDER\nANTAL\nTILLV.", fill="black", font=bold_font)
    ritare.text((200, 10), ': '+ordernummer+'\n'+': '+f'{antal}st'+'\n'+': '+vendor, fill="black", font=regular_font)
    ritare.text((20,135),text_title,fill='black',font=small_font)
    #ritare.text((20, 400), "SKU:", fill="black", font=bold_font)
    ritare.text((110, 450), 'SKU: ' +sku, fill="black", font=regular_font)

    #ritare.text((120, 100), title, fill="black", font=regular_font)

    #ritare.text((200, 140), vendor, fill="black", font=regular_font)

    #ritare.text((120, 180), f"{antal}st", fill="black", font=regular_font)

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
    bild.paste(streckkod_bild.resize((732, 75)), (0, 380))  # Anpassa bredden till 700 pixlar och centrera med 16 pixlar marginal

    # Spara etiketten som bildfil
    bildfilnamn = 'label.png'
    bild.save(bildfilnamn)
    bild.show()
    print(f"Etikett skapad: {bildfilnamn}")

# Mata in SKU, ordernummer och antal manuellt
while True:
    if False:
        sku = input("Ange SKU (eller skriv 'exit' för att avsluta): ")
        if sku.lower() == 'exit':
            break
        ordernummer = input("Ange ordernummer: ")
        antal = input("Ange antal: ")
    else:
        sku = "JAMICON-47UF250V"
        ordernummer = "#1552"
        antal = "2"
        input('Enter för fortsätt')

    skapa_etikett(sku, ordernummer, antal)
