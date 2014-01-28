from setuptools import setup

setup(
    name="nlp_services",
    version= "0.0.1",
    author = "Robert Elwell",
    author_email = "robert.elwell@gmail.com",
    description = "A collection of services for interacting with NLP data extracted from Stanford CoreNLP",
    license = "Other",
    packages = ["nlp_services", "nlp_services.caching", "nlp_services.discourse",
                "nlp_services.document_access", "nlp_services.syntax",
                "nlp_services.title_confirmation", "nlp_services.authority"],
    depends = ["corenlp_xml", "flask", "flask-restful", "boto", "mrg_utils"]
    )