import logging
from GLOBAL_CONFIG import CONFIG

# Create and configure logger
logging.basicConfig(filename=CONFIG.PATH_FILE_LOG,
                    format='%(asctime)s %(message)s',
                    filemode='a')

# Creación del objeto
logger = logging.getLogger()

# Configurar el nivel de registro
logger.setLevel(logging.ERROR)


# Cacturar el error
def capture_error(error: str, function: str):
    fun = str(function)
    logger.error("------"+fun+"------" + error)
