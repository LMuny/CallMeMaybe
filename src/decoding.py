from llm_sdk import Small_LLM_Model
from pydantic import BaseModel


class Decoding(BaseModel):

    @staticmethod
    def constrained_decoding(
        ids: list,
        vocab_dict: dict,
        names: list
    ) -> list:

        model = Small_LLM_Model()
        id_to_token = {}

        for tok, tok_id in vocab_dict.items():
            id_to_token[tok_id] = tok

        ids += model.encode('{"name": "')[0].tolist()

        generated = ""
        while generated not in names:
            logits = model.get_logits_from_input_ids(ids)

            for tok, tok_id in vocab_dict.items():
                candidate = generated + tok.replace("Ġ", " ")

                allowed = False
                for n in names:
                    if n.startswith(candidate):
                        allowed = True
                        break
                if not allowed:
                    logits[tok_id] = float("-inf")
            token = logits.index(max(logits))
            ids.append(token)
            generated += id_to_token[token].replace("Ġ", " ")

        ids += model.encode('", "parameters": {')[0].tolist()

        return ids
