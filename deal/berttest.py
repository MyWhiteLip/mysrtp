import torch
from transformers import BertModel, BertTokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')
def getsimi_base_on_bert(sentenceA,sentenceB):
    text_dictA = tokenizer.encode_plus(sentenceA, add_special_tokens=True, return_attention_mask=True)
    input_ids = torch.tensor(text_dictA['input_ids']).unsqueeze(0)
    token_type_ids = torch.tensor(text_dictA['token_type_ids']).unsqueeze(0)
    attention_mask = torch.tensor(text_dictA['attention_mask']).unsqueeze(0)
    resA = model(input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids)
    afterA = resA[1].squeeze(0)
    text_dictB = tokenizer.encode_plus(sentenceB, add_special_tokens=True, return_attention_mask=True)
    input_ids = torch.tensor(text_dictB['input_ids']).unsqueeze(0)
    token_type_ids = torch.tensor(text_dictB['token_type_ids']).unsqueeze(0)
    attention_mask = torch.tensor(text_dictB['attention_mask']).unsqueeze(0)
    resB = model(input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids)
    afterB = resB[1].squeeze(0)
    return torch.cosine_similarity(afterA, afterB, dim=0).data.item()
seta= "hello, I am a chinese"
setb="we are pigs."
setc="hello, we are chinese"

print(getsimi_base_on_bert(seta,setb))
print(getsimi_base_on_bert(seta,setc))