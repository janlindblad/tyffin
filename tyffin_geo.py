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

EARTH = "earth"
COUNTRY = "country"
STATE = "state"
CITY = "city/county"
VENUE = "venue"
Z = None

def geo_get_label(geo_info):
  return geo_info[0] if isinstance(geo_info, tuple) else geo_info

def geo_get_title(geo_subcat, geo_path):
  path = geo_path[1:]
  if path == []:
    return f"Which country is the event in?"
  return f"Which {geo_subcat} in {path[-1]} is the event in?"

canonical_names = {
  COUNTRY:{
#      "Earth":Z,
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
    "Boujdour Province": "Morocco",
    "Kotli":"Pakistan",
    "Shigar":"Pakistan",
    "Yasin Valley":"Pakistan",
    "PR":"Puerto Rico",
    "Jeddah Saudi Arabia":"Saudi Arabia",
    "Riyadh Saudi Arabia":"Saudi Arabia",
    "Umeå Universitet":"Sweden",  
    "Dubai - United Arab Emirates":"United Arab Emirates",
  }
}

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
      "Bangladesh":Z,
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
      "Canada":Z,
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
      "India":Z,
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
      "USA":Z,
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
