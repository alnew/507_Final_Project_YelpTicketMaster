Data Sources Used:

Yelp Fusion:
  -Required an API key - How to obtain API Key:
  -Create a Yelp Account here by clicking Sign Up: https://www.yelp.com/login?return_url=%2Fdevelopers%2Fv3%2Fmanage_app
  -Get your API key on this page: https://www.yelp.com/developers/v3/manage_app
  -Required getting more than the 20 returned


TicketMaster: API site - https://developer.ticketmaster.com/products-and-docs/apis/discovery-api/v2/
  -Required an API key - How to obtain an API key:
  -Register for an API here: https://developer-acct.ticketmaster.com/user/register
  -Log in to your account
  -Click on this page for your Consumer Key: https://developer-acct.ticketmaster.com/user/8225/apps


API Secrets Location
  Create a separate file for your API keys that you will .gitignore when pushing to GitHub
  My Secrets File: final_proj_secrets.py


Postal Code Data from CSV:
  -Click on this link and download the .csv file: https://www.aggdata.com/node/86


Plotly Visualizations
  -How to sign up: https://plot.ly/
  -Create a free account: https://plot.ly/ssu/
  pip install Plotly if not already on your machine with the following command: pip install plotly
  -Then grab the API here: https://plot.ly/python/getting-started/
  -Set up your credentials with the following:
      import plotly
      plotly.tools.set_credentials_file(username='DemoAccount', api_key='lr1c37zw81')
  -Fill in username with your Plotly username
  -Fill in api_key with your API key (found here :https://plot.ly/settings/api)
  -For tutorials and other visualization options, go here: https://plot.ly/python/


Functions
Some of the more important functions for this program include:

init_db(db_name, csv_file)
  This function does the following:
  -Creates a connection for sqlite3
  -Creates all three tables for the database ('food_event.db'): Restaurants, Events, PostalCodes
  -Inputs data from two .json files (‘yelp_data.json’ and ‘ticket_master_data.json) and one .csv file ('us_postal_codes.csv') into the tables
  -Updates foreign keys by inserting the postal code Id from the PostalCode table into the place where the actual postal code/zip code is in both the Restaurants and Events tables
  -Closes the connection with the database


get_from_yelp(term, location)
  -This function specifies which data to get from the Yelp Fusion API
  -In the params dictionary, I set it to search by term, which in this case, I used “food” in order to search for restaurants, location, to search by city, and increased the limit to the highest amount Yelp allows to gather 50 data points per location searched
  -This function utilizes the yelp_make_request_using_cache(baseurl,params=None, headers=None) function which makes the actual API call if there is no data in the yelp_data.json cache


get_ticketmaster_data(ticket_city)
  -This function specifies which data to get from the TicketMaster API
  -In the ticket_dict, or search parameters, is the API key, the search limit set to return 100 events, and the parameter to search by city
  -This function utilizes the t_master_make_request_using_cache(baseurl, params) function, which makes the actual API call if there is no data in the  ticket_master_data.json cache


User Guide
-Fork this project, then click on the Clone or Download button, copy the link and use the following command in your command line: git clone ‘put the link here’
-Once all of the files are in the same folder on your machine, open final_proj_4_14.py
-Follow the steps above to retrieve your API keys from Yelp Fusion and TicketMaster, then put them in the file (make sure to save it): final_proj_secrets.py
-To create a database using the data saved, run the final_proj_4_14.py file as is
    -To gather new data, delete the files: yelp_data.json and ticket_master_data.json
    -Then run the file in your terminal with the following command: python3 final_proj_4_14.py
    -This will create and store new data and create a database: food_event.db
    -Once the database is filled, you will be prompted at the command line to enter a city name: Chicago, San Francisco, New York, and Ann Arbor
    -After you choose a city, you will be prompted for the type of data visualization you would like, choose from: rating table, address, rating chart, or map
    -For help, type help for the help.txt file to print in your terminal
    -To exit the program, type exit
