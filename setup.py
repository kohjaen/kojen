import setuptools

with open("README.MD", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="kojen",
    version="1.1.3",
    author="kohjaen",
    author_email="koh.jaen@yahoo.de",
    description="Code generation tools.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kohjaen/kojen",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6.8',
	package_data={'': ['allplatforms/CPP/*.*', 
                       'allplatforms/CPP/sml/include/boost/*.*', 
                       'allplatforms/CPP/testsuite/*.*', 
                       'allplatforms/CPP/testsuite/minunit/minunit.h', 
                       'allplatforms/CPP/testsuite/minunit/minunit.cpp', 
                       'classdiagram_templates/C#/*.*', 
                       'classdiagram_templates/CPP/*.*', 
                       'protocol_templates/CPP/*.*', 
                       'protocol_templates/PY/*.*',
                       'statemachine_templates_embedded_arm/*.*',
                       'statemachine_templates_pc_boost/*.*', 
                       'docs/images/*.*', 
                       'docs/*.*']},
	include_package_data=True,
    install_requires=['cogapp>=3.0.0',],
)
