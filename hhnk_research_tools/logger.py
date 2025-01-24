# %%
"""
These functions allow for adding logging to the console.
This is applied by default in the __init__ of hhnk_research_tools. So when it is imported
in a project, the logging will be set according to these rules.
"""

import logging
import sys

# from logging import *  # noqa: F401,F403 # type: ignore
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Union

LOGFORMAT = "%(asctime)s|%(levelname)-8s| %(name)s:%(lineno)-4d| %(message)s"  # default logformat
DATEFMT = "%H:%M:%S"  # default dateformat for console logger


def get_logconfig_dict(level_root="WARNING", level_dict=None, log_filepath=None):
    """Make a dict for the logging.

    Parameters
    ----------
    level_root : str
        Default log level, warnings are printed to console.
    level_dict : dict[level:list]
        e.g. {"INFO" : ['hhnk_research_tools','hhnk_threedi_tools']}
        Apply a different loglevel for these packages.
    log_filepath : str
        Option to write a log_filepath.
    """
    logconfig_dict = {
        "version": 1,
        "disable_existing_loggers": False,
        "loggers": {
            "": {  # root logger
                "level": level_root,
                "handlers": ["debug_console_handler", "stderr"],  # , 'info_rotating_file_handler'],
            },
        },
        "handlers": {
            "null": {
                "class": "logging.NullHandler",
            },
            "debug_console_handler": {
                "level": "NOTSET",
                "formatter": "time_level_name",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
            "stderr": {
                "level": "ERROR",
                "formatter": "time_level_name",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            },
        },
        "formatters": {
            "time_level_name": {
                "format": LOGFORMAT,
                # "format": "%(asctime)s|%(levelname)-8s| %(name)s-%(process)d::%(module)s|%(lineno)-4s: %(message)s",
                "datefmt": DATEFMT,
            },
            # "error": {"format": "%(asctime)s-%(levelname)s-%(name)s-%(process)d::%(module)s|%(lineno)s:: %(message)s"},
        },
    }

    # Apply a different loglevel for these packages.
    if level_dict:
        for loglevel, level_list in level_dict.items():
            if not isinstance(level_list, list):
                raise TypeError("Level_dict should provide lists.")

            for pkg in level_list:
                logconfig_dict["loggers"][pkg] = {
                    "level": loglevel,
                    # "propagate": False, # This will stop the logger from propagating to the root logger
                    # "handlers": ["debug_console_handler"], # When propagate is False, this is needed
                }

    if log_filepath:
        # Not possible to add a default filepath because it would always create this file,
        # even when nothing is being written to it.
        logconfig_dict["handlers"]["info_rotating_file_handler"] = {
            "level": "INFO",
            "formatter": "time_level_name",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "when": "D",
            "backupCount": 7,
            "filename": log_filepath,
        }
    return logconfig_dict


def set_default_logconfig(level_root="WARNING", level_dict=None, log_filepath=None):
    """Use this to set the default config, which will log to the console.

    In the __init__.py of hrt the hrt logger is initiated. We only need logging.GetLogger to add
    loggers to functions and classes. Same can be done for other packages.
    Use this in functions:

    import hhnk_research_tools as hrt
    logger = hrt.logging.get_logger(name=__name__, level='INFO')

    Example changing the default behaviour:
    hrt.logging.set_default_logconfig(
        level_root="WARNING",
        level_dict={
            "DEBUG": ["__main__"],
            "INFO": ["hhnk_research_tools", "hhnk_threedi_tools"],
            "WARNING": ['fiona', 'rasterio']
        },
    )
    """
    log_config = get_logconfig_dict(level_root=level_root, level_dict=level_dict, log_filepath=log_filepath)

    logging.config.dictConfig(log_config)


def add_file_handler(
    logger,
    filepath: Union[str, Path],
    filemode="a",
    filelevel: str = "",
    fmt=LOGFORMAT,
    datefmt="%Y-%m-%d %H:%M:%S",
    maxBytes=10 * 1024 * 1024,
    backupCount=5,
    rotate=False,
    logfilter=None,
):
    """Add a filehandler to the logger. Removes the a filehandler when it is already present

    Parameters
    ----------
    filepath : Union[str, Path]
        filepath to write logs to.
    filemode : str, default is "a"
        writemode, 'w' is write, 'a' is append.
    filelevel : str, default is ""
        Set a different level for writing than the console logger.
    datefmt : str, default is "%Y-%m-%d %H:%M:%S"
        Dateformat for the filehandler. Can differ from the console logger.
    """

    # Remove filehandler when already present
    for handler in logger.handlers:
        if isinstance(handler, (logging.FileHandler, RotatingFileHandler)):
            if Path(handler.stream.name) == filepath:
                logger.removeHandler(handler)
                logger.debug("Removed existing FileHandler, logger probably imported multiple times")

    if rotate:
        file_handler = logging.FileHandler(str(filepath), mode=filemode)
    else:
        file_handler = RotatingFileHandler(str(filepath), mode=filemode, maxBytes=maxBytes, backupCount=backupCount)

    # This formatter includes longdate.
    formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)
    file_handler.setFormatter(formatter)

    # Set level of filehandler, can be different from logger.
    if filelevel == "":
        filelevel = logger.level
    file_handler.setLevel(filelevel)

    if logfilter:
        file_handler.addFilter(logfilter)
        logger.debug("Added filter to FileHandler")

    logger.addHandler(file_handler)


def _add_or_update_streamhandler_format(logger, fmt, datefmt):
    """Add a StreamHandler with the given formatter to the logger.
    If the logger has no handlers, create a new one
    """
    # Check if the logger already has a StreamHandler with the correct formatter
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            # Update the formatter if the StreamHandler is found
            handler.setFormatter(logging.Formatter(fmt=fmt, datefmt=datefmt))
            logger.debug("Updated StreamHandler formatter")
            return

    # If no matching StreamHandler was found, add a new one

    # Detach the logger from the root. This is needed because even when logger.handlers
    # is empty, it still inherits them from the root. This would require us to change
    # the root logger to change just a single logger.
    # logger.propagate = False

    # TODO formatter should be changed on the root streamhandler since we dont propagate.

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(logging.Formatter(fmt=fmt, datefmt=datefmt))
    logger.addHandler(stream_handler)
    logger.debug("Added new StreamHandler with formatter")


def get_logger(name: str, level=None, fmt=LOGFORMAT, datefmt: str = DATEFMT) -> logging.Logger:
    """
    Name should default to __name__, so the logger is linked to the correct file

    When using in a (sub)class, dont use this function. The logger will inherit the settings.
    Use:
        self.logger = hrt.logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    Othwerise:
        logger = hrt.logging.get_logger(name=__name__, level='INFO')

    The names of loggers can be replaced here as well. This creates a shorter logmessage.
    e.g. "hhnk_research_tools" -> "hrt"

    Parameters
    ----------
    name : str
        Default use
        name = __name__
    level : str
        Only use this when debugging. Otherwise make the logger inherit the level from the config.
        When None it will use the default from get_logconfig_dict.
    datefmt : str, default is "%H:%M:%S"
        Change the default dateformatter to e.g. "%Y-%m-%d %H:%M:%S"
    """
    # Rename long names with shorter ones
    replacements = {
        "hhnk_research_tools": "hrt",
        "hhnk_threedi_tools": "htt",
    }

    for old, new in replacements.items():
        name = name.replace(old, new)

    logger = logging.getLogger(name)

    # Change log level
    if level is not None:
        logger.setLevel(level)

    # Change log format or datefmt
    if (fmt != LOGFORMAT) or (datefmt != DATEFMT):
        # Detach the logger from the root. This is needed because even when logger.handlers
        # is empty, it still inherits them from the root. This would require us to change
        # the root logger to change just a single logger.
        # logger.propagate = False
        _add_or_update_streamhandler_format(logger, fmt, datefmt)

    return logger


# %%
