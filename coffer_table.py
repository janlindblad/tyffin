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

from datetime import datetime, timedelta
from pymongo import MongoClient
from oauth2client.service_account import ServiceAccountCredentials
from collections import MutableMapping
import gspread

class Table():
  max_age = timedelta(minutes=15)

  def db_connect(dbid):
    print(f"Table.db_connect()")
    Table.client = MongoClient('mongodb://localhost:27017/')
    Table.db = Table.client[dbid]

  def get_collection_names(name_starts_with = ""):
    return [coll_name for coll_name in Table.db.collection_names(include_system_collections=False) 
      if coll_name.startswith(name_starts_with)]

  def __init__(self, tableid):
    self.tableid = tableid
    self.table = Table.db[self.tableid]
    self.refreshed = Table.db.refreshed.find_one({'tableid':self.tableid})
    self.keymapper = None
    #print(f"Table db={self.db} table={self.table} refreshed={self.refreshed}")

  def get_external_records(self):
    # May be overridden/extended by subclasses
    return []

  def refresh_table(self, external_records = None):
    if external_records == None:
      external_records = self.get_external_records()
    if self.keymapper:
      external_records = [{self.keymapper[key]:str(dct[key]) for key in dct if dct[key] != ''} for dct in external_records]
    #print(f"Table.refresh_table() inserting {len(external_records)} records")
    if external_records:
      self.table.delete_many({})
      print(f"Table.refresh_table({self.tableid}) destroyed contents")
      #print(f"Table.refresh_table({self.table.name}) refill records {external_records}")
      self.table.insert_many(external_records)
      print(f"Table.refresh_table({self.tableid}) refilled {len(external_records)} records")
    else:
      print(f"Table.refresh_table({self.tableid}) not refreshed")

  def refresh(self):
    #print(f"Table.refresh({self.tableid})")
    self.refresh_table()
    self.refreshed = datetime.now()
    result = Table.db.refreshed.replace_one({'tableid':self.tableid}, {'refreshed':self.refreshed}, upsert=True)

  def get_table(self):
    #print(f"Table.get_table({self.tableid})")
    if True or not self.refreshed or self.refreshed < datetime.now() - Table.max_age:
      self.refresh()
    else:
      print(f"Table.get_table({self.tableid}) no refresh needed")
    return self.table

  def read_all(self):
    return list(self.get_table().find({}))

class Item(MutableMapping):
  def __init__(self):
    self._dict = {}
    __getattr__ = self._dict.__getitem__
    __setattr__ = self._dict.__setitem__
    __delattr__ = self._dict.__delitem__

  def __delitem__(self, key): return self._dict.__delitem__(key)
  def __getitem__(self, key): return self._dict.__getitem__(key)
  def __setitem__(self, key, val): return self._dict.__setitem__(key, val)
  def __iter__(self): return self._dict.__iter__()
  def __len__(self): return self._dict.__len__()

class GS_Table(Table):
  def __init__(self, tableid, sheetid, tabid, keymapper = None):
    super().__init__(tableid)
    self.tab = GS_Tab(sheetid, tabid)
    self.keymapper = keymapper

  def get_external_records(self):
    return self.tab.read_all()

class GS_Tab:
  def __init__(self, sheetid, tabid):
    self.client = {}
    self.sheetid = sheetid
    self.tabid = tabid

  def _get_client(self, scopes):
    #scope = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    #scope = ['https://www.googleapis.com/auth/spreadsheets  ']
    scopekey = "+".join(scopes)
    if(not scopekey in self.client):
      creds = ServiceAccountCredentials.from_json_keyfile_name('toughchassis_secret.json', scopes)
      self.client[scopekey] = gspread.authorize(creds)
    return self.client[scopekey]

  def read_all(self):
    scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    handle = self._get_client(scopes).open_by_key(self.sheetid).worksheet(self.tabid)
    all_recs = handle.get_all_records()
    #print(f"GS_Tab({self.sheetid},{self.tabid}) returning {len(all_recs)} records")
    return all_recs

