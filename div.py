import logging

def log_setup():
    logging.basicConfig(  
        filename='dashboard_debug.log',
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Add a handler to print logs to console as well
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logging.getLogger('').addHandler(console)
    logging.debug("Logging initialized")

def log(*args):

    message = " ".join(str(arg) for arg in args)
    logging.debug(message)