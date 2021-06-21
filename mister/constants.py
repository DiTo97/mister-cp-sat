import pathlib


Paths = {
    'CONFS_DIR': pathlib.Path(__file__).absolute() \
                        .parents[1] / 'configs'
}


Filenames = {
    'CONF': 'scenario.json',
    'SOLU': 'solution.json'
}
