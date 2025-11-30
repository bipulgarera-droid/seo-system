
from api.index import supabase
page_id = '004cf9cf-0620-43b9-9516-b524f7bba4e3'
res = supabase.table('pages').select('page_type, url').eq('id', page_id).single().execute()
print(res.data)
