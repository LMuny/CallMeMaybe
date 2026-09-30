import json
from llm_sdk import Small_LLM_Model
from src.decoding import Decoding

# 1. load functions and tests
with open("data/input/functions_definition.json", "r") as f:
    functions = json.load(f)
with open("data/input/function_calling_tests.json", "r") as f:
    tests = json.load(f)

names = []
for func in functions:
    names.append(func["name"])

# 2. model + vocab
model = Small_LLM_Model()
with open(model.get_path_to_vocab_file(), "r") as f:  # check the real name in the SDK
    vocab_dict = json.load(f)

# 3. build the prompt (function list + user request)
prompt = "Available functions:\n"
for func in functions:
    prompt += func["name"] + ": " + func["description"] + "\n"
prompt += "\nRequest: " + tests[0]["prompt"] + "\n"

ids = model.encode(prompt)[0].tolist()

# 4. run the decoding and print the result as text
result_ids = Decoding.constrained_decoding(ids, vocab_dict, names)
print(model.decode(result_ids))
