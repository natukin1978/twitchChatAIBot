import sys

import google.generativeai as genai

from config_helper import readConfig

args = len(sys.argv)
if args <= 1:
    exit(1)
questions = sys.argv[1:]

config = readConfig()

genai.configure(api_key=config["google"]["geminiApiKey"])
genaiModel = genai.GenerativeModel(config["google"]["modelName"])
genaiChat = genaiModel.start_chat(history=[])
responseAI = genaiChat.send_message(config["basePrompt"])
print(responseAI.text)

for question in questions:
    responseAI = genaiChat.send_message(question)
    print(responseAI.text)
