import requests, json, sqlite3, csv, sys
import plotly as py
import plotly.plotly as py
import plotly.graph_objs as go
from collections import Counter
from final_proj_secrets import *


def params_unique_combination(baseurl, params):
    alphabetized_keys = sorted(params.keys())
    res = []
    for k in alphabetized_keys:
        res.append("{}-{}".format(k, params[k]))
    return baseurl + "_".join(res)

#----------------------
# Yelp Cache
#----------------------
CACHE_FNAME1 = 'yelp_data.json'
try:
    print("Opening Yelp Cache")
    cache_file = open(CACHE_FNAME1, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION_1 = json.loads(cache_contents)
    cache_file.close()
except:
    CACHE_DICTION_1 = {}

#----------------------
# TicketMaster Cache
#----------------------
CACHE_FNAME2 = 'ticket_master_data.json'
try:
    print("Opening TMaster Cache")
    cache_file = open(CACHE_FNAME2, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION_2 = json.loads(cache_contents)
    cache_file.close()
except:
    CACHE_DICTION_2 = {}

####################
# GETTING YELP DATA
####################
def yelp_make_request_using_cache(baseurl,params=None, headers=None):
    unique_ident = params_unique_combination(baseurl,params)

    if unique_ident in CACHE_DICTION_1:
        print("Getting cached data...Yelp")
        return CACHE_DICTION_1[unique_ident]
    else:
        print("Making a request for new data...Yelp")
        resp = requests.get(baseurl, headers=headers, params=params)
        CACHE_DICTION_1[unique_ident] = json.loads(resp.text)
        dumped_json_cache = json.dumps(CACHE_DICTION_1)
        fw = open(CACHE_FNAME1,"w")
        fw.write(dumped_json_cache)
        fw.close()
        return CACHE_DICTION_1[unique_ident]

def get_from_yelp(term, location):
    baseurl = "https://api.yelp.com/v3/businesses/search"
    params = {'term': term, "location": location, 'limit':50}
    headers={'Authorization': 'Bearer '+ yelp_api_key}
    m = yelp_make_request_using_cache(baseurl, headers = headers, params=params)



############################
# GETTING TICKETMASTER DATA
###########################
def t_master_make_request_using_cache(baseurl, params):
    unique_ident = params_unique_combination(baseurl,params)

    if unique_ident in CACHE_DICTION_2:
        print("Getting cached data...TicketMaster")
        return CACHE_DICTION_2[unique_ident]
    else:
        print("Making a request for new data...Ticket Master")
        resp = requests.get(baseurl, params)
        CACHE_DICTION_2[unique_ident] = json.loads(resp.text)
        dumped_json_cache = json.dumps(CACHE_DICTION_2)
        fw = open(CACHE_FNAME2,"w")
        fw.write(dumped_json_cache)
        fw.close()
        return CACHE_DICTION_2[unique_ident]

def get_ticketmaster_data(ticket_city):
    ticket_baseurl = "https://app.ticketmaster.com/discovery/v2/events"
    ticket_dict = {}
    ticket_dict["apikey"] = ticket_api_key
    ticket_dict["size"] = '100'
    ticket_dict["city"] = ticket_city

    # m = requests.get(ticket_baseurl, ticket_dict)

    return t_master_make_request_using_cache(ticket_baseurl, ticket_dict)


DBNAME = 'food_event.db'
CSV = 'us_postal_codes.csv'

def init_db(db_name, csv_file):
    CACHE_FNAME1 = 'yelp_data.json'
    CACHE_FNAME2 = 'ticket_master_data.json'

    try:
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
    except Error as e:
        print(e)


    #----------------------
    # Drop tables if they exist
    #----------------------
    statement = '''
        DROP TABLE IF EXISTS 'Restaurants'
    '''
    cur.execute(statement)
    conn.commit()

    statement = '''
        DROP TABLE IF EXISTS 'Events'
    '''
    cur.execute(statement)
    conn.commit()

    statement = '''
        DROP TABLE IF EXISTS 'PostalCodes'
    '''
    cur.execute(statement)
    conn.commit()


    # Create 3 tables, Restaurants and Events and Postal Codes

    # Table 1: Restaurant data from YELP
    statement = '''
    CREATE TABLE 'Restaurants' (
    'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
    'name' TEXT,
    'url' TEXT,
    'category1' TEXT,
    'category2' TEXT,
    'category3' TEXT,
    'rating' TEXT,
    'latitude' TEXT,
    'longitude' TEXT,
    'streetAdress' TEXT,
    'city' TEXT,
    'state' TEXT,
    'locationZip_code' TEXT,
    'display_phone' TEXT
    )
    '''
    cur.execute(statement)
    conn.commit()

    # Table 2: Event Data from TICKETMASTER
    statement = '''
    CREATE TABLE 'Events' (
    'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
    'name' TEXT,
    'url' TEXT,
    'localDate' TEXT,
    'codeAvailability' TEXT,
    'venue' TEXT,
    'longitude' TEXT,
    'latitude' TEXT,
    'streetAdress' TEXT,
    'city' TEXT,
    'state' TEXT,
    'PostalCode' TEXT
    )
    '''
    cur.execute(statement)
    conn.commit()


    statement = '''
    CREATE TABLE 'PostalCodes' (
    'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
    'PostalCode' TEXT,
    'city' TEXT,
    'state' TEXT,
    'stateAbbreviation' TEXT,
    'county' TEXT,
    'latitude' TEXT,
    'longitude' TEXT
    )
    '''
    cur.execute(statement)
    conn.commit()



###########################
#### POPULATE YELP TABLE
###########################

    # Populate RESTAURANT Table with YELP Data
    restaurant_data = json.load(open(CACHE_FNAME1))
    for ele in restaurant_data.values():
        ele_values = list(ele.values())
        for yelp_lst in ele_values[0]:

            try:
                restaurant_insertion = (None, yelp_lst['name'], yelp_lst['url'], yelp_lst['categories'][0]['title'],
                yelp_lst['categories'][1]['title'], yelp_lst['categories'][2]['title'],
                yelp_lst['rating'], yelp_lst['coordinates']['latitude'],
                yelp_lst['coordinates']['longitude'], yelp_lst['location']['address1'], yelp_lst['location']['city'],
                yelp_lst['location']['state'], yelp_lst['location']['zip_code'], yelp_lst['display_phone'])

            except:
                restaurant_insertion = (None, yelp_lst['name'], yelp_lst['url'], None, None, None, yelp_lst['rating'], yelp_lst['coordinates']['latitude'],
                yelp_lst['coordinates']['longitude'], yelp_lst['location']['address1'], yelp_lst['location']['city'],
                yelp_lst['location']['state'], yelp_lst['location']['zip_code'], yelp_lst['display_phone'])

            # print(restaurant_insertion)
            restaurant_statement = 'INSERT INTO "Restaurants" '
            restaurant_statement += 'VALUES(?, ?, ? , ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) '

            cur.execute(restaurant_statement, restaurant_insertion)


    ##################################
    #### POPULATE TICKETMASTER TABLE
    ##################################
    counter = 0
    dict_list = []
    event_dict_lst = []
    # # Populate EVENT Table with TICKETMASTER Data
    event_data = json.load(open(CACHE_FNAME2))
    for ele in event_data.values(): # this gets to the _embedded level of the dictionary
        ele_values = list(ele.values()) #this will give a list that has the dictionary with the events and all of its keys in it
        for ele in ele_values:
            dict_list.append(ele)

    # This code adds all of the events dictionaries to event_dict_lst, use this dictionary to add info to the tables
    while len(dict_list) > counter:
        event_dict_lst.append(dict_list[counter])
        counter +=3

    # Extracting each event dictionary from event_dict_lst
    for each_dict in event_dict_lst:
        event_lst = each_dict['events']
        for ele in event_lst:
            try:
                event_insertion = (None, ele['name'],
                ele['url'], ele['dates']['start']['localDate'],
                ele['dates']['status']['code'],
                ele['_embedded']['venues'][0]['name'],
                ele['_embedded']['venues'][0]['location']['longitude'],
                ele['_embedded']['venues'][0]['location']['latitude'],
                ele['_embedded']['venues'][0]['address']['line1'],
                ele['_embedded']['venues'][0]['city']['name'],
                ele['_embedded']['venues'][0]['state']['stateCode'], ele['_embedded']['venues'][0]['postalCode'])
            except:
                event_insertion = (None, ele['name'],
                ele['url'], ele['dates']['start']['localDate'], ele['dates']['status']['code'],
                ele['_embedded']['venues'][0]['name'],
                None, None, ele['_embedded']['venues'][0]['address']['line1'],
                ele['_embedded']['venues'][0]['city']['name'],
                ele['_embedded']['venues'][0]['state']['stateCode'], ele['_embedded']['venues'][0]['postalCode'])

            # print(event_insertion)
            event_statement = 'INSERT INTO "Events" '
            event_statement += 'VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) '

            cur.execute(event_statement, event_insertion)



    #############################
    # POPULATE POSTAL CODE TABLE
    #############################
    # CSV file obtained from: https://www.aggdata.com/node/86
    with open(csv_file) as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader, None)
        for row in csvreader:
            postalCode_insertion = (None, row[0], row[1], row[2], row[3], row[4], row[5], row[6])

            postalCode_statement ='INSERT INTO "PostalCodes" '
            postalCode_statement += 'VALUES(?, ?, ?, ?, ?, ?, ?, ?) '

            cur.execute(postalCode_statement, postalCode_insertion)


    #############################
    # UPDATE WITH FOREIGN KEYS
    #############################

    # Puts Id from PostalCodes Table into Restaurant and Event Table Zip Codes
    # NOTE: this will return a 5-digit Id code that looks like a zip code but is not

    update_restaurants = '''
        UPDATE Restaurants
        SET locationZip_code = (
        SELECT Id
        FROM PostalCodes as P
        WHERE Restaurants.locationZip_code=P.PostalCode)
        '''
    cur.execute(update_restaurants)

    update_events = '''
        UPDATE Events
        SET PostalCode = (
        SELECT Id
        FROM PostalCodes as P
        WHERE Events.PostalCode=P.PostalCode)
        '''
    cur.execute(update_events)

    conn.commit()
    conn.close()




#######################
# DATA REPRESENTATION 1
#######################
# Data lists for Plotly Table 1:
e_r_name_lst_ename = []
e_r_name_lst_edate = []
e_r_name_lst_rname = []
e_r_name_lst_rrating = []


def ratings(city):
    try:
        conn = sqlite3.connect('food_event.db')
        cur = conn.cursor()
    except Error as e:
        print(e)


    cur.execute("""SELECT Restaurants.name AS [Restaurant Name], Restaurants.rating FROM Restaurants WHERE Restaurants.city like ?""",(city,))

    data_0 = cur.fetchall()
    for row in data_0:
        e_r_name_lst_rname.append(row[0])
        e_r_name_lst_rrating.append(row[1])
    # print (e_r_name_lst_rrating)
    conn.close()

# ratings()



def names_and_ratings(city):
    try:
        conn = sqlite3.connect('food_event.db')
        cur = conn.cursor()
    except Error as e:
        print(e)
    # This query will return a list including the name of an event, the date of that event, the name of a restaurant, and the restaurant's rating
    query_1 = '''
    SELECT E.name AS [Event Name], E.localDate, Restaurants.name AS [Restaurant Name], Restaurants.rating
    FROM Events as E
	JOIN Restaurants ON  E.PostalCode = Restaurants.locationZip_code WHERE Restaurants.city like ?
    '''

    cur.execute(query_1, (city,))
    data = cur.fetchall()
    # print(data)
    for row in data:
        #print(row)
        e_r_name_lst_ename.append(row[0])
        e_r_name_lst_edate.append(row[1])
        # e_r_name_lst_rname.append(row[2])

    conn.close()

# names_and_ratings()

#----------------------------------------------------------------
# This code creates a Plotly Table of Event Name, Event Date, Restauran Name, and Restaurant Rating
#----------------------------------------------------------------
def plotly_table_1():
    trace = go.Table(
        header=dict(values=['Event Name', 'localDate', 'Restaurant Name', 'rating'],
                    line = dict(color='#7D7F80'),
                    fill = dict(color='#a1c3d1'),
                    align = ['left'] * 5),
        cells=dict(values=[e_r_name_lst_ename, e_r_name_lst_edate,
                        e_r_name_lst_rname, e_r_name_lst_rrating],
                   line = dict(color='#7D7F80'),
                   fill = dict(color='#EDFAFF'),
                   align = ['left'] * 5))

    layout = dict(width=500, height=300)
    data = [trace]
    fig = dict(data=data, layout=layout)
    py.plot(fig, filename = 'styled_table')

#----------------------------------------------------------------
# CALLING PLOTLY TABLE - Event Name, Event Date, Restauran Name, and Restaurant Rating
#----------------------------------------------------------------
# plotly_table_1()



#######################
# DATA REPRESENTATION 2
#######################

#-------------------------------------------------------------------------------------------
# CREATING PLOTLY TABLE - Restaurant Name, Restaurant Price Range, Event Name, Event Price Range
#-------------------------------------------------------------------------------------------
rest_street_address =[]
event_venue_name = []
event_venue_street_address = []

def rest_event_address(city):
    try:
        conn = sqlite3.connect('food_event.db')
        cur = conn.cursor()
    except Error as e:
        print(e)

    query_2 = '''
    SELECT Restaurants.name AS [Restaurant Name], Restaurants.streetAdress AS [Restaurant Address],
    E.name AS [Event Name], E.venue AS [Venue], E.streetAdress AS [Event Address]
    FROM Events as E
	JOIN Restaurants ON  E.PostalCode = Restaurants.locationZip_code
    WHERE E.city like ?
    '''

    cur.execute(query_2,(city,))
    data = cur.fetchall()
    for row in data:
        rest_street_address.append(row[1])
        event_venue_name.append(row[3])
        event_venue_street_address.append(row[4])

# rest_event_address()

#-------------------------------------------------------------------------------------------
# This code creates a Plotly Table of Restaurant Name, Restaurant Type, Event Name, Event Type
#-------------------------------------------------------------------------------------------
def plotly_table_2():
    trace = go.Table(
        header=dict(values=['Restaurant Name', 'Restaurant Address', 'Event Name', 'Venue', 'Event Address'],
                    line = dict(color='#7D7F80'),
                    fill = dict(color='#a1c3d1'),
                    align = ['left'] * 5),
        cells=dict(values=[e_r_name_lst_rname, rest_street_address, e_r_name_lst_ename,
                        event_venue_name, event_venue_street_address],
                   line = dict(color='#7D7F80'),
                   fill = dict(color='#EDFAFF'),
                   align = ['left'] * 5))

    layout = dict(width=500, height=300)
    data = [trace]
    fig = dict(data=data, layout=layout)
    py.plot(fig, filename = 'styled_table2')

#-----------------------------------------------------------------------------------------------------
# CALLING PLOTLY TABLE 2 - Restaurant Name, Restaurant Address, Event Name, Event Venue, Event Address
#-----------------------------------------------------------------------------------------------------
#plotly_table_2()



#######################
# DATA REPRESENTATION 3
#######################

#----------------------------------------------------------------
# Lists for Plotly Map of Restaurant and Event Locations
#----------------------------------------------------------------
event_lat_vals = []
event_lon_vals = []
event_text_vals = []
restaurant_lat_vals = []
restaurant_lon_vals = []
restaurant_text_vals = []

def rest_event_location_query(city):
    try:
        conn = sqlite3.connect('food_event.db')
        cur = conn.cursor()
    except Error as e:
        print(e)

    query_3 = '''
    SELECT E.name AS [Event Name], E.longitude, E.latitude, R.name AS [Restaurant Name], R.latitude, R.longitude
    FROM Events as E
	JOIN Restaurants AS R ON  E.PostalCode = R.locationZip_code
    WHERE R.city like ?
    GROUP BY R.name, E.name
    '''
    cur.execute(query_3, (city,))
    data = cur.fetchall()
    for row in data:
        event_lat_vals.append(row[2])
        event_lon_vals.append(row[1])
        event_text_vals.append(row[0])
        restaurant_lat_vals.append(row[4])
        restaurant_lon_vals.append(row[5])
        restaurant_text_vals.append(row[3])

    conn.close()

#----------------------------------------------------------------
# Gets restaurant and event data from SQL:
#----------------------------------------------------------------
# rest_event_location_query()


def plotly_map_r_e_locations():
    try:
        trace1 = dict(
            type='scattergeo',
            locationmode='USA-states',
            lon=event_lon_vals,
            lat=event_lat_vals,
            text=event_text_vals,
            mode='markers',
            marker=dict(
                size=20,
                symbol='star',
                color='red'
            ))
        trace2 = dict(
            type='scattergeo',
            locationmode='USA-states',
            lon=restaurant_lon_vals,
            lat=restaurant_lat_vals,
            text=restaurant_text_vals,
            mode='markers',
            marker=dict(
                size=8,
                symbol='circle',
                color='blue'
            ))

        data = [trace1, trace2]

        min_lat = 10000
        max_lat = -10000
        min_lon = 10000
        max_lon = -10000

        lat_vals = event_lat_vals + restaurant_lat_vals
        lon_vals = event_lon_vals + restaurant_lon_vals
        for str_v in lat_vals:
            v = float(str_v)
            if v < min_lat:
                min_lat = v
            if v > max_lat:
                max_lat = v
        for str_v in lon_vals:
            v = float(str_v)
            if v < min_lon:
                min_lon = v
            if v > max_lon:
                max_lon = v

        center_lat = (max_lat + min_lat) / 2
        center_lon = (max_lon + min_lon) / 2

        max_range = max(abs(max_lat - min_lat), abs(max_lon - min_lon))
        padding = max_range * .10
        lat_axis = [min_lat - padding, max_lat + padding]
        lon_axis = [min_lon - padding, max_lon + padding]

        layout = dict(
            title='Local Restaurants and Events<br>(Hover for site names)',
            geo=dict(
                scope='usa',
                projection=dict(type='albers usa'),
                showland=True,
                landcolor="rgb(250, 250, 250)",
                subunitcolor="rgb(100, 217, 217)",
                countrycolor="rgb(217, 100, 217)",
                lataxis={'range': lat_axis},
                lonaxis={'range': lon_axis},
                center={'lat': center_lat, 'lon': center_lon},
                countrywidth=3,
                subunitwidth=3
            ),
        )

        fig = dict(data=data, layout=layout)
        py.plot(fig, filename='restaurants_and_local_events')
    except ValueError:
        pass

#----------------------------------------------------------------
# Calling Map that Plots Restaurant and Event Locations in Plotly - from SQL data
#----------------------------------------------------------------
# plotly_map_r_e_locations()

#######################
# DATA REPRESENTATION 4
#######################
# dictionary of all restaurant ratings

# BAR CHART OF RATINGS - THIS WORKS: NEEDS A TITLE
def ratings_bar_graph():
    global ratings_dict
    ratings_dict = Counter(e_r_name_lst_rrating)
    # print('inside bar graph function=======')
    data = [go.Bar(
        # Turning dictionary items into lists so they can be utilized in Plotly
        x= list(ratings_dict.keys()),
        y= list(ratings_dict.values())
    )]

    py.plot(data, filename='basic-bar')

# ratings_bar_graph()



####################################
# INTERACTIVE PART
###################################
def load_help_text():
    with open('help.txt') as f:
        return f.read()

def interactive_prompt():
    help_text = load_help_text()
    response_lst = ['chicago', 'san francisco', 'new york', 'ann arbor']
    response = ''
    while response != "exit":

        response = input('Enter the name of a city: ("Chicago, IL", "San Francisco, CA", "New York, NY", "Ann Arbor, MI") ')
        response = response.lower()
        response = response.strip()
        response = response.split(',')
        # print(response)

        if 'help' in response:
            print(help_text)
            continue

        elif 'exit' in response:
            print("bye")
            exit()


        elif response[0] in response_lst:
            query = input("Please enter a command - rating table, address, rating chart, map:  ")
            query = query.lower()

            if 'table' in query:
                ratings(response[0])
                names_and_ratings(response[0])
                plotly_table_1()
                # continue
            elif 'address' in query:
                ratings(response[0])
                names_and_ratings(response[0])
                rest_event_address(response[0])
                plotly_table_2()
                # continue
            elif 'chart' in query:
                ratings(response[0])
                # names_and_ratings(response[0])
                ratings_bar_graph()
            elif 'map' in query:
                rest_event_location_query(response[0])
                plotly_map_r_e_locations()
            else:
                print("Please enter a valid command: ")
                continue
        else:
            print("Please enter a valid response or type help or exit ")
            continue



#----------------
# Call for Data
#----------------
if __name__ == "__main__":
    #---------------------------------
    # CODE TO GET DATA FROM API CALLS
    #---------------------------------
    # yelp_city_lst = ["Chicago, IL", "San Francisco, CA", "New York, NY", "Ann Arbor, MI"]
    # ticket_m_city_lst = ["Chicago", "San Francisco", "New York", "Ann Arbor"]
    #
    # for city in yelp_city_lst:
    #     get_from_yelp("food", city)
    #
    # for city in ticket_m_city_lst:
    #     get_ticketmaster_data(city)

    class Calling_data():
        def __init__(self):
            self.yelp_city_lst = ["Chicago, IL", "San Francisco, CA", "New York, NY", "Ann Arbor, MI"]
            self.ticket_m_city_lst = ["Chicago", "San Francisco", "New York", "Ann Arbor"]

        def calling(self):
            for city in self.yelp_city_lst:
                get_from_yelp("food", city)

            for city in self.ticket_m_city_lst:
                get_ticketmaster_data(city)


    data = Calling_data()
    data.calling()

    #---------------------------------
    # CALL TO CREATE DATABASE
    #---------------------------------
    init_db(DBNAME, CSV)
    interactive_prompt()
