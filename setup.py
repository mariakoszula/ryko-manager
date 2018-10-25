from setuptools import setup, find_packages

setup(
    name='rykomanager',
    version='1.4',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask',
        'flask_sqlalchemy',
        'docx-mailmerge',

    ],
)