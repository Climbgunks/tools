
To connect to the cloud redis server:

     1) create a file containing the service credentials (in JSON format)
     2) run ./create-stunnel.py -c <cred_file> [-p localport]    # defaults to 6379
     3) redis-cli
     	AUTH <password>


