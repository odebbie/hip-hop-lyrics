import json
import ast
from ollama import chat
from ollama import ChatResponse
from pydantic import BaseModel, ValidationError

with open(r"lyrics_gpt.json") as fd:
    data = [json.loads(line) for line in fd]

class songInfo(BaseModel):
  main: str
  title: str
  justification: str
  rap_song_subtype_label: list[str]

for i in data:

    response: ChatResponse = chat(
        model='lyrics-class',
        messages=[{'role': 'user', 'content': "main: " + str(i['main']) + " title: " + i['title'] + " lyrics: " + i['cleaned_lyrics']}],
        stream=False,
        format=songInfo.model_json_schema(),
        options={'temperature': 0}
    )

    try:
        d = songInfo.model_validate_json(response.message.content)
        d =  ast.literal_eval(response.message.content) #ValidationError
        d['id'] = i['id']

        with open('llm_class.json', 'a') as json_file:
            json.dump(d, json_file)
            json_file.write('\n')

        print("Saved: ", i['id'])

    except:
        print("Unable to save: ", i['id'])
        continue

