from flask import Flask, render_template, url_for,request,make_response,send_file,redirect
import random as rd
import os
import os.path as pt
import plotly
import plotly.graph_objs as go
from chardet.universaldetector import UniversalDetector
import docx2txt
import collections as cl
from collections import OrderedDict
import time
import re
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
wsgi_app = app.wsgi_app
home_path=os.getcwd()
input_path=pt.join(home_path,'input')
output_path=pt.join(home_path,'output')
ALLOWED_EXTENSIONS=set(['txt','docx'])
limit=20
@app.route('/send_file')
def send_to():
    filename=pt.join(output_path,request.cookies.get('username')+'.html')
    send_file(filename,mimetype='text/html')
    return 
def get_encoding(filename):
    detector = UniversalDetector()
    with open(filename, 'rb') as fh:
        for line in fh:
            detector.feed(line)
            if detector.done:
                break
        detector.close()
    return detector.result
def make_graph(counter):
    x=list(counter.keys())
    y=list(counter.values())
    fig = go.Figure([go.Bar(x=x, y=y)])
    filename=pt.join(output_path,request.cookies.get('username')+'.html')    
    plotly.offline.plot(fig,filename=filename,auto_open=False)   
    #send_file(filename,mimetype='text/html')
    return send_file(filename,mimetype='text/html')
def make_graph_words(major_x,major_y,less_x,less_y):
    filename=pt.join(output_path,request.cookies.get('username')+'.html')
    less=go.Bar(x=less_x,y=less_y)
    major=go.Bar(x=major_x,y=major_y)
    fig=plotly.subplots.make_subplots(rows=2,cols=1,subplot_titles=('3 и менее','Более 3х'))
    fig.append_trace(less,1,1)
    fig.append_trace(major,2,1)
    fig['layout'].update(height=720,width=1366,title='Результаты')
    plotly.offline.plot(fig,filename=filename,auto_open=False)
    #send_file(filename,as_attachment=True,mimetype='text/html')
    #data={'filename':filename}
    return send_file(filename,as_attachment=False,mimetype='text/html')
def allowed_file(filename):
    if '.' in filename:    
        extension=filename.rsplit('.', 1)[1]#rsplit разбивает справа налево  str.rsplit(sep[, maxsplit])
        flag=extension in ALLOWED_EXTENSIONS    
        return [flag,extension]
    else:
        flag=False
        extension=''
        return [flag,extension]
def make_alphabet():    
    for i in range(0,10000):
        if chr(i) == 'А':
            first = i
        elif chr(i) == 'я':
            last = i
            break # выход из цикла
    alphabet=[]    
    for i in range(first,last+1):
        alphabet.append(chr(i))
    for i in range(0,10000):
        if chr(i) == 'Ё':
            first = i
        elif chr(i) == 'ё':
            last = i
            break # выход из цикла
    alphabet.insert(alphabet.index('е')+1,chr(last))
    alphabet.insert(alphabet.index('Е')+1,chr(first))
    print('make_alphabet --OK')
    return alphabet
def count_letters(text,alphabet):
    counter={} #Создаем словарь в который будем сохранять результат
    for letter in alphabet:
        n=text.count(letter)
        if n!=0:
            counter[letter]=n #Добавляем элемент в словарь "Буква = число со счетчика"
    print('count_letter --OK')
    return counter
def count_words(my_text):
    #print(my_text)
    text=''
    #for letter in my_text:
    #    if letter not in list('!@#$%^&*()_–-,+<,.>"''»«1234567890'):
    #        text+=letter
    text=re.sub(r'[!@#$%^&*()_\–\-,+<,.>»«1234567890]','',my_text)
    less=[]
    major=[]
    for word in text.split():
        if len(word)<4:
            less.append(word)
        else:
            major.append(word)
    major_dict=cl.Counter(major)
    less_dict=cl.Counter(less)
    sorted_major = sorted(major_dict.items(), key=lambda kv: kv[1])
    sorted_less = sorted(less_dict.items(), key=lambda kv: kv[1])
    major_dict=OrderedDict(sorted_major)
    less_dict=OrderedDict(sorted_less)  
    major_x=[]
    major_y=[]
    less_x=[]
    less_y=[]
    for item in major_dict:
        major_x.append(item)
        major_y.append(major_dict[item])
    major_x=major_x[-limit:]
    major_y=major_y[-limit:]
    for item in less_dict:
        less_x.append(item)
        less_y.append(less_dict[item])
    less_x=less_x[-limit:]
    less_y=less_y[-limit:]
    return make_graph_words(major_x,major_y,less_x,less_y)
def make_dirs(input_path,output_path):
	try:    
		os.mkdir(input_path)    
	except FileExistsError:
		print(input_path,'существует')
	try:    
		os.mkdir(output_path)
	except FileExistsError:
		print(output_path,'существует')
	return('!!!')
make_dirs(input_path,output_path)
@app.route('/')
@app.route('/index')
def index():
    username=request.cookies.get('username')
    #username=False
    if username:
        username=username.split('-')[0]
        data={'username':username}
        print('index to upload --OK')
        return render_template('upload.html',data=data)
    else:
        print('index to index --OK')
        return render_template('index.html')
@app.route('/set_cookie')
def set_cookie():
    user=request.args.get('user_name')
    cook_user=user+'-'+str(rd.randint(1000,9999))
    data={'username':user}
    resp = make_response(render_template('upload.html',data=data))
    resp.set_cookie('username', cook_user)# max_age=86400
    print('set_cookie --OK')
    return resp
	#return render_template('upload.html',data=data)
@app.route('/action',methods=['GET','POST'])
def action():
    print(request.files)
    if request.method == 'POST':        
        file = request.files['text']
        choise=request.form['count']
        print(choise)
        allowed=allowed_file(file.filename)
        if file and allowed[0]:
            if allowed[1]=='txt':
                filename=pt.join(input_path,request.cookies.get('username')+'.txt')
                file.save(
                      filename)
                encoding=get_encoding(filename)
                f=open(filename,'r',encoding=encoding['encoding'])
                text=f.read()
                f.close()
            if allowed[1]=='docx':
                filename=pt.join(input_path,request.cookies.get('username')+'.docx')
                file.save(filename)
                text=docx2txt.process(filename)           
            print('action good file --OK')
            if choise=='letters':                
                return make_graph(count_letters(text,make_alphabet()))
            if choise=='words':
                return count_words(text)
        else:
            print('action bad file --OK')
            return render_template('error.html')
    else:
        result = request.args.get['text']
        print('action bad method --OK')
        return result

@app.route('/clear')#не задействована 
def clear():
    time.sleep(10)
    os.remove(pt.join(input_path,request.cookies.get('username')+'.txt'))
    os.remove(pt.join(output_path,request.cookies.get('username')+'.html'))
    return render_template('index.html')
if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
