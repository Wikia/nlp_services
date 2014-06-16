=====================================
API Endpoints for Document-Level Data
=====================================

.. contents::

Entities
========
Entity services are split by the data source used to drive entity identification.


Wikia-Based Entities
--------------------
.. http:get:: /Doc/(str:doc_id)/Entities/Wikia

   Provides entities based on titles and redirects in Wikia

   **Example request**:

   .. sourcecode:: http

      GET /Doc/831_50/Entities/Wikia HTTP/1.1
      Host: nlp_services_api.example.com
      Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/json


      {
          "status": 200,
          "831_50": {
              "titles": ["foo", "bar"],
              "redirects": {"baz": "bar"}
          }
      }

   :resheader Content-Type: application/json
   :statuscode 200: no error

.. http:get:: /Doc/(str:doc_id)/Entities/Wikia/Counts

   Provides counts of entities based on titles and redirects in Wikia

   **Example request**:

   .. sourcecode:: http

      GET /Doc/831_50/Entities/Wikia/Counts HTTP/1.1
      Host: nlp_services_api.example.com
      Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/json


      {
          "status": 200,
          "831_50": {
              "foo": 50,
              "bar": 25,
              "baz": 75
          }
      }

   :resheader Content-Type: application/json
   :statuscode 200: no error


Wikipedia-Based Entities
------------------------
.. http:get:: /Doc/(str:doc_id)/Entities/Wikipedia

   Provides entities based on titles and redirects in Wikipedia

   **Example request**:

   .. sourcecode:: http

      GET /Doc/831_50/Entities/Wikipedia HTTP/1.1
      Host: nlp_services_api.example.com
      Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/json


      {
          "status": 200,
          "831_50": {
              "titles": ["foo", "bar"],
              "redirects": {"baz": "bar"}
          }
      }

   :resheader Content-Type: application/json
   :statuscode 200: no error

.. http:get:: /Doc/(str:doc_id)/Entities/Wikipedia/Counts

   Provides counts of entities based on titles and redirects in Wikipedia

   **Example request**:

   .. sourcecode:: http

      GET /Doc/831_50/Entities/Wikipedia/Counts HTTP/1.1
      Host: nlp_services_api.example.com
      Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/json


      {
          "status": 200,
          "831_50": {
              "foo": 50,
              "bar": 25,
              "baz": 75
          }
      }

   :resheader Content-Type: application/json
   :statuscode 200: no error



Entities from All Sources
-------------------------
.. http:get:: /Doc/(str:doc_id)/Entities/All

   Provides entities based on titles and redirects in all data sources

   **Example request**:

   .. sourcecode:: http

      GET /Doc/831_50/Entities/All HTTP/1.1
      Host: nlp_services_api.example.com
      Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/json


      {
          "status": 200,
          "831_50": {
              "titles": ["foo", "bar"],
              "redirects": {"baz": "bar"}
          }
      }

   :resheader Content-Type: application/json
   :statuscode 200: no error

.. http:get:: /Doc/(str:doc_id)/Entities/All/Counts

   Provides counts of entities based on titles and redirects from all data sources

   **Example request**:

   .. sourcecode:: http

      GET /Doc/831_50/Entities/All/Counts HTTP/1.1
      Host: nlp_services_api.example.com
      Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/json


      {
          "status": 200,
          "831_50": {
              "foo": 50,
              "bar": 25,
              "baz": 75
          }
      }

   :resheader Content-Type: application/json
   :statuscode 200: no error


Syntax
======
.. http:get:: /Doc/(str:doc_id)/NPs

   Returns all noun phrases from the provided document

   **Example request**:

   .. sourcecode:: http

      GET /Doc/831_50/NPs HTTP/1.1
      Host: nlp_services_api.example.com
      Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/json


      {
          "status": 200,
          "831_50": ["the dog who ate a sandwich", "the dog", "a sandwich"]
      }

   :resheader Content-Type: application/json
   :statuscode 200: no error

.. http:get:: /Doc/(str:doc_id)/VPs

   Returns all verb phrases from the provided document

   **Example request**:

   .. sourcecode:: http

      GET /Doc/831_50/VPs HTTP/1.1
      Host: nlp_services_api.example.com
      Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/json


      {
          "status": 200,
          "831_50": ["ate a sandwich", "ate", "fed the dog", "fed"]
      }

   :resheader Content-Type: application/json
   :statuscode 200: no error

.. http:get:: /Doc/(str:doc_id)/Heads

   Returns all semantic heads from the provided document

   **Example request**:

   .. sourcecode:: http

      GET /Doc/831_50/VPs HTTP/1.1
      Host: nlp_services_api.example.com
      Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/json


      {
          "status": 200,
          "831_50": ["ate", "fed", "gave", "angry"]
      }

   :resheader Content-Type: application/json
   :statuscode 200: no error

Sentiment
=========
.. http:get:: /Doc/(str:doc_id)/Sentiment

   Returns average sentiment among all sentences and for  all coreference phrases in the document

   **Example request**:

   .. sourcecode:: http

      GET /Doc/831_50/Sentiment HTTP/1.1
      Host: nlp_services_api.example.com
      Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/json


      {
          "status": 200,
          "831_50": {
              "averageSentiment": 3.1,
              "averagePhraseSentiment": {
                  "foo": 2.3,
                  "bar": 1.1
              }
          }
      }

   :resheader Content-Type: application/json
   :statuscode 200: no error

.. http:get:: /Doc/(str:doc_id)/Entities/Wikia/Sentiment

   Returns average sentiment cross-referenced with Wikia entities

   **Example request**:

   .. sourcecode:: http

      GET /Doc/831_50/Entities/Wikia/Sentiment HTTP/1.1
      Host: nlp_services_api.example.com
      Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/json


      {
          "status": 200,
          "831_50": {
              "foo": 2.3,
              "bar": 1.1
          }
      }

   :resheader Content-Type: application/json
   :statuscode 200: no error

.. http:get:: /Doc/(str:doc_id)/Entities/Wikipedia/Sentiment

   Returns average sentiment cross-referenced with Wikipedia entities

   **Example request**:

   .. sourcecode:: http

      GET /Doc/831_50/Entities/Wikipedia/Sentiment HTTP/1.1
      Host: nlp_services_api.example.com
      Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/json


      {
          "status": 200,
          "831_50": {
              "foo": 2.3,
              "bar": 1.1
          }
      }

   :resheader Content-Type: application/json
   :statuscode 200: no error

.. http:get:: /Doc/(str:doc_id)/Entities/All/Sentiment

   Returns average sentiment cross-referenced with entities from all data sources

   **Example request**:

   .. sourcecode:: http

      GET /Doc/831_50/Entities/All/Sentiment HTTP/1.1
      Host: nlp_services_api.example.com
      Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/json


      {
          "status": 200,
          "831_50": {
              "foo": 2.3,
              "bar": 1.1
          }
      }

   :resheader Content-Type: application/json
   :statuscode 200: no error




Miscellaneous
=============
.. http:get:: /Doc/(str:doc_id)/CoreferenceCounts

   Returns coreference information directly from parse data

   **Example request**:

   .. sourcecode:: http

      GET /Doc/831_50/CoferenceCounts HTTP/1.1
      Host: nlp_services_api.example.com
      Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/json


      {
          "status": 200,
          "831_50": {
              "mentionCounts": {
                  "foo": 4
              },
              "paraphrases": {
                  "foo": ["bar", "baz", "qux"]
              }
          }
      }

   :resheader Content-Type: application/json
   :statuscode 200: no error

.. http:get:: /Doc/(str:doc_id)/XML

   Returns XML string from parse output.

   **Example request**:

   .. sourcecode:: http

      GET /Doc/831_50/XML HTTP/1.1
      Host: nlp_services_api.example.com
      Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/json


      {
          "status": 200,
          "831_50": "<xml>...</xml>"
      }

   :resheader Content-Type: application/json
   :statuscode 200: no error

