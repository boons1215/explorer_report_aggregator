# explorer_report_aggregator
Support PCE 21.x explorer report format only

# Installing pipenv:
```
pip install --upgrade setuptools wheel
pip install --user pipenv
```

# Navigate to the directory and run:
```
pipenv shell
```

# Run the requirements.txt file:
```
pipenv install -r requirements.txt
```

# Instructions:
```
❯ pipenv run python aggregator.py -h
usage: aggregator.py [-h] [-b] [-i] [-w] [files ...]

positional arguments:
  files

optional arguments:
  -h, --help  show this help message and exit
  -b, --both  import explorer reports and start web app, COMMAND: aggregator.py -b <file.csv>
  -i, --imp   processing explorer reports only, COMMAND: aggregator.py -i <file.csv>
  -w, --web   start dash web app only, COMMAND: aggregator.py -w
```

Example:
```
❯ pipenv run python aggregator.py -b data/rawreports.csv          
```


After the scripts executed, check out /reports directory.
There are at least 5 files created:
- updated_raw_<date>.csv -> report after data processing from the imported csv file
- consumer_iplist_agg_report<date>.csv -> report when consumer is iplist and provider is app group
- provider_iplist_agg_report<date>.csv -> report when provider is iplist and consumer is app group
- intrascope_agg_report<date>.csv -> intrascope report
- extrascope_agg_report<date>.csv -> extrascope report

Dash web app will be running after processing, navigate to http://127.0.0.1:8050/ then import the csv file.
  
![Alt text](https://github.com/boons1215/explorer_report_aggregator/blob/main/mainpage.png)

Dash table output:
You could toggle column that you want to see, either hide or sort it. 
By clicking the export button, you could export the current table output.
![Alt text](https://github.com/boons1215/explorer_report_aggregator/blob/main/dashtable.png)
  
Bar chart output:
![Alt text](https://github.com/boons1215/explorer_report_aggregator/blob/main/barchart.png)
  
