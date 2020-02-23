#   FridaysForFuture TypeForm Input Generator
#   Copyright (C) 2020 Jan Lindblad, Lena Douglas
# 
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
# 
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
# 
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys, os
import requests, json

# The Geo class handles the atlas data structure, which lists all
# countries, states, cities, and venues known to FFF.

class Geo:
  
  # The atlas contains names of different sub-categories:
  EARTH = "earth"
  COUNTRY = "country"
  STATE = "state"
  CITY = "city/county"
  VENUE = "venue"
  Z = None
  
  # The atlas can be filtered in two levels, filter1 and filter2, corresponding to the levels
  #   Region    - which could include one or many countries, for example a whole contintent, and
  #   District  - which could be a geographical part of the Region (e.g. the North part of Europe) 
  #               or a group of states.
  # The countries / states can be grouped in different ways by editing the data in the 
  # .csv-file "filtered_geo_data.csv"
  
  def __init__(self, _filter1, _filter2):
    
    Geo.canonical_names = Geo.define_canonical_names()
    Geo.atlas = Geo.define_atlas(_filter1, _filter2)
    
    return
  

  # Initialize the atlas datastructure with information from the map
  # database. Normally this is fetched from the open json file on the
  # web, but a filename may also be specified.
  #
  # The atlas datastructure has hardcoded information about countries
  # and states. This function adds cities and venues into that structure.
  def init_from_livedata(geo_filename = None):
    if geo_filename:
      with open(geo_filename, "rt", encoding="utf-8") as source_file:
        livedata = json.loads(source_file.read())
    else:
      reply = requests.get("https://allforeco.github.io/fridaysforfuture/fff-global-map.json")
      if reply.status_code != 200:
        raise Exception("Could not download fff data from servers")
      livedata = reply.json()
    country_names = Geo.atlas['Earth'][1]
    
    # Loop over all the map pins
    for live in livedata['data']:
      # If a map pin doesn't have "Town" information, it's broken, skip it
      if 'Town' not in live: continue
      #print(f"live={live}")

      # Split town and venue names from map pin data
      live_city_venue = Geo.get_city_name(live['Town']).split(', ')
      live_city = live_city_venue[-1]
      live_venue = live_city_venue[-2] if len(live_city_venue) > 1 else None

      # Split country and state names from map pin data
      live_country_state = Geo.get_city_name(live['Country']).split('--')
      live_country = live_country_state[0]
      if live_country not in Geo.atlas['Earth'][1]:
        if live_country in Geo.canonical_names[Geo.COUNTRY]:
          live_country = Geo.canonical_names[Geo.COUNTRY][live_country]
        else:
          # The country name is not in the atlas structure, skip this pin
          print(f"Skipping country {live_country}")
          continue
      if len(live_country_state) > 1: 
        # This pin is in a country which has states
        live_state = live_country_state[1] 
        if live_state not in Geo.atlas['Earth'][1][live_country][1]:
          if live_state in Geo.canonical_names[Geo.STATE][live_country]:
            live_state = Geo.canonical_names[Geo.STATE][live_country][live_state]
        #print(f"Adding {live_country}:{live_state}:{live_city}")
        if Geo.atlas['Earth'][1][live_country] == Geo.Z:
          Geo.atlas['Earth'][1][live_country] = (Geo.STATE, {})
        if live_state not in Geo.atlas['Earth'][1][live_country][1] or Geo.atlas['Earth'][1][live_country][1][live_state] == Geo.Z:
          Geo.atlas['Earth'][1][live_country][1][live_state] = (Geo.CITY, {})
        if live_venue:
          # This map pin has a venue
          if live_city not in Geo.atlas['Earth'][1][live_country][1][live_state][1]:
            Geo.atlas['Earth'][1][live_country][1][live_state][1][live_city] = (Geo.VENUE, {})
          Geo.atlas['Earth'][1][live_country][1][live_state][1][live_city][1][live_venue] = Geo.Z
        else:
          # This map pin doesn't have a venue
          Geo.atlas['Earth'][1][live_country][1][live_state][1][live_city] = Geo.Z
      else:
        # This pin is in a country which doesn't have states
        #print(f"Adding {live_country}:{live_city}")
        if live_country in Geo.atlas['Earth'][1]:
          if Geo.atlas['Earth'][1][live_country] == Geo.Z:
            Geo.atlas['Earth'][1][live_country] = (Geo.CITY, {})
          if live_venue:
            # This map pin has a venue
            if live_city not in Geo.atlas['Earth'][1][live_country][1]:
              Geo.atlas['Earth'][1][live_country][1][live_city] = (Geo.VENUE, {})
            Geo.atlas['Earth'][1][live_country][1][live_city][1][live_venue] = Geo.Z
          else:
            # This map pin doesn't have a venue
            Geo.atlas['Earth'][1][live_country][1][live_city] = Geo.Z
    #print(f"Atlas={Geo.atlas}")

  # This function removes unwanted words from the Town name, as 
  # received from Google Maps. Names often contain Zip codes, or 
  # unwanted words like "Prefecture" or "Municipality"
  def clean_zip(name_with_zip):
    def is_clean_word(word):
      tipp = "0123456789()"
      for ch in word:
        if ch in tipp:
          return False
      return True
    name_words = name_with_zip.split(" ")
    clean_name = []
    # We don't want words containing these characters and words
    for name_word in name_words:
      if is_clean_word(name_word) and name_word not in ['Municipality', 'Prefecture', 'District']:
        clean_name += [name_word]
    result = " ".join([w for w in clean_name if w != ''])
    return result

  # Returns the actual city name part of a Google Maps name
  def get_city_name(raw_city_name):
    return Geo.clean_zip(raw_city_name.split(",")[-1])

  # Returns the name of a location regardless if it has sub-locations
  # or not
  def get_label(geo_info):
    return geo_info[0] if isinstance(geo_info, tuple) else geo_info

  # Returns the location tuple for a given atlas path
  def get_named_loc(geo_path):
    p = Geo.atlas["Earth"]
    for pname in geo_path:
      if p == None:
        print(f"### geo_get_path({geo_path}): {pname} not found")
        return None
      if not isinstance(p, tuple):
        print(f"### geo_get_path({geo_path}): {pname} gives '{p}', strange format")
        return None
      if pname in p[1]:
        p = p[1][pname]
      else:
        return None
    return p

  # Return the subcategory string ("country", etc) from a location tuple
  def get_subcat(geo_tuple):
    return geo_tuple[0]
  # Return the location name("USA", "Paris", etc) from a location tuple
  def get_name(geo_tuple):
    return geo_tuple[1]
  
  def define_canonical_names():
      # The canonical_names data structure contains names that we sometimes 
    # get from Google Maps, which are wrong. At least from our perspective.
    # the canonical names remap such names to the name we want.
    canonical_names = {
      Geo.COUNTRY:{
        "Trikomo":"Cyprus",
        "Maharashtra":"India",
        "Kalimantan":"Indonesia",
        "Prizren":"Kosovo",
        "Prishtina":"Kosovo",
        "Pulwama":"Jammu and Kashmir",
        "Muzaffarabad":"Jammu and Kashmir",
        "Sopore":"Jammu and Kashmir",
        "Jammu":"Jammu and Kashmir",
        "Kashmir":"Jammu and Kashmir",
        "Kathua":"Jammu and Kashmir",
        "Sonamarg":"Jammu and Kashmir",
        "Boujdour Province": "Morocco",
        "Kotli":"Pakistan",
        "Shigar":"Pakistan",
        "Yasin Valley":"Pakistan",
        "PR":"Puerto Rico",
        "Jeddah Saudi Arabia":"Saudi Arabia",
        "Riyadh Saudi Arabia":"Saudi Arabia",
        "Umeå":"Sweden",  
        "Umeå Universitet":"Sweden",  
        "united states": "USA",
        "united kingdom": "UK",
        "Dubai - United Arab Emirates":"United Arab Emirates",
      },
      Geo.STATE:{
        "Bangladesh":{},
        "Canada":{
          "AB":"AB-Alberta",
          "BC":"BC-British Columbia",
          "MB":"MB-Manitoba",
          "NB":"NB-New Brunswick",
          "NL":"NL-Newfoundland and Labrador",
          "NS":"NS-Nova Scotia",
          "NT":"NT-Northwest Territories",
          "NU":"NU-Nunavut",
          "ON":"ON-Ontario",
          "PE":"PE-Prince Edward Island",
          "QC":"QC-Quebec",
          "SK":"SK-Saskatchewan",
          "YT":"YT-Yukon",
        },
        "India":{},
        "USA":{
          "AL":"AL-Alabama",
          "AK":"AK-Alaska",
          "AZ":"AZ-Arizona",
          "AR":"AR-Arkansas",
          "CA":"CA-California",
          "CO":"CO-Colorado",
          "CT":"CT-Connecticut",
          "DE":"DE-Delaware",
          "FL":"FL-Florida",
          "GA":"GA-Georgia",
          "HI":"HI-Hawaii",
          "ID":"ID-Idaho",
          "IL":"IL-Illinois",
          "IN":"IN-Indiana",
          "IA":"IA-Iowa",
          "KS":"KS-Kansas",
          "KY":"KY-Kentucky",
          "LA":"LA-Louisiana",
          "ME":"ME-Maine",
          "MD":"MD-Maryland",
          "MA":"MA-Massachusetts",
          "MI":"MI-Michigan",
          "MN":"MN-Minnesota",
          "MS":"MS-Mississippi",
          "MO":"MO-Missouri",
          "MT":"MT-Montana",
          "NE":"NE-Nebraska",
          "NV":"NV-Nevada",
          "NH":"NH-New Hampshire",
          "NJ":"NJ-New Jersey",
          "NM":"NM-New Mexico",
          "NY":"NY-New York",
          "NC":"NC-North Carolina",
          "ND":"ND-North Dakota",
          "OH":"OH-Ohio",
          "OK":"OK-Oklahoma",
          "OR":"OR-Oregon",
          "PA":"PA-Pennsylvania",
          "RI":"RI-Rhode Island",
          "SC":"SC-South Carolina",
          "SD":"SD-South Dakota",
          "TN":"TN-Tennessee",
          "TX":"TX-Texas",
          "UT":"UT-Utah",
          "VT":"VT-Vermont",
          "VA":"VA-Virginia",
          "WA":"WA-Washington",
          "DC":"DC-District of Columbia",
          "WV":"WV-West Virginia",
          "WI":"WI-Wisconsin",
          "WY":"WY-Wyoming",
        },
      },
    }
    return canonical_names
    
  def define_atlas(_filter1, _filter2):
  # _filter1 and _filter2 are filters to filter the country and state data with
  
  # atlas data structure
    #
    # The atlas data structure is built up as a set of a dictionary where 
    # each element is either None (called Z in the structures), when there
    # is no further data about this place, or a 2-tuple (level, dict), 
    # where level is a string indicating if what the members of the dict
    # are, e.g. countries, states, cities or venues.
    #
    # The structure is hard initialized to contain the known list of 
    # countries and states around the world, as given by the Google Maps API
    # Before the structure is used, it is filled with all the cities and 
    # venues that have been reported in any FFF forms so far. This is done
    # by calling Geo.init_from_livedata()
    
    # The data will be filtered if _filter1 or _filter2 are given, i.e. only 
    # countrys/states that match the filters will be included.

    ## Example structure:
    ##atlas = {"Earth":(COUNTRY, {
      ##  "Abkhazia":(CITY, {
      ##    "Sokhumi":Z,
      ##  }),
      ##  "Sweden":(CITY, {
      ##    "Abisko":Z,
      ##    "Stockholm":(VENUE, {
      ##      "Akalla":Z,
      ##      "Bromma":Z,
      ##      "Mynttorget":Z,
      ##    }),
      ##    "Alingsås":Z,
      ##    "Ammarnäs":Z,
      ##    "Aneby":Z,
      ##    "Arboga":Z,
      ##    "Arjeplog":Z,
      ##    "Arvika":Z,
      ##    "Avesta":Z,
      ##  }),
      ##  "USA":(STATE, {
      ##    "NY-New York":(CITY, {
      ##      "New York":(VENUE, {
      ##        "Bronx":Z,
      ##        "Central Park":Z,
      ##        "UN Building":Z,
      ##      }),
      ##      "Newark":Z,
      ##    }),
      ##    "AL-Alabama":Z,
      ##  }),
      ##  "France":(CITY, {
      ##    "Paimpol":Z,
      ##    "Paris":(VENUE, {
      ##      "Gare du Nord":Z,
      ##      "Champs de Mars":Z,
      ##    }),
      ##    "Pau":Z,
      ##    "Pavie":Z,
      ##    "Payrac":Z,
      ##    "Perpignan":Z,
      ##    "Pierrelatte":Z,
      ##    "Versailles":(VENUE,{
      ##      "Place d'Armes":Z,
      ##    }),
      ##    "Plaimpied-Givaudins":Z,
      ##    "Ploërmel":Z,
      ##    "Plœuc-L'Hermitage":(VENUE, {
      ##      "Plœuc-sur-Lié":Z,
      ##    }),
      ##    "Poitiers":Z,
      ##    "Pont-Audemer":Z,
      ##    "Pont-l'Abbé":Z,
      ##  }),
      
    
    # file to read geo data from
    geo_data_filename = "filtered_geo_data.csv"
    
    # columns in geo_data_filename
    col_filter1 = 0
    col_filter2 = 1
    col_country = 2
    col_state = 3
    
    f = open(geo_data_filename, "r", encoding="latin-1")
    # skip the first line which is the header line
    line = f.readline() 
    
    countries = {}
    for line in f:
      words = [x.strip() for x in line.split(',')]
        
      # check if the filters match
      if len(_filter1) > 0 and words[col_filter1] != _filter1:
        continue
      if len(_filter2) > 0 and words[col_filter2] != _filter2:
        continue
        
      # if we got this far, both filters are OK    
      country = words[col_country]
          
      if len(words[col_state])==0: # this country does not have states
        if country in countries:
            print('Country ' + country + ' has already been added, is this a duplicate?')
        else: # add the country
          countries[country] = Geo.Z                
      else: # this country does have states to add
        state = words[col_state]
        if not country in countries:
            # this is the first state
            states = {}
        # add the new state
        states[state] = Geo.Z
        # add the states to the country
        country = (Geo.STATE, states)
        # add the country again
        countries[words[col_country]] = country

    countries = (Geo.COUNTRY, countries)
    atlas = {'Earth': countries}    
    return atlas
    
if __name__ == '__main__':
  main()