# Redash Methods

## Execute only selected queries

To execute only selected queries we have two ways.

### Command line

To execute selected queries from the command line:

1. Access the virtual machine
2. ```cd /home/dev/redash```
3. ```sudo -u redash bin/run ./manage.py refresh_only_selected_queries <MONTHS> <PUBLISHERS> [--global-queries|-gq] [--non-monthly-publisher-queries|-nmpq] [--no-query-execution|-nqe]``` where:
    * ```<MONTHS>``` is a comma-separated list of months in the form YYYYMM, e.g. 202010,202009,202003
    * ```<PUBLISHERS>``` is a comma-separated list of publishers, e.g. Publisher1,Publisher2,PublisherN. To specify all publishers type ```ALL```
    * ```--global-queries OR -gq``` are flags that make the global queries (Salesforce, etc.) be updated as well (specify just one of the two, they are equivalent)
    * ```--non-monthly-publisher-queries OR -nmpq``` are flags that make the non-monthly publisher queries (Profile views for segments, etc.) be updated as well (specify just one of the two, they are equivalent)
    * ```--no-query-execution OR -nqe``` is a flag that if set to True makes so that the queries are not executed. It can be used when we're only interested in the query text and not executing them
4. You should receive in return the following json:

    ```
    [
      {
          "task": {
            "status": <TASK_STATUS>,
            "error": <TASK_ERROR>,
            "id": <TASK_ID>,
            "query_result_id": <QUERY_RESULT_ID>,
            "updated_at": <UPDATED_AT>
          },
          "query_text": <QUERY_TEXT>,
          "view_name": <VIEW_NAME>
      }, {
        ...
      }
    ]
    ```
    where task is optional and doesn't appear when the ```-nqe``` flag is specified

### API

The API works almost as the command line process. To execute selected queries from the APIs:

1. Send a POST request to: ```<INSTANCE_URL>/api/queries/refresh/only_selected```
2. The body of the JSON request must be:
    ```
    {
        "token": <REDASH_TOKEN>,
        "months": <MONTHS>,
        "publishers": <PUBLISHERS>,
        "global_queries": <BOOLEAN>,
        "non_monthly_publisher_queries": <BOOLEAN>,
        "no_query_execution": <BOOLEAN>
    }
    ```
    where:
    * ```<MONTHS>``` is a list of months in the form YYYYMM, e.g. ```["202010", "202009", "202003"]```
    * ```<PUBLISHERS>``` is a list of publishers, e.g. ```["Publisher1", "Publisher2", "PublisherN"]```
    * ```global-queries``` is flag that (if set to true) makes the global queries (Salesforce, etc.) be updated as well
    * ```non_monthly_publisher_queries``` are flags that make the non-monthly publisher queries (Profile views for segments, etc.) be updated as well
    * ```non_monthly_publisher_queries``` are flags that make the non-monthly publisher queries (Profile views for segments, etc.) be updated as well
3. You should receive in return the following json:
    ```
    [
      {
          "task": {
            "status": <TASK_STATUS>,
            "error": <TASK_ERROR>,
            "id": <TASK_ID>,
            "query_result_id": <QUERY_RESULT_ID>,
            "updated_at": <UPDATED_AT>
          },
          "query_text": <QUERY_TEXT>,
          "view_name": <DASHBOARD_NAME>.<VIEW_NAME>,
      }, {
        ...
      }
    ]
    ```
    where task is optional and doesn't appear when the ```no_query_execution``` flag is set to True
