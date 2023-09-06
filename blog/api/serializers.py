from rest_framework import serializers
from .models import NormalUser, GovBodyUser, GovBodyAddress, Blogs, Comments


# giv user signup
class GovSignupSeriaizers(serializers.ModelSerializer):
    class Meta:
        model = GovBodyUser
        fields = '__all__'



class GovBodyAddressSerializer(serializers.ModelSerializer):

    # excluding form is_valied() checking
    gov_body = serializers.CharField(required=False)
    class Meta:
        model = GovBodyAddress
        fields = '__all__'



# normal users
class NormalUserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = NormalUser
        fields = '__all__'



# blog post serializer
class BlogsSerializer(serializers.ModelSerializer):

    #forign key: excluding from is_valied() validation
    blogger = serializers.CharField(required=False)
    class Meta:
        model= Blogs
        fields = '__all__'



class GetCommentSerializer(serializers.ModelSerializer):

    blog_number = serializers.ReadOnlyField(source='blog_number.blog_number')
    class Meta:
        model = Comments
        fields = ['blog_number','commenter','parent','comment_text','comment_date','replay_set']



class GetBlogSerializer(serializers.ModelSerializer):

    comment_set = serializers.PrimaryKeyRelatedField(many=True,read_only=True)
    class Meta:
        model = Blogs
        fields = ['blog_number','blog_image','blog_descripton','blog_date','is_vote','comment_set']



class CommentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = '__all__'
        