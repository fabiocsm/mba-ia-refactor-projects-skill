from datetime import datetime, timezone


def utc_now():
    """UTC atual sem tzinfo, compatível com colunas DateTime sem fuso."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
