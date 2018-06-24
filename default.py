# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# This is a sample controller
# this file is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

import os
from os.path import basename
import face_recognition
from gluon import current
from gluon.serializers import json

# ---- example index page ----
def index():
    response.flash = T("Hello World")
    return dict(message=T('Welcome to web2py!'))

# ---- API (example) -----
#@auth.requires_login()
def api_get_user_email():
    if not request.env.request_method == 'GET': raise HTTP(403)
    return response.json({'status':'success', 'email':auth.user.email})

# ---- Smart Grid (example) -----
#@auth.requires_membership('admin') # can only be accessed by members of admin groupd
def grid():
    response.view = 'generic.html' # use a generic view
    tablename = request.args(0)
    if not tablename in db.tables: raise HTTP(403)
    grid = SQLFORM.smartgrid(db[tablename], args=[tablename], deletable=False, editable=False)
    return dict(grid=grid)

# ---- Embedded wiki (example) ----
def wiki():
    auth.wikimenu() # add the wiki to the menu
    return auth.wiki() 

#---Server API returning CLient request with enco---
def getCurrentSessionEncodings():
	standard = request.vars.standard
	#standard = 1
	result = db(db.std_image.standard==int(standard)).select(db.std_image.ALL)
	return json(result)
	#return standard

#@auth.requires_login()
def camera():
	if not session.curr_session:
		classes = db().select(db.standard.ALL)
		return dict(message="",students="",session=False,classes=classes)
	students = db().select(db.student.ALL)
	return dict(message=T('Capture Group Photo'),students=students,session=True,class_id=session.curr_session)

#@auth.requires_login()
def imageview():
	table = TABLE(THEAD(TR(TD("ID"),TD("Name"),TD("Image"))),_with='100%')
	students = db().select(db.student.ALL)
	for row in students:
		images = db(db.std_image.student == row.id).select(db.std_image.ALL)
		div_Img = DIV()
		for image in images:
			div_Img.append(IMG(_src=URL('default/download',image.picture),_class='profile'))
		table.append(TR(TD(row.id),TD(row.name),TD(div_Img)))
	return dict(message = table)

#@auth.requires_login()	
def upload():
	form = SQLFORM(db.std_image, deletable=True,upload=URL('download'))
	if form.process().accepted:
		image_path = os.path.join(request.folder, 'uploads', form.vars.picture)
		known_face_encoding = face_recognition.face_encodings(face_recognition.load_image_file(image_path))[0]
		db(db.std_image.id==form.vars.id).update(face_encoding=",".join(map(str,known_face_encoding)))
		db.commit()
		response.flash = 'form accepted'
	elif form.errors:
		response.flash = 'form has errors'
	return dict(message = form)

	
#@auth.requires_login()	
def upload1():
	form = SQLFORM(db.std_image, deletable=True,upload=URL('download'))
	if form.process().accepted:
		image_path = os.path.join(request.folder, 'uploads', form.vars.picture)
		known_face_encoding = face_recognition.face_encodings(face_recognition.load_image_file(image_path))[0]
		db(db.std_image.id==form.vars.id).update(face_encoding=",".join(map(str,known_face_encoding)))
		db.commit()
		response.flash = 'form accepted'
	elif form.errors:
		response.flash = 'form has errors'
	return dict(message = form)	
	
#@auth.requires_login()
def attendance():
	table = button = ""
	form = SQLFORM.factory(
		Field('class_name', requires = IS_IN_DB(db,db.standard.id, '%(name)s'), default=1),
		Field('start_date', 'datetime'),
		Field('end_date', 'datetime')
	)
	if form.process().accepted:
		class_name = form.vars.class_name
		start_date = form.vars.start_date
		end_date = form.vars.end_date
		button = BUTTON(T('CSV Export'),_class='btn btn-primary',_onClick="$('#attendance_table').tableExport({type:'csv',escape:'false'});")
		table = generateAttendanceTable(class_name,start_date,end_date)
		
	elif form.errors:
		response.flash = 'form has errors'

	return dict(message = DIV(form,button,table))

def generateAttendanceTable(class_id,start_date,end_date):
	students = db(db.student.standard==class_id).select(db.student.ALL)
	sessions = db((db.class_session.standard==class_id) & (db.class_session.start_time>start_date) & (db.class_session.start_time<end_date)).select(db.class_session.ALL)
	thead_tr = TR(TD("Name"))
	for session in sessions:
		thead_tr.append(TD(session.start_time.strftime('%b-%d %H:%M')))
	table = TABLE(THEAD(thead_tr),_class="table table-bordered table-striped", _id="attendance_table")
	for student in students:
		student_row = TR(TD(student.name))
		for session in sessions:
			attendance = db((db.attendance.student_id==student.id) & (db.attendance.session_id==session.id) ).select(db.attendance.ALL)
			student_row.append(TD("P" if attendance else "-"))
		table.append(student_row)
	return table
	
#@auth.requires_login()	
#@auth.requires_membership('admin')
def student():
	form = SQLFORM.grid(db.student, user_signature=False, deletable=True,upload=URL('download') ,create=True, editable=True)
	return dict(message = form)	
	
#@auth.requires_login()
#@auth.requires_membership('admin')
def standard():
	query=((db.standard.id >0))
	form = SQLFORM.grid(query=query, user_signature=False, deletable=True,upload=URL('download') ,create=True, editable=True)
	return dict(message = form)	
	
def test():
	return dict(message = "")	


# ---- Action for login/register/etc (required for auth) -----
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())

# ---- action to server uploaded static content (required) ---
@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)
