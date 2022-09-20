import pip._internal

packages = ("catboost", "certifi", "charset-normalizer", "cycler", "et-xmlfile", "fonttools", "future",
            "graphviz", "idna", "joblib", "kiwisolver", "latexcodec", "matplotlib", "monty", "mpmath",
            "networkx", "numpy", "openpyxl", "packaging", "palettable", "pandas", "Pillow", "plotly",
            "pybtex", "pymatgen", "pyparsing", "python-dateutil", "pytz", "PyYAML", "requests", "ruamel.yaml",
            "ruamel.yaml.clib", "scikit-learn", "scipy", "seaborn", "six", "spglib", "sympy", "tabulate", "tenacity",
            "threadpoolctl", "tqdm", "uncertainties", "urllib3", "XlsxWriter")
for package in packages:
    try:
        __import__(package)
    except ImportError:
        pip._internal.main(["install", package.split()[0]])
