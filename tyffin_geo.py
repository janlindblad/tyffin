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

  # Initialize the atlas datastructure with information from the map
  # database.
  # FIXME: This information is currently loaded from a file, not the web
  #
  # The atlas datastructure has hardcoded information about countries
  # and states. This function adds cities and venues into that structure.
  def init_from_livedata():
    geo_filename = 'fff-global-map.json'
    with open(geo_filename, "rt", encoding="utf-8") as source_file:
      livedata = json.loads(source_file.read())
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

  # The canonical_names data structure contains names that we sometimes 
  # get from Google Maps, which are wrong. At least from our perspective.
  # the canonical names remap such names to the name we want.
  canonical_names = {
    COUNTRY:{
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
    STATE:{
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

  atlas = {"Earth":(COUNTRY, {
    ## Example structure:
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
    "Abkhazia":Z,
    "Afghanistan":Z,
    "Albania":Z,
    "Algeria":Z,
    "Andorra":Z,
    "Angola":Z,
    "Antarctica":Z,
    "Antigua and Barbuda":Z,
    "Arctic":Z,
    "Argentina":Z,
    "Armenia":Z,
    "Aruba":Z,
    "Assam":Z,
    "Australia":Z,
    "Austria":Z,
    "Azerbaijan":Z,
    "Bahrain":Z,
    "Bangladesh":(STATE,{
      "Dhaka":Z,
      "Noakhali":Z,
      "Chittagong":Z,
      "Jessore":Z,
      "Tangail":Z,
      "Satkhira":Z,
      "Gazipur":Z,
      "Khulna":Z,
      "Feni":Z,
      "Rajshahi":Z,
      "Kushtia":Z,
      "Gaibandha":Z,
      "Jaipurhat":Z,
      "Jamalpur":Z,
      "Barisal":Z,
      "Gopalganj":Z,
      "Satkhira":Z,
      "Netrokona":Z,
      "Pirojpur":Z,
      "Barguna":Z,
      "Jhalokati":Z,
      "Bhola":Z,
      "Sunamganj":Z,
      "Habiganj":Z,
      "Moulvi Bazar":Z,
      "Sherpur":Z,
      "Mymensingh":Z,
      "Rangpur":Z,
      "Sylhet":Z,
      "Brahmanbaria":Z,
      "Cox's Bazar":Z,
      "Narayanganj Sadar Upazila":Z,
      "Thakurgaon":Z,
      "Nilphamari":Z,
      "Meherpur":Z,
      "Lakshmipur":Z,
      "Narsingdi":Z,
      "Kishoreganj":Z,
      "Chuadanga":Z,
      "Magura":Z,
      "Bogra":Z,
      "Pabna":Z,
      "Chapainawabganj":Z,
      "Natore":Z,
      "Savar Upazila":Z,
      "Comilla":Z,
      "Faridpur":Z,
    }),
    "Belarus":Z,
    "Belgium":Z,
    "Belize":Z,
    "Benin":Z,
    "Bermuda":Z,
    "Bhutan":Z,
    "Bolivia":Z,
    "Bosnia and Herzegovina":Z,
    "Botswana":Z,
    "Brazil":Z,
    "British Virgin Islands":Z,
    "Brunei":Z,
    "Bulgaria":Z,
    "Burkina Faso":Z,
    "Burundi":Z,
    "CNMI":Z,
    "Cambodia":Z,
    "Cameroon":Z,
    "Canada":(STATE,{
      "AB-Alberta":Z,
      "BC-British Columbia":Z,
      "MB-Manitoba":Z,
      "NB-New Brunswick":Z,
      "NL-Newfoundland and Labrador":Z,
      "NS-Nova Scotia":Z,
      "NT-Northwest Territories":Z,
      "NU-Nunavut":Z,
      "ON-Ontario":Z,
      "PE-Prince Edward Island":Z,
      "QC-Quebec":Z,
      "SK-Saskatchewan":Z,
      "YT-Yukon":Z,
    }),
    "Caribbean":Z,
    "Cayman Islands":Z,
    "Chile":Z,
    "China":Z,
    "Colombia":Z,
    "Costa Rica":Z,
    "Croatia":Z,
    "Cuba":Z,
    "Curaçao":Z,
    "Cyprus":Z,
    "Czechia":Z,
    "Côte d'Ivoire":Z,
    "Democratic Republic of the Congo":Z,
    "Denmark":Z,
    "Djibouti":Z,
    "Dominica":Z,
    "Dominican Republic":Z,
    "Ecuador":Z,
    "Egypt":Z,
    "El Salvador":Z,
    "Equatorial Guinea":Z,
    "Estonia":Z,
    "Eswatini":Z,
    "Ethiopia":Z,
    "Famagusta":Z,
    "Faroe Islands":Z,
    "Fiji":Z,
    "Finland":Z,
    "France":Z,
    "Gazimağusa":Z,
    "Georgia":Z,
    "Germany":Z,
    "Ghana":Z,
    "Gibraltar":Z,
    "Gilgit":Z,
    "Greece":Z,
    "Greenland":Z,
    "Grenada":Z,
    "Guadeloupe":Z,
    "Guam":Z,
    "Guatemala":Z,
    "Guernsey":Z,
    "Guinea":Z,
    "Guinea-Bissau":Z,
    "Guyana":Z,
    "Haiti":Z,
    "Honduras":Z,
    "Hong Kong":Z,
    "Hungary":Z,
    "Iceland":Z,
    "India":(STATE,{
      "Tamil Nadu":Z,
      "Bihar":Z,
      "Mumbai":Z,
      "West Bengal":Z,
      "Maharashtra":Z,
      "Jharkhand":Z,
      "Telangana":Z,
      "Madhya Pradesh":Z,
      "Karnataka":Z,
      "Haryana":Z,
      "Kerala":Z,
      "Punjab":Z,
      "Uttar Pradesh":Z,
      "Uttarakhand":Z,
      "Delhi":Z,
      "Chhattisgarh":Z,
      "Assam":Z,
      "Nagaland":Z,
      "Andhra Pradesh":Z,
      "Gujarat":Z,
      "Odisha":Z,
      "Rajasthan":Z,
      "Goa":Z,
      "Jammu & Kashmir":Z,
      "Himachal Pradesh":Z,
      "Chandigarh":Z,
      "Meghalaya":Z,
    }),
    "Indonesia":Z,
    "Iran":Z,
    "Iraq":Z,
    "Ireland":Z,
    "Isle of Man":Z,
    "Israel":Z,
    "Italy":Z,
    "Jamaica":Z,
    "Jammu and Kashmir":Z,
    "Japan":Z,
    "Jersey":Z,
    "Jordan":Z,
    "Kazakhstan":Z,
    "Kenya":Z,
    "Kiribati":Z,
    "Kosovo":Z,
    "Kuwait":Z,
    "Kyrenia":Z,
    "Kyrgyzstan":Z,
    "Latvia":Z,
    "Lebanon":Z,
    "Liberia":Z,
    "Libya":Z,
    "Liechtenstein":Z,
    "Lithuania":Z,
    "Luxembourg":Z,
    "Macedonia":Z,
    "Madagascar":Z,
    "Malawi":Z,
    "Malaysia":Z,
    "Maldives":Z,
    "Mali":Z,
    "Malta":Z,
    "Martinique":Z,
    "Mauritania":Z,
    "Mauritius":Z,
    "Mayotte":Z,
    "Mexico":Z,
    "Moldova":Z,
    "Mongolia":Z,
    "Montenegro":Z,
    "Morocco":Z,
    "Mozambique":Z,
    "Myanmar":Z,
    "Namibia":Z,
    "Nepal":Z,
    "Netherlands":Z,
    "New Caledonia":Z,
    "New Zealand":Z,
    "Nicaragua":Z,
    "Niger":Z,
    "Nigeria":Z,
    "Norfolk Island":Z,
    "North Macedonia":Z,
    "Norway":Z,
    "Pakistan":Z,
    "Palestine":Z,
    "Panama":Z,
    "Papua New Guinea":Z,
    "Paraguay":Z,
    "Peru":Z,
    "Philippines":Z,
    "Poland":Z,
    "Portugal":Z,
    "Puerto Rico":Z,
    "Qatar":Z,
    "Romania":Z,
    "Russia":Z,
    "Rwanda":Z,
    u"Réunion":Z,
    "San Marino":Z,
    "Senegal":Z,
    "Serbia":Z,
    "Seychelles":Z,
    "Sierra Leone":Z,
    "Singapore":Z,
    "Slovakia":Z,
    "Slovenia":Z,
    "Somalia":Z,
    "South Africa":Z,
    "South Korea":Z,
    "Spain":Z,
    "Sri Lanka":Z,
    "St Kitts & Nevis":Z,
    "St Vincent and the Grenadines":Z,
    "Sudan":Z,
    "Svalbard and Jan Mayen":Z,
    "Sweden":Z,
    "Switzerland":Z,
    "Syria":Z,
    "Taiwan":Z,
    "Tanzania":Z,
    "Thailand":Z,
    "The Bahamas":Z,
    "The Gambia":Z,
    "Togo":Z,
    "Tokelau":Z,
    "Trinidad and Tobago":Z,
    "Tunisia":Z,
    "Turkey":Z,
    "Turks and Caicos Islands":Z,
    "U.S. Virgin Islands":Z,
    "UK":Z,
    "USA":(STATE,{
      "AL-Alabama":Z,
      "AK-Alaska":Z,
      "AZ-Arizona":Z,
      "AR-Arkansas":Z,
      "CA-California":Z,
      "CO-Colorado":Z,
      "CT-Connecticut":Z,
      "DE-Delaware":Z,
      "FL-Florida":Z,
      "GA-Georgia":Z,
      "HI-Hawaii":Z,
      "ID-Idaho":Z,
      "IL-Illinois":Z,
      "IN-Indiana":Z,
      "IA-Iowa":Z,
      "KS-Kansas":Z,
      "KY-Kentucky":Z,
      "LA-Louisiana":Z,
      "ME-Maine":Z,
      "MD-Maryland":Z,
      "MA-Massachusetts":Z,
      "MI-Michigan":Z,
      "MN-Minnesota":Z,
      "MS-Mississippi":Z,
      "MO-Missouri":Z,
      "MT-Montana":Z,
      "NE-Nebraska":Z,
      "NV-Nevada":Z,
      "NH-New Hampshire":Z,
      "NJ-New Jersey":Z,
      "NM-New Mexico":Z,
      "NY-New York":Z,
      "NC-North Carolina":Z,
      "ND-North Dakota":Z,
      "OH-Ohio":Z,
      "OK-Oklahoma":Z,
      "OR-Oregon":Z,
      "PA-Pennsylvania":Z,
      "RI-Rhode Island":Z,
      "SC-South Carolina":Z,
      "SD-South Dakota":Z,
      "TN-Tennessee":Z,
      "TX-Texas":Z,
      "UT-Utah":Z,
      "VT-Vermont":Z,
      "VA-Virginia":Z,
      "WA-Washington":Z,
      "DC-District of Columbia":Z,
      "WV-West Virginia":Z,
      "WI-Wisconsin":Z,
      "WY-Wyoming":Z,
    }),
    "Uganda":Z,
    "Ukraine":Z,
    "United Arab Emirates":Z,
    "Uruguay":Z,
    "Uzbekistan":Z,
    "Vanuatu":Z,
    "Venezuela":Z,
    "Vietnam":Z,
    "Yemen":Z,
    "Zambia":Z,
    "Zimbabwe":Z,
    "Åland Islands":Z,
  })}
