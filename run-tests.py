"""Run tests for all models.
"""

import argparse
import os
import subprocess
import sys
import unittest


def run_unit_tests():
    """
    Runs unit tests (without subprocesses).
    """
    model_dirs = [os.path.join('streamflow', 'pystreamflow')]

    for dir in model_dirs:
        tests = os.path.join(dir, 'tests')
        suite = unittest.defaultTestLoader.discover(tests, pattern='test*.py')
        res = unittest.TextTestRunner(verbosity=2).run(suite)
        sys.exit(0 if res.wasSuccessful() else 1)


def run_flake8():
    """
    Runs flake8 in a subprocess, exits if it doesn't finish.
    """
    print('Running flake8 ... ')
    sys.stdout.flush()
    p = subprocess.Popen(
        [sys.executable, '-m', 'flake8'], stderr=subprocess.PIPE
    )
    try:
        ret = p.wait()
    except KeyboardInterrupt:
        try:
            p.terminate()
        except OSError:
            pass
        p.wait()
        print('')
        sys.exit(1)
    if ret == 0:
        print('ok')
    else:
        print('FAILED')
        sys.exit(ret)


if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Run unit tests for pints-models.',
    )

    parser.add_argument(
        '--unit',
        action='store_true',
        help='Run all unit tests using the `python` interpreter.',
    )

    parser.add_argument(
        '--style',
        action='store_true',
        help='Run style checks using flake8.',
    )

    args = parser.parse_args()

    # Run tests based on parsed arguments
    has_run = False

    if args.unit:
        has_run = True
        run_unit_tests()

    if args.style:
        has_run = True
        run_flake8()

    # Help if nothing ran
    if not has_run:
        parser.print_help()
