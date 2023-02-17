import os
import re
import requests
import warnings

__all__ = [
    'get_imported_modules',
    'get_builtin_citations',
    'get_github_url',
    'get_bibfiles_from_github',
]

builtin_citation_attrs = [
    '__citation__',
    '__bibtex__',
]


def _read_from_url(url):
    r = requests.get(url)
    if r.ok:
        return r.text
    return None


def get_imported_modules(code, unique=True):
    pattern = r"(?m)^(?:import[ ]|from[ ]|[ ]+import[ ]|[ ]+from[ ])([^. \n]+)"
    result = re.findall(pattern, code)

    if unique:
        return list(set(result))

    return result


def get_builtin_citations(modules):
    citations = dict()
    for module in modules:
        try:
            mod = __import__(module)
        except ImportError:
            warnings.warn(f"Module {module} couldn't be imported.")

        for cite_attr in builtin_citation_attrs:
            citation = getattr(mod, cite_attr, None)
            if citation is not None:
                citations[module] = citation

    return citations


def get_github_url(module):
    url = f"https://pypi.org/pypi/{module}/json"
    data = requests.get(url).json()
    homepage = data['info']['home_page']
    if 'github.com' in homepage.lower():
        return homepage

    project_urls = data['info']['project_urls']
    source_code_key = [k for k in project_urls.keys() if 'source' in k.lower()]
    if len(source_code_key):
        github_url = project_urls[source_code_key[0]]
        return github_url


def get_bibfiles_from_github(github_url):
    url = str(github_url)

    if 'raw' not in url.lower():
        url = url.replace("github.com", "raw.githubusercontent.com")

    if not url.endswith('/'):
        url += '/'

    default_branch_names = ['main', 'master']
    default_dir_names = ['', 'docs']
    default_filenames = ['CITATION.bib']

    bibfile = None
    try_urls = []
    for branch in default_branch_names:
        for fn in default_filenames:
            for dirname in default_dir_names:
                try_urls.append(url + '/'.join(
                    [i for i in [branch, dirname, fn] if len(i)]
                ))

    for try_url in try_urls:
        if try_url.endswith('.bib'):
            bibfile = _read_from_url(try_url)
            if bibfile is not None:
                break

    return bibfile


def get_script_from_notebooks(paths):
    from nbconvert import export, ScriptExporter

    scripts_concat = ""

    for notebook_path in paths:
        # convert notebook to script
        script, resources = export(ScriptExporter, notebook_path)

        scripts_concat += script + 3 * '\n'

    return scripts_concat


def find_files(search_dir):
    include_extensions = ['py', 'ipynb']
    ignore_dirs = ['docs']
    files_to_check = {k: [] for k in include_extensions}

    for root, dirs, files in os.walk(search_dir):
        # skips hidden and ignored dirs:
        files = [f for f in files if not f[0] == '.']
        dirs[:] = [d for d in dirs if not d[0] == '.' and d not in ignore_dirs]

        for f in files:
            file_root, file_ext = os.path.splitext(f)
            # look for files with included extensions
            if file_ext[1:] in include_extensions and file_root != '__init__':
                files_to_check[file_ext[1:]].append(os.path.join(root, f))
