import pytest

from ..core import (
    get_imported_modules,
    get_github_url,
    get_bibfiles_from_github
)


examples = [
    # test code:
    ["""
import os
from astropy import nddata
import astropy.units as u
if True:
    import numpy as np
    from os import path

    if True:
        from numpy.linalg import solve
""",
     # expected output:
     ['os', 'astropy', 'astropy', 'numpy', 'os', 'numpy']],
    # ----------
    # test code:
    ["""
from astropy.modeling.models import BlackBody
import numpy.linalg
from celerite2 import terms
""",
     # expected output:
     ['astropy', 'numpy', 'celerite2']]
]


@pytest.mark.parametrize(
    "code, result", examples
)
def test_parser(code, result):
    assert sorted(get_imported_modules(code, unique=False)) == sorted(result)
    assert sorted(get_imported_modules(code, unique=True)) == sorted(list(set(result)))


github_repos = dict(
    numpy="https://github.com/numpy/numpy",
    scipy="https://github.com/scipy/scipy",
    arviz="https://github.com/arviz-devs/arviz",
    emcee="https://github.com/dfm/emcee",
)


@pytest.mark.parametrize(
    "module, url", [[k, v] for k, v in github_repos.items()]
)
def test_github_urls(module, url):
    github_url = get_github_url(module)
    # dodge mismatches because http vs https
    # (this prefix is called the scheme):
    strip_scheme = lambda x: x.split('//')[1]
    assert strip_scheme(github_url) == strip_scheme(url)


@pytest.mark.remote_data
def test_scipy_url_detect_bib_retrieve():
    github_url = get_github_url("scipy")
    bibtex = get_bibfiles_from_github(github_url)
    assert "@ARTICLE{" in bibtex
    assert "SciPy" in bibtex
    assert "doi" in bibtex

