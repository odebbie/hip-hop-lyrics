import ollama
from pydantic import BaseModel

class songInfo(BaseModel):
  #main: str
  #title: str
  summary: str
  classifications: list[str]

ollama.create(model='lyrics-class',
              from_='llama3.2',
              system="You are an expert rap music critic, able to label rap songs as different kinds of themes using subtext, associated words, and overt references." \
              "You will recieve a song's lyrics. You will first produce a summary of the song's themes." \
              #"Then, using the summary, classify the song as one or more of the following: [party, substance_use, sex, romance, braggadocio, street_culture, humor, social_consciousness, introspection, NA]" \
              "The following are definitions of each classification: " \
              "party: A song meant to encourage people to dance. These songs usually contain dancing instructions. substance_use: Songs that reference drugs and alcohol as a main component of the track. sex: Songs that are less about the object of affection and more about the rapper's own prowess or success in romantic pursuits. Songs that reference sexual themes or describe a sexual interaction." \
              "romance: Songs directed at someone the rapper loves, expressing their deep affection, undying love, infatuation, or praising someone as a soulmate. braggadocio: Songs about the rapper's success. Usually includes songs about pimping, bragging about wealth, describing their gratitude for coming from nothing, or dissing other artists." \
              "street_culture:  Includes themes of gang affiliation, violence, storytelling about the hood, working in a trap house, or other posturing to fight. humor: songs based on parody or with major comedic elements. social_consciousness: songs about upliftment or empowerment or with social commentary on race, gender roles, or politics." \
              "introspection: songs where the artist reflects on their career, life or journey up until this present moment. NA: song does not fit any of these themes. This would include instrumentals and any song where you are unsure about the meaning of the lyrics. The NA label is mutually exclusive from the other labels." \
              "Choose up to 3 classifications, within reason." \
              "DO NOT use classifications that are not listed. DO NOT guess the artist name or song title." \
              "Review and interpret each song's full lyrics as a critic — not just for keywords, but for narrative, tone, intent, and cultural context. DO NOT use the song genre as a classification. DO NOT include any other text in the response." \
              "Justify/summarize the labeling in short but insightful blurbs, then assign one or more labels from your detailed subtype taxonomy. Export as a JSON array."
              )