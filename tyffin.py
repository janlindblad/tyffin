#!/usr/bin/env python3.6
#
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

import sys, os, getopt
import requests, json, uuid
from typeform import Typeform
from tyffin_geo import *

geo_filename = 'fff-global-map.json'
# json global constants
true = True
false = False

class Formtree:
  def __init__(self, form_id):
    self.tree = self.fetch_typeform(form_id)
    with open(geo_filename, "rt", encoding="utf-8") as source_file:
      self.geo_live = json.loads(source_file.read())
      self.init_geo_data()
    self.fields = []
    self.logic = []

  def fetch_typeform(self, form_id):
    token_env = 'TYPEFORM_TOKEN'
    if token_env not in os.environ:
      raise Exception(f"Environment variable '{token_env}' not set")
    forms = Typeform(os.environ[token_env]).forms
    form_dict = forms.get(form_id)
    return form_dict

  def load_typeform_file(self, source_filename):
    with open(source_filename, "rt", encoding="utf-8") as source_file:
      self.tree = json.loads(source_file.read())

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
      if is_clean_word(name_word) and name_word not in ['Municipality', 'Prefecture']:
        clean_name += [name_word]
    result = " ".join([w for w in clean_name if w != ''])
    return result

  def get_city_name(raw_city_name):
    return Formtree.clean_zip(raw_city_name.split(",")[-1])

  def init_geo_data(self):
    country_names = atlas['Earth'][1]
    for live in self.geo_live['data']:
      if 'Town' not in live: continue
      #print(f"live={live}")
      live_city_venue = Formtree.get_city_name(live['Town']).split(', ')
      live_city = live_city_venue[-1]
      live_venue = live_city_venue[-2] if len(live_city_venue) > 1 else None
      live_country_state = Formtree.get_city_name(live['Country']).split('--')
      live_country = live_country_state[0]
      if live_country not in atlas['Earth'][1]:
        print(f"Skipping country {live_country}")
        continue
      if len(live_country_state) > 1: # Has state
        live_state = live_country_state[1] 
        if atlas['Earth'][1][live_country] == Z:
          atlas['Earth'][1][live_country] = (STATE, {})
        if live_state not in atlas['Earth'][1][live_country][1]:
          atlas['Earth'][1][live_country][1][live_state] = (CITY, {})
        if live_venue:
          if live_city not in atlas['Earth'][1][live_country][1][live_state][1]:
            atlas['Earth'][1][live_country][1][live_state][1][live_city] = (VENUE, {})
          atlas['Earth'][1][live_country][1][live_state][1][live_city][1][live_venue] = Z
        else:
          atlas['Earth'][1][live_country][1][live_state][1][live_city] = Z
      else:
        if atlas['Earth'][1][live_country] == Z:
          atlas['Earth'][1][live_country] = (CITY, {})
        if live_venue:
          if live_city not in atlas['Earth'][1][live_country][1]:
            atlas['Earth'][1][live_country][1][live_city] = (VENUE, {})
          atlas['Earth'][1][live_country][1][live_city][1][live_venue] = Z
        else:
          atlas['Earth'][1][live_country][1][live_city] = Z
    print(f"Atlas={atlas}")

  def gen_uuid():
    return str(uuid.uuid4())

  def make_geo_qs(self):
    self._make_geo_rec('Earth', atlas['Earth'], [])

  def _make_geo_rec(self, geo_name, geo_info, geo_path):
    (geo_subcat, geo_sub) = geo_info
    new_path = geo_path + [geo_name]
    this_qid = Formtree.gen_uuid()
    label_other = '== Other =='
    self.fields += [{
      "title": geo_get_title(geo_subcat, new_path),
      "ref": this_qid,
      "properties": {
          "alphabetical_order": true,
          "randomize": false,
          #"allow_multiple_selection": false,
          #"allow_other_choice": true if geo_subcat not in [COUNTRY, STATE] else false,
          #"vertical_alignment": true,
          "choices": [
              {
                  "label": geo_get_label(geo_loc)
              } for geo_loc in geo_sub if geo_loc
          ] + ([{
                  "label": label_other
          }] if geo_subcat not in [COUNTRY, STATE] else [])
      },
      "validations": {
          "required": true
      },
      "type": "dropdown"
      #"type": "multiple_choice"
    }]
    actions = []
    for geo_loc in geo_sub:
      if not isinstance(geo_sub[geo_loc], tuple):
        continue
      next_q = self._make_geo_rec(geo_loc, geo_sub[geo_loc], new_path)
      if next_q:
        actions += [{
            "action": "jump",
            "details": {
                "to": {
                    "type": "field",
                    "value": next_q
                }
            },
            "condition": {
                "op": "equal",
                "vars": [
                    {
                        "type": "field",
                        "value": this_qid
                    },
                    {
                        "type": "constant",
                        "value": geo_loc
                    }
                ]
            }
        }]

    self.logic += [{
        "type": "field",
        "ref": this_qid,
        "actions": actions + [
            {
                "action": "jump",
                "details": {
                    "to": {
                        "type": "thankyou",
                        "value": "default_tys"
                    }
                },
                "condition": {
                    "op": "always",
                    "vars": []
                }
            }
        ]
    }]
    return this_qid

  def merge_changes(self):
    self.tree['fields'] += self.fields
    if 'logic' not in self.tree:
      self.tree['logic'] = []
    self.tree['logic'] += self.logic

  def write(self, output_file):
    with open(output_file, "wt", encoding="utf-8") as out:
      out.write(json.dumps(self.tree, indent=2))

def usage():
  print("Hej")#FIXME

def main():
  input_file = None
  output_file = None
  try:
    opts, args = getopt.getopt(sys.argv[1:],"hi:o:",
      ["help", "input=", "output=", "debug"])
  except getopt.GetoptError:
    usage()
    sys.exit(2)
  for opt, arg in opts:
    if opt in ('-h', '--help'):
      usage()
      sys.exit()
    elif opt in ("-i", "--input"):
      input_file = arg
    elif opt in ("-o", "--output"):
      output_file = arg

  tree = Formtree('DFFFuY')
  #tree.clean_prototypes()
  tree.make_geo_qs()
  tree.merge_changes()
  tree.write(output_file)

if __name__ == '__main__':
  main()
