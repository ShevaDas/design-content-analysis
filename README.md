# design-content-analysis

This is a simple Python tool designed to provide various statistics about the length of content in various tables. This information could come in handy if you're creating a new site design and (sensibly) don't want to make assumptions about content length. Just run the script from the command line (after making sure MySQL is running) and it will walk you through the rest.

Right now it only works with Drupal-created databases because it makes the assumption that you want data only from tables whose names begin with "field_data_".

Configuring it to work with other databases should be trivial (just update the SQL query to use the CMS-appropriate prefix).

## Dependencies

* mysql-python
