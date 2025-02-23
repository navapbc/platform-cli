def str_to_bool(val: str) -> bool:
    """Convert a string representation of truth to `True` or `False`.

    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.

    Raises ValueError if 'val' is anything else.

    Similar to the old `distutils.util.strtobool`.
    """
    val = val.lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        return True
    elif val in ("n", "no", "f", "false", "off", "0"):
        return False
    else:
        raise ValueError(f"invalid truth value '{val}'")
