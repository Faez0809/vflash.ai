import os
import app.services.groq_provider as groq_provider

api_key = groq_provider.get_search_key()
print("API Key retrieved:", api_key)
