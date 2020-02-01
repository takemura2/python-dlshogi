from setuptools import setup, find_packages

packages = find_packages('pydlshogi'),
setup(
    name='pydlshogi',
    version='1.0.0',
    author='たけむら',
    url='https://github.com/takemura2/python-dlshogi',
    author_email='takemura2@gmail.com',
    description='たけむら将棋',
    license='MIT',
    keywords='game shogi deeplearning',
    packages=find_packages(where='./',
                           exclude=[
                               'utils'
                           ]
                           ),
    install_requires=['cupy == 7.0.0',
                      'chainer == 7.0.0',
                      'python-shogi == 1.0.9'
                      ],
    scripts=[],

)
