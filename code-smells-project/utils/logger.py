import logging

_logger = logging.getLogger("loja")


def configure_logging(level=logging.INFO):
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(message)s")


def info(message):
    _logger.info(message)


def error(message):
    _logger.error(message)
