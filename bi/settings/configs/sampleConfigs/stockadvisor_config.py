def get_stockadvisor_config():
    stockConfig = {
          "config": {
            "COLUMN_SETTINGS": {
              "analysis_type": [
                "metaData"
              ]
            },
            "DATE_SETTINGS": {

            },
            "DATA_SOURCE": {
              "datasource_type": "",
              "datasource_details": ""
            },
            "STOCK_SETTINGS": {
              "stockSymbolList": [
                "googl",
                "appl"
              ],
              "dataAPI": "http://madvisordev.marlabsai.com:80/api/stockdatasetfiles/helloa3-o5u0hyx56t/"
            },
            "FILE_SETTINGS": {
              "inputfile": [
                ""
              ]
            }
          },
          "job_config": {
            "message_url": "http://madvisordev.marlabsai.com:80/api/messages/Job_stockadvisor-helloa3-o5u0hyx56t-xzmtl0c1z9_123/",
            "get_config": {
              "action": "get_config",
              "method": "GET"
            },
            "error_reporting_url": "http://madvisordev.marlabsai.com:80/api/set_job_report/stockadvisor-helloa3-o5u0hyx56t-xzmtl0c1z9/",
            "set_result": {
              "action": "result",
              "method": "PUT"
            },
            "job_url": "http://madvisordev.marlabsai.com:80/api/job/stockadvisor-helloa3-o5u0hyx56t-xzmtl0c1z9/",
            "job_type": "stockAdvisor",
            "job_name": "HelloA3",
            "xml_url": "http://madvisordev.marlabsai.com:80/api/xml/stockadvisor-helloa3-o5u0hyx56t-xzmtl0c1z9/",
            "app_id": None
          }
      }
    return stockConfig
