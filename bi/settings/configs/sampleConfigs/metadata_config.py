def get_metadata_config():
    metaDataConfig = {
      "config": {
        "COLUMN_SETTINGS": {
          "analysis_type": [
            "metaData"
          ]
        },
        "DATE_SETTINGS": {

        },
        "DATA_SOURCE": {
          "datasource_type": "fileUpload",
          "datasource_details": ""
        },
        "FILE_SETTINGS": {
          "inputfile": [
            "file:///home/gulshan/marlabs/datasets/insuranceClaimsV2All12MonthDistintDates.csv"
          ]
        }
      },
      "job_config": {
        "message_url": "http://34.196.204.54:9012/api/messages/Job_metadata-insuranceclaimsv2all12monthdistintdatescsv-07wg9nidz0-bzzrdw3nqu_123/",
        "get_config": {
          "action": "get_config",
          "method": "GET"
        },
        "error_reporting_url": "http://34.196.204.54:9012/api/set_job_report/metadata-insuranceclaimsv2all12monthdistintdatescsv-07wg9nidz0-bzzrdw3nqu/",
        "set_result": {
          "action": "result",
          "method": "PUT"
        },
        "job_url": "http://34.196.204.54:9012/api/job/metadata-insuranceclaimsv2all12monthdistintdatescsv-07wg9nidz0-bzzrdw3nqu/",
        "job_type": "metaData",
        "job_name": "insuranceClaimsV2All12MonthDistintDates.csv",
        "xml_url": "http://34.196.204.54:9012/api/xml/metadata-insuranceclaimsv2all12monthdistintdatescsv-07wg9nidz0-bzzrdw3nqu/",
        "app_id": None
      }
    }
    return metaDataConfig
