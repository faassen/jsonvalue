from setuptools import setup, find_packages

long_description = (
    open('README.rst').read()
    + '\n' +
    open('CHANGES.txt').read())

tests_require = [
    'pytest >= 2.0',
    'pytest-cov',
    ]

setup(
    name='jsonvalue',
    version='0.1',
    description="Rich values for JSON",
    long_description=long_description,
    author="Martijn Faassen",
    author_email="faassen@startifact.com",
    license="BSD",
    keywords='jsonvalue',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'PyLD >= 0.6.1',
        'isodate >= 0.5.0',
    ],
    tests_require=tests_require,
    extras_require=dict(
        test=tests_require,
    )
)
