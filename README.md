# explorer_report_aggregator
Support PCE 21.x version

# Installing pipenv:
pip install --upgrade setuptools wheel
pip install --user pipenv

# Navigate to the directory and run:
pipenv shell

# Run the requirements.txt file:
pipenv install -r requirements.txt

# Run the script:
pipenv run python aggregator.py <explorer_csv_file>

# Instructions:
After the scripts executed, check out /reports directory.
There are at least 5 files created:
- updated_raw_<date>.csv -> report after data processing from the imported csv file
- consumer_iplist_agg_report<date>.csv -> report when consumer is iplist and provider is app group
- provider_iplist_agg_report<date>.csv -> report when provider is iplist and consumer is app group
- intrascope_agg_report<date>.csv -> intrascope report
- extrascope_agg_report<date>.csv -> extrascope report

Dash web app will be running after processing, navigate to http://127.0.0.1:8050/ then import the csv file.
