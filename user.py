# Copyright 2012 Hai Thanh Nguyen
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from datetime import datetime, timedelta
from google.appengine.ext import ndb
from utils import generate_random_string
from webapp2_extras.i18n import _lazy as _
import model

class UserModel(model.FormModel):
    username = ndb.StringProperty(verbose_name=_(u"Username"))
    display_name = ndb.StringProperty(verbose_name=_(u"Display Name"))
    password = model.PasswordProperty(verbose_name=_(u"Password"))
    email = ndb.StringProperty(verbose_name=_(u"Email"))
    created = ndb.DateTimeProperty(auto_now_add=True)
    verified = model.BooleanProperty(verbose_name=_(u"Verified"))
    _password_confirm = model.UnsavedProperty(verbose_name=_(u"Confirm Password"))

    def __init__(self, *args, **kwds):
        super(UserModel, self).__init__(*args, **kwds)

    def _validation(self):
        return {
                "username": {"required": (), "word": (), "unique": ()},
                "display_name": {"required": ()},
                "email": {"required": (), "email": (), "unique": ()},
                "password": {"required": (), "password": (), "min_length": (8,)},
                "_password_confirm": {"required": (), "confirm_password": (self.password,)},
                }


    def login(self):
        q = ndb.gql("SELECT password, verified FROM UserModel WHERE username = :1",
                    self.username).get()
        if not q: return 0
        if (model.PasswordProperty.do_hash(self.password) == q.password):
            if q.verified:
                self.key = q.key
                return 1
            else:
                return -1
        else: return 0

class UserCookieModel(ndb.Model):
    token = ndb.StringProperty()

"""Generate a random string for cookie validation"""
def generate_cookie_token():
    return generate_random_string(50)

"""Save userid and the token for cookie validation to the cookie and database"""
def save_cookie(handler, userkey, cookie_model=None):
    token = generate_cookie_token()
    cookie_value = userkey.urlsafe() + "|" + token
    expire = datetime.now() + timedelta(days=30)
    handler.response.set_cookie("_", cookie_value, expires = expire, httponly=True, overwrite=True)
    q = cookie_model if cookie_model else ndb.Key("UserCookieModel", userkey.id()).get()
    if not q:
        model = UserCookieModel(id=userkey.id(), token=token)
        model.put()
    else:
        q.token = token
        q.put()

"""A normal lightweight class, just to be used for the return of get_current_user"""
class UserInfo:
    def __init__(self, userkey, username, email):
        self.key = ndb.Key(urlsafe=userkey)
        self.username = username
        self.email = email

"""Get the current logged in user"""
def get_current_user(handler):
    username = handler.session.get("username", None)
    if username == None:
        value = handler.request.cookies.get("_", None)
        if value == None: return None
        l = value.split("|")
        key = l[0]
        token = l[1]
        userkey = ndb.Key(urlsafe=key)
        userid = userkey.id()
        q = ndb.Key("UserCookieModel", userid).get()
        if (not q) or (q.token != token):
            return None
        else:
            save_cookie(handler, userkey, q)
            usr = userkey.get()
            handler.session["userkey"] = key
            handler.session["username"] = usr.username
            handler.session["email"] = usr.email
            return UserInfo(key, usr.username, usr.email)
    else:
        return UserInfo(handler.session.get("userkey"), username, handler.session.get("email"))
