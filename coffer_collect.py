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

from coffer_task import Task, GS_Tasklist

class Collect_Task(Task):
  def __init__(self, task_dict):
    super().__init__(task_dict)

class GS_Collect_Task(Collect_Task):
  def __init__(self, title = None, sheet = None, tab = None, task_dict = None):
    if task_dict:
      super().__init__(task_dict)
      self._dict['_class'] = 'GS_Collect_Task'
      (title, sheet, tab) = task_dict['GS_Tasklist']
      self.tasklist = GS_Tasklist(title, sheet, tab)
    else:
      super().__init__({'Title': title, '_class':'GS_Collect_Task', 'GS_Tasklist':(title, sheet, tab)})
      #self._dict['Title'] = title
      #print(f"GS_Collect_Task({self.GS_Tasklist}, {1})")
      self.tasklist = GS_Tasklist('gs', sheet, tab)

  def run(self, selector = None):
    print(f"GS_Collect_Task.run(selector={selector})")
    subtasks = self.tasklist.get_tasks(selector)
    for subtask in subtasks:
      if not selector or ('Title' in subtask and selector[0] in subtask['Title']):
        #print(f"GS_Collect_Task.run ==> {subtask}")
        sheet_title = subtask['Title']
        sheetid = subtask['Sheet']
        tabid = subtask['Input']
        if not tabid or not sheetid:
          #print(f"GS_Collect_Task.run({sheet_title}) missing sheetid/tabid '{sheetid}'/'{tabid}', skipping")
          continue
        tableid = f"Coffin#{sheet_title}#{sheetid}#{tabid}"
        print(f"GS_Collect_Task.run ==> fetching ({tableid})")
        table = GS_Table(tableid, sheetid, tabid, keymapper=FFF_GS_Dataformat.keymapper)
        num_recs = len(table.read_all())
        print(f"GS_Collect_Task.run stored {num_recs} records")
      else:
        pass
        #print(f"GS_Collect_Task.run skipping subtask")

Task.factory_register('GS_Collect_Task', GS_Collect_Task)

class Tyffin_Collect_Task(Collect_Task):
  pass
#Task.factory_register('Tyffin_Collect_Task', Tyffin_Collect_Task)
