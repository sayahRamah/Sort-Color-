
from setuptools import setup, find_packages

setup(
    name="water-sort-bot",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "python-telegram-bot==20.7",
        "opencv-python-headless==4.8.1.78",
        "numpy==1.24.3",
        "Pillow==10.1.0",
        "python-dotenv==1.0.0",
        "Flask==2.3.3",
        "gunicorn==20.1.0",
        "setuptools==70.0.0",
        "wheel==0.43.0"
    ],
    python_requires=">=3.10",
)
