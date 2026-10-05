import json
from llm_sdk import Small_LLM_Model
from src.decoding import Decoding

# 1. load functions and tests
with open("data/input/functions_definition.json", "r") as f:
    functions = json.load(f)
with open("data/input/function_calling_tests.json", "r") as f:
    tests = json.load(f)

names = [func["name"] for func in functions]
params_by_name = {func["name"]: func["parameters"] for func in functions}

# 2. model + vocab (loaded once)
model = Small_LLM_Model()
with open(model.get_path_to_vocab_file(), "r") as f:
    vocab_dict = json.load(f)

# 3. base prompt (function list), built once
base_prompt = "Available functions:\n"
for func in functions:
    base_prompt += func["name"] + ": " + func["description"] + "\n"

# 4. one decoding per question
results = []
for test in tests:
    prompt = base_prompt + "\nRequest: " + test["prompt"] + "\n"
    ids = model.encode(prompt)[0].tolist()
    result_ids = Decoding.constrained_decoding(
        model, ids, vocab_dict, names, params_by_name
    )
    text = model.decode(result_ids[len(ids):])
    print(text)
    try:
        results.append(json.loads(text))
    except json.JSONDecodeError:
        print("Invalid JSON for:", test["prompt"])
