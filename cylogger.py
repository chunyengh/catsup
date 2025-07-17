import logging

cylogger = logging.getLogger(__name__)
logging.basicConfig(filename='cyc.log', level=logging.DEBUG)
logging.info("start")