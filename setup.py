from setuptools import find_packages, setup

setup(
    name="fitconnect_client",
    packages=find_packages(include=["fitconnect_client", "fitconnect_client.objects"]),
    version="0.1.0",
    description="A python SDK to interact with the German Fitconnect system",
    long_description="A python SDK to interact with the German Fitconnect system",
    author="Jon Bulica",
    author_email="jonbulica99@gmail.com",
    install_requires=[
        "urllib3",
        "requests",
        "jwcrypto"
    ]
)
