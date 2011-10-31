try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='libbattlelog',
    author='Armin Ronacher',
    author_email='armin.ronacher@active-4.com',
    version='0.2',
    url='http://github.com/mitsuhiko/libbattlelog',
    py_modules=['libbattlelog'],
    description='Accesses the Battlefield 3 Battlelog',
    install_requires=['requests'],
    zip_safe=False,
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python'
    ]
)
