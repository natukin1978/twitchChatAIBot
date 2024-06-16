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

for question in questions:
    responseAI = genaiModel.generate_content(question + "\n" + config["basePrompt"])
    print(responseAI.text)
