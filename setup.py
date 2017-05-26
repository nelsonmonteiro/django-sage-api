from setuptools import setup, find_packages
from io import open

setup(
    name='django-sage-api',
    version='0.1',
    description='Django module for Sage 200 / Sage 200 Extra API',
    long_description=open('README.md', encoding='utf-8').read(),
    author='Nelson Monteiro',
    author_email='nelson.reis.monteiro@gmail.com',
    url='https://github.com/nelsonmonteiro/django-sage-api',
    #download_url='https://pypi.python.org/pypi/django-sage-api',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'django>=1.5.4',
        'uuid>=1.30',
        'pytz>=2017.2',
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
