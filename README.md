starks
============

## Quick Start

```
$ grep -rl 'starks' ./ |  xargs  sed -i "" -e "s/starks/foobar_robot/g"
$ grep -rl 'STARKS' ./ |  xargs  sed -i "" -e "s/STARKS/FOOBAR_ROBOT/g"
$ mv PROJECT foobar_robot
```

## Development

#### 1. Install pip

[Installing with get-pip.py](https://bootstrap.pypa.io/get-pip.py)

#### 2. Install virtualenv

`$ pip install virtualenv`

#### 3. Install pip-tools

`$ sudo pip install --upgrade pip`

`$ sudo pip install pip-tools`

#### 4. Create virtual environment

`$ virtualenv venv`

#### 5. Activate virtual environment

`$ . ./venv/bin/activate`

#### 6. Install dependencies

`$ pip install -r requirements.txt`

#### 7. Environment configuartion

`$ cp .env.sample .env`

Edit `.env` according to your envrionments.

#### 8. Start server

`$ honcho start`
