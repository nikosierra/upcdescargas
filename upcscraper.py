import os
import time
import requests
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

# Configuración de Selenium
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Crear carpeta para guardar imágenes si no existe
if not os.path.exists("imagenes"):
    os.makedirs("imagenes")


@app.route("/descargar", methods=["POST"])
def descargar_imagen():
    data = request.get_json()
    codigos = data.get("codigos", [])

    if not codigos:
        return jsonify({"error": "No se proporcionaron códigos UPC"}), 400

    resultados = []

    for codigo in codigos:
        print(f"🔍 Buscando imagen para: {codigo}")
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
                resultados.append({"codigo": codigo, "imagen": img_name})
                print(f"✅ Imagen descargada: {img_name}")
            except Exception as e:
                resultados.append({"codigo": codigo, "error": str(e)})
                print(f"❌ Error al descargar imagen para {codigo}: {e}")
        else:
            resultados.append({"codigo": codigo, "error": "No se encontró imagen"})
            print(f"❌ No se encontró imagen para {codigo}")

    return jsonify({"resultados": resultados})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
