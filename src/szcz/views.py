from pyramid.view import view_config
from .models import DBSession, MyModel
from szcz.resources import szcz


class Context(object):
    """
    Default context factory.
    """

    def __init__(self, request):
        szcz.need()
        self.request = request


@view_config(route_name='home', renderer='templates/home.pt')
def my_view(request):
    one = DBSession.query(MyModel).filter(MyModel.name=='one').first()
    return {'one':one, 'project':'szcz'}
