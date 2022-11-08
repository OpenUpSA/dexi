import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, authentication
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.generic import ListView
from django.views.generic.edit import FormView
from django.shortcuts import redirect
from django.core import serializers
from django.utils import timezone
from django.db.models.functions import Lower
from django.core.paginator import Paginator
from django.db.models import Count, OuterRef, Subquery, Q

from .models import Project, Doc, Extraction, Entity, EntityFound, Reference
from .serializers import ProjectSerializer, ProjectPermissionSerializer, DocSerializer, ExtractionSerializer, EntitySerializer, EntityFoundSerializer, ReferenceSerializer

from .tasks_ocr import doc_ocr
from .tasks_extract_nlp import doc_extract_nlp
from .tasks_extract_reference import doc_extract_reference
from .tasks_extract_quick import url_extract_quick
        
# DOCS

class DocListApiView(APIView):
    
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]

    def get(self, request, *args, **kwargs):
        docs = Doc.objects.filter(project_id=kwargs.get('project_id'), user_id=request.user.id).order_by('id')
        serializer = DocSerializer(docs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):

        if request.data.get('action') == 'upload':

            files = request.data.getlist('file')
            
            for file in files:
                serializer = DocSerializer(data={ 
                    'file': file,
                    'name': file.name,
                    'type': file.content_type if file.content_type else None,
                    'project': kwargs.get('project_id'), 
                    'status': 1, 
                    'user': request.user.id
                })
                if serializer.is_valid():
                    serializer.save()
                else:
                    # What if one file bombs? 
                    # continue ?
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    
            return Response('Done', status=status.HTTP_201_CREATED)
        
        elif request.data.get('action') == 'convert':

            # Convert
            field_name_list = ['id','name','file','type','project','status','user']

            selected_docs = request.data.getlist('docs')
            docs = Doc.objects.filter(id__in=selected_docs[0].split(','))
            docs = docs.values(*field_name_list)
            
            for doc in docs:
                ocr = doc_ocr(doc['id'])

            return Response('Sent to worker for conversion', status=status.HTTP_200_OK)

        elif request.data.get('action') == 'new':
        
            data = {
                'name': request.data.get('name'),
                'description': request.data.get('description'),
                'project': kwargs.get('project_id'),
                'reference': request.data.get('extractor'),
                'user': request.user.id
            }

            serializer = ExtractionSerializer(data=data)
            
            if serializer.is_valid():
                extraction = serializer.save()

                return Response(serializer.data, status=status.HTTP_201_CREATED)


        elif request.data.get('action') == 'extract':

            # Extract
            field_name_list = ['id','name','file','type','project','status','user']

            selected_docs = request.data.getlist('docs')
            extraction_id = request.data.get('extraction_id')
            docs = Doc.objects.filter(id__in=selected_docs[0].split(','))
            docs = docs.values(*field_name_list)

            for doc in docs:
                if(request.data.get('extractor') == 'nlp'):
                    extract = doc_extract_nlp(doc['id'], extraction_id)
                else:
                    extract = doc_extract_reference(doc['id'], extraction_id)
    
            return Response('Extraction Done - Maybe', status=status.HTTP_200_OK)

        elif request.data.get('action') == 'move':
                
                # Move
                field_name_list = ['id','name','file','type','project','status','user']
    
                selected_docs = request.data.getlist('docs')
                docs = Doc.objects.filter(id__in=selected_docs[0].split(','))
                docs = docs.values(*field_name_list)
    
                for doc in docs:
                    Doc.objects.filter(id=doc['id']).update(project=request.data.get('project'))
    
                return Response('Moved', status=status.HTTP_200_OK)

        elif request.data.get('action') == 'delete':
                
                # Delete
                field_name_list = ['id','name','file','type','project','status','user']
    
                selected_docs = request.data.getlist('docs')
                docs = Doc.objects.filter(id__in=selected_docs[0].split(','))
                docs = docs.values(*field_name_list)
    
                for doc in docs:
                    Doc.objects.filter(id=doc['id']).delete()
    
                return Response('Deleted', status=status.HTTP_200_OK)

        else:
            # No Action
            return Response('Invalid Action', status=status.HTTP_400_BAD_REQUEST)

class ExtractionListApiView(APIView):
    
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]

    def get(self, request, *args, **kwargs):
        
        if 'doc_id' in kwargs:
            entitiesFound = EntityFound.objects.filter(doc=kwargs.get('doc_id'))
            entities = Entity.objects.filter(id__in=entitiesFound.values('entity_id'))
            extraction = Extraction.objects.filter(id__in=entities.values('extraction_id'))

            serializer = ExtractionSerializer(extraction, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            extraction = Extraction.objects.filter(project_id=kwargs.get('project_id'), user_id=request.user.id).order_by('id')
            serializer = ExtractionSerializer(extraction, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
class EntityListApiView(APIView):
        
        permission_classes = [permissions.IsAuthenticated]
        authentication_classes = [authentication.TokenAuthentication]
    
        def get(self, request, *args, **kwargs):

            entities = Entity.objects.filter(extraction=kwargs.get('extraction_id')).order_by('entity')
            serializer = EntitySerializer(entities, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        def post(self, request, *args, **kwargs):
            if request.data.get('action') == 'delete':
                
                # Delete
                selected_entities = request.data.getlist('entities')

                entities = Entity.objects.filter(id__in=selected_entities[0].split(','))
    
                for entity in entities:
                    Entity.objects.filter(id=entity.id).delete()
    
                return Response('Deleted', status=status.HTTP_200_OK)

class EntityFoundListApiView(APIView):
        
        permission_classes = [permissions.IsAuthenticated]
        authentication_classes = [authentication.TokenAuthentication]
    
        def get(self, request, *args, **kwargs):

            if (kwargs.get('entity_id') != None):
                entitiesFound = EntityFound.objects.filter(entity=kwargs.get('entity_id')).order_by('id')
                serializer = EntityFoundSerializer(entitiesFound, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                entitiesFound = EntityFound.objects.filter(doc=kwargs.get('doc_id')).order_by('id')
                serializer = EntityFoundSerializer(entitiesFound, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            

class DocDetailApiView(APIView):
    
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, doc_id, user_id):
       
        try:
            return Doc.objects.get(id=doc_id, user = user_id)
        except Doc.DoesNotExist:
            return None

    
    def get(self, request, doc_id, *args, **kwargs):
        
        doc_instance = self.get_object(doc_id, request.user.id)
        
        serializer = DocSerializer(doc_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


# PROJECT

class ProjectListApiView(APIView):
    
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]

    
    def get(self, request, *args, **kwargs):
        
        projects = Project.objects.filter(user_id = request.user.id)
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    
    def post(self, request, *args, **kwargs):

        if request.data.get('action') == 'new':
        
            data = {
                'name': request.data.get('name'),
                'description': request.data.get('description'),
                'user': request.user.id
            }

            serializer = ProjectSerializer(data=data)
            
            if serializer.is_valid():
                project = serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif request.data.get('action') == 'permissions':

            print('Permissions')

            return Response({"res": "Permission"}, status=status.HTTP_200_OK)


class ProjectDetailApiView(APIView):
    
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, project_id, user_id):
        
        try:
            return Project.objects.get(id=project_id, user = user_id)
        except Project.DoesNotExist:
            return None

    
    def get(self, request, project_id, *args, **kwargs):
        
        project_instance = self.get_object(project_id, request.user.id)
        if not project_instance:
            return Response(
                {"res": "Project with id does not exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ProjectSerializer(project_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, project_id, *args, **kwargs):
        
        print('Project PUT')

        return Response({"res": "Project PUT"}, status=status.HTTP_200_OK)

    
    def delete(self, request, project_id, *args, **kwargs):
        
        project_instance = self.get_object(project_id, request.user.id)
        if not project_instance:
            return Response(
                {"res": "Project with id does not exists"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        project_instance.delete()
        return Response({"res": "Project deleted!"}, status=status.HTTP_200_OK)



#  References

class ReferenceListApiView(APIView):
    
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]

    
    def get(self, request, *args, **kwargs):
        
        references = Reference.objects.filter(user_id = request.user.id)
        serializer = ReferenceSerializer(references, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    
    def post(self, request, *args, **kwargs):

        if request.data.get('action') == 'upload':

            files = request.data.getlist('file')
            
            for file in files:
                serializer = ReferenceSerializer(data={ 
                    'file': file,
                    'name': file.name,
                    'type': file.content_type if file.content_type else None,
                    'user': request.user.id
                })
                if serializer.is_valid():
                    serializer.save()
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    
            return Response('Done', status=status.HTTP_201_CREATED)

        elif request.data.get('action') == 'delete':
                
            # Delete

            selected_references = request.data.getlist('references')
            references = Reference.objects.filter(id__in=selected_references[0].split(','))
            

            for reference in references:
                Reference.objects.filter(id=reference.id).delete()

            return Response('Deleted', status=status.HTTP_200_OK)

class QuickExtractApiView(APIView):
    
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]

    def post(self, request, *args, **kwargs):

        extract = url_extract_quick(request.data.get('url'))

        return Response(extract, status=status.HTTP_200_OK)