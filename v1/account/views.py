from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.authtoken.models import Token
from rest_framework import status
from .requests import getFirebaseUser
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from .serializers import UserSerializer,AccountSerializer


class GetCreateToken(APIView):
    #Excempt route from token authentication
    authentication_classes = ()
    permission_classes = ()

    def post(self,request):
        #Get IdToken
        token=request.data.get("token")
        if(not token):
            return Response({"detail":"Missing identity token"}, status=status.HTTP_400_BAD_REQUEST)

        #Get Firebase user
        firebase_user=getFirebaseUser(token)
        print(firebase_user)
        if(firebase_user.get("uid") and not User.objects.filter(username=firebase_user.get('uid')).exists()):
            uid = firebase_user.get('uid')
            email = firebase_user.get('email')
            phone = firebase_user.get('phone')
            name = firebase_user.get('name')
           
            #If login is regular(Google or Phone) create regular user
            if(firebase_user.get("provider") != "firebase" and (firebase_user.get("phone") or firebase_user.get("email"))):
                serializer = UserSerializer(data={"username":uid, "account":{"name":name, "phone":phone, "email":email,"account_type":"RG"}})
            else: #create demo user
                serializer = UserSerializer(data={"username":"demo_"+uid, "account":{"name":"Demo", "phone":phone, "email":email,"account_type":"DM"}})

            if(serializer.is_valid(raise_exception=True)):
                user = serializer.save()
                token, _ = Token.objects.get_or_create(user=user)
                return Response({"token":token.key})

        elif(firebase_user.get("uid") and User.objects.filter(username=firebase_user.get('uid')).exists()):
            uid = firebase_user.get('uid')
            email = firebase_user.get('email')
            phone = firebase_user.get('phone')
            name = firebase_user.get('name')

            user = get_object_or_404(User,username=uid)

            #Update account info
            AccountSerializer(user.account,data={"name":name, "phone":phone, "email":email},partial=True)

            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token":token.key})
        else:
            return Response({"detail":"Error signing in"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetUser(GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class=UserSerializer
    

    def get_queryset(self):
        return User.objects.filter(username=self.request.user.username)
    
    def get(self,request):
        user=self.get_queryset().first()
        return Response(self.get_serializer_class()(user).data)

#logout??
