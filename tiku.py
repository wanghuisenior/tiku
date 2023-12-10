#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 @FileName: 强国题库.py
 @Date: 2020/12/2 10:30
 @Description:
"""
import json
import time

import requests
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
			print('删除了0行')
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
	'''
	function updateToServer(question, answer) {
		console.info("开始上传")
		var res = http.post(server + "/insertOrUpdate", {"question": question, "answer": answer});
		//log(res.statusCode)
		var data = res.body.string();
		var d1 = JSON.parse(data);
		console.info(d1)
	}
	'''
	data = request.POST.decode('utf-8')
	question = data.get('question')
	answer = data.get('answer')
	t = time.strftime('%Y-%m-%d %H:%M:%S')
	db = DbTool()
	q = db.query('select * from tiku where question = "' + question + '" and answer = "' + answer + '"')
	if not len(q):
		flag = db.execute('insert into tiku(question,answer,datetime) values (?,?,?)',
						  (question, answer, t))
		if flag:
			return json.dumps({'code': 200, 'msg': '添加成功'})
	else:
		return json.dumps({'code': 202, 'msg': '失败，该题目已存在'})


@route('/search', method=['GET'])
def search():
	keyword = request.GET.decode('utf-8').get('keyword', '')
	page = int(request.GET.decode('utf-8').get('page', 1))
	rows = int(request.GET.decode('utf-8').get('rows', 10))
	limit = (page - 1) * rows
	db = DbTool()
	total = db.query(
		'select count(*) from tiku where question like ' + '"%' + keyword + '%"' + 'or answer like ' + '"%' + keyword + '%"')
	result = db.query(
		'select * from tiku where question like ' + '"%' + keyword + '%"' + 'or answer like ' + '"%' + keyword + '%" LIMIT ' +
		str(limit) + ',' + str(rows))
	data = {'total': total[0][0], 'rows': []}
	for r in result:
		# data['rows'].append({'id': r[0], 'question': r[1], 'answer': r[2], 'datetime': 0})
		data['rows'].append({'id': r[0], 'question': r[1], 'answer': r[2], 'datetime': r[3]})
	###################################将tikuNet表中的题库，插入到tiku表中###############
	# question = r[1]
	# answer = r[2]
	# db = DbTool()
	# q = db.query('select * from ' + 'tiku' + ' where question = "' + question + '" and answer = "' + answer + '"')
	# if not len(q):
	# 	result = db.execute('insert into ' + 'tiku' + '(question,answer) values (?,?)', (question, answer))
	# 	print(result)
	###################################将tikuNet表中的题库，插入到tiku表中###############
	return json.dumps(data)


@route('/searchRepeatData', method=['GET'])
def searchRepeatData():
	tableName = 'tiku'
	db = DbTool()
	q = 'SELECT * FROM ' + tableName + ' GROUP BY question HAVING count( question ) > 1'
	result = db.query(q)
	data = {'total': len(result), 'rows': []}
	for r in result:
		data['rows'].append({'id': r[0], 'question': r[1], 'answer': r[2], 'datetime': r[3]})
	return json.dumps(data)


@route('/deleteById', method=['GET'])
def deleteById():
	tableName = 'tiku'
	pwd = request.query.decode('utf-8').get('pwd')
	qid = request.query.decode('utf-8').get('id')
	ids = request.GET.decode('utf-8').get('ids[]')
	if pwd == 'wanghui':
		if qid:
			deleteQ(tableName, qid)
		elif ids:
			for item in json.loads(ids):
				deleteQ(tableName, str(item))
		else:
			print('error')
		return json.dumps(200)
	else:
		return json.dumps(500)


def deleteQ(tableName, qid):
	db = DbTool()
	# res = db.execute('delete from ' + tableName + ' where id in ' + ids)
	sql = 'delete from ' + tableName + ' where id = "' + qid + '"'
	res = db.execute(sql)
	return res


@route('/onekeyclear', method=['GET'])
def onekeyclear():
	# 一键清楚重复数据
	tableName = 'tiku'
	sql = """
		DELETE 
		FROM
			""" + tableName + """
		WHERE
			( """ + tableName + """.question,""" + tableName + """.answer ) IN ( SELECT question,answer FROM """ + tableName + """ GROUP BY question,answer HAVING count( * ) > 1 ) 
			AND rowid NOT IN (
		SELECT
			min( rowid ) 
		FROM
			""" + tableName + """ 
		GROUP BY
			question,answer 
		HAVING
			count( * ) > 1)
	"""
	db = DbTool()
	res = db.execute(sql)
	return json.dumps(200 if res else 500)


@route('/getAnswerByQuestion')
def getAnswerByQuestion():
	'''
	function getAnswerByQuestion(question) {
		var res = http.get(server + "/getAnswerByQuestion?question=" + question);
		if (res.statusCode == 200) {
			return res.body.string()
		} else {
			log("getAnswerByQuestion出问题");
		}
	}
	'''
	tableName = 'tiku'
	question = request.GET.decode('utf-8').get('question', '')
	if question.startswith("'") and question.startswith("'"):
		question = question[1: -1]
	if question.startswith('"') and question.startswith('"'):
		question = question[1: -1]
	db = DbTool()
	# select question,answer,datetime from tiku where question like "%aa%"or answer like "%aa%" LIMIT 0,10
	sql = 'select answer from ' + tableName + ' where question like "%' + question + '%"'
	result = db.query(sql)
	return result[0][0]


@route('/update', method=['POST'])
def update():
	f = request.POST.decode('utf-8')
	id = f.get('id')
	question = f.get('question')
	answer = f.get('answer')
	t = time.strftime('%Y-%m-%d %H:%M:%S')
	db = DbTool()
	result = db.execute('update tiku set question=?,answer=?,datetime =? where id =?',
						(question, answer, t, id))
	return json.dumps(200)


# q = db.query('select * from ' + tableName + ' where question = "' + question + '" and answer = "' + answer + '"')
# if not len(q):
# 	result = db.execute('insert into ' + tableName + '(question,answer,datetime) values (?,?,?)',
# 						(question, answer, t))
# 	return json.dumps(200 if result else 500)
# else:
# 	return json.dumps(202)

run(host='0.0.0.0', port=8088)
# run(host='localhost', port=8088)
