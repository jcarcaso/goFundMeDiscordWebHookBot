# Discord Webhook Bot for GoFundMe Donations
A discord webhook bot that scans GoFundMe campaigns for donations in the last X ms.

This project is a lambda function that fires via a scheduled EventBridge call. The lambda parses the donation data for a GoFundMe campaign and looks for donations that occurred within the interval being processed. If detected, the bot sends a message to a Discord channel via a webhook as donations occur.

## Prerequisites
The following components are required for this project:
* Python 3.9 or greater
* An Amazon Web Services (AWS) account to createa a Lambda function, layer, and EventBridge configured to run every X milliseconds
* GoFundMe Campaign Name
  * For example, the campaign name for https://www.gofundme.com/f/postfinasteride-syndrome-pfs-fundraiser is postfinasteride-syndrome-pfs-fundraiser
* Discord server channel access to create a webhook to send messages to

## Project Structure
* lambda_function.py - The main lambda function that parses the donation data, and sends a message to discord if new donations are found within the defined interval
* constant.py - Constants for the project
* lambda-layer.zip - A zip file of the python libraries required for `lambda_function.py`. Excluded is the python folder to build this 
* EventWatchConfig.json - Sample config information required for EventBridge to pass the correct parameters to lambda. This is also important for your testing function

## Set Up
Follow the following steps to set up your AWS components. Please note this guide assumes you have knowledge of AWS and can navigate such that you can achieve the following.
1. Create a lambda function
2. Create a consant file
3. Create a layer
4. Create a schedule with EventBridge with the correct config

## TO DO
* More in this wiki to come
