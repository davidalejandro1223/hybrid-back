import subprocess

if __name__ == "__main__":
    try:
        # run from /opt/spacebooking
        #subprocess.call("python ../manage.py loaddata ../fixtures/country.json",shell=True)
        subprocess.call("python ../manage.py loaddata ../fixtures/location.json",shell=True)
        #subprocess.call("python ../manage.py loaddata ../fixtures/users.json",shell=True)
        #subprocess.call("python ../manage.py loaddata ../fixtures/group.json",shell=True)

    except Exception as e:
        print('An error happened: "%s"' % str(e))
