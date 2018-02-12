#!/bin/bash

# Exit immediately if any command fails
set -e

echo "This is travis-install-dependencies..."

echo "Installing the packages that CKAN requires..."
sudo apt-get install postgresql-$PGVERSION solr-jetty

echo "Installing CKAN and its Python dependencies..."
git clone https://github.com/ckan/ckan
cd ckan
git checkout "ckan-2.7.2"
python setup.py develop
# Unpin CKAN's psycopg2 dependency get an important bugfix
# https://stackoverflow.com/questions/47044854/error-installing-psycopg2-2-6-2
sed -i '/psycopg2/c\psycopg2' requirements.txt
pip install -r requirements.txt
pip install -r dev-requirements.txt
pip install coveralls
cd -

echo "Creating the PostgreSQL user and database..."
sudo -u postgres psql -c "CREATE USER ckan_default WITH PASSWORD 'pass';"
sudo -u postgres psql -c 'CREATE DATABASE ckan_test WITH OWNER ckan_default;'

echo "Initializing the database..."
cd ckan
paster db init -c test-core.ini
cd -

echo "Installing ckanext-geoview and its requirements..."
python setup.py develop
pip install -r pip-requirements.txt

echo "travis-install-dependencies is done."
