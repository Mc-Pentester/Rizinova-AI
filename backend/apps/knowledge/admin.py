from django.contrib import admin 
from .models import KnowledgeDocument  
 
@admin.register(KnowledgeDocument) 
class KnowledgeDocumentAdmin(admin.ModelAdmin): 
    list_display = ('title', 'content', 'region')     
    list_filter = ('title', 'region', )     
     