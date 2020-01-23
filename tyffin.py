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
from tyffin_geo import Geo

# json global constants
true = True
false = False

class Formtree:
  master_typeform = 'DFFFuY'

  def __init__(self, form_id):
    self.tree = self.fetch_typeform(form_id)
    if 'logic' not in self.tree:
      self.tree['logic'] = []
    Geo.init_from_livedata()
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

  def gen_uuid():
    return str(uuid.uuid4())

  def make_geo_qs(self):
    self.ref_jump_back_q = self.find_ref_for_title('How many people')
    self.ref_first_place_q = self._make_geo_rec('Earth', Geo.atlas['Earth'], [])

  def _make_geo_rec(self, geo_name, geo_info, geo_path):
    (geo_subcat, geo_sub) = geo_info
    new_path = geo_path + [geo_name]
    this_qid = Formtree.gen_uuid()
    label_other = '== Other =='
    self.fields += [{
      "title": Geo.get_title(geo_subcat, new_path),
      "ref": this_qid,
      "properties": {
          "alphabetical_order": true,
          "randomize": false,
          #"allow_multiple_selection": false,
          #"allow_other_choice": true if geo_subcat not in [COUNTRY, STATE] else false,
          #"vertical_alignment": true,
          "choices": [
              {
                  "label": Geo.get_label(geo_loc)
              } for geo_loc in geo_sub if geo_loc
          ] + ([{
                  "label": label_other
          }] if geo_subcat not in [Geo.COUNTRY, Geo.STATE] else [])
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
                        "type": "field",
                        "value": self.ref_jump_back_q
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

  def clean_prototypes(self):
    deleted_refs = {'914f7827-62cd-413a-8bea-0f11b1d1d974':0}
    deleted_count = 0
    for (n,q) in enumerate(list(self.tree['fields'])):
      question_words = q['title'].split(" ")
      if question_words[0] == "Which" and question_words[1] in [
          Geo.COUNTRY, Geo.STATE, Geo.CITY, Geo.VENUE]:
        #print(f"Cleaning out '{q['title']}:{q}'")
        deleted_refs[q['ref']] = None
        del self.tree['fields'][n - deleted_count]
        deleted_count += 1
    print(f"Cleaned out {deleted_count} questions")
    deleted_count = 0
    for (n,j) in enumerate(list(self.tree['logic'])):
      #{"actions": [ { "details": { "to": { "value": ]
      if j['ref'] in deleted_refs or j.get('actions',[{}])[0].get('details',{}).get('to',{}).get('value') in deleted_refs:
        print(f"Cleaning out logic jump {j['ref']}")
        del self.tree['logic'][n - deleted_count]
        deleted_count += 1
    print(f"Cleaned out {deleted_count} logic jumps")

  def find_ref_for_title(self, title_start):
    for q in self.tree['fields']:
      #print(f"Looking for {title_start} in {q['title']}")
      if q['title'].startswith(title_start):
        return q['ref']
    print(f"### Did not find any question starting '{title_start}'")
    return None

  def add_jump_out_logic(self):
    ref_jump_out_q = self.find_ref_for_title('What time of day')
    self.logic += [{
        "type": "field",
        "ref": ref_jump_out_q,
        "actions": [
            {
                "action": "jump",
                "details": {
                    "to": {
                        "type": "field",
                        "value": self.ref_first_place_q
                    }
                },
                "condition": {
                    "op": "always",
                    "vars": []
                }
            }
        ]
    }]

  def merge_changes(self):
    self.tree['fields'] += self.fields
    self.tree['logic'] += self.logic

  def validate_refs(self):
    fields = {}
    for q in self.tree['fields']:
      fields[q['ref']] = 0
    for j in self.tree['logic']:
      if 'ref' not in j:
        print(f"### No ref in jump")
        continue
      if j['ref'] not in fields:
        print(f"### Jump from unknown field {j['ref']}")
        continue
      if 'actions' not in j:
        print(f"### No actions in jump: {j}")
        continue
      for act in j['actions']:
        if 'details' not in act:
          print(f"### No details in jump: {j}")
          continue
        if 'to' not in act['details']:
          print(f"### No to in jump")
          continue
        if 'value' not in act['details']['to']:
          print(f"### No value in jump")
          continue
        if act['details']['to']['value'] not in fields:
          print(f"### Jump to unknown field {act['details']['to']['value']}")
          continue
        if 'condition' not in act:
          print(f"### No condition in jump")
          continue
        if 'vars' not in act['condition']:
          print(f"### No vars in jump")
          continue
        for var in act['condition']['vars']:
          if 'value' not in var:
            print(f"### No value in jump condition")
            continue
          if var['value'] not in fields:
            print(f"### Jump reference to unknown field {var['value']}")
            continue
    for f in fields:
      print(f"{f} : {fields[f]}")

  def write(self, output_file):
    with open(output_file, "wt", encoding="utf-8") as out:
      out.write(json.dumps(self.tree, indent=2))

def usage():
  print("Hej")#FIXME

def main():
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
    elif opt in ("-o", "--output"):
      output_file = arg


  tree = Formtree(Formtree.master_typeform)  
  tree.clean_prototypes()
  tree.make_geo_qs()
  tree.add_jump_out_logic()
  tree.merge_changes()
  tree.validate_refs()

  # DFFFuY
  if output_file:
    tree.write(output_file)
  else:
    pass # tree.upload_typeform('yQuH5S')

if __name__ == '__main__':
  main()
