import json

f = open('items.txt', 'r', encoding='utf-8')
json_string = f.read()
json_string = json_string.lower()
price_list = json.loads(json_string)
print(price_list)
for i in price_list:
    price_list[i] = 'minecraft:' + price_list[i]
print(price_list)
f.close()
f = open('items_ok.txt', 'w')
f.write(str(price_list))