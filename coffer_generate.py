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

from coffer_task import Task, Tasklist
from coffer_table import Table

class Generate_Task(Task):
  results = {}

  def __init__(self, task_dict):
    super().__init__(task_dict)

class GS_Generate_Task(Generate_Task):
  def __init__(self, title = None, table_id = None, task_dict = None):
    if task_dict:
      super().__init__(task_dict)
      self._dict['_class'] = 'GS_Generate_Task'
      self.tasklist = Tasklist(task_dict['table_id'])
    else:
      super().__init__({'Title': title, '_class':'GS_Generate_Task', 'table_id':table_id})
      self.tasklist = Tasklist(table_id)

  def run(self, selector = None):
    print(f"GS_Generate_Task.run(selector={selector})")
    subtasks = self.tasklist.get_tasks(selector)
    for subtask in subtasks:
      if not selector or ('Title' in subtask and selector[0] in subtask['Title']):
        print(f"GS_Generate_Task.run ==> {subtask.get('Title','noname')}")
        #print(f"GS_Generate_Task.run subtask = {subtask}")
        subtask_frequency = subtask.get('Frequency', '')
        if subtask_frequency != 'daily':
          print(f"Not daily")
          continue
        subtask_source = subtask.get('Source', '')
        if subtask_source == "*":
          records = []
          for table_id in Table.get_collection_names(name_starts_with="Coffin#"):
            print(f"GS_Generate_Task.run adding {table_id}")
            records += Table(table_id).read_all()
        else:
          print(f"GS_Generate_Task.run getting '{subtask_source}'")
          records = Generate_Task.results.get(subtask_source, None)
          if not records:
            print(f"(from coffin)")
            records = Table("Coffin#" + subtask_source).read_all()
          else:
            print(f"(from memory)")
        print(f"GS_Generate_Task.run contains {len(records)} records")
        Generate_Task.results[subtask['Title']] = records
      else:
        print(f"GS_Generate_Task.run skipping task")

Task.factory_register('GS_Generate_Task', GS_Generate_Task)
