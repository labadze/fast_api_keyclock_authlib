# Oauthlib based Keycloak fast api Application

There is very, very simple keycloak implementation using oauthlib using fast api

## Keycloak setup

First run Keycloak:

Pull docker image from here:

[https://hub.docker.com/r/jboss/keycloak/](https://hub.docker.com/r/jboss/keycloak/)

run docker image

`docker run -p 8080:8080 -e KEYCLOAK_USER=admin -e KEYCLOAK_PASSWORD=admin jboss/keycloak`

Access instance on [http://localhost:8080](http://localhost:8080) using admin as username and admin as password

 - Create new realm
 - Create new client
 - Create new user

### In realm settings
    
Go to "Login" tab and enable user login (Everything else as you want)

### In client settings

 - In Settings tab change _Access Type_ to `confidential`
 - Also in Settings tab enable __Authorization Enabled__
 - And here __Valid Redirect URIs__ Add `http://localhost:8000/auth`

_Save changes_ and then get client secret from __Credentials__ tab

## In user settings

 - Make sure that user is enabled and email verified
 - Go to __Credentials__ tab and set password turn of __Temporary__

## How to set up app

 - Clone or download project `git clone`
 - Create virtual environment check [https://docs.python.org/3/library/venv.html](https://docs.python.org/3/library/venv.html)
 - Install everything from `requirements.txt` using command `pip install -r requirements.txt`
 - Set up envs or hardcode values

Check this params

        issuer = os.getenv('ISSUER', 'http://localhost:8080/auth/realms/fast-api-oauth-lib')
        client_id = os.getenv('CLIENT_ID', 'fast-api-oauth-lib')
        client_secret = os.getenv('CLIENT_SECRET', 'UB8uxVJFRoa30HFukKA1PePXhcBM8Dpt')
        oidc_discovery_url = f'{issuer}/.well-known/openid-configuration'
        callback_url = 'http://localhost:8000/auth'
        end_session_endpoint = f'{issuer}/protocol/openid-connect/logout'

In most cases you just need to change: client_id, client_secret and URL(s) but there are some other setting check lines from `15` to `35`.

## Time to run app

    `uvicorn run main:app --reload`
your app will run on [http://localhost:8000](http://localhost:8000)

## Folder stricture
    .
    ├── ...
    ├── tests                            # test folder
    │   ├── http_test.py                 # Http test same as e2e [integration]
    │   └── unit_test.py                 # Unit test (no needed)
    ├── .gitignore                       # Need for git
    ├── LICENSE                          # Standard license from upwork copied here
    ├── main.py                          # Programmatically everything nice happens here
    ├── README.md                        # you're here
    ├── requirements.txt                 # Installed packeges via pip are stored here.
    └── test_main.http                   # Http filte to execude tests