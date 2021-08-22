
from App import LogManager

def TEST():


    from App import API
    C_API = API.Service()
    stSvc = C_API.StopService('CMS')

if __name__ == '__main__':
    TEST()