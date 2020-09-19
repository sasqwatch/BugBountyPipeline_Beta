# BugBountyPipeline_Beta
ETL Pipeline with a strong focus on Bug Bounty Recon and Attack pipelines.

For testing purposes, you can remove the 'store' function within the main pipeline files (subdomain_enum and remote_subdomain_enum) if you don't want to store results to a database... I am designing a database to handle all the data collected from the pipeline, so that it on the TODO list.

For testing purposes, you can add your DigitalOcean API key to the remote_subdomain_enum.py file if you want to use the remote_subdomain_enum.py tool

For testing purposes, you should add any api keys that are requested in the src/task/config/command.ini file
