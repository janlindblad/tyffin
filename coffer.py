#!/usr/bin/env python3.6
#
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

import sys, os, getopt
import requests, json, uuid
from datetime import datetime, timedelta

from coffer_table import Table
from coffer_task import Task, Constant_Tasklist
from coffer_collect import GS_Collect_Task, Tyffin_Collect_Task
from coffer_generate import GS_Generate_Task

class RunControl:
  def init():
    print(f"RunControl.init()")
    RunControl.root_tasklist = Constant_Tasklist("root_tasklist", [
      GS_Collect_Task('collect-gs', '1oE86UrOlmO7chBSMHKqU78Yzec-xOYaKlgRBtSetijk', 'Copy of Control'),
      GS_Generate_Task('generate-gs', 'collect-gs'),
      #Tyffin_Collect_Task({'Title':'collect-tyffin'}),
      #Collect_Task({'Title':'collect-earthday'}),
      #Coffer_Task('All Inputs',       ]),
      #Gen_Task({'Title':'tyffin'}),
      #Task({'Title':'run', 'Tasklist':("GS_Tasklist",'gs','1oE86UrOlmO7chBSMHKqU78Yzec-xOYaKlgRBtSetijk','Copy of Control')}),
    ])

  def run(*, selector = ""):
    print(f"RunControl.run(selector={selector})")
    Table.db_connect('test_database')
    RunControl.init()
    RunControl.root_tasklist.run(selector)

def usage():
  print('%s -s <command>'%sys.argv[0])
  print('Fetch and process FFF data')
  print('-h | --help                     Show this help')
  print('-s | --selector=<command>       Name of command to run')

def main():
  print(f"main()")
  debug = False
  selector = ""
  try:
    opts, args = getopt.getopt(sys.argv[1:],"h:s:",
      ["help", "debug", "selector="])
  except getopt.GetoptError:
    usage()
    sys.exit(2)
  for opt, arg in opts:
    if opt in ('-h', '--help'):
      usage()
      sys.exit()
    elif opt in ("-s", "--selector"):
      selector = arg
    elif opt in ("--debug"):
      debug = True
    else:
      print('Unknown option "%s", exiting.'%opt)
      sys.exit(2)
  RunControl.run(selector = selector.split(':'))

if __name__ == '__main__':
  main()
