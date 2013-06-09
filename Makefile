gen:
	env/bin/python env/bin/hyde gen

verbose:
	env/bin/python env/bin/hyde -v gen

serve:
	env/bin/python env/bin/hyde serve

init:
	virtualenv env

update:
	env/bin/python env/bin/pip install -r requirements.txt


clean:
	rm -rf deploy
	rm -rf content/.thumbnails
