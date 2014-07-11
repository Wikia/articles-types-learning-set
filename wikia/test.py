#s = search.WikiaSearch()
#resp = s.query('ns:0', 0, 10, 'random_1+asc')
#print resp['response']['docs']
import api, search

a = api.DocumentProvider(search.WikiaSearch())
a.set_hub_filter("Entertainment,Gaming")
resp = a.generate_new_sample(10)




