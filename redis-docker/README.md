
To build
   docker build -f Dockerfile-<platform> -t <tag> .
   
To run
   docker run -d [--name ***] <tag>


WORKDIR /tmp
copy service credentials to /tmp
copy dump.rdb to /tmp/dump.rdb

# start local redis that reads the dump.rdb file
redis-service &    # uses port 6379

# create an stunnel to the redis cloud service
./create-stunnel.py -c credentials.json -p 7000

# test the connection
redis-cli -p 7000
  auth PASSWORD (as shown by create-stunnel.py)

# modify sugariq-redis-migrate.py to point to the correct source/target
# then run it
# for the actual migration source and target db will be 0
# I've been using db=3 for the target (r2) db for testing
./sugariq-redis-migrate.py






   

   