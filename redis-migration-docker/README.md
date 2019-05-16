
To build
   docker build -f Dockerfile-<platform> -t <tag> .
   docker tag .....
   docker push .....
   
To run
   locally) docker run -d [--name ***] <tag>
   or
   cloud) kubectl run redis-migration-tool --image=<tag>


Example migration workflow
---------------------------

WORKDIR /tmp
copy service credentials to /tmp/credentials.json
copy dump.rdb to /tmp/dump.rdb

# start local redis that reads the dump.rdb file
redis-service &    # uses port 6379

# test local redis
redis-cli
  dbsize


# create an stunnel to the redis cloud service
# we're going to use port 7000
./create-stunnel.py -c credentials.json -p 7000

# test the remote connection
redis-cli -p 7000
  auth PASSWORD (as shown by create-stunnel.py)
  dbsize
  !! if you're using a db other than 0 !!
  select 3
  !! if you need to clear the remote db before migration !!
  flushdb
  

# copy redis data from source to target  
# for the actual migration source and target db will be 0
# I've been using db=3 for the target (r2) db for testing

./sugariq-redis-migrate.py --help

./sugariq-redis-migrate.py -t 7000 -p <password> --target-db 3   # testing to cloud redis db 3

./sugariq-redis-migrate.py -t 7000 -p <password> --flushdb --danger  # copy to db 0, remove whatever was there






   

   