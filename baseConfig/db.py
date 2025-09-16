from supabase import create_client
from baseConfig.config import SUPABASE_URL, SUPABASE_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Utility functions
def fetch_one(table: str, filters: dict):
    query = supabase.table(table).select("*")  # Dummy condition to start the query
    for k, v in filters.items():
        query = query.eq(k, v)
    
    final_response = {"data": None, "error": None}
    try:
        response = query.maybe_single().execute()
    except Exception as e:
        final_response["error"] = str(e)
    else:
        if response:
            final_response["data"] = response.data
    return final_response

def fetch_all(table: str, filters: dict = None):
    query = supabase.table(table).select("*")
    if filters:
        for k, v in filters.items():
            query = query.eq(k, v)
    final_response = {"data": None, "error": None}
    try:
        response = query.execute()
    except Exception as e:
        final_response["error"] = str(e)
    else:
        final_response["data"] = response.data
    return final_response

def insert(table: str, data: dict):
    final_response = {"data": "success", "error": None}
    try:
        supabase.table(table).insert(data).execute()
    except Exception as e:
        final_response["error"] = str(e)

    return final_response

def update(table, data: dict, filters: dict):

    query = supabase.table(table).update(data)

    for k, v in filters.items():
        query = query.eq(k, v)
    final_response = {"data": None, "error": None}
    try:
        response = query.execute()
    except Exception as e:
        final_response["error"] = str(e)
    else:
        final_response["data"] = response.data
    return final_response