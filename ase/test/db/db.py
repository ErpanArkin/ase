import os
from ase.test import cli
from ase.db import connect

cmd = """
ase build H | ase run emt -d y.json &&
ase build H2O | ase run emt -d y.json &&
ase build O2 | ase run emt -d y.json &&
ase build H2 | ase run emt -f 0.02 -d y.json &&
ase build O2 | ase run emt -f 0.02 -d y.json &&
ase build -x fcc Cu | ase run emt -E 5,1 -d y.json &&
ase db -v y.json natoms=1,Cu=1 --delete --yes &&
ase db -v y.json "H>0" -k hydro=1,abc=42,foo=bar &&
ase db -v y.json "H>0" --delete-keys foo"""


def count(n, *args, **kwargs):
    m = len(list(con.select(*args, **kwargs)))
    assert m == n, (m, n)


for name in ['y.json', 'y.db', 'postgresql']:
    if name == 'postgresql':
        if os.environ.get('POSTGRES_DB'):  # gitlab-ci
            name = 'postgresql://ase:pw@postgres:5432/y'
        else:  # local
            name = 'postgresql://ase:pw@localhost:5432/y'
            # psql -c "drop database if exists y;" &
            # psql -c "drop role if exists ase;" &
            pgcmd = """
            psql -c "create role ase with password 'pw';" &
            psql -c "create database y;"
            """
            cli(pgcmd)

    con = connect(name)
    if 'postgres' in name:
        for row in con.select():
            del con[row.id]

    cli(cmd.replace('y.json', name))

    assert con.get_atoms(H=1)[0].magmom == 1
    count(5)
    count(3, 'hydro')
    count(0, 'foo')
    count(3, abc=42)
    count(3, 'abc')
    count(0, 'abc,foo')
    count(3, 'abc,hydro')
    count(0, foo='bar')
    count(1, formula='H2')
    count(1, formula='H2O')
    count(3, 'fmax<0.1')
    count(1, '0.5<mass<1.5')
    count(5, 'energy')

    id = con.reserve(abc=7)
    assert con[id].abc == 7

    for key in ['calculator', 'energy', 'abc', 'name', 'fmax']:
        count(6, sort=key)
        count(6, sort='-' + key)

    cli('ase -T gui --terminal {}@3'.format(name))
