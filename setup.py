from setuptools import setup
setup(
    name='pydlshogi',
    version='1.0.0',
    author='たけむら',
    description='たけむら将棋',
    packages=['pydlshogi'],
    install_requires=['cupy == 7.0.0',
                      'chainer == 7.0.0',
                      'python-shogi == 1.0.9'
                      ],
    scripts=[],

)
