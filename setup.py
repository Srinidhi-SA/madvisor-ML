import os

from setuptools import setup, find_packages

# from pip.req import parse_requirements
# install_reqs = parse_requirements("requirements.txt",  session=False)
# reqs = [str(ir.req) for ir in install_reqs]


setup(
        name='marlabs-bi-jobs',
        version=os.getenv('SJS_VERSION', '0.0.0'),
        description='Marlabs BI jobs for Spark Job Server',
        include_package_data=True,
        #url='https://github.com/spark-jobserver/spark-jobserver',
        #license='Apache License 2.0',
        packages=find_packages(exclude=['test*','example*','config*','doc*','spark-ware*']),
        #install_requires=['numpy','scipy','pyhocon', 'py4j','pandas','statsmodels','jinja2','pattern']
        install_requires=['numpy','scipy','pyhocon','pandas','statsmodels','jinja2','pattern']
)
