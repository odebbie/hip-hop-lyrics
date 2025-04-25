import json
import csv
import ast
from ollama import chat
from ollama import ChatResponse
from pydantic import BaseModel, ValidationError

with open(r"lyrics_gpt.json") as fd:
    data = [json.loads(line) for line in fd]

with open(r"random_samples.json") as fd:
    samples = [json.loads(line) for line in fd]

class songInfo(BaseModel):
  #main: str
  #title: str
  summary: str
  party: bool
  substance_use: bool
  sex: bool
  romance: bool
  braggadocio: bool
  street_culture: bool
  humor: bool
  social_consciousness: bool
  introspection: bool
  NA: bool
  #classifications: list[str]


for i in data:

    response: ChatResponse = chat(
        model='lyrics-class',
        messages=[
        {"role": "user", "content": samples[9]['lyrics']},
        {"role": "assistant", "content": "{summary: 'talks about a woman who has a bodacious butt', party: True, substance_use: False, sex: True, romance: False, braggadocio: False, street_culture: False, humor: False, social_consciousness: False, introspection: False}" },
        {"role": "user", "content": samples[35]['lyrics']},
        {"role": "assistant", "content": "{summary: 'expresses longing for his romantic partner by showing that he is constantly daydreaming about her', party: False, substance_use: False, sex: False, romance: True, braggadocio: False, street_culture: False, humor: False, social_consciousness: False, introspection: False}"},
        {"role": "user", "content": samples[51]['lyrics']},
        {"role": "assistant", "content": "{summary: 'tells a story about a kid losing his life because he got involved with gangs', party: False, substance_use: False, sex: False, romance: False, braggadocio: False, street_culture: True, humor: False, social_consciousness: True, introspection: False}"},
        {"role": "user", "content": samples[48]['lyrics']},
        {"role": "assistant", "content": "{summary: 'describes his experience with being betrayed by friends, family and lovers. reflects on his past struggles', party: False, substance_use: False, sex: False, romance: False, braggadocio: False, street_culture: False, humor: False, social_consciousness: False, introspection: True}"},
        {'role': 'user', 'content': i['cleaned_lyrics']}
    ],
        stream=False,
        format=songInfo.model_json_schema(),
        options={'temperature': 0.75}
    )

    #print(response.message.content)

    try:
        songInfo.model_validate_json(response.message.content) #throws ValidationError if bad
        #d = ast.literal_eval(response.message.content) #doesnt handle the dictionary string very well
        d = json.loads(response.message.content)
        d['id'] = i['id']
        d['title'] = i['title']

        with open('llm_class.json', 'a') as json_file:
            json.dump(d, json_file)
            json_file.write('\n')

        print("Saved: ", i['id'])

    except Exception as e:
        print("Unable to save: ", i['id'], "\n Error: ", e)
        continue

