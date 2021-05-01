"""
Entry point.
"""

# add package to global path -------------------------------------------------------------------------------------------
import sys
import pathlib


sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
# ----------------------------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    from core.main import main

    main()
