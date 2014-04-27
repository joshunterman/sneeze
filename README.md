sneeze
===============
Messing around with getting stuff for my fantasy baseball league with the yahoo api.

Installation
--------------
In a Python 2.7.6 virtualenv, I did this:
pip install rauth
pip install prettytable

Then I grabbed this:
python-yahooapi ( https://github.com/dkempiners/python-yahooapi  )

I had to make these tweaks to that:
diff --git a/yahooapi.py b/yahooapi.py
index 913fdb3..f0c9393 100644
--- a/yahooapi.py
+++ b/yahooapi.py
@@ -40,7 +40,7 @@ class YahooAPI:
                 f = open(tokenfile, "r")
                 self.saved_token = pickle.load(f)
                 f.close()
-            except IOError:
+            except (IOError,EOFError):
                 self.saved_token = None

         if (self.saved_token is not None and
@@ -116,4 +116,4 @@ class YahooAPI:
         if tdiff > self.access_token_lifetime - 60:
             self.refresh_access_token()

-        return self.session.get(request_str)
+        return self.session.get(request_str, params={'format': 'json'})

The default config points to a file named "keyfile" and a file named "tokenfile".
The keyfile needs some stuff in it (1 line - "<KEY> <SECRET>"). You need to get that from me or apply for your own Yahoo key.
The tokenfile should start empty.
The first time you try to run, since there's no token saved, you will be given a URL to follow in a browser and prompted for the result.
In the browser, once you click "Agree", Yahoo will give you some text.
Paste it at the prompt, hit return, and you should be good to go from now on.
The .gitignore file should keep the keyfile and tokenfile from getting pushed up to github.
The script also assumes there are directories named results and cache around to store stuff in.
