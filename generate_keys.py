import music_cloud_api as api
import pickle
import sys

print("Generating secret keys...")
secret_keys=[]
count=int(sys.argv[1])
for i in range(count):
    print("\r{}/{}({:.2%})".format(i+1,count,(i+1)/count),end="")
    secret_keys.append(api.generate_secpair())
open("keys","wb").write(pickle.dumps(secret_keys))
