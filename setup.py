from setuptools import setup, find_packages

setup(
    name="trillm_orchestrator",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        # Add your dependencies here
    ],
    extras_require={
        'test': [
            'pytest',
            'pytest-asyncio',
            # Add other test dependencies here
        ],
    },
) 