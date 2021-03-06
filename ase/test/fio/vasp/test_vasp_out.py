# flake8: noqa
import inspect
import pytest
import numpy as np
from ase import Atoms
from ase.io import read, iread


@pytest.fixture
def outcar(datadir):
    return datadir / 'vasp' / 'OUTCAR_example_1'


@pytest.fixture
def atoms(outcar):
    return read(outcar, index=-1)


@pytest.fixture
def calc(atoms):
    return atoms.calc


def test_vasp_out(outcar):
    tol = 1e-6

    a1 = read(outcar, index=-1)
    assert isinstance(a1, Atoms)
    assert np.isclose(a1.get_potential_energy(force_consistent=True),
                      -68.22868532,
                      atol=tol)
    assert np.isclose(a1.get_potential_energy(force_consistent=False),
                      -68.23102426,
                      atol=tol)

    a2 = read(outcar, index=':')
    assert isinstance(a2, list)
    assert isinstance(a2[0], Atoms)
    assert len(a2) == 1

    gen = iread(outcar, index=':')
    assert inspect.isgenerator(gen)
    for fc in (True, False):
        for a3 in gen:
            assert isinstance(a3, Atoms)
            assert np.isclose(a3.get_potential_energy(force_consistent=fc),
                              a1.get_potential_energy(force_consistent=fc),
                              atol=tol)


def test_vasp_out_kpoints(calc):
    assert calc.get_number_of_spins() == 2
    assert len(calc.kpts) == 2
    assert len(calc.get_occupation_numbers()) == 128
    assert len(calc.get_eigenvalues()) == 128


@pytest.mark.parametrize('kpt, spin, n, eps_n, f_n',
                         [(0, 0, 98, -3.7404, 0.50014),
                          (0, 1, 82, -3.7208, 0.33798),
                          (0, 1, 36, -4.9193, 1.0)])
def test_vasp_kpt_value(calc, kpt, spin, n, eps_n, f_n):
    # Test a few specific k-points we read off from the OUTCAR file
    assert np.isclose(calc.get_occupation_numbers(kpt=kpt, spin=spin)[n], f_n)
    assert np.isclose(calc.get_eigenvalues(kpt=kpt, spin=spin)[n], eps_n)
