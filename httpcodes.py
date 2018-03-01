
def write_not_found(self):
    self.response.status = '404 Not Found'
def write_created(self):
    self.response.status = '201 Created'
def write_bad_request(self):
    self.response.status = '400 Bad Request'
def write_ok(self):
    self.response.status = '200 OK'
def write_no_content(self):
    self.response.status = '204 No Content'
def write_method_not_allowed(self):
    self.response.status = '405 Method Not Allowed'
def write_conflict(self):
    self.response.status = '409 Conflict'
def write_forbidden(self):
    self.response.status = '403 Forbidden'
