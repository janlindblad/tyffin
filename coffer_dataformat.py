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

class FFF_GS_Dataformat:
  keymapper = {
    # RECORD
    'Timestamp': 'RTIME', 
    'RecSource': 'RSOURCE',
    # CONTACT
    'Email Address': 'CEMAIL', 
    'Your name': 'CNAME', 
    'Organisation': 'CORG1',
    'Organization that you represent (optional)': 'CORG2', 
    'Spokesperson Consent': 'CSPOKE', 
    'Phone number in international format (optional)': 'CPHONE', 
    'Notes (optional)': 'CNOTES', 
    'Organizational Color': 'CCOL',
    'Registration Consent': 'CCONS', 
    # EVENT
    'Country': 'ECOUNTRY', 
    'Town': 'ECITY', 
    'Address': 'ELOCATION', 
    'Event Type': 'ETYPE',
    'Time': 'ETIME', 
    'Date': 'EDATE', 
    'DateOrig': 'EDATEORIG',
    'Frequency': 'EFREQ', 
    'Event Type': 'ETYPE', 
    'Link to event (URL), e.g. Facebook, Instagram, Twitter, web': 'ELINK',
    '(URL) link, e.g. Facebook, Instagram, Twitter, web with photos, video, news article, blogg and your view.':'ELINK', 
    'Event Consent': 'ECONS', 
    'Number of hours':'EHOURS',
    # APPROVER
    'Approve': 'AAPPROVE', 
    'OrgType': 'AORGTYPE', 
    'Comment': 'ACOMMENT',
    'Approval time': 'ATIME', 
    'Approver email': 'AEMAIL', 
    # GEOLOC
    'Loc': 'GLOC', 
    'State': 'GSTATE',
    'Lat': 'GLAT', 
    'Lon': 'GLON', 
    # REPORT EVENT
    'Number of people': 'REVNUM',
    'Upload photo or attach link for video, news article, blogg and other.': 'REVPROOF',
    '':'',
  }

class FFF_Controlsheet_Dataformat:
  freq_key = 'Frequency'
  title_key = 'Title'
