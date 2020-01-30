#!/usr/bin/env python3.6
#
#   FridaysForFuture TypeForm Response Retriever
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
import json
from typeform import Typeform

# This program retrieves the responses from a TypeForm form, stored in a dictionary and
# written to an outputfile. The form is identified through:
form_id = 'FORM_ID_HERE' # replace with the current form_id
token_env = 'TYPEFORM_TOKEN' # stored in system environmental variables

# If no outputfile is given the responses are only written to the screen, else to the file.
output_file = 'response_output_file.txt' # or None to only print to screen

# All responses to the TypeForm form are retrieved without any limits, except to which type
# of entries that should be fetched, as controlled by the following parameter:
#   - if True only entries that have been submitted will be fetched/deleted
#   - if False only non submitted entries will be fetched/deleted
#   - if None all entries will be fetched/deleted
only_completed_entries = None 

# After writing the responses to an output file the responses can be deleted from the TypeForm:
#   - if True the responses will be deleted after writing to file
delete_after_retrieving = True

# FIXME: Now all response items data is fetched, the resulting dictionary probably needs formatting.
# FIXME: If all entries are fetched, i.e. both completed and not completed, 
#        only the completed ones should probably be written to file. 
# FIXME: Possibly only the completed ones should be deleted?
# FIXME: If not all data is fetched every time some of the settings for responses.list() will need to be adjusted.

#-------------------------------------------------------------
def fetch_responses_dict(responses, form_id, completed_entries_only):
    
    # settings for fetching the responses
    completed = completed_entries_only
    
    # no other limits for now, fetch all
    # parametrizing all anyway, for clarity
    page_size = None #maximum
    since = None 
    until = None
    after = None
    before = None
    included_response_ids = None
    sort = None
    query = None
    fields = None
    
    # fetch a typeform response list
    output = responses.list(form_id, page_size, since, until, after, before, 
                            included_response_ids, completed, sort, query, fields)
    # create output dictionary
    dict = {}
    dict['total_items'] = output['total_items']
    dict['page_count'] = output['page_count']
    dict['items'] = output['items']
    
    return dict

#-------------------------------------------------------------
def delete_responses_list(responses, form_id, dict):
    # find all tokens for responses to delete
    responses_to_delete = []
    for item in dict['items']:
        t = item['token']
        responses_to_delete.append(t) 
    
    if len(responses_to_delete) == 0:
        print("There are no responses to delete.")
        return
    
    # delete the responses
    print("Responses that will be deleted: ", responses_to_delete)
    sys.stdout.write("Are you sure you want to delete the responses (y/n)?   ")
    ans = input().lower()    
    if ans == 'y':
        str = responses.delete(form_id, responses_to_delete)
        if str == 'OK':
            print("Responses have been successfully deleted.")
        else:
            print("Delete failed: ", str)
    return        

#-------------------------------------------------------------
def write(output_file, dict):
    # write responses to a local file
    with open(output_file, "wt", encoding="utf-8") as out:
        out.write(json.dumps(dict, indent=2))
    print(f"TypeForm responses have been written to file '{output_file}'")
    
    
####################################################################    
def main():
    
    # make sure token_env has been set
    if token_env not in os.environ:
      raise Exception(f"Environment variable '{token_env}' not set")
    
    # retrieve the responses     
    print(f"Retreiving TypeForm results for form '{form_id}'")  
    responses = Typeform(os.environ[token_env]).responses
    
    # retrieve the responses dictionary 
    dict = fetch_responses_dict(responses, form_id, only_completed_entries)
    
    if output_file:
        # write the responses dictionary to an output file
        write(output_file, dict)
    else:
        # print the responses to screen
        print(json.dumps(dict, indent = 2))
        print("No responses were written to file, and no responses were deleted.")
        return # don't want to risk deleting responses if not stored
    
    # if True, delete the responses
    if delete_after_retrieving:
        delete_responses_list(responses, form_id, dict)
        
 
    
if __name__ == '__main__':
  main()
