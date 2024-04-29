import sys
import os
import base64
import binascii

from vantage6.common.globals import STRING_ENCODING, ENV_VAR_EQUALS_REPLACEMENT
from vantage6.algorithm.tools.exceptions import EnvironmentVariableError


def info(msg: str) -> None:
    """
    Print an info message to stdout.

    Parameters
    ----------
    msg : str
        Message to be printed
    """
    sys.stdout.write(f"info > {msg}\n")


def warn(msg: str) -> None:
    """
    Print a warning message to stdout.

    Parameters
    ----------
    msg : str
        Warning message to be printed
    """
    sys.stdout.write(f"warn > {msg}\n")


def error(msg: str) -> None:
    """
    Print an error message to stdout.

    Parameters
    ----------
    msg : str
        Error message to be printed
    """
    sys.stdout.write(f"error > {msg}\n")


def get_env_var(
    var_name: str,
    default: str | None = None,
    as_type="str",
    only_positive: bool = False,
) -> str:
    """
    Get the value of an environment variable. Environment variables are encoded
    by the node so they need to be decoded here.

    Note that this decoding follows the reverse of the encoding in the node:
    first replace '=' back and then decode the base32 string.

    Parameters
    ----------
    var_name : str
        Name of the environment variable
    default : str | None
        Default value to return if the environment variable is not found
    as_type : str
        Type to convert the environment variable to. Default is 'str', other options
        are 'bool' and 'int'.
    only_positive : bool
        If True, the environment variable must be a positive. Only relevant if as_type
        is 'int'.

    Returns
    -------
    var_value : str | None
        Value of the environment variable, or default value if not found

    Raises
    ------
    EnvironmentVariableError
        If the environment variable value cannot be converted to e.g. an integer or
        boolean when that is requested.
    """
    try:
        encoded_env_var_value = (
            os.environ[var_name]
            .replace(ENV_VAR_EQUALS_REPLACEMENT, "=")
            .encode(STRING_ENCODING)
        )
        value = base64.b32decode(encoded_env_var_value).decode(STRING_ENCODING)
    except KeyError:
        value = default
    except binascii.Error:
        # If the decoding fails, return the original value
        value = os.environ[var_name]

    if as_type == "str":
        return value
    elif as_type == "bool":
        return _convert_envvar_to_bool(var_name, value)
    elif as_type == "int":
        return _convert_envvar_to_int(var_name, value, only_positive)


def _convert_envvar_to_bool(envvar_name, envvar_value: str) -> bool:
    """
    Convert an environment variable to a boolean value.

    Parameters
    ----------
    envvar_name : str
        The environment variable name.
    envvar_value : str
        The environment variable value.

    Returns
    -------
    bool
        The boolean value of the environment variable.

    Raises
    ------
    EnvironmentVariableError
        If the environment variable value cannot be converted to a boolean value.
    """
    if envvar_value in ["true", "1", "yes", "t"]:
        return True
    elif envvar_value in ["false", "0", "no", "f"]:
        return False
    else:
        raise EnvironmentVariableError(
            f"Environment variable '{envvar_name}' has value '{envvar_value}' which "
            "cannot be converted to a boolean value. Please use 'false' or 'true'."
        )


def _convert_envvar_to_int(
    envvar_name: str, envvar_value: str, only_positive: bool
) -> int:
    """
    Convert an environment variable to an integer value.

    Parameters
    ----------
    envvar_name : str
        The environment variable name.
    envvar_value : str
        The environment variable value.

    Returns
    -------
    int
        The integer value of the environment variable.
    """
    try:
        envvar_value = int(envvar_value)
    except ValueError as exc:
        raise EnvironmentVariableError(
            f"Environment variable '{envvar_name}' has value '{envvar_value}' which "
            "cannot be converted to an integer."
        ) from exc
    if envvar_value < 0 and only_positive:
        raise EnvironmentVariableError(
            f"Environment variable '{envvar_name}' has value '{envvar_value}' but a "
            "positive integer value is required."
        ) from exc
    return envvar_value
