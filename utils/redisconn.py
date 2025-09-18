import redis

r = redis.Redis(host='localhost', port=6379, db=0)
my_dict = {'name': 'Alice', 'age': '30', 'city': 'New York'}
r.hset('user:1000', mapping=my_dict)

retrieved_dict = r.hgetall('user:1000')
print(retrieved_dict)
print(retrieved_dict.items())
retrieved_dict = {k.decode(): v.decode() for k, v in retrieved_dict.items()}

print(retrieved_dict)
