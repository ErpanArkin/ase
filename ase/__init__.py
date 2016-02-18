# Copyright 2008, 2009 CAMd
# (see accompanying license files for details).

"""Atomic Simulation Environment."""

import numpy as np

from ase.atom import Atom
from ase.atoms import Atoms

__all__ = ['Atoms', 'Atom']
__version__ = '3.10.0'

from distutils.version import LooseVersion
if LooseVersion(np.__version__) < '1.9':
    # Make isinstance(x, numbers.Integral) work also for np.intxx:
    import numbers
    numbers.Integral.register(np.integer)
    del numbers
