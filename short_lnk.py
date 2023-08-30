import random
import time
import urllib.parse
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from GLOBAL_CONFIG import CONFIG
from logs import capture_error

# para obtener el path absoluta del proyecto
path = Path().resolve()

chromedriver = str(path) + '\chromedriver.exe'


def open_browser():
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' \
                 '(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.51'
    PATH_CHROMEDRIVER_WIN = chromedriver

    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument("--window-size=1080,720")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument("--disable-extensions")

    """
    False: No mostrar interfaz gráfica.
    True: mostrar interfaz gráfica.
    """
    if not CONFIG.SHOW_GRAPHICAL_INTERFACE:
        options.add_argument("--start-maximized")
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')

    # Desactiva la salida de la consola
    options.add_argument('--log-level=3')
    service = Service(executable_path=PATH_CHROMEDRIVER_WIN)
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(CONFIG.URL_lnk_login)

    # Definir un tiempo de espera máximo
    wait = WebDriverWait(driver, 10)  # Espera hasta 10 segundos
    email = wait.until(EC.visibility_of_element_located((By.ID, 'email')))
    email.send_keys(CONFIG.USER_EMAIL)
    pwd = wait.until(EC.visibility_of_element_located((By.ID, 'password')))
    pwd.send_keys(CONFIG.USER_PASS)
    btn_entry = wait.until(EC.visibility_of_element_located((By.ID, 'submit')))
    btn_entry.submit()

    # Abrir página donde se va a cortar la url
    driver.get(CONFIG.URL_lnk_shorturl)

    # Ejecutar Script JS para insertar un nuevo elemento
    # donde se va a colocar los valores para obtener los datos (url)
    driver.execute_script(script="""
        let elemento = document.createElement('span');
        elemento.id = 'newLinkShort';
        elemento.setAttribute('data-link', '');
        elemento.textContent = 'Aquí saldrá los enlaces';
        document.querySelector('.container').append(elemento);
    """)

    # Esperar 3 segundo para comenzar a realizar la operación
    time.sleep(3)

    try:
        with open(CONFIG.PATH_URLS_START) as urls:
            for url in urls.readlines():
                url = str(url).strip()
                if url != "":

                    custom_random_url = ''
                    custom_random_url_keyword = 'abcdefghijklmnopqrstuvwxyz0123456789'
                    # el digito 5, es para cambiar el rango de longitud de caracteres a seleccionar
                    for letter in range(5):
                        custom_random_url += random.choice(custom_random_url_keyword)

                    # Titulo de todos los enlaces
                    title = f"{CONFIG.TITLE_lnk_URL}"
                    # link el cual se va a convertir
                    link = f'{url}'

                    # Primera parte del script
                    script1 = """
                    function createlnkLink() {
                        formHideErrors($('#SH_add'))
                        let data = {};
                    """
                    # segunda parte del Script
                    # aquí se introducen los datos que se van a cambiar en
                    # cada petición realizada.
                    datos = f"""
                        data['title'] = '{title}';
                        data['link'] = '{link}';
                        data['handle'] = '{CONFIG.CUSTOM_URL}_{custom_random_url}';
                        data['include_username'] = 'false';
                    """
                    # tercera parte del Script
                    # aquí se agregó un fragmento de código para que
                    # cuando se reciba la petición se cambie el contenido y
                    # el atrubuto del elemento a modificar
                    script2 = """
                        data['ACTION'] = "ST_add";
                        data.token = CSFR_TOKEN;
                        $.ajax({
                            type: 'POST',
                            url: "/api/",
                            data: data,
                            dataType: "json",
                            success: function (res) {
                            stopLoadingButton()
                            reEnableButton()
                            if (res.status) {
                                let html = res['info']['html']
                                let strStart = html.substr(html.indexOf('value=')+7)
                                let newLink = html.substr(html.indexOf('value=')+7, strStart.indexOf('"'))
                                document.querySelector('#newLinkShort').setAttribute('data-link', newLink);
                                document.querySelector('#newLinkShort').textContent = newLink;
                                $('#NL_LinksContainer').prepend(res.info.html);
                                $('#LN_Link_'+res.info.id).slideDown('slow')
                                LN_ResetMainForm()
                                footerPositionUpdate()
                            } else {
                                formShowErrors($('#SH_add'), res.errors[0])
                            }
                        }
                    });
                    }
                    createlnkLink()
                    """

                    script = script1 + datos + script2

                    # Ejecutar el script para enviar la petición
                    # de creación de enlace
                    driver.execute_script(script=script)

                    new_url = wait.until(EC.visibility_of_element_located((By.ID, 'newLinkShort')))
                    time.sleep(0.5)

                    try:
                        enlace_listo = new_url.get_attribute('data-link')
                        with open(CONFIG.PATH_URLS_lnk_END, 'a') as urls_end:
                            print('Enlace acortado: ', enlace_listo)
                            urls_end.write(enlace_listo + '\n')

                    except Exception as error:
                        capture_error(str(error), 'funcion short-lnk - get_attribute')

    except Exception as error:
        capture_error(str(error), 'funcion short-lnk')


open_browser()
print("Trabajo finalizado.")
