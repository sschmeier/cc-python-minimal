#!/usr/bin/env python
"""
NAME: {{cookiecutter.scriptname}}
=========

DESCRIPTION
===========

INSTALLATION
============

USAGE
=====

VERSION HISTORY
===============

{{cookiecutter.version}}    {{cookiecutter.date}}    Initial version.

LICENCE
=======
{{cookiecutter.date}}, copyright {{cookiecutter.author_name}}
{{cookiecutter.author_email}} // {{cookiecutter.author_www}}

template version: 2.0 (2018/12/19)
"""
import sys
import os
import argparse
import csv
import gzip
import bz2
import zipfile
import time

__version__ = '{{cookiecutter.version}}'
__date__ = '{{cookiecutter.date}}'
__email__ = '{{cookiecutter.author_email}}'
__author__ = '{{cookiecutter.author_name}}'

# For color handling on the shell
try:
    from colorama import init, Fore
    # INIT color
    # Initialise colours for multi-platform support.
    init()
    reset = Fore.RESET
    colors = {'success': Fore.GREEN,
              'error': Fore.RED,
              'warning': Fore.YELLOW,
              'info': ''}
except ImportError:
    sys.stderr.write('colorama lib desirable. ' +
                     'Install with "conda install colorama".\n\n')
    reset = ''
    colors = {'success': '', 'error': '', 'warning': '', 'info': ''}


def alert(atype, text, log, repeat=False):
    if repeat:
        textout = '{} [{}] {}\r'.format(time.strftime('%Y%m%d-%H:%M:%S'),
                                        atype.rjust(7),
                                        text)
    else:
        textout = '{} [{}] {}\n'.format(time.strftime('%Y%m%d-%H:%M:%S'),
                                        atype.rjust(7),
                                        text)

    log.write('{}{}{}'.format(colors[atype], textout, reset))
    if atype == 'error':
        raise SystemExit


def success(text, log=sys.stderr):
    alert('success', text, log)


def error(text, log=sys.stderr):
    alert('error', text, log)


def warning(text, log=sys.stderr):
    alert('warning', text, log)


def info(text, log=sys.stderr, repeat=False):
    alert('info', text, log)


def parse_cmdline():
    """ Parse command-line args. """
    # parse cmd-line ----------------------------------------------------------
    description = 'Read delimited file.'
    version = 'version {}, date {}'.format(__version__, __date__)
    epilog = 'Copyright {} ({})'.format(__author__, __email__)

    parser = argparse.ArgumentParser(description=description, epilog=epilog)

    parser.add_argument('--version',
                        action='version',
                        version='{}'.format(version))

    parser.add_argument(
        'str_file',
        metavar='FILE',
        help='Delimited file. [use "-" or "stdin" to read from standard in]')
    parser.add_argument('-d',
                        '--delimiter',
                        metavar='STRING',
                        dest='delimiter_str',
                        default='\t',
                        help='Delimiter used in file.  [default: "tab"]')
    parser.add_argument('-o',
                        '--out',
                        metavar='STRING',
                        dest='outfile_name',
                        default=None,
                        help='Out-file. [default: "stdout"]')

    # if no arguments supplied print help
    if len(sys.argv) == 1:
        parser.print_help()
        raise SystemExit

    args = parser.parse_args()
    return args, parser


def load_file(filename):
    """ LOADING FILES """
    if filename in ['-', 'stdin']:
        filehandle = sys.stdin
    elif filename.split('.')[-1] == 'gz':
        filehandle = gzip.open(filename, 'rt')
    elif filename.split('.')[-1] == 'bz2':
        filehandle = bz2.open(filename, 'rt')
    elif filename.split('.')[-1] == 'zip':
        filehandle = zipfile.ZipFile(filename)
    else:
        filehandle = open(filename)
    return filehandle


def main():
    """ The main funtion. """
    args, parser = parse_cmdline()

    try:
        fileobj = load_file(args.str_file)
    except IOError:
        error('Could not load file "{}". EXIT.'.format(args.str_file))

    # create outfile object
    if not args.outfile_name:
        outfileobj = sys.stdout
    elif args.outfile_name in ['-', 'stdout']:
        outfileobj = sys.stdout
    elif args.outfile_name.split('.')[-1] == 'gz':
        outfileobj = gzip.open(args.outfile_name, 'wt')
    else:
        outfileobj = open(args.outfile_name, 'w')

    # delimited file handler
    csv_reader_obj = csv.reader(fileobj, delimiter=args.delimiter_str)
    header = next(csv_reader_obj)

    # For printing to stdout
    # SIGPIPE is throwing exception when piping output to other tools
    # like head. => http://docs.python.org/library/signal.html
    # use a try - except clause to handle
    try:
        outfileobj.write('{}\n'.format(args.delimiter_str.join(header)))
        for a in csv_reader_obj:
            outfileobj.write('{}\n'.format(args.delimiter_str.join(a)))
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
    outfileobj.close()
    return


if __name__ == '__main__':
    sys.exit(main())
