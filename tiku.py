#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 @FileName: 强国题库.py
 @Date: 2020/12/2 10:30
 @Description:
"""
import json
import time

from bottle import route, run, static_file, request
import sqlite3


class DbTool:
	def __init__(self):
		self.db = sqlite3.connect('tiku.db')
		self.c = self.db.cursor()

	def close(self):
		"""
		关闭数据库
		"""
		self.c.close()
		self.db.close()

	def execute(self, sql, param=None):
		"""
		执行数据库的增、删、改
		sql：sql语句
		param：数据，可以是list或tuple，亦可是None
		retutn：成功返回True
		"""
		# print('sql=', sql, 'param=', param)
		try:
			if param is None:
				self.c.execute(sql)
			else:
				if type(param) is list:
					self.c.executemany(sql, param)
				else:
					self.c.execute(sql, param)
			count = self.db.total_changes
			self.db.commit()
		except Exception as e:
			print('Exception:', e)
			return False
		if count > 0:
			return True
		else:
			return False

	def query(self, sql, param=None):
		"""
		查询语句
		sql：sql语句
		param：参数,可为None
		retutn：成功返回True
		"""
		# print('sql=', sql, 'param=', param)
		if param is None:
			self.c.execute(sql)
		else:
			self.c.execute(sql, param)
		return self.c.fetchall()


@route("/<path:path>")
def callback(path):
	return static_file(path, "")  # 指定静态文件目录assets


@route('/datalist')
def index():
	return static_file('index.html', root='.')


@route('/insertOrUpdate', method=['POST'])
def insertOrUpdate():
	f = request.POST.decode('utf-8')
	question = f.get('question')
	answer = f.get('answer')
	print('question=', question, 'answer=', answer)
	t = time.strftime('%Y-%m-%d %H:%M:%S')
	db = DbTool()
	q = db.query('select * from tikuNet where question = "' + question + '" and answer = "' + answer + '"')
	if not len(q):
		result = db.execute('insert into tikuNet(question,answer,datetime) values (?,?,?)', (question, answer, t))
		return json.dumps(200 if result else 500)
	else:
		return json.dumps(202)


@route('/search', method=['GET'])
def search():
	keyword = request.GET.decode('utf-8').get('keyword', '')
	page = int(request.GET.decode('utf-8').get('page', 1))
	rows = int(request.GET.decode('utf-8').get('rows', 10))
	limit = (page - 1) * rows
	db = DbTool()
	total = db.query(
		'select count(*) from tikuNet where question like ' + '"%' + keyword + '%"' + 'or answer like ' + '"%' + keyword + '%"')
	result = db.query(
		'select * from tikuNet where question like ' + '"%' + keyword + '%"' + 'or answer like ' + '"%' + keyword + '%" LIMIT ' +
		str(limit) + ',' + str(rows))
	data = {'total': total[0][0], 'rows': []}
	for r in result:
		data['rows'].append({'id': r[0], 'question': r[1], 'answer': r[2], 'datetime': r[3]})
	return json.dumps(data)


@route('/searchRepeatData', method=['GET'])
def searchRepeatData():
	db = DbTool()
	# q = 'select * from tikuNet where question in (select  question  from  tikuNet  group  by  question  having  count(question) > 1)'
	q = 'select *  from  tikuNet  group  by  question  having  count(question) > 1'
	result = db.query(q)
	data = {'total': len(result), 'rows': []}
	for r in result:
		data['rows'].append({'id': r[0], 'question': r[1], 'answer': r[2], 'datetime': r[3]})
	return json.dumps(data)


@route('/deleteById', method=['GET'])
def deleteById():
	ids = request.query.decode('utf-8').getall('ids[]')
	if len(ids) == 1:
		ids = '(' + ids[0] + ')'
	else:
		ids = str(tuple(ids))
	db = DbTool()
	res = db.execute('delete from tikuNet where id in ' + ids)
	return json.dumps(200 if res else 500)


@route('/onekeyclear', method=['GET'])
def onekeyclear():
	sql = """
		DELETE 
		FROM
			tikuNet 
		WHERE
			( tikuNet.question,tikuNet.answer ) IN ( SELECT question,answer FROM tikuNet GROUP BY question,answer HAVING count( * ) > 1 ) 
			AND rowid NOT IN (
		SELECT
			min( rowid ) 
		FROM
			tikuNet 
		GROUP BY
			question,answer 
		HAVING
			count( * ) > 1)
	"""
	db = DbTool()
	res = db.execute(sql)
	return json.dumps(200 if res else 500)


run(host='0.0.0.0', port=8088)
# run(host='localhost', port=8088)
