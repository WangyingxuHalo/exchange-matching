# def _init():
#     global trans_id
#     trans_id = 0
# def add_value():
#     trans_id += 1
# def get_value():
#     return trans_id

class transId:
    trans_id = 0
    def __init__(self, tmp):
        self.trans_id = tmp
        pass

    def add_value(self):
        self.trans_id += 1

    def get_value(self):
        return self.trans_id

   