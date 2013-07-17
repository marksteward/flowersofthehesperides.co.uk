gen:
	env/bin/python env/bin/hyde gen

verbose:
	env/bin/python env/bin/hyde -v gen

serve:
	env/bin/python env/bin/hyde -v serve -p 8080

init:
	virtualenv -p python2.7 env
	env/bin/python env/bin/pip install -U distribute

update:
	env/bin/python env/bin/pip install -r requirements.txt


clean:
	rm -rf deploy
	rm -rf content/.thumbnails
