AssetHub
========

AssetHub is meant to be a place where artists could share their resources,
which they use in creative software. I call such resources `assets'. For
example, it can be:

* Brush presets
* Example files
* Textures
* Clipart
* Scripts for scriptable components of software
* and so on.

Business requirements, or what I wanted
---------------------------------------

Each creative free software project seem to have an idea of central repository,
where users could share example settings, or pieces of artwork, or whatever. We
all know, that when such a place exists, it can boost creative power of
community so much. One of most known examples is GitHub.

So I dream of `github for assets'. Ideally, this should be one giant site for
all projects, like GitHub is. But I am not an enterpreneur or manager of any
kind to create realistic business plans or something like that. And I
understand, that creating one place for all would require a lot of very
different people from different projects to talk together and to cooperate.
This is not very realistic at the first step. More realistic would be if each
project create it's own site for sharing assets. Some projects already do have
such sites, for example Blender Foundation has its own Cloud. But if each
project create its own site from scratch, it would be enormous waste of human
power, and enormous mess in interfaces of all kinds.

So the basic requirements are:

* There should be an engine for web applications of very special kind. It could
  be installed on one large site, or it could be installed on dozens of small
  sites.
* It should allow to share creative assets of different kinds.
* It should allow to search by complex criterias among thousands of assets.
* It should care of copyrights, licenses and legal stuff, because it is very
  sad when you download a texture to use in your project and then realize than
  it is not legal to use it in commercial projects.
* It should care of versions of a) assets themselves and b) software; because
  it is sad to download a brush and then understand that it is compatible only
  with SomeProgram v10.3 but you have only v9.8.
* To be really useful, the site should contain a lot of contents. For that, the
  site should become very popular among creative people, comparable with
  popularity of github among programmers. For that, it should be easy to use
  and easy to comunicate. It should understand all modern social web concepts,
  such as `comments', `liking', `following', and so on. It should not make
  people to have yet another account, but allow to use their accounts in G+ or
  Facebook or whatever else, if they want.
* For site to have lots of contents, it should be very easy to upload assets.
  The simplest way of doing that would be right from the creative application.
  For example, one could share brush preset for Krita by just pressing a button
  in Krita. For that, the site should have public and standard API so that it
  would be relatively easy to integrate any software with it.

Technical requirements, or how I think it could be done
-------------------------------------------------------

Since I want the engine to be useful for many projects, and for one very big
project, I think its implementation should be very straightforward and as easy
to maintain as possible. For that,

* It should use very popular programming language, so it will be always easy to
  find a man to maintan the code. I think Python is such a language.
* It should use very popular frameworks and libraries. I selected Django.

Features, or what is implemented currently
------------------------------------------

* Simple structure to store assets:
** The site contains several Applications (for example, Krita, Blender, MyPaint);
** Each Application has several Components (for example Krita can have Brushes and Gradients);
** Components contain assets.
** Supported set of applications and components is configured by site administrator.
* Each asset has the following set of attributes:
** Author, meaning the user who uploaded it to site;
** Original author, for case if user uploads asset which was created by another man;
** License; supported set of licenses is configured by site administrator.
** Title and notes; Markdown is supported for notes.
** Thumbnail image and data file.
** URL for author's site or something like that.
** Asset version (for example, brush pack version).
** Range of Application versions, with which the asset is compatible.
** Set of tags.
** Rating aka score aka votes number. Each user can vote for one asset not more than one time.
* Comments are supported for assets. Markdown is supported for comments.
* The user can `follow' other users and have a feed of assets uploaded by them.
* Authentication with G+ account (other social networks to be supported) and
  registration via usual 2-step process.
* Simple and advanced search of assets is implemented.
* Administration interface via standard Django admin features.
* REST API to list and upload assets. More complex REST API calls to be added.


License: BSD-3.

