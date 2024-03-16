from setuptools import setup, find_packages

# Reading the contents of the README.md file to include it in the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='e-pdf-form-reader',
    version='1.0.0',
    author='Your Name',
    author_email='emmanuele@exedre.org',
    description='A Python package for reading forms from PDF pages',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/exedre/e-pdf-form-reader',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'PyMuPDF',  # Dependency required for reading PDFs
    ],
    entry_points={
        'console_scripts': [
            'pdf-form = e_pdf_form_reader.main:main',  # Command for executing the module
        ],
    },

    # List development dependencies (e.g., unittest)
    extras_require={
        'dev': ['unittest']
    },

    # Specify package classifications
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],

    test_suite='tests',

    python_requires='>=3.6',
)

