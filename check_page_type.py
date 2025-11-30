
from api.index import supabase
page_id = '063be1eb-e729-499e-8e5d-f4eb35b291fe'
res = supabase.table('pages').select('page_type, project_id').eq('id', page_id).single().execute()
print(res.data)
