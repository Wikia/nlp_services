from setuptools import setup

setup(
    name="nlp_services",
    version= "0.0.1",
    author="Robert Elwell",
    author_email="robert.elwell@gmail.com",
    description="A collection of services for interacting with NLP data extracted from Stanford CoreNLP",
    license="Other",
    packages=["nlp_services", "nlp_services.caching", "nlp_services.discourse",
              "nlp_services.document_access", "nlp_services.syntax",
              "nlp_services.title_confirmation", "nlp_services.authority",
              "nlp_services.test", "nlp_services.wikia_utils"],
    install_requires=["boto", "flask", "flask-restful", "numpy", "nltk", "lxml",
                      "phpserialize", "mock", "corenlp_xml>=0.0.1", "mrg_utils>=0.0.1"],
    dependency_links=["https://github.com/relwell/corenlp-xml-lib/archive/master.zip#egg=corenlp_xml-0.0.1",
                      "https://github.com/relwell/mrg_utils/archive/master.zip#egg=mrg_utils-0.0.1"
                      ],
    data_files = [("nlp_services/data", ["nlp_services/data/hostnames.json"])],
    test_suite="nlp_services.test.suite"
    )
