#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import webapp2
import jinja2
import cgi
from google.appengine.ext import db



template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
								autoescape = True)

class Post(db.Model):
	title = db.StringProperty()
	body = db.TextProperty()
	created = db.DateTimeProperty(auto_now_add =True)


class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)
	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)
	def render_error(self, error_code):
		self.error(error_code)
		self.response.write("Oopsie!!")
	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

class Blog(webapp2.RequestHandler):
	def get(self):
		body = db.GqlQuery("SELECT * from Post ORDER BY created DESC LIMIT 5")
		t = jinja_env.get_template("mainblog.html")
		content = t.render(body = body, error = self.request.get("error"))
		self.response.write(content)

class NewPost(webapp2.RequestHandler):
	def get(self):
		t = jinja_env.get_template("newpost.html")
		content = t.render(error = self.request.get("error"))
		self.response.write(content)
	
	def post(self):
		title = self.request.get("title")
		body = self.request.get("body")
		if (not title) or (not body) or title.strip()=="" or body.strip()=="":
			error = "Please complete your entry"
			self.redirect("newpost?error=" + cgi.escape(error))
		else:
			title_escaped = cgi.escape(title, quote=True)
			body_escaped = cgi.escape(body, quote = True)

			post = Post(title = title_escaped, body = body_escaped)
			post.put()
			id = post.key().id()
			self.redirect("/blog/%s" % (id))


class ViewPost(webapp2.RequestHandler):
	def get(self, id):
		post = Post.get_by_id(int(id))

		t = jinja_env.get_template("onepost.html")
		content = t.render(post = post)
		self.response.out.write(content)
			


app = webapp2.WSGIApplication([
    ('/', Blog),
    ('/blog/newpost', NewPost),
    (webapp2.Route('/blog/<id:\d+>', ViewPost))
], debug=True)
