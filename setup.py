from setuptools import setup, find_packages

setup(
    name='rykomanager',
    version='3.10.2',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask',
        'flask_sqlalchemy',
        'docx-mailmerge',
        'python-docx',
        'pywin32',
        'flask-session',
        'werkzeug',
        'wheel'
    ],
)
