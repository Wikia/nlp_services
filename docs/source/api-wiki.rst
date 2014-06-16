=================================
API Endpoints for Wiki-Level Data
=================================

.. contents::


Entities
========

The following API services specifically relate to entities within the scope of a wiki.
These services are split by the data source used to determine whether a phrase is an entity.

Wikia-Based Entities
--------------------

.. http:get:: /Wiki/(str:wiki_id)/Entities/Wikia/Counts

   Keys counts to each entity for the wiki. Entities are based on Wikia titles only.


   **Example request**:

   .. sourcecode:: http

      GET /Wiki/831/Entities/Wikia/Counts HTTP/1.1
      Host: nlp_services_api.example.com
      Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/json


      {
          "status": 200,
          "831": {
              "123": ["foo", "bar"],
              "234": ["baz", "qux"]
          }
      }

   :resheader Content-Type: application/json
   :statuscode 200: no error

.. http:get:: /Wiki/(str:wiki_id)/Entities/Wikia/Top

   Provides the top 50 wikia-based entities for the wiki, along with count.


   **Example request**:

   .. sourcecode:: http

      GET /Wiki/831/Entities/Wikia HTTP/1.1
      Host: nlp_services_api.example.com
      Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/json


      {
          "status": 200,
          "831": [["foo", 123], ["bar", 123], ["baz", 122], ... ]
      }

   :resheader Content-Type: application/json
   :statuscode 200: no error

.. http:get:: /Wiki/(str:wiki_id)/Pages/Entities/Wikia

   Provides page-based entity responses for Wikia titles for each page in the wiki.


   **Example request**:

   .. sourcecode:: http

      GET /Wiki/831/Pages/Entities/Wikia HTTP/1.1
      Host: nlp_services_api.example.com
      Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/json


      {
          "status": 200,
          "831": {
              "831_50": {
                  "titles": ["foo", "bar"],
                  "redirects": {"baz": "bar"}
              }
          }
      }

   :resheader Content-Type: application/json
   :statuscode 200: no error

.. http:get:: /Wiki/(str:wiki_id)/Pages/Entities/Wikia/Counts

   Provides page-based entity counts for Wikia titles for each page in the wiki.


   **Example request**:

   .. sourcecode:: http

      GET /Wiki/831/Pages/Entities/Wikia/Counts HTTP/1.1
      Host: nlp_services_api.example.com
      Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/json


      {
          "status": 200,
          "831": {
              "831_50": {
                  "titles": ["foo", "bar"],
                  "redirects": {"baz": "bar"}
              }
          }
      }

   :resheader Content-Type: application/json
   :statuscode 200: no error

.. http:get:: /Wiki/(str:wiki_id)/Pages/Entities/Wikia/DocumentCounts

   Provides number of documents containing each Wikia-based entity


   **Example request**:

   .. sourcecode:: http

      GET /Wiki/831/Pages/Entities/Wikia/DocumentCounts HTTP/1.1
      Host: nlp_services_api.example.com
      Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/json


      {
          "status": 200,
          "831": {
              50: ["foo", "bar", "baz"],
              49: ["qux"]
          }
      }

   :resheader Content-Type: application/json
   :statuscode 200: no error



Wikipedia-Based Entities
------------------------

.. http:get:: /Wiki/(str:wiki_id)/Entities/Wikipedia/Counts

   Keys counts to each entity for the wiki. Entities are based on Wikipedia titles only.


   **Example request**:

   .. sourcecode:: http

      GET /Wiki/831/Entities/Wikipedia/Counts HTTP/1.1
      Host: nlp_services_api.example.com
      Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/json


      {
          "status": 200,
          "831": {
              "123": ["foo", "bar"],
              "234": ["baz", "qux"]
          }
      }

   :resheader Content-Type: application/json
   :statuscode 200: no error

.. http:get:: /Wiki/(str:wiki_id)/Entities/Wikipedia/Top

   Provides the top 50 wikipedia-based entities for the wiki, along with count.


   **Example request**:

   .. sourcecode:: http

      GET /Wiki/831/Entities/Wikipedia HTTP/1.1
      Host: nlp_services_api.example.com
      Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/json


      {
          "status": 200,
          "831": [["foo", 123], ["bar", 123], ["baz", 122], ... ]
      }

   :resheader Content-Type: application/json
   :statuscode 200: no error

.. http:get:: /Wiki/(str:wiki_id)/Pages/Entities/Wikipedia

   Provides page-based entity responses for Wikipedia titles for each page in the wiki.


   **Example request**:

   .. sourcecode:: http

      GET /Wiki/831/Pages/Entities/Wikipedia HTTP/1.1
      Host: nlp_services_api.example.com
      Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/json


      {
          "status": 200,
          "831": {
              "831_50": {
                  "titles": ["foo", "bar"],
                  "redirects": {"baz": "bar"}
              }
          }
      }

   :resheader Content-Type: application/json
   :statuscode 200: no error

.. http:get:: /Wiki/(str:wiki_id)/Pages/Entities/Wikipedia/Counts

   Provides page-based entity counts for Wikipedia titles for each page in the wiki.


   **Example request**:

   .. sourcecode:: http

      GET /Wiki/831/Pages/Entities/Wikipedia/Counts HTTP/1.1
      Host: nlp_services_api.example.com
      Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/json


      {
          "status": 200,
          "831": {
              "831_50": {
                  "titles": ["foo", "bar"],
                  "redirects": {"baz": "bar"}
              }
          }
      }

   :resheader Content-Type: application/json
   :statuscode 200: no error

.. http:get:: /Wiki/(str:wiki_id)/Pages/Entities/Wikipedia/DocumentCounts

   Provides number of documents containing each Wikipedia-based entity


   **Example request**:

   .. sourcecode:: http

      GET /Wiki/831/Pages/Entities/Wikipedia/DocumentCounts HTTP/1.1
      Host: nlp_services_api.example.com
      Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/json


      {
          "status": 200,
          "831": {
              50: ["foo", "bar", "baz"],
              49: ["qux"]
          }
      }

   :resheader Content-Type: application/json
   :statuscode 200: no error


Entities from All Sources
-------------------------

.. http:get:: /Wiki/(str:wiki_id)/Entities/All/Counts

   Keys counts to each entity for the wiki. Entities are based on all data sources.


   **Example request**:

   .. sourcecode:: http

      GET /Wiki/831/Entities/All/Count HTTP/1.1
      Host: nlp_services_api.example.com
      Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/json


      {
          "status": 200,
          "831": {
              "123": ["foo", "bar"],
              "234": ["baz", "qux"]
          }
      }

   :resheader Content-Type: application/json
   :statuscode 200: no error

.. http:get:: /Wiki/(str:wiki_id)/Entities/All/Top

   Provides the top 50 entities for the wiki, along with count, from all data sources.


   **Example request**:

   .. sourcecode:: http

      GET /Wiki/831/Entities/Wikipedia HTTP/1.1
      Host: nlp_services_api.example.com
      Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/json


      {
          "status": 200,
          "831": [["foo", 123], ["bar", 123], ["baz", 122], ... ]
      }

   :resheader Content-Type: application/json
   :statuscode 200: no error


.. http:get:: /Wiki/(str:wiki_id)/Pages/Entities/All

   Provides page-based entity responses for all data sources for each page in the wiki.


   **Example request**:

   .. sourcecode:: http

      GET /Wiki/831/Pages/Entities/All HTTP/1.1
      Host: nlp_services_api.example.com
      Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/json


      {
          "status": 200,
          "831": {
              "831_50": {
                  "titles": ["foo", "bar"],
                  "redirects": {"baz": "bar"}
              }
          }
      }

   :resheader Content-Type: application/json
   :statuscode 200: no error

.. http:get:: /Wiki/(str:wiki_id)/Pages/Entities/All/Counts

   Provides page-based entity counts from all data sources for each page in the wiki.


   **Example request**:

   .. sourcecode:: http

      GET /Wiki/831/Pages/Entities/All/Counts HTTP/1.1
      Host: nlp_services_api.example.com
      Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/json


      {
          "status": 200,
          "831": {
              "831_50": {
                  "titles": ["foo", "bar"],
                  "redirects": {"baz": "bar"}
              }
          }
      }

   :resheader Content-Type: application/json
   :statuscode 200: no error


.. http:get:: /Wiki/(str:wiki_id)/Pages/Entities/All/DocumentCounts

   Provides number of documents containing each entity from all sources


   **Example request**:

   .. sourcecode:: http

      GET /Wiki/831/Pages/Entities/All/DocumentCounts HTTP/1.1
      Host: nlp_services_api.example.com
      Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/json


      {
          "status": 200,
          "831": {
              50: ["foo", "bar", "baz"],
              49: ["qux"]
          }
      }

   :resheader Content-Type: application/json
   :statuscode 200: no error


Miscellaneous
=============

.. http:get:: /Wiki/(str:wiki_id)/Pages/Heads

Provides the semantic heads of each sentence for each page on the wiki.

   **Example request**:

   .. sourcecode:: http

      GET /Wiki/831/Pages/Heads HTTP/1.1
      Host: nlp_services_api.example.com
      Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/json


      {
          "status": 200,
          "831": {
              "831_50": ["foo", "bar", "baz"]
          }
      }

   :resheader Content-Type: application/json
   :statuscode 200: no error


.. http:get:: /Wiki/(str:wiki_id)/Heads/Counts

Provides counts for all semantic heads found on this wiki.

   **Example request**:

   .. sourcecode:: http

      GET /Wiki/831/Heads/Counts HTTP/1.1
      Host: nlp_services_api.example.com
      Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/json


      {
          "status": 200,
          "831": {
              "831_50": {"foo": 50,  "bar": 25, "baz": 75}
          }
      }

   :resheader Content-Type: application/json
   :statuscode 200: no error


.. http:get:: /Wiki/(str:wiki_id)/Heads/Top

Provides tuples of head to count for the top 50 semantic heads for this wiki.

   **Example request**:

   .. sourcecode:: http

      GET /Wiki/831/Heads/Top HTTP/1.1
      Host: nlp_services_api.example.com
      Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/json


      {
          "status": 200,
          "831": {
              "831_50": [["foo", 99], ["bar", 98], ["baz", 20]]
          }
      }

   :resheader Content-Type: application/json
   :statuscode 200: no error




.. http:get:: /Wiki/(str:wiki_id)/Entities/All/SentimentAndCounts

Provides counts and sentiment for all entities mentioned in this wiki.

   **Example request**:

   .. sourcecode:: http

      GET /Wiki/831/Pages/Entities/All/SentimentAndCounts HTTP/1.1
      Host: nlp_services_api.example.com
      Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/json


      {
          "status": 200,
          "831": {
              "entity_foo": {
                  "count": 1234,
                  "sentiment": 2.5
              }
          }
      }

   :resheader Content-Type: application/json
   :statuscode 200: no error
