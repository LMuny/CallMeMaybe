from llm_sdk import Small_LLM_Model
from pydantic import BaseModel
import json


class Decoding(BaseModel):

    @staticmethod
    def _find_end(raw: str) -> int:
        i = 0
        while i < len(raw):
            if raw[i] == "\\":
                i += 2
                continue
            if raw[i] == '"':
                return i
            i += 1
        return -1

    @staticmethod
    def _get_number_pieces(vocab_dict: dict) -> tuple:
        digit_ids = set()
        for tok, tok_id in vocab_dict.items():
            if len(tok) == 1 and tok in "0123456789":
                digit_ids.add(tok_id)
        dot_id = vocab_dict["."]
        minus_id = vocab_dict["-"]
        return digit_ids, dot_id, minus_id

    @staticmethod
    def _allowed_number_ids(text: str,
                            digits_ids: set,
                            dot_id: int,
                            minus_id: int,
                            is_int: bool) -> set:

        if text == "":
            return digits_ids | {minus_id}
        if text == '-':
            return digits_ids
        if '.' in text or is_int:
            return digits_ids
        return digits_ids | {dot_id}

    @staticmethod
    def _choose(model: Small_LLM_Model,
                ids: list,
                vocab_dict: dict,
                id_to_token: dict,
                options: list) -> str:
        generated = ""
        while generated not in options:
            logits = model.get_logits_from_input_ids(ids)
            allowed_ids = set()
            for tok, tok_id in vocab_dict.items():
                candidate = generated + tok.replace("Ġ", " ")
                if any(o.startswith(candidate) for o in options):
                    allowed_ids.add(tok_id)
            for i in range(len(logits)):
                if i not in allowed_ids:
                    logits[i] = float("-inf")
            token = logits.index(max(logits))
            ids.append(token)
            generated += id_to_token[token].replace("Ġ", " ")
        return generated

    @staticmethod
    def constrained_decoding(
        model: Small_LLM_Model,
        ids: list,
        vocab_dict: dict,
        names: list,
        params_by_name: dict
    ) -> list:

        ids = list(ids)
        id_to_token = {}

        for tok, tok_id in vocab_dict.items():
            id_to_token[tok_id] = tok

        ids += model.encode('{"name": "')[0].tolist()

        generated = ""

        generated = Decoding._choose(model, ids, vocab_dict,
                                     id_to_token, names)

        ids += model.encode('", "parameters": {')[0].tolist()
        params = params_by_name[generated]

        first = True
        for key, spec in params.items():
            prefix = ('' if first else ', ') + '"' + key + '": '
            ids += model.encode(prefix)[0].tolist()
            first = False

            d_ids, dot_id, min_id = Decoding._get_number_pieces(vocab_dict)

            if spec["type"] in ("number", "integer"):
                text = ""
                is_int = spec["type"] == "integer"
                for _ in range(20):
                    allowed = Decoding._allowed_number_ids(
                        text, d_ids, dot_id, min_id, is_int)
                    logits = model.get_logits_from_input_ids(ids)
                    for i in range(len(logits)):
                        if i not in id_to_token:
                            logits[i] = float("-inf")
                    best = logits.index(max(logits))
                    has_digit = any(c.isdigit() for c in text)
                    if best not in allowed and has_digit:
                        break
                    for i in range(len(logits)):
                        if i not in allowed:
                            logits[i] = float("-inf")
                    token = logits.index(max(logits))
                    ids.append(token)
                    text += id_to_token[token]

                fix = ""
                if text in ("", "-") or text.endswith("."):
                    fix = "0"
                if not is_int and "." not in text + fix:
                    fix += ".0"
                if fix:
                    ids += model.encode(fix)[0].tolist()

            elif spec["type"] == "string":
                ids += model.encode('"')[0].tolist()
                start = len(ids)
                raw = ""
                for _ in range(100):
                    logits = model.get_logits_from_input_ids(ids)
                    for i in range(len(logits)):
                        if i not in id_to_token:
                            logits[i] = float("-inf")
                    token = logits.index(max(logits))
                    raw += (id_to_token[token]
                            .replace("Ġ", " ").replace("Ċ", "\n"))
                    end = Decoding._find_end(raw)
                    if end != -1:
                        raw = raw[:end]
                        break
                    ids.append(token)
                try:
                    json.loads('"' + raw + '"')
                except ValueError:
                    raw = json.dumps(raw)[1:-1]
                ids = ids[:start] + model.encode(raw + '"')[0].tolist()

            elif spec["type"] == "boolean":
                Decoding._choose(model, ids, vocab_dict,
                                 id_to_token, ["true", "false"])

        ids += model.encode('}}')[0].tolist()
        return ids
