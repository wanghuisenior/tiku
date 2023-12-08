# tiku
在线题库服务器，基于python bottle轻量型web服务端框架，部署后可进行题库的增删改查，配合autojs可建设自己的在线题库服务器
## 使用说明
## 部署
1. 安装python3.7
2. 安装bottle：windows服务器 pip install bottle
3. 将代码上传至服务器，更改tiku.py文件最后一行port端口为服务器已经开通的端口号
4. 双击start.cmd，运行服务，出现<br>
Bottle v0.12.18 server starting up (using WSGIRefServer())...<br>
Listening on http://0.0.0.0:8088/<br>
Hit Ctrl-C to quit.<br>即为启动成功，出现其他异常表示失败
5. 打开浏览器访问 http://服务器IP:端口/datalist 即可打开题库管理页面。进行题库的增删改查（直接运行访问http://127.0.0.1:8000/datalist即可）
## 题库训练上传
1. 配合autojs脚本使用，在答题函数所在js添加以下函数，

	    function updateToServer(question,answer) {
            console.info("开始上传")
            var res = http.post("http://服务器IP:端口/insertOrUpdate", 
            {"question": question,"answer": answer});
            if (res.body.json()==200) {
                console.info("成功")
            }
    	}
    	
    	function getAnswerByQuestion(question) {
            var ans = http.get("http://服务器IP:端口/getAnswerByQuestion?question="+question);
            return ans;
        }
2. 在答题函数获取到问题和答案的地方调用该函数：updateToServer(question,answer)即可上传题库。
3. 修改端口：修改tiku.py 最后一行run(host='0.0.0.0', port=8088)，中的port即可修改对应的端口。
# 注：本项目为个人学习bottle编写，不得用于违法或商业用途，否则造成的一切后果自负！
