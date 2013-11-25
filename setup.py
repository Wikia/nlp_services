from setuptools import setup

setup(
    name="nlp_services",
    version= "0.0.1",
    author = "Robert Elwell",
    author_email = "robert.elwell@gmail.com",
    description = "A collection of services for interacting with NLP data extracted from Stanford CoreNLP",
    license = "Other",
    packages = ["nlp_services"],
    depends = ["corenlp_xml"]
    )