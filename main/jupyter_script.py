import tensorflow as tf
import tensorflow_hub as hub

import numpy as np
import matplotlib.pyplot as plt
import librosa
from librosa import display as librosadisplay

import logging
import math
import statistics
import sys

from IPython.display import Audio, Javascript
from scipy.io import wavfile

from base64 import b64decode

import music21
from pydub import AudioSegment

from main import app
import os

logger = logging.getLogger()
logger.setLevel(logging.ERROR)

print("tensorflow: %s" % tf.__version__)
#print("librosa: %s" % librosa.__version__)

model = hub.load("https://tfhub.dev/google/spice/2")

#####################################
#####################################
#####################################


EXPECTED_SAMPLE_RATE = 16000

def convert_audio_for_model(user_file, output_file='converted_audio_file.wav', output_folder=os.path.join(app.root_path,'static','converted_hummings')):
  
  # user_file = os.path.basename(user_file)
  
  audio = AudioSegment.from_file(user_file)
  audio = audio.set_frame_rate(EXPECTED_SAMPLE_RATE).set_channels(1)

  file_name, file_extension = os.path.basename(user_file).rsplit('.', 1)
  output_file = f"{file_name}_converted.{file_extension}"
  
  output_path = os.path.join(output_folder, output_file)

  if not os.path.exists(output_folder):
        os.makedirs(output_folder)

  audio.export(output_path, format="wav")
  return output_path


def audio_samples(converted_audio_file):
  sample_rate, audio_samples = wavfile.read(converted_audio_file, 'rb')
  return audio_samples,sample_rate


def pitch_confidence(audio_samples):


  model_output = model.signatures["serving_default"](tf.constant(audio_samples, tf.float32))

  pitch_outputs = model_output["pitch"]
  uncertainty_outputs = model_output["uncertainty"]

  confidence_outputs = 1.0 - uncertainty_outputs

  return pitch_outputs, confidence_outputs

#####################################
#####################################

import os
import pandas as pd


folder_path = '/Users/krishnapahuja/Documents/Class Programming/Sem 4/Project_on_venv/HummingBird/main/static/hummings'

df = pd.DataFrame(columns=["Song Name", "Path", "PitchArray", "ConfidenceArray"])

for filename in os.listdir(folder_path):
  # Extract song name (assuming filename is the same as song name)
  song_name = filename

  # Construct the full path to the song file
  file_path = os.path.join(folder_path, filename)

  # if song_name == ".DS_Store":
  #   os.remove(file_path)
  #   print("File .DS_Store deleted.")
  #   continue

  try:
    #######
    if file_path == app.root_path+'/static/hummings/.ipynb_checkpoints':
      continue
    converted_audio_file = convert_audio_for_model(file_path) # here uploaded = c-scale.wav
    audio_samp, sample_rate = audio_samples(converted_audio_file)
    po, co = pitch_confidence(audio_samp)


    ### converson to np.arrays from tensor ### -> remove if dtw alignment does not work
    po = np.array(po)
    co = np.array(co)

  ####### v.v.v.v.v important code
  ## breaking into fragments with 50% ovelaping
    # size = 100 # uncomment if slow but better
    # size = len(po)-1 # toggle comment between line above it and this
    size = len(po)//10
    i = 0
    while i+size < len(po):
      new_row = pd.DataFrame({
        "Song Name": song_name,
        "Path": file_path,
        "PitchArray": [(po[i:i+size])],
        "ConfidenceArray": [(co[i:i+size])]
      })
      df = pd.concat([df, new_row], ignore_index=True)
      i+=(int(0.7*size)) # change this to alter overlapping ratio currently 99% overlapping
  ## end of breaking array into fragments

    ######

    # Create a new row with song name, path, and placeholders for pitch and confidence
    new_row = pd.DataFrame({
        "Song Name": song_name,
        "Path": file_path,
        "PitchArray": [po],
      "ConfidenceArray": [co]
    })

    # Append the new row to the DataFrame
    df = pd.concat([df, new_row], ignore_index=True)
  except Exception as e:
    # Handle the error
    print(f"Error processing file: {song_name}")

# Print the DataFrame
df.to_csv(os.path.join(app.root_path,'static','converted_hummings', 'numeric_audio'))
#####################################
# df = pd.read_csv(os.path.join(app.root_path,'static','converted_hummings', 'numeric_audio'))
# df.columns = ["S.no", "Song Name", "Path", "PitchArray", "ConfidenceArray"]

# def csv_file_formatting(temp):
#     temp = temp[1:len(temp)-1]
#     temp = temp.split()
#     temp = list(map(float, temp))
#     temp = np.array(temp)
#     return temp

# df.PitchArray = pd.Series(map(csv_file_formatting, df.PitchArray))
# df.ConfidenceArray = pd.Series(map(csv_file_formatting, df.ConfidenceArray))


# import ast

# def parse_array_string(array_string):
#     array_string = array_string[1:len(array_string)-1]
#     array_string = array_string.split()
#     to_return  = ast.literal_eval(array_string)
#     pritn(to_return)
#     return to_return

# df = pd.read_csv(os.path.join(app.root_path,'static','converted_hummings', 'numeric_audio'), converters={'PitchArray': parse_array_string, 'ConfidenceArray': parse_array_string})

# #####################################

from fastdtw import fastdtw
import pandas as pd
import numpy as np

def find_best_match4(user_pitch_sequence, song_dataframe, radius_value=1):
    # Initialize variables to store the best match information
    best_song_name = None
    best_distance = float('inf')  # Initialize with a large value

    # Iterate through each row in the DataFrame

    ############################# adding new feature kp(11/4/24)
    similar_songs = []
    ##################################

    for index, row in song_dataframe.iterrows():
        # Get the pitch sequence of the current song
        song_pitch_sequence = np.array(row['PitchArray'])

        # Calculate DTW distance using fastdtw with different radius values
        distance, _ = fastdtw(song_pitch_sequence, user_pitch_sequence, radius=radius_value)

        ########################
        # print(f"for song: {row['Song Name']} distance is {distance}")
        ########################

        similar_songs.append(((row['Song Name'])[0:-4], distance))

        # Update best match information if the current song has a lower distance
        if distance < best_distance:
            best_distance = distance
            best_song_name = row['Song Name']


    ######################## 
    # can add threshold value such as if best_distance > 50 then "could'nt find what you were looking for"
    ######################


    similar_songs.sort(key=lambda x: x[1])
    # print("similar_songs = ", *similar_songs)
    four_songs = []

    answer_song = best_song_name[0:-4]
    for tu in similar_songs:
       if (len(four_songs) == 4):
          break
       song = tu[0]
       if song != answer_song and song not in four_songs:
          four_songs.append(song)
    best_song_name = best_song_name[0:-4]
    return best_song_name, four_songs

#####################################
#####################################



def perform_main(file_path):

    converted_audio_file = convert_audio_for_model(file_path) # here uploaded = c-scale.wav
    audio_samp, sample_rate = audio_samples(converted_audio_file)
    po, co = pitch_confidence(audio_samp)

    po = np.array(po)
    co = np.array(co)

    # radius_values_to_try = [1, 50, 300]

    # for radius_value in radius_values_to_try:
    #     best_match = find_best_match4(po, df, radius_value=radius_value)
    #     print(f"The best match for radius {radius_value} is: {best_match}")
    
    radius_value = 1
    best_match, similar_songs_li = find_best_match4(po, df, radius_value=radius_value)
    return best_match, similar_songs_li
