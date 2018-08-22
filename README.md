# logs-analysis-project
Source code for the Logs Analysis Project.

## Install
Install can be done on Python 2.6+ or 3.4+ as long as the `future` package is installed.

      $ pip install -r requirements.txt
      $ unzip logs-analysis-project.zip
      $ cd logs-analysis-project

## Usage
First time usage (creates the necessary views for the database):
      
    $ python tool.py create_views

To print a report:

    $ python tool.py create_report

## Test

    $ pylint tool.py && pep8 tool.py

## License
MIT
