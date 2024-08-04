import logging
import colorlog

def setup_logger(name):
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        "%(blue)s%(asctime)s%(reset)s %(log_color)s%(levelname)-8s - %(message_log_color)s%(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'bg_red,white',
        },
        secondary_log_colors={
            'message': {
                'DEBUG':    'blue',
                'INFO':     'white',
                'WARNING':  'white',
                'ERROR':    'red',
                'CRITICAL': 'bg_red,white',
            },
        },
        style='%'
    ))

    logger = colorlog.getLogger(name)
    
    for h in logger.handlers:
        logger.removeHandler(h)

    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False 

    uvicorn_error_logger = logging.getLogger("uvicorn.access")
    for h in uvicorn_error_logger.handlers:
        uvicorn_error_logger.removeHandler(h)
    uvicorn_error_logger.addHandler(handler)



    return logger

def log_messages(logger):
    try:
        logger.debug("A debug message")
        logger.info("An info message")
        logger.warning("A warning message")
        logger.error("An error message")
        logger.critical("A critical message")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

def main():
    logger = setup_logger('example')
    log_messages(logger)

if __name__ == "__main__":
    main()