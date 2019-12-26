from models import TableUser


class ServiceUser:
    def __init__(self):
        self.model = TableUser()

    def create(self, params):
        result = self.model.create(params["name"], params["email"], params["password"], params["type"])
        return result

    def reads(self, params):
        result = self.model.reads(params['email'])
        return result


