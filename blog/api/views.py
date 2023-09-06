from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import AllowAny,IsAuthenticated
from .customauth import GovuserJwtAuthentication
from .serializers import BlogsSerializer, GetBlogSerializer, CommentsSerializer
from .models import Blogs
from rest_framework import viewsets
from rest_framework.decorators import action
# Create your views here.



"---------------------- GOV USER -----------------------------"

class Blog(APIView):

    serializer_class = BlogsSerializer
    authentication_classes = [GovuserJwtAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        """
        accept: blog details
        return: posted blog
        this method is posting a blog using the giver cridencials
        """

        # fetching gov user instance
        user = request.user

        # serializing data and validating
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # create new blog if the data is valied using the autherized gov user
        serializer.save(blogger=user)

        return Response(serializer.data,status=201)


    def get(self, request, fromat=None):
        """
        return blogs of the authenticated gov user
        """

        # fetch user and filter users blogs
        user = request.user
        blog_set = Blogs.objects.filter(blogger=user)
        print(blog_set)
        # serialize and return
        serializer = GetBlogSerializer(blog_set, many=True)
        print(serializer)
        return Response(serializer.data, status=200)



"------------------ PUBLIC BLOG OPERATIONS -------------------"


class GetBlogs(APIView):

    permission_classes = [AllowAny]
    serializer_class = GetBlogSerializer
    model = Blogs

    def get(self, request, format=None):
        """
        this fucntion is returning all blogs
        add filter options later
        """

        # fetch all blogs, serialize and return
        blog_set = self.model.objects.all()
        serializer = self.serializer_class(blog_set, many=True)
        return Response(serializer.data, status=200)


# add comment
class AddComment(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CommentsSerializer

    def post(self, request, fomat=None):
        """
        accept : blognumber
                parent-optional(replay to comment id if any)
                comment_text
        comment may be subcomment for a parant comment or a direct comment
        direct comment parent field defaultly set to null
        """

        # fetch data, serialize and validate it
        user = request.user
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # post comment
        try:
            serializer.save(commenter=user)
        except Exception as e:
            print("cant update comment")
            return Response({"details":"cant update comment"},status=500)
        
        return Response(serializer.data, status=201)
        
        



        
        
        


        
    
    






