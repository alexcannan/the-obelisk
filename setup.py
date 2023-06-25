from setuptools import setup, find_namespace_packages

libs = "libfst.so.16 libkaldi-base.so libkaldi-chain.so libkaldi-cudamatrix.so libkaldi-decoder.so libkaldi-feat.so libkaldi-fstext.so libkaldi-gmm.so libkaldi-hmm.so libkaldi-ivector.so libkaldi-lat.so libkaldi-matrix.so libkaldi-nnet2.so libkaldi-nnet3.so libkaldi-online2.so libkaldi-transform.so libkaldi-tree.so libkaldi-util.so".split()

setup(
    name='obelisk',
    version='1',
    python_requires='>=3.10',
    author='Alex Cannan',
    author_email='alexfcannan@gmail.com',
    packages=find_namespace_packages(include=['obelisk.*', 'obelisk']),
    long_description="the obelisk offers sage advice for those in need",
    install_requires=[
        "fastapi",
        "jinja2",
        "uvicorn",
        "loguru",
        "aiohttp",
    ],
)
