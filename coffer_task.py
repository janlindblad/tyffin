#   FridaysForFuture Database Collector Function
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

from coffer_table import Table, Item, GS_Table, GS_Tab
from coffer_dataformat import FFF_Controlsheet_Dataformat, FFF_GS_Dataformat
import re

class Task(Item):
  factory_registry = {}

  def factory_register(name, builder_func):
    Task.factory_registry[name] = builder_func

  def factory(task_dict): #FIXME
    if 'Trafis' in task_dict and 'Title' in task_dict and task_dict['Title']:
      return CS_Task(task_dict)
    if '_class' not in task_dict:
      return None
    builder_func = Task.factory_registry.get(task_dict['_class'], None)
    if builder_func:
      return builder_func(task_dict=task_dict)
    return None

  def __init__(self, task_dict):
    super().__init__()
    #print(f"Task({task_dict})")
    self._dict = task_dict
    self.Title = task_dict[FFF_Controlsheet_Dataformat.title_key] if FFF_Controlsheet_Dataformat.title_key in task_dict else "Untitled"

  def __repr__(self):
    return f"(Task: Title='{self.Title}' size={len(self._dict)})"

  def run(self, selector = None):
    print(f"### Starting task default {self.Title}: {self._dict}")
    ret = []
    print(f"### Finished task default {self.Title}: {ret}")
    return ret

class CS_Task(Task):
  def __init__(self, task_dict):
    super().__init__(task_dict)
    self._dict['_class'] = 'CS_Task'
    #{'Title': 'FFF Global Map WFF', 'Frequency': 'daily', 'Link': 'Open', 'Columns': 'ECOUNTRY, ECITY, ELOCATION, ETIME, EDATE, EFREQ, ELINK, ETYPE, GLAT, GLON, CNAME, CEMAIL, CPHONE, CNOTES, CORG2, CCOL', 'Trafis': 'isApproved, tISODate, tGoogleLoc, tisRecurringOn', 'Sumfis': 'sumGroupByCity, sumCountCountries, sumForkRecurringEvents', 'Params': 'date:2019-09-20+2019-09-21--2019-09-27', 'Delivery': 'toGoogle', 'Sheet': '1bFdJDjElWlNUOabE0p9lXM8OeGr4KyPxFF00zyHL5nE', 'Input': '', 'Global Sync': '', 'Map Organiser': '', 'Notify email': '', 'Comments': '', 'Actual Title': '', 'Sheet link view only': '', 'Social Media': '', 'Country Organising Minutes': '', 'Country bulk reporting systeme': ''}]

class Tasklist(Table):
  def __init__(self, tableid):
    self.name = tableid
    super().__init__(tableid)

  def get_tasks(self, selector):
    #print(f"Tasklist.get_tasks({self.name}, selector={selector})")
    tasks = []
    search_dict = {}
    if selector and selector[0]:
      search_dict[FFF_Controlsheet_Dataformat.title_key] = {"$regex": f".*{re.escape(selector[0])}.*"}
    print(f"Tasklist.get_tasks({self.name}, {selector}) search_dict = {search_dict}")
    table = self.get_table()
    #print(f"Tasklist.get_tasks all tasks = {list(table.find())}")
    for task_dict in table.find(search_dict):
      print(f"Tasklist.get_tasks found = {task_dict}")
      new_task = Task.factory(task_dict)
      if new_task:
        tasks += [new_task]
    print(f"Tasklist.get_tasks({self.name}, {selector}) returning {len(tasks)} tasks")
    return tasks

  def run(self, selector):
    #print(f"Tasklist.run({self.name}, selector={selector})")
    for task in self.get_tasks(selector):
      task.run(selector=selector[1:])

class Constant_Tasklist(Tasklist):
  def __init__(self, tableid, tasks):
    self.constant_tasks = tasks
    super().__init__(tableid)

  def get_external_records(self):
    #print(f"Constant_Tasklist.get_external_records() returning {len(self.constant_tasks)} tasks")
    return self.constant_tasks

class GS_Tasklist(Tasklist):
  def __init__(self, tableid, sheetid, tabid):
    super().__init__(tableid)
    self.tab = GS_Tab(sheetid, tabid)

  def get_external_records(self):
    external_tasks = self.tab.read_all()
    #print(f"GS_Tasklist.get_external_records() returning {len(external_tasks)} tasks")
    return external_tasks
