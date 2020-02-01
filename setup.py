from setuptools import setup, find_packages

_package_name = 'pydlshogi'

_version = '1.0.0'

_packages = find_packages(
    where='./',
    exclude=[
        'utils'
    ]
)

setup(
    name=_package_name,
    version=_version,
    author='たけむら',
    url='https://github.com/takemura2/python-dlshogi',
    author_email='takemura2@gmail.com',
    description='たけむら将棋',
    license='MIT',
    keywords='game shogi deeplearning',
    packages=_packages,
    package_data={'pydlshogi': ['model_data/*']},
    install_requires=['cupy == 7.0.0',
                      'chainer == 7.0.0',
                      'python-shogi == 1.0.9'
                      ],
    scripts=[],

)
