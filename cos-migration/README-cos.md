
* COS data copy

The cos.py utility allows you to view, download, upload, and delete content from Cloud Object Storage.

** Prerequisites:

This utility requires the boto3 and botocore python modules, as well as a few of their dependencies.  Which dependcies depend on what your python installation already has installed.  In this tarball, there are directories that contain the necessary pre-requisites for python2 and anaconda3 (python3).

1) check which python you have <br>
   % python --version
2) check which pip (if any) you have <br>
   % which pip

If you have a python2.x version and don't have pip installed, you can install it via: <br>
  % sudo rpm -i python2/python2-pip*.rpm

To install the necessary python modules, I would suggest the following:
1) sudo -i   (become root, whichever means you use)
2) cd into either python2 or anaconda3 contained in this tarball, depending on the result of 'which python' above
3) umask 022   # this gives the modules the correct visibility to all users
3) pip install boto*.whl <br>
   This may have some failed dependencies, continue to include them (they should be in the same directory) until all dependencies are satisfied.<br>
   In this manner, we will not overwrite any exising modules.

** Credentials:

We now need to get our COS credentials from the https://cloud.ibm.com  dashboard:    dashboard -> storage -> pick the correct COS -> choose 'Service Credentials' from the left hand menu <br>

If there are existing credentials, it is important that they include a populated 'cos_hmac_keys' section.  If not, create new credentials, and check the 'include HMAC credential' box.<br>

Copy and paste the json credentials into a file (e.g.: /opt/tools/cos-migration/cred.json) on the server.<br>

Also, find and record the bucket name you will use for storage.  Buckets can be seen under the 'Buckets' section in the left hand menu.   Note:  if you create your own bucket, the name has to be globally unique across all of IBM's COS;  also, create all buckets in Dallas/US-south for fastest transfer rates to our environments.   <br>

** Usage:

   In general, you will invoke the cos script via: <br>

   1) /opt/tools/cos-migration/cos.py -c /opt/tools/cos-migration/cred.json -b bucket_name command <br>

   commands are: <br>
      list <br>
      upload filename <br>
      download objectname <br>
      delete objectname <br>
      listbuckets # still requires a bucket name but is ignored <br>

** Example:

  In the data migration case, we first upload DB2 export file to COS, then download it in another environment:

 1) from the source side (old environment): <br>
    % /opt/tools/cos-migration/cos.py -c /opt/tools/cos-migration/cred.json -b bucket_name upload <path-to>/export.tgz <br>

 2) we can then see it in COS, either from the UI or via: <br>
    % /opt/tools/cos-migration/cos.py -c /opt/tools/cos-migration/cred.json -b bucket_name list
   
 3) On the target side (new environment): <br>
    % /opt/tools/cos-migration/cos.py -c /opt/tools/cos-migration/cred.json -b bucket_name download export.tgz <br>
    

  