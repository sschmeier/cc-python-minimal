#!/usr/bin/env python3
"""
NAME: {{cookiecutter.scriptname}}
=====================

DESCRIPTION
-----------

INSTALLATION
------------

USAGE
-----

VERSION HISTORY
---------------

{{cookiecutter.version}}    {{cookiecutter.date}}    Initial version.

LICENCE
-------
{{cookiecutter.date}}, copyright {{cookiecutter.author_name}}
{{cookiecutter.author_email}} // {{cookiecutter.author_www}}

template version: 2.2 (2020/02/08)
"""
__version__ = "{{cookiecutter.version}}"
__date__ = "{{cookiecutter.date}}"
__email__ = "{{cookiecutter.author_email}}"
__author__ = "{{cookiecutter.author_name}}"

import sys
import os
import argparse
import csv
import gzip
import bz2
import zipfile
import time
import logging

# set up logging
logger = logging.getLogger()

_programpath = os.path.realpath(__file__)


def print_logo(filehandle=sys.stderr):
    try:
        from pyfiglet import figlet_format

        text = figlet_format("{{cookiecutter.scriptname}}", font="slant")
    except ImportError:
        text = "\n\t\t{}\n\n".format("{{cookiecutter.scriptname}}")
    filehandle.write("{}\n".format("*" * 60))
    filehandle.write(text)
    filehandle.write("version: {}  date: {}\n".format(__version__, __date__))
    filehandle.write("Using executable at: {}\n".format(_programpath))
    filehandle.write("{}\n\n".format("*" * 60))


def parse_cmdline():
    """ Parse command-line args. """
    # parse cmd-line ----------------------------------------------------------
    description = "Read delimited file."
    version = "version {}, date {}".format(__version__, __date__)
    epilog = "Copyright {} ({})".format(__author__, __email__)

    parser = argparse.ArgumentParser(description=description, epilog=epilog)

    parser.add_argument("--version", action="version", version="{}".format(version))

    parser.add_argument(
        "str_file",
        metavar="FILE",
        help='Delimited file. [use "-" or "stdin" to read from standard in]',
    )
    parser.add_argument(
        "-d",
        "--delimiter",
        metavar="STRING",
        dest="delimiter_str",
        default="\t",
        help='Delimiter used in file.  [default: "tab"]',
    )
    parser.add_argument(
        "-o",
        "--out",
        metavar="STRING",
        dest="outfile_name",
        default=None,
        help='Out-file. [default: "stdout"]',
    )

    log = parser.add_argument_group("logging arguments")
    log.add_argument(
        "--log",
        metavar="STRING",
        dest="loglevel",
        default="INFO",
        help='Logging level. [default: "INFO"]',
    )

    # if no arguments supplied print help
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    return args, parser


def open_infile(filename):
    """ OPEN FILES FOR READING """
    if filename in ["-", "stdin"]:
        filehandle = sys.stdin
    elif filename.split(".")[-1] == "gz":
        filehandle = gzip.open(filename, "rt")
    elif filename.split(".")[-1] == "bz2":
        filehandle = bz2.open(filename, "rt")
    elif filename.split(".")[-1] == "zip":
        filehandle = zipfile.ZipFile(filename)
    else:
        filehandle = open(filename)
    return filehandle


def get_outfile(filename):
    """ Create outfile object """
    if not filename:
        filehandle = sys.stdout
    elif filename in ["-", "stdout"]:
        filehandle = sys.stdout
    elif filename.split(".")[-1] == "gz":
        filehandle = gzip.open(filename, "wt")
    elif filename.split(".")[-1] == "bz2":
        filehandle = bz2.BZ2File(filename, "wt")
    else:
        filehandle = open(filename, "w")
    return filehandle


def main():
    """ The main funtion. """
    # comment out to remove logo printing
    print_logo(filehandle=sys.stderr)
    # parse commandline args
    args, parser = parse_cmdline()

    # set up logger
    numeric_level = getattr(logging, args.loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {args.loglevel}")
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s [%(levelname)8s] (%(filename)s:%(funcName)20s():%(lineno)4s): %(message)s ",
        datefmt="%Y%m%d-%H:%M:%S",
    )
    logger.info("Program start.")
    # test the logging system
    # logger.debug("Debug event")
    # logger.critical("Critical event")

    try:
        fileobj = open_infile(args.str_file)
    except FileNotFoundError as e:
        logger.critical(f'Could not load file "{args.str_file}". EXIT.')
        raise

    # delimited file handler
    csv_reader_obj = csv.reader(fileobj, delimiter=args.delimiter_str)
    # get header
    header = next(csv_reader_obj)

    # outfileobj = get_outfile(args.outfile_name)
    # contextmanager better, no closing file required
    with get_outfile(args.outfile_name) as outfileobj:
        # For printing to stdout
        # SIGPIPE is throwing exception when piping output to other tools
        # like head. => http://docs.python.org/library/signal.html
        # use a try - except clause to handle
        try:
            # HERE THE MAIN STUFF IS HAPPENING
            outfileobj.write("{}\n".format(args.delimiter_str.join(header)))
            for a in csv_reader_obj:
                # DO stuff
                # ...
                # print
                outfileobj.write("{}\n".format(args.delimiter_str.join(a)))
            # flush output here to force SIGPIPE to be triggered
            # while inside this try block.
            sys.stdout.flush()
        except BrokenPipeError:
            # Python flushes standard streams on exit; redirect remaining output
            # to devnull to avoid another BrokenPipeError at shut-down
            devnull = os.open(os.devnull, os.O_WRONLY)
            os.dup2(devnull, sys.stdout.fileno())
            sys.exit(1)  # Python exits with error code 1 on EPIPE

    # ------------------------------------------------------
    # outfileobj.close()
    fileobj.close()
    return


if __name__ == "__main__":
    sys.exit(main())
