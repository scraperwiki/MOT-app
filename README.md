# Developer instructions

To develop the code, you need to download a couple of data files from S3 to the app/dockermount directory

https://s3-eu-west-1.amazonaws.com/sw-mot/WholeDataRates.csv - this one is ~2MB
https://s3-eu-west-1.amazonaws.com/sw-mot/WholeDataFaults.txt - this one is ~500MB

Then from the root of the repository run:

`python app/main_route.py`

The application can also be run in Docker