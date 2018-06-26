# soundz

Audio fingerprinting and identification in Python. [See the dev blog for more details](https://soundz.jakerunzer.com/).

## Build

This is a Python 3 application that uses [Pipenv](https://docs.pipenv.org/).

- Install the dependencies

```sh
> pipenv install
```

- Activate the shell

```sh
> pipenv shell
```

## Saving Songs

A PostgreSQL database is assumed to be running on port 5432 with the username and password being "soundz". The database url can be changed in `database.py`.

Songs can be added and used for later identication with 

```sh
> python save_songs.py FILE|DIRECTORY
```

where FILE is the relative or absolute path of an audio file and DIRECTORY is the relative or absolute path of an directory containing audio files. The only supported audio formats at the moment are mp3 and mp4.

## Identification

Audio identification is done using the microphone. The command

```sh
> python lookup.py
```

can be used to record and identify 10 seconds of audio. The amount of time can be changed in `lookup.py`
