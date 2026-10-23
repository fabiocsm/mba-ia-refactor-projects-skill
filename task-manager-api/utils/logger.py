import logging


def configure_logging(level='INFO'):
    resolved_level = getattr(logging, str(level).upper(), logging.INFO)
    logging.basicConfig(level=resolved_level, format='%(asctime)s %(levelname)s %(name)s %(message)s')
