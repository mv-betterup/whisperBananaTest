import json

import torch
import stable_whisper
import os
import base64
from io import BytesIO

# Init is ran on server startup
# Load your model to GPU as a global variable here using the variable name "model"
def init():
    global model
    
    model = stable_whisper.load_model("base")

# Inference is ran for every server call
# Reference your preloaded global model variable here.
def inference(model_inputs:dict) -> dict:
    global model

    # Parse out your arguments
    mp3BytesString = model_inputs.get('mp3BytesString', None)
    getWordTranscript = model_inputs.get('useWordTranscription', None)
    getSentenceTranscript = model_inputs.get('useSentenceTranscription', None)
    if mp3BytesString is None:
        return {'message': "No input provided"}
    
    mp3Bytes = BytesIO(base64.b64decode(mp3BytesString.encode("ISO-8859-1")))
    with open('input.mp3','wb') as file:
        file.write(mp3Bytes.getbuffer())
    
    # Run the model
    result = model.transcribe("input.mp3")
    wordResults = None
    sentResults = None
    if getWordTranscript is not None:
        wordResults = stable_whisper.results_to_word_srt(result)
    if getSentenceTranscript is not None:
        sentResults = stable_whisper.results_to_sentence_srt(result)
    output = {"text":result["text"], "Word Transcription":wordResults, "Sentence Transcription":sentResults}
    os.remove("input.mp3")
    # Return the results as a dictionary
    return output


def output_word_transcribe_to_json(transcriptionFileName=None, jsonFileName=None):
    with open(transcriptionFileName, 'r') as file:
        resultsWordstamps = file.readlines()

    words = []
    timeStarts = []
    timeEnds = []

    i = 0
    max = len(resultsWordstamps)
    while i < len(resultsWordstamps):
        line = resultsWordstamps[i]
        i += 1
        if i % 4 == 2:
            timeBits = line.split(" --> ")
            (startH, startM, startS, startMS) = timeBits[0].replace(',',' ').replace(':',' ').split()
            (endH, endM, endS, endMS) = timeBits[1].replace(',',' ').replace(':',' ').split()
            startTimeMS = (int(startH) * 3600 + int(startM) * 60 + int(startS)) * 1000 + int(startMS)
            endTimeMS = (int(endH) * 3600 + int(endM) * 60 + int(endS)) * 1000 + int(endMS)
            timeStarts.append(startTimeMS)
            timeEnds.append(endTimeMS)
        elif i % 4 == 3:
            words.append(line)

    wordResultsJsonOutput = [{"word": t, "startTime": s, "endTime": e} for t, s, e in zip(words, timeStarts, timeEnds)]
    json_object = json.dumps(wordResultsJsonOutput, sort_keys=True, indent=4)
    # Writing to sample.json
    with open(jsonFileName, "w") as outfile:
        outfile.write(json_object)
