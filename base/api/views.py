
from rest_framework.decorators import api_view
from rest_framework.response import Response
from base.models import Room
from .serializers import RoomSerializer

@api_view(['GET']) # allow only get method to access API
def getRoutes(request):
    routes=[
        'GET /api',
        'GET /api/rooms',
        'GET /api/rooms/:id'
    ]
    return Response(routes)

@api_view(['GET'])
def getRooms(request):
    rooms=Room.objects.all()
    serializer=RoomSerializer(rooms, many=True) # many specify multiple object tp serialize
    return Response(serializer.data) #python object can not be return by response


@api_view(['GET'])
def getRoom(request, pk):
    room=Room.objects.get(id=pk)
    serializer=RoomSerializer(room, many=False)
    return Response(serializer.data)