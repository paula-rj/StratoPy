from stratopy.remote_access import base

class Test_Connector(base.Connector):
    pass

#def test_connector():
#    a = Test_Connector()
    #if esto me tira error type error cant instanciate etc esta ok
#    return None

class Test_Connector(base.Connector):
     def get_endpoint(self):
        return None
     def _makequery(self,ep,date):
         return None
     def _download(self,query):
        return None
     def _parse_result(self,res):
        return None

a = Test_Connector()
#if lo instancia y esta todo bien then anda

#testeo goes
goesobj = base.Goes16()
goesobj.get_endpoint()
goesobj._makequery("a","b")
goesobj._download("gquery")
