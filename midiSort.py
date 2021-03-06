# Python script for sorting MIDI files on a database
# Februrary 2021
# runs on Python 3.x on Mac OS 12.0.1

################
# import modules
################

# import datetime
from datetime import datetime

# sys for command line arguments
import sys

# os for listing files and directories
import os

# shutil for copy and paste files
import shutil

# Path for creating new directories and files
from pathlib import Path

# csv for CSV files
import csv

# pandas for .xls to CSV
import pandas as pd

# mido for MIDI files
from mido import MetaMessage
from mido import MidiFile

################################
# retrieve current date and time
################################

def getCurrentDate():
  # retrieve system date
  now = datetime.now()

  # parse
  year = now.strftime("%Y")
  month = now.strftime("%m")
  day = now.strftime("%d")
  hour =  now.strftime("%H")
  minute =  now.strftime("%M")
  second = now.strftime("%S")

  # return YYYYMMDD-HHMMSS
  currentDate = year + month + day + "-" + hour + minute + second
  return currentDate

###################
# default variables
###################

libraryPathOriginal = "libraryOriginal"
libraryPathNew = "library" + getCurrentDate()
libraryPathFiles = "filesRaw"

libraryPathSorted = "filesSorted"

libraryPathWithSoft = "withSoft"
libraryPathWithoutSoft = "withoutSoft"

# artists are each manufacturer of the rolls
libraryPathRolls = ["Ampico", "Duo-Art", "Welte-T-100", "Welte-Licensee"]

libraryCSVFileName = "libraryNew.csv"

libraryMetadataFolder = "DOCUMENTATION"
libraryMetadataExtensionNew = ".csv"
# OLD
# libraryMetadataFilename = "All_Rolls"
# libraryMetadataExtensionOriginal = ".xls"
# NEW
libraryMetadataFilename = "All_Rolls_modified"
libraryMetadataExtensionOriginal = ".xlsx"

libraryRollsSuffixes = ["emP", "emR"]

# variable for storing the names of each MIDI file
midiFilesNames = []
midiFilesPaths = []

# variable for storing a subset of MIDI files: only 1 word ones
midiFilesShortNames = []
midiFilesShortPaths = []

##############################
# create files and directories
##############################

# if it doesnt exist, create new directory for storing the modified library
def createDirectories():

  # create folder for raw original files
  Path("./" + libraryPathNew + "/" + libraryPathFiles).mkdir(parents=True, exist_ok=True)
  # create subfolders for with and without softpedal
  Path("./" + libraryPathNew + "/" + libraryPathFiles + "/" + libraryPathWithSoft).mkdir(parents=True, exist_ok=True)
  Path("./" + libraryPathNew + "/" + libraryPathFiles + "/" + libraryPathWithoutSoft).mkdir(parents=True, exist_ok=True)

  # create folder for sorted files
  Path("./" + libraryPathNew + "/" + libraryPathSorted).mkdir(parents=True, exist_ok=True)

# create new file with CSV list
def createFiles():
  newFile = open("./" + libraryPathNew + "/" + libraryCSVFileName, "w")
  writer = csv.writer(newFile)
  newFile.close()

###########
# CSV files
###########

def readCSVFile(filename, column, delimiter):
  with open(filename, newline='') as myCSVFile:
    reader = csv.reader(myCSVFile, delimiter=delimiter, quotechar='|')
    result = []
    for row in reader:
      result.append(row[column])
    return result

def createListMIDIFiles():
  with open("./" + libraryPathNew + "/" + libraryCSVFileName, "w", newline="") as csvFile:
    csvWriter = csv.writer(csvFile, delimiter = " ", quotechar='|', quoting=csv.QUOTE_MINIMAL)
    for i in range(len(midiFilesShortNames)):
      csvWriter.writerow([midiFilesShortNames[i], midiFilesShortPaths[i]])

#################################
# parse metadata from AllRolls.xls
#################################

def readLibraryMetadata():

  # read Excel file with pandas
  readXLSFile = pd.read_excel("./" + libraryPathOriginal + "/" + libraryMetadataFolder + "/" + libraryMetadataFilename + libraryMetadataExtensionOriginal)

  # convert to CSV
  readXLSFile.to_csv("./" + libraryPathNew + "/" + libraryMetadataFilename + libraryMetadataExtensionNew, index = None, header = True, sep = "\t")

############
# MIDI files
############

# find all MIDI files in libraryOriginal
def findMIDIFiles():
  
  # get current working directory
  cwd = os.getcwd()

  for root, directories, files in os.walk(cwd + "/" +libraryPathOriginal + "/"):
    for filename in files:
      filepath = os.path.join(root, filename)
      # append if it is a filename
      if filepath.endswith(".mid") or filepath.endswith(".MID"):
        # append them to the list
        midiFilesNames.append(os.path.splitext(os.path.basename(filepath))[0])
        midiFilesPaths.append(os.path.relpath(filepath))
        # append to the shorter list if they are only one word
        if (len(os.path.splitext(os.path.basename(filepath))[0].split()) == 1):
          midiFilesShortNames.append(os.path.splitext(os.path.basename(filepath))[0])
          midiFilesShortPaths.append(os.path.relpath(filepath))

# open a MIDI file
def readMIDIFile(filename):
  myFile = MidiFile(filename)
  return myFile

# print the meta messages of MIDI file
def printMetaMessages(file):

  for i, track in enumerate(file.tracks):
    print('Track {}: {}'.format(i, track.name))
    for msg in track:
        if msg.is_meta:
          print(msg)

# copy MIDI files from original folder to new folder
# only do the 1 word ones
def copyMIDIFiles():
  # retrieve paths of original MIDI files
  midiPaths = readCSVFile("./" + libraryPathNew + "/" + libraryCSVFileName, column=1, delimiter=" ")
  # copy them to the new library
  for i in range(len(midiPaths)):
    # sort them between with and without soft pedal, according to suffix
    if midiPaths[i][len(midiPaths[i])-7:-4] == "emP":
      shutil.copy(midiPaths[i], './' + libraryPathNew + "/" + libraryPathFiles + "/" + libraryPathWithSoft)
    elif midiPaths[i][len(midiPaths[i])-7:-4] == "emR":
      shutil.copy(midiPaths[i], './' + libraryPathNew + "/" + libraryPathFiles + "/" + libraryPathWithoutSoft)

# check if any of the copied files matches with an entry on AllRolls.csv
def sortMIDIFiles():

  # read All_Rolls.csv, retrieve these columns:

  # column 0 for title
  AllRollsTitles = readCSVFile("./" + libraryPathNew + "/" + libraryMetadataFilename + libraryMetadataExtensionNew, column=0, delimiter= "\t")

  # column 1 for composer
  AllRollsComposers = readCSVFile("./" + libraryPathNew + "/" + libraryMetadataFilename + libraryMetadataExtensionNew, column=1, delimiter= "\t")

  # column 2 for pianist
  AllRollsPianists = readCSVFile("./" + libraryPathNew + "/" + libraryMetadataFilename + libraryMetadataExtensionNew, column=2, delimiter= "\t")

   # column 3 for manufacturer
  AllRollsManufacturers = readCSVFile("./" + libraryPathNew + "/" + libraryMetadataFilename + libraryMetadataExtensionNew, column=3, delimiter= "\t")

  # column 4 for roll numbers
  AllRollsNumbers = readCSVFile("./" + libraryPathNew + "/" + libraryMetadataFilename + libraryMetadataExtensionNew, column=4, delimiter= "\t")

  # column 5 for filename
  AllRollsNames = readCSVFile("./" + libraryPathNew + "/" + libraryMetadataFilename + libraryMetadataExtensionNew, column=5, delimiter= "\t")

  print(len(midiFilesShortNames))

  # create a subfolder for each artist / manufacturer
  # OLD, iterate over libraryPathRolls
  # for i in range(len(libraryPathRolls)):
  # NEW iterate over composers
  for i in range(len(AllRollsComposers)):

    # OLD
    # Path("./" + libraryPathNew + "/" + libraryPathSorted + "/" + libraryPathRolls[i]).mkdir(parents=True, exist_ok=True)
    # NEW
    Path("./" + libraryPathNew + "/" + libraryPathSorted + "/" + AllRollsComposers[i]).mkdir(parents=True, exist_ok=True)


  # go through every MIDI file with 1 word
  for i in range(len(midiFilesShortNames)):

    # retrieve filename
    name = midiFilesShortNames[i]

    # check if the filename ends on the suffixes emR or emP
    if name[-3:] in libraryRollsSuffixes:
      # retrieve the name without suffix
      name = name[:-3]

    # go through filenames in All_Rolls
    for i in range(len(AllRollsNames)):

      # check if there is a match
      if (AllRollsNames[i] == name):

        # get current working directory
        cwd = os.getcwd()

        for j in range(len(libraryPathRolls)):
          if AllRollsManufacturers[i] == libraryPathRolls[j]:
            # create path for album OLD
            Path("./" + libraryPathNew + "/" + libraryPathSorted + "/" + AllRollsManufacturers[i] + "/" + AllRollsPianists[i]).mkdir(parents=True, exist_ok=True)
            # create path for album NEW
            Path("./" + libraryPathNew + "/" + libraryPathSorted + "/" + AllRollsComposers[i] + "/" + AllRollsPianists[i]).mkdir(parents=True, exist_ok=True)

            try:
              # shutil.copy(cwd + "/" + libraryPathNew +"/" + "filesRaw" + "/" + "withoutSoft" + "/" + AllRollsNames[i] + "emR" ".mid", './' + libraryPathNew + "/" + libraryPathSorted + "/" + libraryPathRolls[j] + "/" + AllRollsPianists[i])
               shutil.copy(cwd + "/" + libraryPathNew + "/" + "filesRaw" + "/" + "withoutSoft" + "/" + AllRollsNames[i] + "emR" ".mid", './' + libraryPathNew + "/" + libraryPathSorted + "/" + AllRollsComposers[i] + "/" + AllRollsPianists[i] + "/" + AllRollsTitles[i] + ".mid")
            except:
              print("file not found: " + AllRollsNames[i])

        # print(AllRollsTitles[i], AllRollsNames[i])

  print(len(AllRollsNames))

######

def addImages():
  # get current working directory
  cwd = os.getcwd()

  # for root, directories, files in os.walk(cwd + "/" +libraryPathSorted + "/" + "Ampico" + "/"):
  #   for directory in directories:
  #     print(directory)

######

#########
# running
#########

# create directories and files
createDirectories()
createFiles()

# find all MIDI files
findMIDIFiles()

# check the contents and length
# print(midiFilesPaths)
# print(midiFilesNames)
# print(len(midiFilesPaths))
# print(len(midiFilesNames))

# create CSV file with MIDI files
createListMIDIFiles()

# read metadata
readLibraryMetadata()

# copy MIDI files from original to new
copyMIDIFiles()

# sort the MIDI files into different folders
sortMIDIFiles()

# add images to folders
addImages()