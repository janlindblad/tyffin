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

# FridaysForFuture lets people send forms to register events around
# the world. These forms need to be properly validated, and for this
# purpose the hosted form entry service TypeForm has been selected.
#
# TypeForm has a nice form editor which people may use to create the
# form with all the questions necessary. Some of the questions relate
# to the country, state, city and venue within a city, that the event
# is taking place at. Historically, this has been left as text entry
# fields. Unfortunately, this has led to data with lower quality than
# necessary, as people spelled and described locations in many 
# different ways.
#
# In order to better validate this information, the form needs to
# contain valid options for the registrant to choose from, plus the
# ability to say "Other", and add a new city or venue. We will not
# allow users to add countries or states. This system already knows
# about all the countries and states that we allow.
#
# Since the set of cities and venues with events grow constantly, and
# there are thousands of locations, this system creates these 
# questions automatically, rather than a human adding choices in the
# TypeForm editor.
#
# This program downloads the TypeForm form, removes all location
# related questions, adds all the location related questions that it
# fetches from the map database, then uploads the result.

# FIXME: Handle venues within cities
# FIXME: Handle new cities ("other" city)
# FIXME: Handle new venues ("other" venue)

class Formtree:
  master_typeform = 'yQuH5S'
  public_typeform = 'DFFFuY'
  
  # Download TypeForm form and initialize processing structures
  def __init__(self, form_id):
    print(f"Reading TypeForm '{form_id}'")
    self.forms = self.fetch_typeform_form_cat()
    self.tree = self.fetch_form_dict(form_id)
    if 'logic' not in self.tree:
      self.tree['logic'] = []
    self.refs = {}
    print(f"Initializing from FFF database")
    Geo.init_from_livedata()
    print(f"Done initializing")

  # Fetch typeform form catalogue from the web
  def fetch_typeform_form_cat(self):
    token_env = 'TYPEFORM_TOKEN'
    if token_env not in os.environ:
      raise Exception(f"Environment variable '{token_env}' not set")
    forms = Typeform(os.environ[token_env]).forms
    return forms
    
  # Fetch a typeform from the web based on form-id
  def fetch_form_dict(self, form_id):
    form_dict = self.forms.get(form_id)
    return form_dict  

  # Load a typeform json file based on filename
  def load_typeform_file(self, source_filename):
    with open(source_filename, "rt", encoding="utf-8") as source_file:
      self.tree = json.loads(source_file.read())

  # Generate a random UUID
  def gen_uuid():
    return str(uuid.uuid4())

  # Generate all the TypeForm questions about locations, i.e.
  # country, state, city or venue. This function is the entrypoint
  # that will traverse all the locations in the Geo.atlas
  def make_geo_qs(self):
    self.refs['L1'] = self._make_geo_rec('Earth', Geo.atlas['Earth'], [])

  def get_title(geo_subcat, geo_path):
    if len(geo_path) < 2:
      return f"[L1] Which country is the event in?"
    return f"[L{len(geo_path)}] Which {geo_subcat} in {geo_path[-1]} is the event in?"

  # Generate a TypeForm question for a particular location.
  # The location could be a country, state, city or venue
  # The function will call itself recursively to generate
  # questions for locations within the location, such as cities
  # within a country.
  def _make_geo_rec(self, geo_name, geo_info, geo_path):
    (geo_subcat, geo_sub) = geo_info
    new_path = geo_path + [geo_name]
    this_qid = Formtree.gen_uuid()
    label_other = '== Other =='

    # Generate question
    self.tree['fields'] += [{
      "title": Formtree.get_title(geo_subcat, new_path),
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

    # Generate logic jump
    actions = []
    for geo_loc in geo_sub:
      # For each choice within this location, generate a sub-question
      if not isinstance(geo_sub[geo_loc], tuple):
        # If this choice has no sub-locations, don't generate anything
        # for this choice
        continue
      # This location has sub-locations, generate them
      next_q = self._make_geo_rec(geo_loc, geo_sub[geo_loc], new_path)
      # Add a logic jump from the parent question, so that if this choice
      # is selected, TypeForm will jump to the relevant sub-question
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

    # Finally, add a catch-all logic jump back to the question that
    # goes after the country, state, city, venue questions
    self.tree['logic'] += [{
        "type": "field",
        "ref": this_qid,
        "actions": actions + [
            {
                "action": "jump",
                "details": {
                    "to": {
                        "type": "field",
                        "value": self.refs['F1']
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

  # Remove any questionb "id" attributes (that we read from TypeForm)
  # TypeForm likes to assign them, and does not tolerate them if 
  # the question did not previously exist (in the form being written)
  def clean_ids(self):
    for q in self.tree['fields']:
      if 'id' in q:
        del q['id']
    
  # Remove any questions that relate to country, state, city or venue
  #
  # This is done by looking at the first few characters of the question
  # title. Location questions will have "[L.]" at the beginning of the
  # question (the dot stands for a number). Then remove all logic jumps 
  # that relate to the removed questions
  def clean_geo_questions(self):
    deleted_refs = {}
    deleted_count = 0
    for (n,q) in enumerate(list(self.tree['fields'])):
      question_words = q['title'].split(" ")
      if q['title'].startswith("[L") or q['title'].startswith("Which city/") or q['title'].startswith("Which state"):
        #print(f"Cleaning out '{q['title']}:{q}'")
        deleted_refs[q['ref']] = None
        del self.tree['fields'][n - deleted_count]
        deleted_count += 1
    print(f"Cleaned out {deleted_count} questions")
    deleted_count = 0
    for (n,j) in enumerate(list(self.tree['logic'])):
      #{"actions": [ { "details": { "to": { "value": ]
      if j['ref'] in deleted_refs or j.get('actions',[{}])[0].get('details',{}).get('to',{}).get('value') in deleted_refs:
        #print(f"Cleaning out logic jump {j['ref']}")
        del self.tree['logic'][n - deleted_count]
        deleted_count += 1
    print(f"Cleaned out {deleted_count} logic jumps")

  # Find the ref code for a question that starts with the given title
  def find_ref_for_title(self, title_start):
    for q in self.tree['fields']:
      #print(f"Looking for {title_start} in {q['title']}")
      if q['title'].startswith(title_start):
        return q['ref']
    print(f"### Did not find any question starting '{title_start}'")
    return None

  # Add logic jump from a particular manually defined question to first
  # generated question
  def add_jump_out_logic(self):
    self.tree['logic'] += [{
        "type": "field",
        "ref": self.refs['EZ'],
        "actions": [
            {
                "action": "jump",
                "details": {
                    "to": {
                        "type": "field",
                        "value": self.refs['L1']
                    }
                },
                "condition": {
                    "op": "always",
                    "vars": []
                }
            }
        ]
    }]

  # Build an index of references to the questions. Used when
  # generating logic jumps
  def scan_questions(self):
    for q in self.tree['fields']:
      #print(f"q = {q['title']}")
      try:
        q_code = q['title'].split(" ")[0]
        if q_code[0] == "[" and q_code[-1] == "]":
          self.refs[q_code[1:-1]] = q['ref']
          #print(f"Ref[{q_code[1:-1]}] = {q['ref']}")
      except:
        pass
    #print(f"Refs = {self.refs}")

  # TypeForm allows logic jumps, but only in the forward direction, 
  # i.e. a logic jump must never jump to an earlier question.
  # Therefore we have to sort questions to ensure they come in the
  # designed sequence below. An asterisk (*) stands for any number
  # or name. Specific questions that are part of the jumping logic
  # have specific names, e.g. [EZ].
  #
  # [C*]   Contact person section
  # [S*]   Spokesperson section
  # [E*]   Event details section
  #   [EZ] Last question in event section
  # [L*]   Location section
  #   [L1] First q
  # [N*]   New location section
  #   [NC] New city
  #   [NV] New venue
  # [F*]   Final section
  #   [F1] First q in final section
  def sort_questions(self):
    classified_qs = { "C": [], "S": [], "E":[], "L":[], "N":[], "F":[] }
    for q in self.tree['fields']:
      try:
        q_code = q['title'].split(" ")[0]
        if q_code[0] == "[" and q_code[-1] == "]":
          q_class = q_code[1]
          classified_qs[q_class] += [q]
          continue
      except:
        pass
      print(f"### sort_questions: Question without classifier: '{q['title']}', skipping")

    # Write back questions
    self.tree['fields'] = []
    # The sections have to go in this order
    for c in ["C", "S", "E", "L", "N", "F"]:
      self.tree['fields'] += classified_qs[c]

  # TypeForm uses UUIDs to identify questions in the
  # logic jumps. This function validates that all logic
  # jumps are referring to questions that actually exist
  def validate_refs(self):
    fields = {}
    for q in self.tree['fields'] + self.tree['thankyou_screens']:
      fields[q['ref']] = 0
    for j in self.tree['logic']:
      if 'ref' not in j:
        print(f"### No ref in jump")
        continue
      if j['ref'] not in fields:
        print(f"### Jump from unknown field {j['ref']}")
        continue
      fields[j['ref']] += 1
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
        fields[act['details']['to']['value']] += 1
        if 'condition' not in act:
          print(f"### No condition in jump")
          continue
        if 'vars' not in act['condition']:
          print(f"### No vars in jump")
          continue
        for var in act['condition']['vars']:
          if 'type' not in var:
            print(f"### No value in jump condition")
            continue
          if var['type'] != 'field':
            continue
          if 'value' not in var:
            print(f"### No value in jump condition")
            continue
          if var['value'] not in fields:
            print(f"### Jump reference to unknown field {var['value']}")
            continue
          fields[var['value']] += 1
    # FIXME: check that refs go forward only
    for f in fields:
      print(f"{f} : {fields[f]} : {[q['title'][:40] for q in self.tree['fields'] if q['ref'] == f]}")

  # Write form to a local file
  def write(self, output_file):
    with open(output_file, "wt", encoding="utf-8") as out:
      out.write(json.dumps(self.tree, indent=2))
    print(f"Wrote TypeForm to file '{output_file}'")

  # Upload updated form to Typeform
  def upload_typeform(self, form_id):
    print(f"Writing TypeForm '{form_id}'")
    updated_tree = {
      key:self.tree[key] for key in [
      'title', 'theme', 'workspace', 'settings', 
      'welcome_screens', 'thankyou_screens', 'fields', 'logic']
    }
    response = self.forms.update(form_id, updated_tree)
    if(response['id'] == form_id):
      print("Uploaded successfully")
    else:
      print(f"Upload failure: {str(response)[:500]}...")
    
def usage():
  print(
    f"""{sys.argv[0]} [-f] [-i input_form] [-o output_form]
        Update Typeform with location questions from the FFF dababase
        -h                Show this help
        -i <input-form>   Typeform 6-character form-id to read from
        -o <output-form>  Typeform 6-character form-id to write to
        -f <output-file>  Send output to file instead
    """)

def main():
  output_file = None
  output_form = Formtree.public_typeform
  input_form = Formtree.master_typeform
  try:
    opts, args = getopt.getopt(sys.argv[1:],"hi:o:f:",
      ["help", "input=", "output=", "debug"])
  except getopt.GetoptError:
    usage()
    sys.exit(2)
  for opt, arg in opts:
    if opt in ('-h', '--help'):
      usage()
      sys.exit()
    elif opt in ("-f", "--file"):
      output_file = arg
    elif opt in ("-i", "--input"):
      input_form = arg
    elif opt in ("-o", "--output"):
      output_form = arg
    
  # Form generation top level:
  # Download existing form from TypeForm servers
  tree = Formtree(input_form)  
  # Remove all country, state, city, venue related questions
  tree.clean_geo_questions()
  # Remove all question id attributes
  tree.clean_ids()
  # Store refs to questions
  tree.scan_questions()
  # Make new country, state, city, venue questions
  tree.make_geo_qs()
  # Update stored refs to questions
  tree.sort_questions()
  # Add additional logic jumps
  tree.add_jump_out_logic()
  # (optional) Validate all question references before uploading
  tree.validate_refs()

  if output_file:
    # File output; can be manually inspected and uploaded to TypeForm
    # by e.g. Postman PUT https://api.typeform.com/forms/DFFFuY
    tree.write(output_file)
  else:
    # Upload the result to TypeForm
    tree.upload_typeform(output_form)

if __name__ == '__main__':
  main()
