import json
import os
from llm_sdk import Small_LLM_Model
from src.decoding import Decoding

OUTPUT = "data/output/function_calls.json"

with open("data/input/functions_definition.json", "r") as f:
    functions = json.load(f)
with open("data/input/function_calling_tests.json", "r") as f:
    tests = json.load(f)

names = []
params_by_name = {}
for func in functions:
    names.append(func["name"])
    params_by_name[func["name"]] = func["parameters"]

model = Small_LLM_Model()
with open(model.get_path_to_vocab_file(), "r") as f:
    vocab_dict = json.load(f)

base_prompt = (
    "You convert a request into a function call as JSON.\n"
    "Rules:\n"
    "- Copy every string value exactly from the request "
    "(same words, same case).\n"
    "- Never invent a shorter or symbolic value: one asterisk "
    "means \"*\", not \"**\".\n"
    "- Use the parameter descriptions to know which part of the "
    "request goes where.\n\n"
    "Functions:\n" + json.dumps(functions, indent=2) + "\n\n"
    "Example:\n"
    "Request: Replace all dashes in 'a-b-c' with PLUS\n"
    '{"name": "fn_example", "parameters": '
    '{"text": "a-b-c", "old": "-", "new": "PLUS"}}\n'
)

results = []
for test in tests:
    prompt = base_prompt + "\nRequest: " + test["prompt"] + "\n"
    ids = model.encode(prompt)[0].tolist()
    result_ids = Decoding.constrained_decoding(
        model, ids, vocab_dict, names, params_by_name
    )
    text = model.decode(result_ids[len(ids):])
    entry = {"prompt": test["prompt"], "name": "", "parameters": {}}
    try:
        data = json.loads(text)
        entry["name"] = data["name"]
        entry["parameters"] = data["parameters"]
    except (json.JSONDecodeError, KeyError):
        print("Invalid JSON for:", test["prompt"])
    results.append(entry)

os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
with open(OUTPUT, "w") as f:
    json.dump(results, f, indent=2)
