import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import streamlit as st

# Crear carpeta para guardar imágenes
if not os.path.exists("imagenes"):
    os.makedirs("imagenes")

# Configurar Selenium
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

def descargar_imagen(codigo):
    url = f"https://go-upc.com/search?q={codigo}"
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    img_tag = soup.find("img", {"src": True})

    if img_tag and "amazonaws" in img_tag["src"]:
        img_url = img_tag["src"]
        img_name = f"imagenes/{codigo}.jpg"
        try:
            img_data = requests.get(img_url).content
            with open(img_name, "wb") as img_file:
                img_file.write(img_data)
            return f"✅ Imagen descargada: {img_name}"
        except Exception as e:
            return f"❌ Error al descargar imagen para: {codigo} ({e})"
    else:
        return f"❌ No se encontró imagen para: {codigo}"

st.title("Descargador de Imágenes por Código")
codigos_input = st.text_area("Introduce los códigos (uno por línea)")

if st.button("Descargar Imágenes"):
    codigos = codigos_input.strip().split("\n")
    st.write(f"Total de códigos encontrados: {len(codigos)}")

    for codigo in codigos:
        if codigo.strip():
            resultado = descargar_imagen(codigo.strip())
            st.write(resultado)

    st.success("Proceso terminado")

# Cerrar navegador al finalizar
driver.quit()
