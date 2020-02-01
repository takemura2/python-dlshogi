from setuptools import setup, find_packages

_package_name = 'pydlshogi'

_version = '1.0.0'

# パッケージを配列で取得
_packages = find_packages(
    where='./',
    exclude=[
        'utils'
    ]
)


def load_requires_from_file(filepath):
    '''
    requirements.txtからdependencyを取得
    '''
    with open(filepath) as fp:
        return [pkg_name.strip() for pkg_name in fp.readlines()]


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
    install_requires=load_requires_from_file('requirements.txt'),
    scripts=[],

)
