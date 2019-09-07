from setuptools import setup, find_packages

setup(
    name='rykomanager',
    version='3.2.1', #update to new semester
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask',
        'flask_sqlalchemy',
        'docx-mailmerge',
        'python-docx',
        'pywin32'

    ],
)